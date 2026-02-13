"""
Módulo de geocodificação para validação e obtenção de coordenadas de endereços.
Integra com Google Maps Geocoding API para enriquecer dados com latitude/longitude.
"""

import requests
import time
from typing import Dict, Optional, List, Tuple
from functools import lru_cache


class GeocoderService:
    """Serviço de geocodificação de endereços usando Google Maps API."""
    
    # Configurações
    GOOGLE_GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    CACHE_SIZE = 1000
    REQUEST_TIMEOUT = 10
    RATE_LIMIT_DELAY = 0.1  # 100ms entre requisições para respeitar rate limit
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o serviço de geocodificação.
        
        Args:
            api_key: Chave da API do Google Maps (opcional, pode ser None para modo offline)
        """
        self.api_key = api_key
        self.enabled = bool(api_key)
        self.last_request_time = 0
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.cache = {}
    
    def _respect_rate_limit(self):
        """Respeita o rate limit da API."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
    
    def _build_address_string(self, address_data: Dict[str, str]) -> str:
        """
        Constrói uma string de endereço para geocodificação.
        
        Args:
            address_data: Dicionário com dados do endereço
            
        Returns:
            String formatada para geocodificação
        """
        parts = []
        
        # Adiciona endereço
        if address_data.get('endereco'):
            parts.append(address_data['endereco'])
        
        # Adiciona número
        if address_data.get('numero') and address_data['numero'] != 's/n':
            parts.append(address_data['numero'])
        
        # Adiciona complemento
        if address_data.get('complemento'):
            parts.append(address_data['complemento'])
        
        # Adiciona bairro
        if address_data.get('bairro'):
            parts.append(address_data['bairro'])
        
        # Adiciona cidade e estado (padrão: São Paulo, SP)
        parts.append("São Paulo, SP, Brasil")
        
        return ", ".join(parts)
    
    def geocode(self, address_data: Dict[str, str]) -> Optional[Dict]:
        """
        Geocodifica um endereço usando Google Maps API.
        
        Args:
            address_data: Dicionário com dados do endereço
            
        Returns:
            Dicionário com coordenadas e informações, ou None se falhar
        """
        if not self.enabled:
            return None
        
        # Constrói string do endereço
        address_string = self._build_address_string(address_data)
        
        # Verifica cache
        if address_string in self.cache:
            return self.cache[address_string]
        
        try:
            # Respeita rate limit
            self._respect_rate_limit()
            
            # Faz requisição à API
            params = {
                'address': address_string,
                'key': self.api_key,
                'language': 'pt-BR'
            }
            
            response = requests.get(
                self.GOOGLE_GEOCODING_API_URL,
                params=params,
                timeout=self.REQUEST_TIMEOUT
            )
            
            self.request_count += 1
            
            # Verifica status da resposta
            if response.status_code != 200:
                self.error_count += 1
                return None
            
            data = response.json()
            
            # Verifica se encontrou resultados
            if data.get('status') != 'OK' or not data.get('results'):
                self.error_count += 1
                return None
            
            # Extrai primeiro resultado
            result = data['results'][0]
            
            # Extrai coordenadas
            location = result.get('geometry', {}).get('location', {})
            latitude = location.get('lat')
            longitude = location.get('lng')
            
            # Extrai componentes do endereço
            address_components = result.get('address_components', [])
            
            # Extrai informações úteis
            formatted_address = result.get('formatted_address', '')
            place_id = result.get('place_id', '')
            
            # Monta resultado
            geocode_result = {
                'latitude': latitude,
                'longitude': longitude,
                'formatted_address': formatted_address,
                'place_id': place_id,
                'status': 'OK',
                'address_components': address_components
            }
            
            # Armazena em cache
            self.cache[address_string] = geocode_result
            self.success_count += 1
            
            return geocode_result
            
        except requests.exceptions.Timeout:
            self.error_count += 1
            return None
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            print(f"Erro na requisição de geocodificação: {str(e)}")
            return None
        except Exception as e:
            self.error_count += 1
            print(f"Erro ao geocodificar: {str(e)}")
            return None
    
    def geocode_batch(self, addresses: List[Dict[str, str]], 
                     show_progress: bool = True) -> List[Optional[Dict]]:
        """
        Geocodifica múltiplos endereços em lote.
        
        Args:
            addresses: Lista de dicionários com dados de endereços
            show_progress: Se deve mostrar progresso
            
        Returns:
            Lista de resultados de geocodificação
        """
        results = []
        
        for i, address in enumerate(addresses):
            if show_progress and (i + 1) % 10 == 0:
                print(f"Geocodificando: {i + 1}/{len(addresses)}")
            
            result = self.geocode(address)
            results.append(result)
        
        return results
    
    def get_distance(self, lat1: float, lon1: float, 
                    lat2: float, lon2: float) -> float:
        """
        Calcula distância aproximada entre dois pontos usando fórmula de Haversine.
        
        Args:
            lat1, lon1: Coordenadas do primeiro ponto
            lat2, lon2: Coordenadas do segundo ponto
            
        Returns:
            Distância em quilômetros
        """
        from math import radians, cos, sin, asin, sqrt
        
        # Converte para radianos
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        
        # Fórmula de Haversine
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        
        return km
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas de geocodificação.
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'enabled': self.enabled,
            'total_requests': self.request_count,
            'successful': self.success_count,
            'failed': self.error_count,
            'cached_results': len(self.cache),
            'success_rate': (self.success_count / self.request_count * 100) 
                          if self.request_count > 0 else 0
        }


