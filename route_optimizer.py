"""
Módulo de otimização de rota para entregas.
Implementa múltiplos algoritmos: Nearest Neighbor, 2-opt e Algoritmo Genético.
"""

import math
import random
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import numpy as np


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


class RouteOptimizer:
    """Otimizador de rotas usando múltiplos algoritmos."""
    
    def __init__(self, stops: List[Stop]):
        """
        Inicializa o otimizador.
        
        Args:
            stops: Lista de paradas
        """
        self.stops = stops
        self.distance_matrix = self._calculate_distance_matrix()
        self.best_route = None
        self.best_distance = float('inf')
        self.optimization_time = 0
    
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
        total = 0
        for i in range(len(route) - 1):
            total += self.distance_matrix[route[i]][route[i + 1]]
        # Retorna ao ponto de partida
        total += self.distance_matrix[route[-1]][route[0]]
        return total
    
    def nearest_neighbor(self, start_index: int = 0) -> Tuple[List[int], float]:
        """
        Algoritmo Nearest Neighbor (guloso).
        Rápido mas não garante solução ótima.
        
        Args:
            start_index: Índice da parada inicial
            
        Returns:
            Tupla (rota, distância total)
        """
        unvisited = set(range(len(self.stops)))
        current = start_index
        route = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: self.distance_matrix[current][x])
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        distance = self._route_distance(route)
        return route, distance
    
    def two_opt(self, route: Optional[List[int]] = None, 
                max_iterations: int = 1000) -> Tuple[List[int], float]:
        """
        Algoritmo 2-opt para melhorar uma rota existente.
        Remove cruzamentos e melhora a solução iterativamente.
        
        Args:
            route: Rota inicial (se None, usa Nearest Neighbor)
            max_iterations: Número máximo de iterações
            
        Returns:
            Tupla (rota otimizada, distância total)
        """
        if route is None:
            route, _ = self.nearest_neighbor()
        else:
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
                    
                    # Calcula economia ao inverter segmento
                    old_distance = (self.distance_matrix[route[i-1]][route[i]] +
                                  self.distance_matrix[route[j]][route[(j+1) % len(route)]])
                    
                    new_distance = (self.distance_matrix[route[i-1]][route[j]] +
                                  self.distance_matrix[route[i]][route[(j+1) % len(route)]])
                    
                    if new_distance < old_distance:
                        # Inverte segmento
                        route[i:j+1] = reversed(route[i:j+1])
                        improved = True
                        break
                
                if improved:
                    break
        
        distance = self._route_distance(route)
        return route, distance
    
    def genetic_algorithm(self, population_size: int = 100, 
                         generations: int = 500,
                         mutation_rate: float = 0.02,
                         elite_size: int = 10) -> Tuple[List[int], float]:
        """
        Algoritmo Genético para otimização de rota.
        Mais lento mas pode encontrar soluções melhores.
        
        Args:
            population_size: Tamanho da população
            generations: Número de gerações
            mutation_rate: Taxa de mutação (0-1)
            elite_size: Número de indivíduos elite a preservar
            
        Returns:
            Tupla (rota otimizada, distância total)
        """
        # Cria população inicial
        population = []
        for _ in range(population_size):
            route = list(range(len(self.stops)))
            random.shuffle(route)
            population.append(route)
        
        best_route = population[0]
        best_distance = self._route_distance(best_route)
        
        for generation in range(generations):
            # Avalia fitness
            fitness = [(self._route_distance(route), route) for route in population]
            fitness.sort(key=lambda x: x[0])
            
            # Atualiza melhor solução
            if fitness[0][0] < best_distance:
                best_distance = fitness[0][0]
                best_route = fitness[0][1]
            
            # Seleciona elite
            elite = [route for _, route in fitness[:elite_size]]
            
            # Cria nova população
            new_population = elite.copy()
            
            while len(new_population) < population_size:
                # Seleção por torneio
                parent1 = self._tournament_selection(fitness)
                parent2 = self._tournament_selection(fitness)
                
                # Crossover (Order Crossover)
                child = self._order_crossover(parent1, parent2)
                
                # Mutação
                if random.random() < mutation_rate:
                    child = self._mutate(child)
                
                new_population.append(child)
            
            population = new_population[:population_size]
        
        return best_route, best_distance
    
    def _tournament_selection(self, fitness: List[Tuple[float, List[int]]],
                             tournament_size: int = 5) -> List[int]:
        """Seleção por torneio."""
        tournament = random.sample(fitness, min(tournament_size, len(fitness)))
        return min(tournament, key=lambda x: x[0])[1]
    
    def _order_crossover(self, parent1: List[int], parent2: List[int]) -> List[int]:
        """Order Crossover (OX)."""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        
        child = [-1] * size
        child[start:end] = parent1[start:end]
        
        pointer = end
        for city in parent2[end:] + parent2[:end]:
            if city not in child:
                if pointer >= size:
                    pointer = 0
                child[pointer] = city
                pointer += 1
        
        return child
    
    def _mutate(self, route: List[int]) -> List[int]:
        """Mutação por swap."""
        route = route.copy()
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
        return route
    
    def optimize(self, method: str = 'two_opt', **kwargs) -> Tuple[List[int], float]:
        """
        Otimiza rota usando método especificado.
        
        Args:
            method: 'nearest_neighbor', 'two_opt' ou 'genetic'
            **kwargs: Argumentos específicos do método
            
        Returns:
            Tupla (rota otimizada, distância total)
        """
        start_time = time.time()
        
        if method == 'nearest_neighbor':
            route, distance = self.nearest_neighbor(**kwargs)
        elif method == 'two_opt':
            route, distance = self.two_opt(**kwargs)
        elif method == 'genetic':
            route, distance = self.genetic_algorithm(**kwargs)
        else:
            raise ValueError(f"Método desconhecido: {method}")
        
        self.optimization_time = time.time() - start_time
        self.best_route = route
        self.best_distance = distance
        
        return route, distance
    
    def get_optimized_route_details(self) -> Dict:
        """Retorna detalhes da rota otimizada."""
        if self.best_route is None:
            return {}
        
        details = {
            'route_indices': self.best_route,
            'route_stops': [self.stops[i] for i in self.best_route],
            'total_distance': self.best_distance,
            'optimization_time': self.optimization_time,
            'number_of_stops': len(self.best_route),
        }
        
        # Calcula detalhes de cada segmento
        segments = []
        for i in range(len(self.best_route)):
            current_idx = self.best_route[i]
            next_idx = self.best_route[(i + 1) % len(self.best_route)]
            
            current_stop = self.stops[current_idx]
            next_stop = self.stops[next_idx]
            segment_distance = self.distance_matrix[current_idx][next_idx]
            
            segments.append({
                'from': current_stop.address,
                'to': next_stop.address,
                'distance': segment_distance,
                'from_id': current_stop.id,
                'to_id': next_stop.id,
            })
        
        details['segments'] = segments
        
        return details
    
    def compare_methods(self) -> Dict:
        """Compara todos os métodos de otimização."""
        results = {}
        
        # Nearest Neighbor
        start = time.time()
        nn_route, nn_distance = self.nearest_neighbor()
        nn_time = time.time() - start
        results['nearest_neighbor'] = {
            'distance': nn_distance,
            'time': nn_time,
            'route': nn_route,
        }
        
        # 2-opt
        start = time.time()
        opt_route, opt_distance = self.two_opt(nn_route)
        opt_time = time.time() - start
        results['two_opt'] = {
            'distance': opt_distance,
            'time': opt_time,
            'route': opt_route,
            'improvement': ((nn_distance - opt_distance) / nn_distance * 100),
        }
        
        # Genetic Algorithm (apenas se houver tempo)
        if len(self.stops) <= 50:  # Limita para rotas pequenas
            start = time.time()
            ga_route, ga_distance = self.genetic_algorithm(
                population_size=50,
                generations=200,
            )
            ga_time = time.time() - start
            results['genetic'] = {
                'distance': ga_distance,
                'time': ga_time,
                'route': ga_route,
                'improvement': ((nn_distance - ga_distance) / nn_distance * 100),
            }
        
        return results


def create_stops_from_dataframe(df) -> List[Stop]:
    """
    Cria lista de paradas a partir de DataFrame.
    
    Args:
        df: DataFrame com colunas: id, latitude, longitude, endereco, quantidade_pacotes
        
    Returns:
        Lista de objetos Stop
    """
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


# Import pandas apenas quando necessário
try:
    import pandas as pd
except ImportError:
    pd = None
