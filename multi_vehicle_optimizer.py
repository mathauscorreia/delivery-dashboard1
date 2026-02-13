"""
Módulo de otimização de rota para múltiplos veículos.
Implementa algoritmos de distribuição de carga e otimização simultânea.
"""

import math
import random
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class Vehicle:
    """Representa um veículo de entrega."""
    id: int
    name: str
    capacity: int  # Capacidade em número de pacotes
    current_load: int = 0
    routes: List[int] = None  # Índices das paradas
    total_distance: float = 0.0
    
    def __post_init__(self):
        if self.routes is None:
            self.routes = []
    
    def can_accept(self, packages: int) -> bool:
        """Verifica se o veículo pode aceitar mais pacotes."""
        return self.current_load + packages <= self.capacity
    
    def add_stop(self, stop_index: int, packages: int) -> bool:
        """Adiciona uma parada ao veículo."""
        if self.can_accept(packages):
            self.routes.append(stop_index)
            self.current_load += packages
            return True
        return False
    
    def get_utilization(self) -> float:
        """Retorna percentual de utilização da capacidade."""
        return (self.current_load / self.capacity * 100) if self.capacity > 0 else 0
    
    def reset(self):
        """Reseta o veículo."""
        self.routes = []
        self.current_load = 0
        self.total_distance = 0.0


@dataclass
class Stop:
    """Representa uma parada de entrega."""
    id: int
    latitude: float
    longitude: float
    address: str
    packages: int
    
    def distance_to(self, other: 'Stop') -> float:
        """Calcula distância até outra parada usando Haversine."""
        if not all([self.latitude, self.longitude, other.latitude, other.longitude]):
            return float('inf')
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # Raio da Terra em km


