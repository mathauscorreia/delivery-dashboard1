# 📊 Dashboard de Histórico de Otimizações - Delivery Optimizer

## Visão Geral

O Dashboard é um sistema completo de visualização e análise de histórico de otimizações de rota. Armazena todas as otimizações em banco de dados SQLite e fornece uma interface web interativa para análise.

## Componentes

| Componente | Descrição |
|-----------|-----------|
| `database.py` | Módulo de banco de dados SQLite |
| `app_dashboard.py` | API Flask para dashboard |
| `templates/dashboard.html` | Interface web do dashboard |

## Funcionalidades

### 📊 Estatísticas Gerais

- ✅ Total de otimizações realizadas
- ✅ Distância total percorrida
- ✅ Utilização média de capacidade
- ✅ Total de paradas processadas
- ✅ Total de veículos utilizados

### 📈 Análises e Gráficos

- ✅ Gráfico de distância por otimização
- ✅ Gráfico de utilização média
- ✅ Comparação de métodos
- ✅ Tendências ao longo do tempo

### 📋 Histórico de Otimizações

- ✅ Lista de todas as otimizações
- ✅ Detalhes completos de cada otimização
- ✅ Filtro por período
- ✅ Busca por arquivo/motorista

### 🔄 Comparação de Otimizações

- ✅ Comparar duas otimizações
- ✅ Visualizar diferenças
- ✅ Melhoria percentual
- ✅ Análise de tendências

### 💾 Gerenciamento de Dados

- ✅ Exportar para JSON
- ✅ Deletar otimizações
- ✅ Backup automático
- ✅ Histórico completo

## Estrutura do Banco de Dados

### Tabela: optimizations

```sql
CREATE TABLE optimizations (
    id INTEGER PRIMARY KEY,
    file_name TEXT,
    driver_name TEXT,
    optimization_date TIMESTAMP,
    total_deliveries INTEGER,
    total_stops INTEGER,
    total_distance REAL,
    optimization_method TEXT,
    total_vehicles INTEGER,
    overall_utilization REAL,
    processing_time REAL,
    status TEXT
)
```

### Tabela: vehicles

```sql
CREATE TABLE vehicles (
    id INTEGER PRIMARY KEY,
    optimization_id INTEGER,
    vehicle_id INTEGER,
    vehicle_name TEXT,
    capacity INTEGER,
    load INTEGER,
    utilization REAL,
    stops_count INTEGER,
    distance REAL,
    FOREIGN KEY (optimization_id) REFERENCES optimizations(id)
)
```

### Tabela: stops

```sql
CREATE TABLE stops (
    id INTEGER PRIMARY KEY,
    optimization_id INTEGER,
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
```

### Tabela: comparisons

```sql
CREATE TABLE comparisons (
    id INTEGER PRIMARY KEY,
    optimization_id INTEGER,
    method_name TEXT,
    total_distance REAL,
    unassigned_stops INTEGER,
    processing_time REAL,
    FOREIGN KEY (optimization_id) REFERENCES optimizations(id)
)
```

## Uso

### Iniciar Dashboard

```bash
python3.11 app_dashboard.py
```

Acesse em: `http://localhost:5001/dashboard`

### API Endpoints

#### GET /api/dashboard/stats

Obtém estatísticas gerais.

**Resposta:**
```json
{
  "success": true,
  "statistics": {
    "total_optimizations": 10,
    "total_distance_km": 250.5,
    "average_utilization": 75.3,
    "total_stops_processed": 450,
    "total_vehicles_used": 25
  }
}
```

#### GET /api/dashboard/history

Obtém histórico de otimizações.

**Query Parameters:**
- `days`: Número de dias (padrão: 30)
- `limit`: Número máximo de registros (padrão: 100)

**Resposta:**
```json
{
  "success": true,
  "count": 10,
  "optimizations": [
    {
      "id": 1,
      "file_name": "entregas.xlsx",
      "driver_name": "João Silva",
      "optimization_date": "2026-02-12 10:30:00",
      "total_stops": 41,
      "total_distance": 19.69,
      "overall_utilization": 67.5
    }
  ]
}
```

#### GET /api/dashboard/optimization/{id}

Obtém detalhes de uma otimização.

**Resposta:**
```json
{
  "success": true,
  "optimization": {
    "id": 1,
    "file_name": "entregas.xlsx",
    "total_stops": 41,
    "total_distance": 19.69,
    "vehicles": [...],
    "stops": [...],
    "comparisons": [...]
  }
}
```

#### POST /api/dashboard/compare

Compara duas otimizações.

**Body:**
```json
{
  "opt_id1": 1,
  "opt_id2": 2
}
```

