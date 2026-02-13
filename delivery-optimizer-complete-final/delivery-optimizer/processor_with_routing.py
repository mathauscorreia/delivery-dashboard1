"""
Extensão do processor com otimização de rota.
Integra normalização, geocodificação e otimização de rota em um pipeline único.
"""

from processor import DeliveryProcessor
from route_optimizer import RouteOptimizer, create_stops_from_dataframe
import pandas as pd
import time
from typing import Dict, Tuple


class DeliveryProcessorWithRouting(DeliveryProcessor):
    """Processador de entregas com otimização de rota integrada."""
    
    def __init__(self, geocoder=None):
        """Inicializa o processador com rota."""
        super().__init__(geocoder=geocoder)
        self.route_optimizer = None
        self.optimized_route = None
        self.route_optimization_time = 0
    
    def process_complete_pipeline(self, file_path: str, 
                                 route_method: str = 'two_opt',
                                 output_excel: str = None) -> Dict:
        """
        Executa pipeline completo: normalização → geocodificação → otimização de rota.
        
        Args:
            file_path: Caminho do arquivo Excel com entregas
            route_method: Método de otimização ('nearest_neighbor', 'two_opt', 'genetic')
            output_excel: Caminho para salvar resultado (opcional)
            
        Returns:
            Dicionário com resultados completos
        """
        pipeline_start = time.time()
        
        # 1. Lê arquivo
        df_original = self.read_excel(file_path)
        
        # 2. Agrupa e geocodifica
        df_grouped = self.group_deliveries(df_original, enable_geocoding=True)
        
        # 3. Otimiza rota
        df_optimized = self.optimize_route(df_grouped, method=route_method)
        
        # 4. Salva resultado (opcional)
        if output_excel:
            self.save_to_excel(df_optimized, output_excel)
        
        pipeline_time = time.time() - pipeline_start
        
        return {
            'original_count': self.original_count,
            'grouped_count': self.grouped_count,
            'optimized_count': len(df_optimized),
            'statistics': self.get_statistics(),
            'route_statistics': self._get_route_statistics(),
            'total_pipeline_time': pipeline_time,
            'dataframe': df_optimized,
        }
    
     def optimize_route(self, df: pd.DataFrame, method: str = 'two_opt') -> pd.DataFrame:

        start_time = time.time()

        df_geocoded = df[df['geocodificado'] == True].copy()

        if len(df_geocoded) < 2:
            return df

        stops = create_stops_from_dataframe(df_geocoded)
        self.route_optimizer = RouteOptimizer(stops)

        if method == 'nearest_neighbor':
            route, distance = self.route_optimizer.nearest_neighbor()
        elif method == 'two_opt':
            route, distance = self.route_optimizer.two_opt()
        elif method == 'genetic':
            route, distance = self.route_optimizer.genetic_algorithm()
        else:
            raise ValueError(f"Método desconhecido: {method}")

        self.optimized_route = route
        self.route_optimization_time = time.time() - start_time

        route_order = {idx: order for order, idx in enumerate(route, 1)}

        df_result = df_geocoded.copy()
        df_result['ordem_rota'] = df_result.index.map(lambda x: route_order.get(x, 0))

        df_result = df_result.sort_values('ordem_rota').reset_index(drop=True)
        df_result['distancia_total_rota'] = distance
        df_result['metodo_otimizacao'] = method

        return df_result
    
    def _get_route_statistics(self) -> Dict:
        """Retorna estatísticas de otimização de rota."""
        if self.route_optimizer is None or self.route_optimizer.best_distance == float('inf'):
            return {}
        
        return {
            'total_distance_km': self.route_optimizer.best_distance,
            'number_of_stops': len(self.route_optimizer.stops),
            'optimization_time': self.route_optimization_time,
            'optimization_method': 'two_opt',  # Padrão
        }
    
    def get_route_details(self) -> Dict:
        """Retorna detalhes completos da rota otimizada."""
        if self.route_optimizer is None or self.optimized_route is None:
            return {}
        
        return self.route_optimizer.get_optimized_route_details()
    
    def compare_route_methods(self) -> Dict:
        """Compara todos os métodos de otimização de rota."""
        if self.route_optimizer is None:
            return {}
        
        return self.route_optimizer.compare_methods()


def process_deliveries_complete(file_path: str, 
                               output_file: str = None,
                               route_method: str = 'two_opt',
                               api_key: str = None) -> Dict:
    """
    Função auxiliar para processar entregas com pipeline completo.
    
    Args:
        file_path: Caminho do arquivo Excel
        output_file: Caminho para salvar resultado
        route_method: Método de otimização de rota
        api_key: Chave da API do Google Maps (opcional)
        
    Returns:
        Dicionário com resultados
    """
    from geocoder import GeocoderService, MockGeocoder
    
    # Inicializa geocodificador
    if api_key:
        geocoder = GeocoderService(api_key=api_key)
    else:
        geocoder = MockGeocoder()
    
    # Cria processador
    processor = DeliveryProcessorWithRouting(geocoder=geocoder)
    
    # Executa pipeline
    results = processor.process_complete_pipeline(
        file_path=file_path,
        route_method=route_method,
        output_excel=output_file
    )
    
    return results
