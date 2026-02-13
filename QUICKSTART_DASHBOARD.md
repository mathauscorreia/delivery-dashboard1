# 🚀 Guia Rápido - Dashboard de Otimizações

## 1️⃣ Instalação

```bash
cd delivery-optimizer
pip install -r requirements.txt
```

## 2️⃣ Iniciar Sistema Completo

### Terminal 1 - API de Otimização

```bash
python3.11 app.py
```

Acessa em: `http://localhost:5000`

### Terminal 2 - Dashboard

```bash
python3.11 app_dashboard.py
```

Acessa em: `http://localhost:5001/dashboard`

## 3️⃣ Usar o Sistema

### Passo 1: Upload de Arquivo

1. Acesse `http://localhost:5000`
2. Clique em "Escolher Arquivo"
3. Selecione seu arquivo Excel com entregas
4. Clique em "Processar"

### Passo 2: Visualizar Resultado

1. Veja as estatísticas na tela
2. Baixe o arquivo otimizado
3. Verifique as rotas por veículo

### Passo 3: Acompanhar Histórico

1. Acesse `http://localhost:5001/dashboard`
2. Veja estatísticas gerais
3. Consulte histórico de otimizações
4. Compare diferentes rotas

## 📊 Dashboard - Funcionalidades

### Estatísticas Gerais

```
Total de Otimizações: 10
Distância Total: 250.5 km
Utilização Média: 75.3%
Total de Paradas: 450
```

### Gráficos

- **Distância por Otimização**: Evolução ao longo do tempo
- **Utilização Média**: Eficiência de cada rota

### Histórico

- Lista de todas as otimizações
- Filtro por período
- Ações rápidas (ver, deletar)

## 🔧 Configurar Veículos

Edite a configuração em `multi_vehicle_optimizer.py`:

```python
vehicles_config = [
    {'id': 1, 'name': 'Moto 1', 'capacity': 15},
    {'id': 2, 'name': 'Moto 2', 'capacity': 15},
    {'id': 3, 'name': 'Carro 1', 'capacity': 25},
    {'id': 4, 'name': 'Carro 2', 'capacity': 25},
    {'id': 5, 'name': 'Van', 'capacity': 40},
]
```

## 📁 Estrutura de Arquivos

```
delivery-optimizer/
├── app.py                          # API principal
├── app_dashboard.py                # API do dashboard
├── database.py                     # Banco de dados
├── normalizer.py                   # Normalização de endereços
├── geocoder.py                     # Geocodificação
├── route_optimizer.py              # Otimização de rota
├── multi_vehicle_optimizer.py      # Multi-veículo
├── processor.py                    # Processamento
├── templates/
│   ├── index.html                  # Interface principal
│   └── dashboard.html              # Dashboard
├── requirements.txt                # Dependências
├── README.md                       # Documentação completa
├── DASHBOARD.md                    # Docs do dashboard
└── output/                         # Arquivos processados
```

## 🧪 Testar com Dados de Exemplo

```bash
# Gera dados de teste
python3.11 test_data.py

# Processa dados de teste
python3.11 test_processor.py

# Testa geocodificação
python3.11 test_geocoding.py

# Testa otimização de rota
python3.11 test_route_optimization.py

# Testa multi-veículo
python3.11 test_multi_vehicle.py

# Testa pipeline completo
python3.11 test_complete_pipeline.py
```

## 📈 API Endpoints

### Otimização

```
POST /api/optimize
POST /api/multi-vehicle/optimize
GET /api/multi-vehicle/vehicles
```

### Dashboard

```
GET /api/dashboard/stats
GET /api/dashboard/history
GET /api/dashboard/optimization/<id>
POST /api/dashboard/compare
DELETE /api/dashboard/delete/<id>
GET /api/dashboard/export/<id>
```

## 🐛 Troubleshooting

### Porta já em uso

```bash
# Mude a porta no código
python3.11 app.py --port 5002
```

### Banco de dados corrompido

```bash
# Remova e recrie
rm optimization_history.db
python3.11 app_dashboard.py
```

### Erro ao processar arquivo

1. Verifique formato Excel
2. Certifique-se de ter colunas: Endereço, Bairro, Latitude, Longitude
3. Veja logs em `.manus-logs/`

## 📞 Suporte

Para mais informações, consulte:
- `README.md` - Documentação completa
- `DASHBOARD.md` - Detalhes do dashboard
- `MULTI_VEHICLE.md` - Otimização multi-veículo

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026