class MultiVehicleOptimizer:
    """Otimizador de rotas para múltiplos veículos com restrições de capacidade."""
    
    def __init__(self, stops: List[Stop], vehicles: List[Vehicle]):
        """
        Inicializa o otimizador.
        
        Args:
            stops: Lista de paradas
            vehicles: Lista de veículos
        """
        self.stops = stops
        self.vehicles = vehicles
        self.distance_matrix = self._calculate_distance_matrix()
        self.optimized_routes = None
        self.optimization_time = 0
        self.total_distance = 0
        self.unassigned_stops = []
    
    def _calculate_distance_matrix(self) -> np.ndarray:
        """Calcula matriz de distâncias entre todas as paradas."""
        n = len(self.stops)
        matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = self.stops[i].distance_to(self.stops[j])
        
        return matrix
    
    def _route_distance(self, route: List[int]) -> float:
        """Calcula distância total de uma rota."""
        if not route:
            return 0
        
        total = 0
        for i in range(len(route) - 1):
            total += self.distance_matrix[route[i]][route[i + 1]]
        # Retorna ao ponto de partida
        if len(route) > 0:
            total += self.distance_matrix[route[-1]][route[0]]
        return total
    
    def greedy_assignment(self) -> Dict:
        """
        Atribui paradas aos veículos usando algoritmo guloso.
        Ordena paradas por número de pacotes e tenta encaixar em veículos.
        
        Returns:
            Dicionário com atribuição de paradas
        """
        start_time = time.time()
        
        # Reseta veículos
        for vehicle in self.vehicles:
            vehicle.reset()
        
        # Ordena paradas por número de pacotes (maior primeiro)
        sorted_stops = sorted(enumerate(self.stops), 
                            key=lambda x: x[1].packages, 
                            reverse=True)
        
        self.unassigned_stops = []
        
        # Tenta atribuir cada parada
        for stop_idx, stop in sorted_stops:
            assigned = False
            
            # Tenta atribuir ao veículo com menor carga
            available_vehicles = [v for v in self.vehicles if v.can_accept(stop.packages)]
            
            if available_vehicles:
                # Escolhe o veículo com menor carga
                vehicle = min(available_vehicles, key=lambda v: v.current_load)
                vehicle.add_stop(stop_idx, stop.packages)
                assigned = True
            
            if not assigned:
                self.unassigned_stops.append(stop_idx)
        
        self.optimization_time = time.time() - start_time
        
        return self._get_routes_dict()
    
    def cluster_first_assignment(self) -> Dict:
        """
        Atribui paradas usando clustering geográfico.
        Agrupa paradas próximas e atribui a veículos.
        
        Returns:
            Dicionário com atribuição de paradas
        """
        start_time = time.time()
        
        # Reseta veículos
        for vehicle in self.vehicles:
            vehicle.reset()
        
        # Cria clusters iniciais (um por veículo)
        clusters = [[] for _ in range(len(self.vehicles))]
        
        # Atribui paradas aos clusters mais próximos
        for stop_idx, stop in enumerate(self.stops):
            # Encontra o cluster com menor distância média
            best_cluster = 0
            best_distance = float('inf')
            
            for cluster_idx, cluster in enumerate(clusters):
                if not cluster:
                    best_cluster = cluster_idx
                    best_distance = 0
                    break
                
                # Calcula distância média para o cluster
                avg_distance = sum(self.distance_matrix[stop_idx][c] for c in cluster) / len(cluster)
                
                if avg_distance < best_distance:
                    best_distance = avg_distance
                    best_cluster = cluster_idx
            
            clusters[best_cluster].append(stop_idx)
        
        # Atribui clusters aos veículos respeitando capacidade
        self.unassigned_stops = []
        
        for vehicle_idx, vehicle in enumerate(self.vehicles):
            cluster = clusters[vehicle_idx]
            
            for stop_idx in cluster:
                if not vehicle.add_stop(stop_idx, self.stops[stop_idx].packages):
                    self.unassigned_stops.append(stop_idx)
        
        self.optimization_time = time.time() - start_time
        
        return self._get_routes_dict()
    
    def optimize_routes(self, method: str = 'two_opt') -> Dict:
        """
        Otimiza as rotas de cada veículo.
        
        Args:
            method: 'two_opt' ou 'nearest_neighbor'
            
        Returns:
            Dicionário com rotas otimizadas
        """
        for vehicle in self.vehicles:
            if len(vehicle.routes) < 2:
                continue
            
            if method == 'two_opt':
                vehicle.routes = self._two_opt_route(vehicle.routes)
            elif method == 'nearest_neighbor':
                vehicle.routes = self._nearest_neighbor_route(vehicle.routes[0])
        
        return self._get_routes_dict()
    
    def _two_opt_route(self, route: List[int], max_iterations: int = 100) -> List[int]:
        """Aplica 2-opt a uma rota individual."""
        route = route.copy()
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            for i in range(1, len(route) - 2):
                for j in range(i + 1, len(route)):
                    if j - i == 1:
                        continue
                    
                    old_distance = (self.distance_matrix[route[i-1]][route[i]] +
                                  self.distance_matrix[route[j]][route[(j+1) % len(route)]])
                    
                    new_distance = (self.distance_matrix[route[i-1]][route[j]] +
                                  self.distance_matrix[route[i]][route[(j+1) % len(route)]])
                    
                    if new_distance < old_distance:
                        route[i:j+1] = reversed(route[i:j+1])
                        improved = True
                        break
                
                if improved:
                    break
        
        return route
    
    def _nearest_neighbor_route(self, start_idx: int) -> List[int]:
        """Cria rota usando Nearest Neighbor."""
        unvisited = set(range(len(self.stops)))
        current = start_idx
        route = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: self.distance_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return route
    
    def _get_routes_dict(self) -> Dict:
        """Retorna dicionário com informações das rotas."""
        self.total_distance = 0
        
        routes_info = {}
        for vehicle in self.vehicles:
            distance = self._route_distance(vehicle.routes)
            vehicle.total_distance = distance
            self.total_distance += distance
            
            routes_info[vehicle.id] = {
                'vehicle_name': vehicle.name,
                'route': vehicle.routes,
                'distance': distance,
                'load': vehicle.current_load,
                'capacity': vehicle.capacity,
                'utilization': vehicle.get_utilization(),
                'stops_count': len(vehicle.routes),
            }
        
        return {
            'routes': routes_info,
            'total_distance': self.total_distance,
            'unassigned_stops': self.unassigned_stops,
            'unassigned_count': len(self.unassigned_stops),
        }
    
    def get_detailed_routes(self) -> Dict:
        """Retorna detalhes completos das rotas."""
        detailed = {}
        
        for vehicle in self.vehicles:
            route_details = []
            
            for i, stop_idx in enumerate(vehicle.routes):
                stop = self.stops[stop_idx]
                
                # Calcula distância até próxima parada
                if i < len(vehicle.routes) - 1:
                    next_stop_idx = vehicle.routes[i + 1]
                    distance_to_next = self.distance_matrix[stop_idx][next_stop_idx]
                else:
                    # Última parada retorna ao início
                    distance_to_next = self.distance_matrix[stop_idx][vehicle.routes[0]]
                
                route_details.append({
                    'order': i + 1,
                    'stop_id': stop.id,
                    'address': stop.address,
                    'latitude': stop.latitude,
                    'longitude': stop.longitude,
                    'packages': stop.packages,
                    'distance_to_next': distance_to_next,
                })
            
            detailed[vehicle.id] = {
                'vehicle_name': vehicle.name,
                'capacity': vehicle.capacity,
                'load': vehicle.current_load,
                'utilization': vehicle.get_utilization(),
                'total_distance': vehicle.total_distance,
                'stops': route_details,
            }
        
        return detailed
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas da otimização."""
        total_capacity = sum(v.capacity for v in self.vehicles)
        total_load = sum(v.current_load for v in self.vehicles)
        total_stops = sum(len(v.routes) for v in self.vehicles)
        
        return {
            'total_vehicles': len(self.vehicles),
            'total_stops': total_stops,
            'unassigned_stops': len(self.unassigned_stops),
            'total_distance_km': self.total_distance,
            'average_distance_per_vehicle': self.total_distance / len(self.vehicles) if self.vehicles else 0,
            'total_capacity': total_capacity,
            'total_load': total_load,
            'overall_utilization': (total_load / total_capacity * 100) if total_capacity > 0 else 0,
            'optimization_time': self.optimization_time,
            'vehicles': [
                {
                    'id': v.id,
                    'name': v.name,
                    'stops': len(v.routes),
                    'load': v.current_load,
                    'capacity': v.capacity,
                    'utilization': v.get_utilization(),
                    'distance': v.total_distance,
                }
                for v in self.vehicles
            ]
        }
    
    def compare_assignment_methods(self) -> Dict:
        """Compara diferentes métodos de atribuição."""
        results = {}
        
        # Método 1: Greedy
        start = time.time()
        greedy_result = self.greedy_assignment()
        greedy_time = time.time() - start
        greedy_distance = greedy_result['total_distance']
        
        results['greedy'] = {
            'total_distance': greedy_distance,
            'unassigned': greedy_result['unassigned_count'],
            'time': greedy_time,
        }
        
        # Método 2: Cluster First
        start = time.time()
        cluster_result = self.cluster_first_assignment()
        cluster_time = time.time() - start
        cluster_distance = cluster_result['total_distance']
        
        results['cluster_first'] = {
            'total_distance': cluster_distance,
            'unassigned': cluster_result['unassigned_count'],
            'time': cluster_time,
        }
        
        # Otimiza ambas as soluções
        self.greedy_assignment()
        self.optimize_routes(method='two_opt')
        greedy_optimized = self.total_distance
        
        self.cluster_first_assignment()
        self.optimize_routes(method='two_opt')
        cluster_optimized = self.total_distance
        
        results['greedy_optimized'] = {
            'total_distance': greedy_optimized,
            'improvement': ((greedy_distance - greedy_optimized) / greedy_distance * 100) if greedy_distance > 0 else 0,
        }
        
        results['cluster_first_optimized'] = {
            'total_distance': cluster_optimized,
            'improvement': ((cluster_distance - cluster_optimized) / cluster_distance * 100) if cluster_distance > 0 else 0,
        }
        
        return results


def create_vehicles_from_config(config: List[Dict]) -> List[Vehicle]:
    """
    Cria lista de veículos a partir de configuração.
    
    Args:
        config: Lista de dicionários com 'id', 'name', 'capacity'
        
    Returns:
        Lista de objetos Vehicle
    """
    vehicles = []
    for item in config:
        vehicle = Vehicle(
            id=item['id'],
            name=item['name'],
            capacity=item['capacity']
        )
        vehicles.append(vehicle)
    return vehicles


def create_stops_from_dataframe(df) -> List[Stop]:
    """
    Cria lista de paradas a partir de DataFrame.
    
    Args:
        df: DataFrame com colunas: id, latitude, longitude, endereco, quantidade_pacotes
        
    Returns:
        Lista de objetos Stop
    """
    import pandas as pd
    
    stops = []
    
    for idx, row in df.iterrows():
        if pd.isna(row['latitude']) or pd.isna(row['longitude']):
            continue
        
        stop = Stop(
            id=int(row['id']) if 'id' in row else idx,
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            address=str(row['endereco']) if 'endereco' in row else f"Stop {idx}",
            packages=int(row['quantidade_pacotes']) if 'quantidade_pacotes' in row else 1,
        )
        stops.append(stop)
    
    return stops
