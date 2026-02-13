# 🚚 Guia de Otimização Multi-Veículo - Delivery Optimizer

## Visão Geral

O Delivery Optimizer inclui um sistema completo de otimização de rota para múltiplos veículos com restrições de capacidade. Implementa algoritmos avançados de distribuição de carga e otimização simultânea de rotas.

- ✅ **Atribuição Gulosa** - Rápida, simples
- ✅ **Clustering Geográfico** - Agrupa paradas próximas
- ✅ **Otimização 2-opt** - Melhora rotas individuais
- ✅ **Balanceamento de Carga** - Distribui equitativamente

## Arquitetura

### Componentes Principais

#### 1. **Classe Vehicle**
Representa um veículo de entrega com capacidade.

```python
from multi_vehicle_optimizer import Vehicle

vehicle = Vehicle(
    id=1,
    name="Veículo 1 (Moto)",
    capacity=15  # Capacidade em pacotes
)

# Verifica se pode aceitar mais pacotes
if vehicle.can_accept(5):
    vehicle.add_stop(stop_index=0, packages=5)

# Obtém utilização
utilization = vehicle.get_utilization()  # 0-100%
```

#### 2. **Classe MultiVehicleOptimizer**
Otimiza rotas para múltiplos veículos.

```python
from multi_vehicle_optimizer import (
    MultiVehicleOptimizer,
    create_vehicles_from_config,
    create_stops_from_dataframe
)

# Configura veículos
vehicles_config = [
    {'id': 1, 'name': 'Moto', 'capacity': 15},
    {'id': 2, 'name': 'Carro', 'capacity': 25},
    {'id': 3, 'name': 'Van', 'capacity': 40},
]

vehicles = create_vehicles_from_config(vehicles_config)

# Cria paradas a partir de DataFrame
stops = create_stops_from_dataframe(df)

# Cria otimizador
optimizer = MultiVehicleOptimizer(stops, vehicles)

# Atribui paradas aos veículos
result = optimizer.greedy_assignment()

# Otimiza rotas
optimizer.optimize_routes(method='two_opt')

# Obtém estatísticas
stats = optimizer.get_statistics()
```

## Algoritmos de Atribuição

### 1. Atribuição Gulosa (Greedy)

**Características:**
- ⚡ Muito rápido (O(n))
- 📍 Ordena paradas por carga e encaixa em veículos
- ✅ Sempre encontra solução se houver capacidade
- 📊 Qualidade: Boa para distribuição equilibrada

**Uso:**
```python
result = optimizer.greedy_assignment()

print(f"Distância total: {result['total_distance']:.2f} km")
print(f"Paradas não atribuídas: {result['unassigned_count']}")

for vehicle_id, route_info in result['routes'].items():
    print(f"{route_info['vehicle_name']}: {route_info['stops_count']} paradas")
```

**Quando usar:**
- Necessidade de resposta rápida
- Distribuição equilibrada entre veículos
- Paradas com carga variável

### 2. Clustering Geográfico

**Características:**
- ⚡ Rápido (O(n²))
- 🗺️ Agrupa paradas próximas geograficamente
- 📍 Minimiza distância total
- 📊 Qualidade: Melhor para minimizar distância

**Uso:**
```python
result = optimizer.cluster_first_assignment()

print(f"Distância total: {result['total_distance']:.2f} km")
print(f"Paradas não atribuídas: {result['unassigned_count']}")
```

**Quando usar:**
- Minimizar distância total é prioridade
- Paradas geograficamente dispersas
- Quer melhor qualidade de rota

### 3. Otimização 2-opt

**Características:**
- ⚡ Rápido (O(n²) por iteração)
- 🔄 Remove cruzamentos em cada rota
- ✅ Melhora solução iterativamente
- 📊 Melhoria típica: 10-40%

**Uso:**
```python
# Primeiro atribui paradas
optimizer.greedy_assignment()

# Depois otimiza rotas
optimizer.optimize_routes(method='two_opt')

stats = optimizer.get_statistics()
print(f"Distância total otimizada: {stats['total_distance_km']:.2f} km")
```

## Uso Prático

### Exemplo Completo

```python
import pandas as pd
from multi_vehicle_optimizer import (
    MultiVehicleOptimizer,
    create_vehicles_from_config,
    create_stops_from_dataframe
)

# Lê dados geocodificados
df = pd.read_excel('entregas_geocodificadas.xlsx')

# Cria paradas
stops = create_stops_from_dataframe(df)

# Configura frota
vehicles_config = [
    {'id': 1, 'name': 'Moto 1', 'capacity': 15},
    {'id': 2, 'name': 'Moto 2', 'capacity': 15},
    {'id': 3, 'name': 'Carro 1', 'capacity': 25},
    {'id': 4, 'name': 'Van', 'capacity': 40},
]

vehicles = create_vehicles_from_config(vehicles_config)

# Cria otimizador
optimizer = MultiVehicleOptimizer(stops, vehicles)

# Atribui e otimiza
optimizer.greedy_assignment()
optimizer.optimize_routes(method='two_opt')

# Obtém estatísticas
stats = optimizer.get_statistics()

print(f"Distância total: {stats['total_distance_km']:.2f} km")
print(f"Utilização geral: {stats['overall_utilization']:.1f}%")

# Exibe detalhes
detailed = optimizer.get_detailed_routes()
for vehicle_id, vehicle_detail in detailed.items():
    print(f"\n{vehicle_detail['vehicle_name']}")
    print(f"  Carga: {vehicle_detail['load']}/{vehicle_detail['capacity']}")
    print(f"  Distância: {vehicle_detail['total_distance']:.2f} km")
    print(f"  Paradas: {len(vehicle_detail['stops'])}")
```

