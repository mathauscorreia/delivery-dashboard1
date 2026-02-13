"""
Extensão do app Flask com suporte a otimização multi-veículo.
Adiciona endpoints para otimizar rotas com múltiplos veículos.
"""

from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
from multi_vehicle_optimizer import (
    MultiVehicleOptimizer,
    create_vehicles_from_config,
    create_stops_from_dataframe
)
from processor_with_routing import DeliveryProcessorWithRouting
from geocoder import MockGeocoder
import json


app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/multi-vehicle/optimize', methods=['POST'])
def optimize_multi_vehicle():
    """
    Endpoint para otimizar rotas com múltiplos veículos.
    
    Esperado:
    - file: Arquivo Excel com entregas
    - vehicles: JSON com configuração de veículos
    - method: 'greedy' ou 'cluster'
    
    Retorna:
    - JSON com rotas otimizadas
    """
    try:
        # Valida arquivo
        if 'file' not in request.files:
            return jsonify({'error': 'Arquivo não fornecido'}), 400
        
        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Formato de arquivo inválido'}), 400
        
        # Valida configuração de veículos
        vehicles_json = request.form.get('vehicles')
        if not vehicles_json:
            return jsonify({'error': 'Configuração de veículos não fornecida'}), 400
        
        try:
            vehicles_config = json.loads(vehicles_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Configuração de veículos inválida'}), 400
        
        # Salva arquivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Lê dados
        df = pd.read_excel(filepath)
        
        # Filtra paradas geocodificadas
        df_geocoded = df[df['geocodificado'] == True].copy()
        
        if len(df_geocoded) < 2:
            return jsonify({'error': 'Não há paradas suficientes para otimizar'}), 400
        
        # Cria paradas e veículos
        stops = create_stops_from_dataframe(df_geocoded)
        vehicles = create_vehicles_from_config(vehicles_config)
        
        # Cria otimizador
        optimizer = MultiVehicleOptimizer(stops, vehicles)
        
        # Obtém método
        method = request.form.get('method', 'greedy')
        
        # Atribui paradas
        if method == 'cluster':
            result = optimizer.cluster_first_assignment()
        else:
            result = optimizer.greedy_assignment()
        
        # Otimiza rotas
        optimizer.optimize_routes(method='two_opt')
        
        # Obtém estatísticas
        stats = optimizer.get_statistics()
        detailed = optimizer.get_detailed_routes()
        
        # Prepara resposta
        response = {
            'success': True,
            'statistics': stats,
            'routes': {},
            'unassigned_stops': optimizer.unassigned_stops,
        }
        
        # Adiciona detalhes das rotas
        for vehicle_id, vehicle_detail in detailed.items():
            response['routes'][vehicle_id] = {
                'vehicle_name': vehicle_detail['vehicle_name'],
                'capacity': vehicle_detail['capacity'],
                'load': vehicle_detail['load'],
                'utilization': vehicle_detail['utilization'],
                'total_distance': vehicle_detail['total_distance'],
                'stops': vehicle_detail['stops'],
            }
        
        # Salva resultado em Excel
        output_file = os.path.join(OUTPUT_FOLDER, f'multi_vehicle_{filename}')
        
        routes_data = []
        for vehicle_id, vehicle_detail in detailed.items():
            for stop in vehicle_detail['stops']:
                routes_data.append({
                    'veiculo_id': vehicle_id,
                    'veiculo_nome': vehicle_detail['vehicle_name'],
                    'ordem': stop['order'],
                    'endereco': stop['address'],
                    'latitude': stop['latitude'],
                    'longitude': stop['longitude'],
                    'pacotes': stop['packages'],
                    'distancia_proxima_parada': stop['distance_to_next'],
                })
        
        df_routes = pd.DataFrame(routes_data)
        df_routes.to_excel(output_file, index=False)
        
        response['output_file'] = output_file
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/multi-vehicle/compare', methods=['POST'])
def compare_multi_vehicle_methods():
    """
    Endpoint para comparar diferentes métodos de otimização.
    
    Esperado:
    - file: Arquivo Excel com entregas
    - vehicles: JSON com configuração de veículos
    
    Retorna:
    - JSON com comparação de métodos
    """
    try:
        # Valida arquivo
        if 'file' not in request.files:
            return jsonify({'error': 'Arquivo não fornecido'}), 400
        
        file = request.files['file']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Formato de arquivo inválido'}), 400
        
        # Valida configuração de veículos
        vehicles_json = request.form.get('vehicles')
        if not vehicles_json:
            return jsonify({'error': 'Configuração de veículos não fornecida'}), 400
        
        try:
            vehicles_config = json.loads(vehicles_json)
        except json.JSONDecodeError:
            return jsonify({'error': 'Configuração de veículos inválida'}), 400
        
        # Salva arquivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Lê dados
        df = pd.read_excel(filepath)
        
        # Filtra paradas geocodificadas
        df_geocoded = df[df['geocodificado'] == True].copy()
        
        if len(df_geocoded) < 2:
            return jsonify({'error': 'Não há paradas suficientes para otimizar'}), 400
        
        # Cria paradas e veículos
        stops = create_stops_from_dataframe(df_geocoded)
        vehicles = create_vehicles_from_config(vehicles_config)
        
        # Cria otimizador
        optimizer = MultiVehicleOptimizer(stops, vehicles)
        
        # Compara métodos
        comparison = optimizer.compare_assignment_methods()
        
        # Formata resposta
        response = {
            'success': True,
            'comparison': comparison,
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/multi-vehicle/vehicles', methods=['GET'])
def get_default_vehicles():
    """
    Endpoint para obter configuração padrão de veículos.
    
    Retorna:
    - JSON com lista de veículos padrão
    """
    default_vehicles = [
        {'id': 1, 'name': 'Moto 1', 'capacity': 15},
        {'id': 2, 'name': 'Moto 2', 'capacity': 15},
        {'id': 3, 'name': 'Carro 1', 'capacity': 25},
        {'id': 4, 'name': 'Carro 2', 'capacity': 25},
        {'id': 5, 'name': 'Van', 'capacity': 40},
    ]
    
    return jsonify({
        'success': True,
        'vehicles': default_vehicles,
    }), 200


@app.route('/api/multi-vehicle/download/<filename>', methods=['GET'])
def download_multi_vehicle_file(filename):
    """
    Endpoint para download de arquivo de rotas otimizadas.
    
    Args:
        filename: Nome do arquivo
        
    Retorna:
        Arquivo Excel
    """
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
