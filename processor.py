"""
Módulo de processamento de planilhas de entregas.
Responsável por ler, agrupar e gerar relatórios.
"""

import pandas as pd
from typing import Dict
from normalizer import AddressNormalizer
from geocoder import MockGeocoder
import time


class DeliveryProcessor:
    """Classe responsável pelo processamento de entregas."""
    
    def __init__(self, geocoder=None):
            self.normalizer = AddressNormalizer()
            self.geocoder = geocoder or MockGeocoder()
            self.original_count = 0
            self.grouped_count = 0
            self.processing_time = 0
            self.geocoding_time = 0
        
    def read_excel(self, file_path: str) -> pd.DataFrame:
            try:
                df = pd.read_excel(file_path)
                df.columns = df.columns.str.strip()

                column_mapping = {
                    "Destination Address": "endereco",
                    "Zipcode/Postal code": "cep",
                    "City": "cidade",
                    "Latitude": "latitude",
                    "Longitude": "longitude",
                    "AT ID": "at_id",
                    "SPX TN": "spx_tn"
                }

                df.rename(columns=column_mapping, inplace=True)
                df.columns = df.columns.str.lower().str.strip()

                if "numero" not in df.columns and "endereco" in df.columns:
                    df["numero"] = df["endereco"].str.extract(r',\s*(\d+)')
                    df["numero"] = df["numero"].fillna("s/n")

                if "bairro" not in df.columns:
                    df["bairro"] = ""

                if "complemento" not in df.columns:
                    df["complemento"] = ""

                if "id" not in df.columns:
                    df["id"] = range(1, len(df) + 1)

                df = df.fillna("")

                for col in ["endereco", "numero", "bairro"]:
                    df[col] = df[col].astype(str)

                return df

            except Exception as e:
                raise Exception(f"Erro ao ler arquivo Excel: {str(e)}")
    
    def group_deliveries(self, df: pd.DataFrame, enable_geocoding: bool = True) -> pd.DataFrame:
        start_time = time.time()
        self.original_count = len(df)

        normalized_addresses = []
        address_keys = []

        for _, row in df.iterrows():
            address_data = {
                'endereco': row['endereco'],
                'numero': row['numero'],
                'complemento': row['complemento'],
                'bairro': row['bairro'],
            }

            normalized = self.normalizer.normalize_address(address_data)
            normalized_addresses.append(normalized)
            key = self.normalizer.create_address_key(normalized)
            address_keys.append(key)

        df['endereco_normalizado'] = [a['endereco'] for a in normalized_addresses]
        df['numero_normalizado'] = [a['numero'] for a in normalized_addresses]
        df['complemento_normalizado'] = [a['complemento'] for a in normalized_addresses]
        df['bairro_normalizado'] = [a['bairro'] for a in normalized_addresses]
        df['address_key'] = address_keys

        grouped = df.groupby('address_key').agg({
            'endereco_normalizado': 'first',
            'numero_normalizado': 'first',
            'complemento_normalizado': lambda x: ', '.join([str(c) for c in x if c]),
            'bairro_normalizado': 'first',
            'at_id': lambda x: ', '.join([str(i) for i in x]),
            'latitude': 'first',      # ✅ PRESERVA LATITUDE
            'longitude': 'first',     # ✅ PRESERVA LONGITUDE
        }).reset_index()


        grouped.rename(columns={
            'endereco_normalizado': 'endereco',
            'numero_normalizado': 'numero',
            'complemento_normalizado': 'complemento',
            'bairro_normalizado': 'bairro',
            'at_id': 'ids_agrupados'
        }, inplace=True)

        grouped['quantidade_pacotes'] = grouped['ids_agrupados'].apply(
            lambda x: len(x.split(', '))
        )

        grouped.drop(columns=['address_key'], inplace=True)

        if enable_geocoding:
            new_latitudes = []
            new_longitudes = []
            geocoded_flags = []
            formatted_addresses = []

            for _, row in grouped.iterrows():

                # mantém coordenadas existentes
                if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                    new_latitudes.append(row['latitude'])
                    new_longitudes.append(row['longitude'])
                    geocoded_flags.append(True)
                    formatted_addresses.append('')
                    continue

                address_data = {
                    'endereco': str(row.get('endereco', '')),
                    'numero': str(row.get('numero', '')),
                    'complemento': str(row.get('complemento', '')),
                    'bairro': str(row.get('bairro', '')),
                }

                result = self.geocoder.geocode(address_data)

                if result is not None:
                    new_latitudes.append(result.get('latitude'))
                    new_longitudes.append(result.get('longitude'))
                    formatted_addresses.append(result.get('formatted_address', ''))
                    geocoded_flags.append(True)
                else:
                    new_latitudes.append(None)
                    new_longitudes.append(None)
                    formatted_addresses.append('')
                    geocoded_flags.append(False)

            grouped['latitude'] = new_latitudes
            grouped['longitude'] = new_longitudes
            grouped['endereco_formatado'] = formatted_addresses
            grouped['geocodificado'] = geocoded_flags

        else:
            grouped['geocodificado'] = False

        return grouped


    
    def save_to_excel(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Salva todas as entregas em uma única aba,
        organizadas por bairro e ordem da rota.
        """
        try:
            # ordena por bairro e ordem da rota
            colunas_ordem = []

            if 'bairro' in df.columns:
                colunas_ordem.append('bairro')

            if 'ordem_rota' in df.columns:
                colunas_ordem.append('ordem_rota')

            if colunas_ordem:
                df = df.sort_values(colunas_ordem)

            # salva em UMA única aba
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

                df.to_excel(
                    writer,
                    index=False,
                    sheet_name='Entregas'
                )

                worksheet = writer.sheets['Entregas']

                # ajusta largura das colunas automaticamente
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
