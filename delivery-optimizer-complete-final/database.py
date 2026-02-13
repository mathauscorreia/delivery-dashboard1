"""
Módulo de banco de dados para armazenar histórico de otimizações.
Usa SQLite para persistência de dados.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class OptimizationDatabase:
    """Gerencia banco de dados de otimizações de rota."""
    
    def __init__(self, db_path: str = 'optimization_history.db'):
        """
        Inicializa banco de dados.
        
        Args:
            db_path: Caminho do arquivo SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Cria tabelas se não existirem."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de otimizações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                driver_name TEXT,
                optimization_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_deliveries INTEGER,
                total_stops INTEGER,
                total_distance REAL,
                optimization_method TEXT,
                total_vehicles INTEGER,
                overall_utilization REAL,
                processing_time REAL,
                status TEXT DEFAULT 'completed'
            )
        ''')
        
        # Tabela de veículos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id INTEGER NOT NULL,
                vehicle_id INTEGER,
                vehicle_name TEXT,
                capacity INTEGER,
                load INTEGER,
                utilization REAL,
                stops_count INTEGER,
                distance REAL,
                FOREIGN KEY (optimization_id) REFERENCES optimizations(id)
            )
        ''')
        
        # Tabela de paradas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id INTEGER NOT NULL,
                vehicle_id INTEGER,
                stop_order INTEGER,
                stop_id INTEGER,
                address TEXT,
                latitude REAL,
                longitude REAL,
                packages INTEGER,
                distance_to_next REAL,
                FOREIGN KEY (optimization_id) REFERENCES optimizations(id)
            )
        ''')
        
        # Tabela de comparações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                optimization_id INTEGER NOT NULL,
                method_name TEXT,
                total_distance REAL,
                unassigned_stops INTEGER,
                processing_time REAL,
                FOREIGN KEY (optimization_id) REFERENCES optimizations(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_optimization(self, 
                         file_name: str,
                         driver_name: Optional[str],
                         stats: Dict,
                         detailed_routes: Dict,
                         comparisons: Dict) -> int:
        """
        Salva uma otimização no banco de dados.
        
        Args:
            file_name: Nome do arquivo processado
            driver_name: Nome do motorista/rota
            stats: Dicionário com estatísticas
            detailed_routes: Dicionário com detalhes das rotas
            comparisons: Dicionário com comparações de métodos
            
        Returns:
            ID da otimização salva
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Salva otimização principal
            cursor.execute('''
                INSERT INTO optimizations 
                (file_name, driver_name, total_deliveries, total_stops, 
                 total_distance, optimization_method, total_vehicles, 
                 overall_utilization, processing_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_name,
                driver_name,
                0,  # Será atualizado se disponível
                stats.get('total_stops', 0),
                stats.get('total_distance_km', 0),
                'multi_vehicle',
                stats.get('total_vehicles', 0),
                stats.get('overall_utilization', 0),
                stats.get('optimization_time', 0),
            ))
            
            optimization_id = cursor.lastrowid
            
            # Salva informações dos veículos
            for vehicle_info in stats.get('vehicles', []):
                cursor.execute('''
                    INSERT INTO vehicles
                    (optimization_id, vehicle_id, vehicle_name, capacity, load,
                     utilization, stops_count, distance)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    optimization_id,
                    vehicle_info.get('id'),
                    vehicle_info.get('name'),
                    vehicle_info.get('capacity'),
                    vehicle_info.get('load'),
                    vehicle_info.get('utilization'),
                    vehicle_info.get('stops'),
                    vehicle_info.get('distance'),
                ))
            
            # Salva detalhes das paradas
            for vehicle_id, vehicle_detail in detailed_routes.items():
                for stop in vehicle_detail.get('stops', []):
                    cursor.execute('''
                        INSERT INTO stops
                        (optimization_id, vehicle_id, stop_order, stop_id,
                         address, latitude, longitude, packages, distance_to_next)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        optimization_id,
                        vehicle_id,
                        stop.get('order'),
                        stop.get('stop_id'),
                        stop.get('address'),
                        stop.get('latitude'),
                        stop.get('longitude'),
                        stop.get('packages'),
                        stop.get('distance_to_next'),
                    ))
            
            # Salva comparações de métodos
            for method_name, method_results in comparisons.items():
                cursor.execute('''
                    INSERT INTO comparisons
                    (optimization_id, method_name, total_distance, unassigned_stops, processing_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    optimization_id,
                    method_name,
                    method_results.get('total_distance', 0),
                    method_results.get('unassigned', 0),
                    method_results.get('time', 0),
                ))
            
            conn.commit()
            return optimization_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_optimization(self, optimization_id: int) -> Optional[Dict]:
        """
        Obtém uma otimização pelo ID.
        
        Args:
            optimization_id: ID da otimização
            
        Returns:
            Dicionário com dados da otimização
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM optimizations WHERE id = ?', (optimization_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            result = dict(row)
            
            # Obtém veículos
            cursor.execute('SELECT * FROM vehicles WHERE optimization_id = ?', (optimization_id,))
            result['vehicles'] = [dict(r) for r in cursor.fetchall()]
            
            # Obtém paradas
            cursor.execute('SELECT * FROM stops WHERE optimization_id = ? ORDER BY vehicle_id, stop_order', 
                          (optimization_id,))
            result['stops'] = [dict(r) for r in cursor.fetchall()]
            
            # Obtém comparações
            cursor.execute('SELECT * FROM comparisons WHERE optimization_id = ?', (optimization_id,))
            result['comparisons'] = [dict(r) for r in cursor.fetchall()]
            
            return result
            
        finally:
            conn.close()
    
    def get_all_optimizations(self, limit: int = 100) -> List[Dict]:
        """
        Obtém todas as otimizações.
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Lista de otimizações
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM optimizations 
                ORDER BY optimization_date DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict:
        """
        Obtém estatísticas gerais do banco de dados.
        
        Returns:
            Dicionário com estatísticas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Total de otimizações
            cursor.execute('SELECT COUNT(*) FROM optimizations')
            total_optimizations = cursor.fetchone()[0]
            
            # Distância total economizada
            cursor.execute('''
                SELECT SUM(total_distance) FROM optimizations
            ''')
            total_distance = cursor.fetchone()[0] or 0
            
            # Média de utilização
            cursor.execute('''
                SELECT AVG(overall_utilization) FROM optimizations
            ''')
            avg_utilization = cursor.fetchone()[0] or 0
            
            # Total de paradas processadas
            cursor.execute('SELECT COUNT(*) FROM stops')
            total_stops = cursor.fetchone()[0]
            
            # Total de veículos utilizados
            cursor.execute('SELECT COUNT(DISTINCT vehicle_id) FROM vehicles')
            total_vehicles = cursor.fetchone()[0]
            
            return {
                'total_optimizations': total_optimizations,
                'total_distance_km': round(total_distance, 2),
                'average_utilization': round(avg_utilization, 1),
                'total_stops_processed': total_stops,
                'total_vehicles_used': total_vehicles,
            }
            
        finally:
            conn.close()
    
    def get_optimization_history(self, days: int = 30) -> List[Dict]:
        """
        Obtém histórico de otimizações dos últimos N dias.
        
        Args:
            days: Número de dias
            
        Returns:
            Lista de otimizações
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM optimizations 
                WHERE optimization_date >= datetime('now', '-' || ? || ' days')
                ORDER BY optimization_date DESC
            ''', (days,))
            
            return [dict(row) for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def delete_optimization(self, optimization_id: int) -> bool:
        """
        Deleta uma otimização e seus dados associados.
        
        Args:
            optimization_id: ID da otimização
            
        Returns:
            True se deletado com sucesso
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Deleta em cascata
            cursor.execute('DELETE FROM stops WHERE optimization_id = ?', (optimization_id,))
            cursor.execute('DELETE FROM vehicles WHERE optimization_id = ?', (optimization_id,))
            cursor.execute('DELETE FROM comparisons WHERE optimization_id = ?', (optimization_id,))
            cursor.execute('DELETE FROM optimizations WHERE id = ?', (optimization_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def compare_optimizations(self, opt_id1: int, opt_id2: int) -> Dict:
        """
        Compara duas otimizações.
        
        Args:
            opt_id1: ID da primeira otimização
            opt_id2: ID da segunda otimização
            
        Returns:
            Dicionário com comparação
        """
        opt1 = self.get_optimization(opt_id1)
        opt2 = self.get_optimization(opt_id2)
        
        if not opt1 or not opt2:
            return {}
        
        distance_improvement = ((opt1['total_distance'] - opt2['total_distance']) / 
                               opt1['total_distance'] * 100) if opt1['total_distance'] > 0 else 0
        
        return {
            'file_1': opt1['file_name'],
            'date_1': opt1['optimization_date'],
            'distance_1': opt1['total_distance'],
            'utilization_1': opt1['overall_utilization'],
            'file_2': opt2['file_name'],
            'date_2': opt2['optimization_date'],
            'distance_2': opt2['total_distance'],
            'utilization_2': opt2['overall_utilization'],
            'distance_improvement': distance_improvement,
            'utilization_difference': opt2['overall_utilization'] - opt1['overall_utilization'],
        }
    
    def export_to_json(self, optimization_id: int) -> str:
        """
        Exporta uma otimização para JSON.
        
        Args:
            optimization_id: ID da otimização
            
        Returns:
            String JSON
        """
        opt = self.get_optimization(optimization_id)
        
        if not opt:
            return '{}'
        
        # Converte para formato JSON-serializable
        for key in ['optimization_date']:
            if key in opt and isinstance(opt[key], str):
                opt[key] = str(opt[key])
        
        return json.dumps(opt, indent=2, default=str)


def create_sample_data():
    """Cria dados de exemplo para testes."""
    db = OptimizationDatabase()
    
    # Dados de exemplo
    stats = {
        'total_stops': 41,
        'total_distance_km': 19.69,
        'total_vehicles': 5,
        'overall_utilization': 67.5,
        'optimization_time': 0.002,
        'vehicles': [
            {'id': 1, 'name': 'Moto 1', 'capacity': 15, 'load': 15, 'utilization': 100.0, 'stops': 6, 'distance': 7.36},
            {'id': 2, 'name': 'Moto 2', 'capacity': 15, 'load': 15, 'utilization': 100.0, 'stops': 7, 'distance': 2.12},
            {'id': 3, 'name': 'Carro 1', 'capacity': 25, 'load': 17, 'utilization': 68.0, 'stops': 9, 'distance': 2.66},
            {'id': 4, 'name': 'Carro 2', 'capacity': 25, 'load': 17, 'utilization': 68.0, 'stops': 9, 'distance': 2.89},
            {'id': 5, 'name': 'Van', 'capacity': 40, 'load': 17, 'utilization': 42.5, 'stops': 10, 'distance': 4.66},
        ]
    }
    
    detailed_routes = {
        1: {'vehicle_name': 'Moto 1', 'stops': []},
        2: {'vehicle_name': 'Moto 2', 'stops': []},
        3: {'vehicle_name': 'Carro 1', 'stops': []},
        4: {'vehicle_name': 'Carro 2', 'stops': []},
        5: {'vehicle_name': 'Van', 'stops': []},
    }
    
    comparisons = {
        'greedy': {'total_distance': 23.78, 'unassigned': 0, 'time': 0.002},
        'two_opt': {'total_distance': 19.69, 'unassigned': 0, 'time': 0.001},
    }
    
    db.save_optimization(
        file_name='MATHAUS_ROTAS_OTIMIZADAS.xlsx',
        driver_name='Mathaus Correia da Silva',
        stats=stats,
        detailed_routes=detailed_routes,
        comparisons=comparisons
    )
    
    print("✅ Dados de exemplo criados com sucesso!")


if __name__ == '__main__':
    create_sample_data()
