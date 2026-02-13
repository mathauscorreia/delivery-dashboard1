"""
Aplicação Flask para otimização de rotas de entrega.
Sistema de agrupamento inteligente de entregas com normalização de endereços e geocodificação.
"""

from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from geocoder import GeocoderService, MockGeocoder
import traceback
from processor_with_routing import DeliveryProcessorWithRouting


app = Flask(__name__)


# Configurações
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'output'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}

# Cria diretórios se não existirem
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Variável global para armazenar estatísticas da última execução
last_stats = None
last_output_file = None

# Inicializa geocodificador (usa MockGeocoder por padrão)
# Para usar Google Maps API, defina a variável de ambiente GOOGLE_MAPS_API_KEY
google_api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
if google_api_key:
    geocoder = GeocoderService(api_key=google_api_key)
else:
    geocoder = MockGeocoder()


def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    """Página inicial com formulário de upload."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Processa upload e agrupamento de entregas."""
    global last_stats, last_output_file
    
    try:
        # Verifica se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        # Verifica se arquivo foi selecionado
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verifica extensão do arquivo
        if not allowed_file(file.filename):
            return jsonify({'error': 'Formato de arquivo não permitido. Use .xlsx ou .xls'}), 400
        
        # Salva arquivo enviado
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)

        # Instancia o processor com roteamento
        processor = DeliveryProcessorWithRouting(geocoder=geocoder)

        # Lê arquivo Excel
        df_original = processor.read_excel(input_path)

        # Agrupa entregas com geocodificação
        df_grouped = processor.group_deliveries(
            df_original,
            enable_geocoding=False
        )


        # 🔥 ADICIONE TAMBÉM A OTIMIZAÇÃO DA ROTA
        df_optimized = processor.optimize_route(df_grouped, method='two_opt')

        # Gera nome do arquivo de saída
        output_filename = f"entregas_otimizadas_{filename}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        # Salva arquivo otimizado
        processor.save_to_excel(df_optimized, output_path)
        
        # Armazena estatísticas
        last_stats = processor.get_statistics()
        last_output_file = output_filename
        
        # Remove arquivo de upload
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'stats': last_stats,
            'output_file': output_filename,
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Faz download do arquivo otimizado."""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Arquivo não encontrado'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stats')
def get_stats():
    """Retorna estatísticas da última execução."""
    if last_stats is None:
        return jsonify({'error': 'Nenhum processamento realizado ainda'}), 404
    
    return jsonify({
        'stats': last_stats,
        'output_file': last_output_file,
    })


@app.route('/geocoder-status')
def geocoder_status():
    """Retorna status do geocodificador."""
    stats = geocoder.get_statistics() if hasattr(geocoder, 'get_statistics') else {}
    
    return jsonify({
        'geocoder_type': type(geocoder).__name__,
        'enabled': geocoder.enabled if hasattr(geocoder, 'enabled') else False,
        'statistics': stats,
    })


@app.route('/health')
def health():
    """Endpoint de verificação de saúde da aplicação."""
    return jsonify({
        'status': 'ok',
        'message': 'Delivery Optimizer está funcionando!',
        'geocoder': type(geocoder).__name__
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚚 DELIVERY OPTIMIZER - Sistema de Otimização de Entregas")
    print("=" * 60)
    print("\n✅ Servidor iniciado com sucesso!")
    print("📍 Acesse: http://127.0.0.1:5000")
    
    # Mostra status do geocodificador
    if hasattr(geocoder, 'enabled'):
        if geocoder.enabled:
            print("🌐 Geocodificador: Google Maps API (ATIVO)")
        else:
            print("🌐 Geocodificador: MockGeocoder (simulado)")
    
    print("\n⚡ Aguardando upload de planilhas...\n")
    
    if __name__ == '__main__':
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)