class MockGeocoder:
    """Geocodificador simulado para testes sem API key."""
    
    def __init__(self):
        """Inicializa o geocodificador simulado."""
        self.enabled = False
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        
        # Coordenadas simuladas para bairros conhecidos de São Paulo
        self.bairro_coordinates = {
            'centro': (-23.5505, -46.6333),
            'bela vista': (-23.5505, -46.6333),
            'sé': (-23.5505, -46.6333),
            'jardins': (-23.5670, -46.6500),
            'pinheiros': (-23.5615, -46.6833),
            'vila mariana': (-23.5870, -46.6170),
            'consolação': (-23.5450, -46.6550),
            'itaim bibi': (-23.5905, -46.6833),
            'vila olímpia': (-23.5950, -46.6950),
            'brooklin': (-23.6150, -46.6950),
            'moema': (-23.6100, -46.5850),
            'campo belo': (-23.6050, -46.5950),
            'indianópolis': (-23.6200, -46.5750),
            'cambuci': (-23.5650, -46.5850),
            'paraíso': (-23.5800, -46.5900),
            'pacaembu': (-23.5350, -46.6650),
            'jardim paulista': (-23.5750, -46.6650),
            'jardim paulistano': (-23.5900, -46.6900),
            'jardim ângela': (-23.7500, -46.7500),
            'república': (-23.5450, -46.6550),
        }
    
    def geocode(self, address_data: Dict[str, str]) -> Optional[Dict]:
        """
        Simula geocodificação com coordenadas aleatórias baseadas no bairro.
        
        Args:
            address_data: Dicionário com dados do endereço
            
        Returns:
            Dicionário simulado com coordenadas
        """
        self.request_count += 1
        
        bairro = address_data.get('bairro', '').lower().strip()
        
        import random
        
        # Tenta encontrar coordenadas para o bairro
        if bairro in self.bairro_coordinates:
            lat, lon = self.bairro_coordinates[bairro]
        else:
            # Se bairro nao encontrado, retorna coordenadas genericas de SP
            lat, lon = -23.5505, -46.6333
        
        # Adiciona pequena variacao para simular enderecos diferentes
        lat += random.uniform(-0.01, 0.01)
        lon += random.uniform(-0.01, 0.01)
        
        self.success_count += 1
        
        return {
            'latitude': float(lat),
            'longitude': float(lon),
            'formatted_address': f"{address_data.get('endereco', '')}, {address_data.get('numero', 's/n')} - {bairro}, Sao Paulo, SP",
            'place_id': f"mock_{id(address_data)}",
            'status': 'OK',
            'address_components': []
        }
    
    def geocode_batch(self, addresses: List[Dict[str, str]], 
                     show_progress: bool = True) -> List[Optional[Dict]]:
        """Geocodifica múltiplos endereços no modo simulado."""
        results = []
        
        for i, address in enumerate(addresses):
            if show_progress and (i + 1) % 10 == 0:
                print(f"Geocodificando (simulado): {i + 1}/{len(addresses)}")
            
            result = self.geocode(address)
            results.append(result)
        
        return results
    
    def get_distance(self, lat1: float, lon1: float, 
                    lat2: float, lon2: float) -> float:
        """Calcula distância usando fórmula de Haversine."""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        km = 6371 * c
        
        return km
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas simuladas."""
        return {
            'enabled': False,
            'total_requests': self.request_count,
            'successful': self.success_count,
            'failed': self.error_count,
            'cached_results': 0,
            'success_rate': (self.success_count / self.request_count * 100) 
                          if self.request_count > 0 else 0
        }
