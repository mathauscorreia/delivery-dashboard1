"""
API Flask para dashboard com histórico de otimizações.
Fornece endpoints para visualizar e comparar otimizações.
"""

from flask import Flask, render_template, jsonify, request
from database import OptimizationDatabase
import json
from datetime import datetime

app = Flask(__name__)
db = OptimizationDatabase()


@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """
    Endpoint para obter estatísticas gerais do dashboard.
    
    Retorna:
    - JSON com estatísticas gerais
    """
    try:
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/history', methods=['GET'])
def get_optimization_history():
    """
    Endpoint para obter histórico de otimizações.
    
    Query Parameters:
    - days: Número de dias (padrão: 30)
    - limit: Número máximo de registros (padrão: 100)
    
    Retorna:
    - JSON com lista de otimizações
    """
    try:
        days = request.args.get('days', 30, type=int)
        limit = request.args.get('limit', 100, type=int)
        
        history = db.get_optimization_history(days=days)
        
        # Limita resultado
        history = history[:limit]
        
        return jsonify({
            'success': True,
            'count': len(history),
            'optimizations': history,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/optimization/<int:opt_id>', methods=['GET'])
def get_optimization_details(opt_id):
    """
    Endpoint para obter detalhes de uma otimização.
    
    Args:
        opt_id: ID da otimização
        
    Retorna:
    - JSON com detalhes completos da otimização
    """
    try:
        opt = db.get_optimization(opt_id)
        
        if not opt:
            return jsonify({'error': 'Otimização não encontrada'}), 404
        
        return jsonify({
            'success': True,
            'optimization': opt,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/compare', methods=['POST'])
def compare_optimizations():
    """
    Endpoint para comparar duas otimizações.
    
    Body:
    - opt_id1: ID da primeira otimização
    - opt_id2: ID da segunda otimização
    
    Retorna:
    - JSON com comparação
    """
    try:
        data = request.get_json()
        
        opt_id1 = data.get('opt_id1')
        opt_id2 = data.get('opt_id2')
        
        if not opt_id1 or not opt_id2:
            return jsonify({'error': 'IDs das otimizações não fornecidos'}), 400
        
        comparison = db.compare_optimizations(opt_id1, opt_id2)
        
        if not comparison:
            return jsonify({'error': 'Otimizações não encontradas'}), 404
        
        return jsonify({
            'success': True,
            'comparison': comparison,
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/delete/<int:opt_id>', methods=['DELETE'])
def delete_optimization(opt_id):
    """
    Endpoint para deletar uma otimização.
    
    Args:
        opt_id: ID da otimização
        
    Retorna:
    - JSON com confirmação
    """
    try:
        success = db.delete_optimization(opt_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Otimização deletada com sucesso',
            }), 200
        else:
            return jsonify({'error': 'Falha ao deletar otimização'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/export/<int:opt_id>', methods=['GET'])
def export_optimization(opt_id):
    """
    Endpoint para exportar uma otimização em JSON.
    
    Args:
        opt_id: ID da otimização
        
    Retorna:
    - JSON com dados da otimização
    """
    try:
        json_data = db.export_to_json(opt_id)
        
        if json_data == '{}':
            return jsonify({'error': 'Otimização não encontrada'}), 404
        
        return json_data, 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dashboard', methods=['GET'])
def dashboard_page():
    """
    Página principal do dashboard.
    
    Retorna:
    - HTML da página do dashboard
    """
    try:
        stats = db.get_statistics()
        recent_optimizations = db.get_optimization_history(days=30)[:10]
        
        return render_template('dashboard.html',
                             stats=stats,
                             recent_optimizations=recent_optimizations)
        
    except Exception as e:
        return f"Erro ao carregar dashboard: {str(e)}", 500


@app.route('/dashboard/optimization/<int:opt_id>', methods=['GET'])
def optimization_detail_page(opt_id):
    """
    Página de detalhes de uma otimização.
    
    Args:
        opt_id: ID da otimização
        
    Retorna:
    - HTML da página de detalhes
    """
    try:
        opt = db.get_optimization(opt_id)
        
        if not opt:
            return "Otimização não encontrada", 404
        
        return render_template('optimization_detail.html', optimization=opt)
        
    except Exception as e:
        return f"Erro ao carregar detalhes: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)