## Comparação de Métodos

### Teste com 46 Paradas e 4 Veículos

| Método | Distância | Não Atribuídas | Tempo |
|--------|-----------|----------------|-------|
| Greedy | 44.48 km | 0 | 0.000s |
| Cluster First | 24.59 km | 7 | 0.001s |
| Greedy + 2-opt | 27.32 km | 0 | 0.001s |
| Cluster + 2-opt | **15.69 km** | 7 | 0.002s |

### Recomendações

| Cenário | Método Recomendado | Motivo |
|---------|-------------------|--------|
| Distribuição equilibrada | Greedy | Rápido, sem não-atribuídas |
| Minimizar distância | Cluster + 2-opt | Melhor qualidade |
| Tempo crítico | Greedy | Mais rápido |
| Balanceamento importante | Greedy | Distribui melhor |

## Métricas e Estatísticas

### Utilização de Capacidade

```python
# Utilização por veículo
for vehicle_info in stats['vehicles']:
    print(f"{vehicle_info['name']}: {vehicle_info['utilization']:.1f}%")

# Utilização geral
overall = stats['overall_utilization']
print(f"Utilização geral: {overall:.1f}%")
```

### Distância Total

```python
# Distância total de todas as rotas
total_distance = stats['total_distance_km']

# Distância média por veículo
avg_distance = stats['average_distance_per_vehicle']

# Distância por veículo
for vehicle_info in stats['vehicles']:
    print(f"{vehicle_info['name']}: {vehicle_info['distance']:.2f} km")
```

### Paradas Não Atribuídas

```python
# Número de paradas que não cabem em nenhum veículo
unassigned = stats['unassigned_stops']

# Índices das paradas não atribuídas
unassigned_indices = optimizer.unassigned_stops
```

## Funcionalidades Avançadas

### Comparar Todos os Métodos

```python
comparison = optimizer.compare_assignment_methods()

for method, results in comparison.items():
    print(f"{method}: {results['total_distance']:.2f} km")
```

### Detalhes Completos das Rotas

```python
detailed = optimizer.get_detailed_routes()

for vehicle_id, vehicle_detail in detailed.items():
    print(f"\n{vehicle_detail['vehicle_name']}")
    
    for stop in vehicle_detail['stops']:
        print(f"  {stop['order']}. {stop['address']}")
        print(f"     Pacotes: {stop['packages']}")
        print(f"     Distância até próxima: {stop['distance_to_next']:.2f} km")
```

### Matriz de Distâncias

```python
# Acessa distância entre parada i e j
distance = optimizer.distance_matrix[i][j]

# Calcula distância de uma rota
route = [0, 5, 10, 3]
distance = optimizer._route_distance(route)
```

## Otimizações de Performance

### Para Muitas Paradas (>100)

```python
# Use apenas atribuição gulosa sem otimização
optimizer.greedy_assignment()

# Não otimize rotas para economizar tempo
# optimizer.optimize_routes()  # Pule esta linha
```

### Para Paradas Médias (10-100)

```python
# Use clustering + 2-opt
optimizer.cluster_first_assignment()
optimizer.optimize_routes(method='two_opt')
```

### Para Poucas Paradas (<10)

```python
# Pode usar ambos os métodos e escolher o melhor
comparison = optimizer.compare_assignment_methods()

# Use o método com melhor resultado
best_method = min(comparison.items(), 
                 key=lambda x: x[1]['total_distance'])
print(f"Melhor método: {best_method[0]}")
```

## Limitações e Considerações

### Atribuição Gulosa
- ✅ Rápida
- ✅ Sempre encontra solução
- ❌ Pode não ser ótima
- ❌ Sensível à ordem das paradas

### Clustering Geográfico
- ✅ Minimiza distância
- ✅ Agrupa logicamente
- ❌ Pode deixar paradas não atribuídas
- ❌ Mais lenta que gulosa

### 2-opt
- ✅ Melhora significativa
- ✅ Rápido
- ❌ Pode ficar em ótimo local
- ❌ Não garante solução global ótima

## Troubleshooting

### Erro: "Paradas não atribuídas"

**Causa:** Capacidade total < Carga total

**Solução:**
```python
# Adicione mais veículos
vehicles_config.append({'id': 5, 'name': 'Van Extra', 'capacity': 40})

# Ou aumente capacidade dos existentes
vehicles[0].capacity = 20
```

### Distância muito alta

**Causa:** Método de atribuição não é ótimo

**Solução:**
```python
# Tente clustering em vez de greedy
optimizer.cluster_first_assignment()
optimizer.optimize_routes(method='two_opt')
```

### Utilização desbalanceada

**Causa:** Algoritmo guloso prioriza carga, não equilíbrio

**Solução:**
```python
# Modifique a estratégia de seleção de veículo
# Escolha o veículo com menor distância em vez de menor carga
```

## Próximos Passos

### 1. Janelas de Tempo
Adicionar restrições de horário de entrega.

### 2. Múltiplos Depósitos
Otimizar rotas com múltiplos pontos de partida.

### 3. Restrições de Zona
Definir zonas de entrega para cada veículo.

### 4. Algoritmo Genético
Usar evolução para encontrar melhores soluções.

## Referências

- [Vehicle Routing Problem (VRP)](https://en.wikipedia.org/wiki/Vehicle_routing_problem)
- [Capacitated VRP (CVRP)](https://en.wikipedia.org/wiki/Vehicle_routing_problem#Capacitated_VRP)
- [Clustering Algorithms](https://en.wikipedia.org/wiki/Cluster_analysis)
- [2-opt Algorithm](https://en.wikipedia.org/wiki/2-opt)

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026