**Resposta:**
```json
{
  "success": true,
  "comparison": {
    "file_1": "entregas1.xlsx",
    "distance_1": 25.5,
    "file_2": "entregas2.xlsx",
    "distance_2": 19.69,
    "distance_improvement": 22.8,
    "utilization_difference": 5.2
  }
}
```

#### DELETE /api/dashboard/delete/{id}

Deleta uma otimização.

**Resposta:**
```json
{
  "success": true,
  "message": "Otimização deletada com sucesso"
}
```

#### GET /api/dashboard/export/{id}

Exporta otimização em JSON.

**Resposta:** JSON com dados completos da otimização

## Exemplos de Uso

### Exemplo 1: Obter Estatísticas

```python
import requests

response = requests.get('http://localhost:5001/api/dashboard/stats')
stats = response.json()

print(f"Total de otimizações: {stats['statistics']['total_optimizations']}")
print(f"Distância total: {stats['statistics']['total_distance_km']:.2f} km")
```

### Exemplo 2: Obter Histórico

```python
response = requests.get('http://localhost:5001/api/dashboard/history?days=7&limit=10')
history = response.json()

for opt in history['optimizations']:
    print(f"{opt['file_name']}: {opt['total_distance']:.2f} km")
```

### Exemplo 3: Comparar Otimizações

```python
data = {
    'opt_id1': 1,
    'opt_id2': 2
}

response = requests.post('http://localhost:5001/api/dashboard/compare', json=data)
comparison = response.json()

improvement = comparison['comparison']['distance_improvement']
print(f"Melhoria: {improvement:.2f}%")
```

### Exemplo 4: Deletar Otimização

```python
response = requests.delete('http://localhost:5001/api/dashboard/delete/1')

if response.ok:
    print("Otimização deletada com sucesso!")
```

## Integração com Sistema de Otimização

### Salvar Otimização após Processamento

```python
from database import OptimizationDatabase
from multi_vehicle_optimizer import MultiVehicleOptimizer

# Após otimizar
optimizer = MultiVehicleOptimizer(stops, vehicles)
optimizer.greedy_assignment()
optimizer.optimize_routes()

# Salva no banco
db = OptimizationDatabase()
opt_id = db.save_optimization(
    file_name='entregas.xlsx',
    driver_name='João Silva',
    stats=optimizer.get_statistics(),
    detailed_routes=optimizer.get_detailed_routes(),
    comparisons=optimizer.compare_assignment_methods()
)

print(f"Otimização salva com ID: {opt_id}")
```

## Dashboard Web

### Funcionalidades

1. **Painel de Estatísticas**
   - Exibe KPIs principais
   - Atualiza em tempo real
   - Cards com cores indicativas

2. **Gráficos Interativos**
   - Distância por otimização
   - Utilização média
   - Tendências ao longo do tempo

3. **Tabela de Histórico**
   - Lista todas as otimizações
   - Ordenação por data
   - Ações rápidas (ver, deletar)

4. **Detalhes de Otimização**
   - Informações completas
   - Rotas por veículo
   - Comparação de métodos

## Métricas Disponíveis

### Por Otimização

- Total de paradas
- Distância total (km)
- Utilização de capacidade (%)
- Tempo de processamento (s)
- Número de veículos
- Paradas não atribuídas

### Por Veículo

- Número de paradas
- Carga (pacotes)
- Utilização (%)
- Distância percorrida (km)

### Comparativas

- Melhoria de distância (%)
- Diferença de utilização (%)
- Tempo economizado (min)
- Eficiência relativa

## Troubleshooting

### Banco de dados não encontrado

**Solução:**
```python
from database import OptimizationDatabase

db = OptimizationDatabase()  # Cria novo banco
```

### Erro ao salvar otimização

**Causa:** Dados incompletos

**Solução:**
```python
# Certifique-se de que stats contém todas as chaves necessárias
stats = optimizer.get_statistics()
print(stats.keys())
```

### Dashboard não carrega

**Causa:** Porta em uso

**Solução:**
```bash
# Use porta diferente
python3.11 app_dashboard.py --port 5002
```

## Próximos Passos

### 1. Alertas e Notificações
- Alertar quando distância aumenta
- Notificar sobre paradas não atribuídas
- Email com resumo diário

### 2. Previsões
- Prever distância baseado em histórico
- Sugerir melhorias
- Análise de tendências

### 3. Integração com Mapas
- Visualizar rotas no mapa
- Heatmap de paradas
- Análise geográfica

### 4. Relatórios
- Relatório PDF mensal
- Comparação período a período
- Análise de performance

## Referências

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026
