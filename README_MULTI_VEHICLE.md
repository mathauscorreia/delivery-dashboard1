# 🚚 Delivery Optimizer - Guia de Otimização Multi-Veículo

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Instalação](#instalação)
3. [Uso Rápido](#uso-rápido)
4. [Exemplos Práticos](#exemplos-práticos)
5. [Configuração de Veículos](#configuração-de-veículos)
6. [Algoritmos](#algoritmos)
7. [API REST](#api-rest)
8. [Troubleshooting](#troubleshooting)

## Visão Geral

O Delivery Optimizer agora inclui **otimização de rota para múltiplos veículos** com restrições de capacidade. Sistema completo que:

- ✅ Distribui paradas entre veículos respeitando capacidade
- ✅ Otimiza cada rota individualmente
- ✅ Minimiza distância total
- ✅ Balanceia carga entre veículos
- ✅ Fornece estatísticas detalhadas

### Componentes

| Componente | Descrição |
|-----------|-----------|
| `multi_vehicle_optimizer.py` | Módulo principal de otimização |
| `test_multi_vehicle.py` | Script de teste com exemplos |
| `app_multi_vehicle.py` | API REST para integração |
| `MULTI_VEHICLE.md` | Documentação completa |

## Instalação

### Dependências

```bash
pip install -r requirements.txt
```

Certifique-se de que `numpy` está instalado:

```bash
pip install numpy
```

## Uso Rápido

### Teste Básico

```bash
python3.11 test_multi_vehicle.py
```

Resultado esperado:
- ✅ 4 veículos configurados
- ✅ 46 paradas distribuídas
- ✅ Rotas otimizadas
- ✅ Arquivo Excel com resultado

### Código Python

```python
import pandas as pd
from multi_vehicle_optimizer import (
    MultiVehicleOptimizer,
    create_vehicles_from_config,
    create_stops_from_dataframe
)

# Lê dados
df = pd.read_excel('entregas.xlsx')

# Cria paradas
stops = create_stops_from_dataframe(df)

# Configura veículos
vehicles = create_vehicles_from_config([
    {'id': 1, 'name': 'Moto', 'capacity': 15},
    {'id': 2, 'name': 'Carro', 'capacity': 25},
    {'id': 3, 'name': 'Van', 'capacity': 40},
])

# Otimiza
optimizer = MultiVehicleOptimizer(stops, vehicles)
optimizer.greedy_assignment()
optimizer.optimize_routes(method='two_opt')

# Resultado
stats = optimizer.get_statistics()
print(f"Distância total: {stats['total_distance_km']:.2f} km")
print(f"Utilização: {stats['overall_utilization']:.1f}%")
```

## Exemplos Práticos

### Exemplo 1: Distribuição Simples

```python
from multi_vehicle_optimizer import (
    MultiVehicleOptimizer,
    create_vehicles_from_config,
    Stop
)

# Cria paradas manualmente
stops = [
    Stop(1, -23.5505, -46.6333, "Centro", 5),
    Stop(2, -23.5615, -46.6833, "Pinheiros", 3),
    Stop(3, -23.5870, -46.6170, "Vila Mariana", 2),
]

# Cria veículos
vehicles = create_vehicles_from_config([
    {'id': 1, 'name': 'Veículo 1', 'capacity': 5},
    {'id': 2, 'name': 'Veículo 2', 'capacity': 5},
])

# Otimiza
optimizer = MultiVehicleOptimizer(stops, vehicles)
optimizer.greedy_assignment()

# Resultado
for v in optimizer.vehicles:
    print(f"{v.name}: {v.current_load}/{v.capacity} pacotes")
```

### Exemplo 2: Comparar Métodos

```python
# Compara atribuição gulosa vs clustering
comparison = optimizer.compare_assignment_methods()

for method, results in comparison.items():
    print(f"{method}:")
    print(f"  Distância: {results['total_distance']:.2f} km")
    if 'improvement' in results:
        print(f"  Melhoria: {results['improvement']:.2f}%")
```

### Exemplo 3: Detalhes Completos

```python
# Obtém detalhes de cada rota
detailed = optimizer.get_detailed_routes()

for vehicle_id, vehicle_detail in detailed.items():
    print(f"\n{vehicle_detail['vehicle_name']}")
    print(f"Carga: {vehicle_detail['load']}/{vehicle_detail['capacity']}")
    print(f"Distância: {vehicle_detail['total_distance']:.2f} km")
    
    for stop in vehicle_detail['stops']:
        print(f"  {stop['order']}. {stop['address']}")
```

## Configuração de Veículos

### Formato de Configuração

```python
vehicles_config = [
    {
        'id': 1,                    # ID único
        'name': 'Moto 1',          # Nome descritivo
        'capacity': 15             # Capacidade em pacotes
    },
    {
        'id': 2,
        'name': 'Carro',
        'capacity': 25
    },
    {
        'id': 3,
        'name': 'Van',
        'capacity': 40
    }
]

vehicles = create_vehicles_from_config(vehicles_config)
```

### Tipos de Veículos Recomendados

| Tipo | Capacidade | Uso |
|------|-----------|-----|
| Moto | 10-20 | Centros urbanos, tráfego intenso |
| Carro | 20-30 | Distribuição geral |
| Van | 30-50 | Grandes volumes, áreas periféricas |
| Caminhão | 50-100 | Distribuição em massa |

## Algoritmos

### 1. Atribuição Gulosa (Greedy)

**Características:**
- ⚡ Muito rápido
- ✅ Sempre encontra solução
- 📊 Qualidade: Boa

**Uso:**
```python
optimizer.greedy_assignment()
```

**Quando usar:**
- Distribuição equilibrada
- Resposta rápida necessária
- Paradas com carga variável

### 2. Clustering Geográfico

**Características:**
- 🗺️ Agrupa paradas próximas
- 📊 Qualidade: Excelente
- ⚠️ Pode deixar paradas não atribuídas

**Uso:**
```python
optimizer.cluster_first_assignment()
```

**Quando usar:**
- Minimizar distância é prioridade
- Paradas geograficamente dispersas
- Qualidade é mais importante que velocidade

### 3. Otimização 2-opt

**Características:**
- 🔄 Remove cruzamentos
- 📊 Melhoria típica: 10-40%
- ⚡ Rápido

**Uso:**
```python
optimizer.optimize_routes(method='two_opt')
```

**Quando usar:**
- Sempre após atribuição
- Melhora significativa com pouco custo

## API REST

### Endpoint: POST /api/multi-vehicle/optimize

Otimiza rotas com múltiplos veículos.

**Parâmetros:**
- `file`: Arquivo Excel com entregas
- `vehicles`: JSON com configuração de veículos
- `method`: 'greedy' ou 'cluster'

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/multi-vehicle/optimize \
  -F "file=@entregas.xlsx" \
  -F "vehicles=[{\"id\":1,\"name\":\"Moto\",\"capacity\":15}]" \
  -F "method=greedy"
```

**Resposta:**
```json
{
  "success": true,
  "statistics": {
    "total_vehicles": 4,
    "total_stops": 39,
    "total_distance_km": 15.69,
    "overall_utilization": 73.3,
    "vehicles": [...]
  },
  "routes": {...},
  "output_file": "output/multi_vehicle_entregas.xlsx"
}
```

### Endpoint: POST /api/multi-vehicle/compare

Compara diferentes métodos de otimização.

**Parâmetros:**
- `file`: Arquivo Excel com entregas
- `vehicles`: JSON com configuração de veículos

**Resposta:**
```json
{
  "success": true,
  "comparison": {
    "greedy": {"total_distance": 44.48, "unassigned": 0},
    "cluster_first": {"total_distance": 24.59, "unassigned": 7},
    "greedy_optimized": {"total_distance": 27.32, "improvement": 38.58},
    "cluster_first_optimized": {"total_distance": 15.69, "improvement": 36.19}
  }
}
```

### Endpoint: GET /api/multi-vehicle/vehicles

Obtém configuração padrão de veículos.

**Resposta:**
```json
{
  "success": true,
  "vehicles": [
    {"id": 1, "name": "Moto 1", "capacity": 15},
    {"id": 2, "name": "Moto 2", "capacity": 15},
    {"id": 3, "name": "Carro 1", "capacity": 25},
    {"id": 4, "name": "Carro 2", "capacity": 25},
    {"id": 5, "name": "Van", "capacity": 40}
  ]
}
```

## Troubleshooting

### Problema: Paradas não atribuídas

**Causa:** Capacidade total < Carga total

**Solução:**
```python
# Adicione mais veículos
vehicles_config.append({'id': 6, 'name': 'Van Extra', 'capacity': 40})

# Ou aumente capacidade
vehicles[0].capacity = 20
```

### Problema: Distância muito alta

**Causa:** Método de atribuição não é ótimo

**Solução:**
```python
# Tente clustering em vez de greedy
optimizer.cluster_first_assignment()
optimizer.optimize_routes(method='two_opt')
```

### Problema: Utilização desbalanceada

**Causa:** Algoritmo guloso prioriza carga, não equilíbrio

**Solução:**
```python
# Modifique a estratégia manualmente
# ou use clustering que distribui melhor
```

## Resultados Esperados

### Com 46 Paradas e 4 Veículos

| Métrica | Valor |
|---------|-------|
| Distância total | 15.69 km |
| Paradas não atribuídas | 7 |
| Utilização média | 73.3% |
| Tempo de otimização | 0.002s |

### Distribuição por Veículo

| Veículo | Paradas | Carga | Utilização | Distância |
|---------|---------|-------|-----------|-----------|
| Moto | 6 | 15/15 | 100% | 3.03 km |
| Carro 1 | 12 | 25/25 | 100% | 6.59 km |
| Carro 2 | 5 | 10/25 | 40% | 1.92 km |
| Van | 16 | 27/40 | 67.5% | 4.15 km |

## Próximos Passos

1. **Visualização em Mapa:** Exibir rotas em Google Maps
2. **Janelas de Tempo:** Adicionar restrições de horário
3. **Múltiplos Depósitos:** Otimizar com vários pontos de partida
4. **Algoritmo Genético:** Melhor qualidade para rotas pequenas

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026
