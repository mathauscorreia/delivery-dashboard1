"""
Módulo de processamento de planilhas de entregas.
Responsável por ler, agrupar e gerar relatórios de otimização com geocodificação.
"""

import pandas as pd
from typing import Dict, List, Tuple
from normalizer import AddressNormalizer
from geocoder import MockGeocoder
import time


class DeliveryProcessor:
    """Classe responsável pelo processamento de entregas."""
    
    def __init__(self, geocoder=None):
        self.normalizer = AddressNormalizer()
        self.geocoder = geocoder or MockGeocoder()  # Usa MockGeocoder por padrão
        self.original_count = 0
        self.grouped_count = 0
        self.processing_time = 0
        self.geocoding_time = 0
        
    def read_excel(self, file_path: str) -> pd.DataFrame:
        """
        Lê arquivo Excel com dados de entregas.
        
        Args:
            file_path: Caminho do arquivo Excel
            
        Returns:
            DataFrame com os dados
        """
        try:
            df = pd.read_excel(file_path)
            
            # Normaliza nomes das colunas para minúsculas e remove espaços
            df.columns = df.columns.str.lower().str.strip()
            
            # Verifica se as colunas necessárias existem
            required_columns = ['endereco', 'numero', 'bairro']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
            
            # Adiciona coluna de complemento se não existir
            if 'complemento' not in df.columns:
                df['complemento'] = ''
            
            # Adiciona coluna de ID se não existir
            if 'id' not in df.columns:
                df['id'] = range(1, len(df) + 1)
            
            # Preenche valores vazios
            df = df.fillna('')
            
            # Converte todas as colunas para string
            for col in ['endereco', 'numero', 'complemento', 'bairro']:
                df[col] = df[col].astype(str)
            
            return df
            
        except Exception as e:
            raise Exception(f"Erro ao ler arquivo Excel: {str(e)}")
    
    def group_deliveries(self, df: pd.DataFrame, enable_geocoding: bool = True) -> pd.DataFrame:
        """
        Agrupa entregas por endereço normalizado e geocodifica.
        
        Args:
            df: DataFrame com entregas originais
            enable_geocoding: Se deve geocodificar os endereços
            
        Returns:
            DataFrame com entregas agrupadas e geocodificadas
        """
        start_time = time.time()
        
        self.original_count = len(df)
        
        # Lista para armazenar endereços normalizados
        normalized_addresses = []
        address_keys = []
        
        # Normaliza cada endereço
        for idx, row in df.iterrows():
            address_data = {
                'endereco': row['endereco'],
                'numero': row['numero'],
                'complemento': row['complemento'],
                'bairro': row['bairro'],
            }
            
            # Normaliza o endereço
            normalized = self.normalizer.normalize_address(address_data)
            normalized_addresses.append(normalized)
            
            # Cria chave para agrupamento
            key = self.normalizer.create_address_key(normalized)
            address_keys.append(key)
        
        # Adiciona colunas normalizadas ao DataFrame
        df['endereco_normalizado'] = [addr['endereco'] for addr in normalized_addresses]
        df['numero_normalizado'] = [addr['numero'] for addr in normalized_addresses]
        df['complemento_normalizado'] = [addr['complemento'] for addr in normalized_addresses]
        df['bairro_normalizado'] = [addr['bairro'] for addr in normalized_addresses]
        df['address_key'] = address_keys
        
        # Agrupa por chave de endereço
        grouped = df.groupby('address_key').agg({
            'endereco_normalizado': 'first',
            'numero_normalizado': 'first',
            'complemento_normalizado': lambda x: ', '.join([str(c) for c in x if c]),
            'bairro_normalizado': 'first',
            'id': lambda x: ', '.join([str(i) for i in x]),
            'endereco': 'first',  # Mantém endereço original para referência
            'numero': 'first',
            'bairro': 'first',
        }).reset_index()
        
        # Conta quantidade de pacotes por parada
        grouped['quantidade_pacotes'] = grouped['id'].apply(lambda x: len(x.split(', ')))
        
        # Renomeia colunas para saída
        grouped = grouped.rename(columns={
            'endereco_normalizado': 'endereco',
            'numero_normalizado': 'numero',
            'complemento_normalizado': 'complemento',
            'bairro_normalizado': 'bairro',
            'id': 'ids_agrupados',
        })
        
        # Geocodifica endereços agrupados
        if enable_geocoding:
            geocoding_start = time.time()
            
            geocode_results = []
            for idx, row in grouped.iterrows():
                address_data = {
                    'endereco': str(row['endereco']),
                    'numero': str(row['numero']),
                    'complemento': str(row['complemento']),
                    'bairro': str(row['bairro']),
                }
                
                result = self.geocoder.geocode(address_data)
                geocode_results.append(result)
            
            # Adiciona coordenadas ao DataFrame
            grouped['latitude'] = [r['latitude'] if r else None for r in geocode_results]
            grouped['longitude'] = [r['longitude'] if r else None for r in geocode_results]
            grouped['endereco_formatado'] = [r['formatted_address'] if r else '' for r in geocode_results]
            grouped['geocodificado'] = [r is not None for r in geocode_results]
            
            self.geocoding_time = time.time() - geocoding_start
        
        # Seleciona e ordena colunas finais
        if enable_geocoding:
            output_columns = [
                'endereco',
                'numero',
                'complemento',
                'bairro',
                'quantidade_pacotes',
                'ids_agrupados',
                'latitude',
                'longitude',
                'endereco_formatado',
                'geocodificado',
            ]
        else:
            output_columns = [
                'endereco',
                'numero',
                'complemento',
                'bairro',
                'quantidade_pacotes',
                'ids_agrupados',
            ]
        
        grouped = grouped[output_columns]
        
        # Ordena por quantidade de pacotes (maior para menor)
        grouped = grouped.sort_values('quantidade_pacotes', ascending=False).reset_index(drop=True)
        
        self.grouped_count = len(grouped)
        self.processing_time = time.time() - start_time
        
        return grouped
    
    def save_to_excel(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Salva DataFrame em arquivo Excel.
        
        Args:
            df: DataFrame a ser salvo
            output_path: Caminho do arquivo de saída
        """
        try:
            # Cria writer do Excel
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Entregas Otimizadas')
                
                # Ajusta largura das colunas
                worksheet = writer.sheets['Entregas Otimizadas']
                for idx, col in enumerate(df.columns, 1):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)
                    
        except Exception as e:
            raise Exception(f"Erro ao salvar arquivo Excel: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do processamento.
        
        Returns:
            Dicionário com estatísticas
        """
        stops_saved = self.original_count - self.grouped_count
        percentage_saved = (stops_saved / self.original_count * 100) if self.original_count > 0 else 0
        
        # Estimativa: 3 minutos por parada
        time_saved_minutes = stops_saved * 3
        
        return {
            'original_count': self.original_count,
            'grouped_count': self.grouped_count,
            'stops_saved': stops_saved,
            'percentage_saved': round(percentage_saved, 2),
            'time_saved_minutes': time_saved_minutes,
            'processing_time': round(self.processing_time, 3),
            'geocoding_time': round(self.geocoding_time, 3),
            'geocoder_stats': self.geocoder.get_statistics() if hasattr(self.geocoder, 'get_statistics') else {},
        }
