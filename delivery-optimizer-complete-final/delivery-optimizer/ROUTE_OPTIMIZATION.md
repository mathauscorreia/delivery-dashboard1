# 🗺️ Guia de Otimização de Rota - Delivery Optimizer

## Visão Geral

O Delivery Optimizer inclui um sistema completo de otimização de rota que utiliza as coordenadas geocodificadas para calcular a melhor sequência de paradas. Implementa múltiplos algoritmos com diferentes características:

- ✅ **Nearest Neighbor** - Rápido, guloso
- ✅ **2-opt** - Otimizado, remove cruzamentos
- ✅ **Algoritmo Genético** - Avançado, busca global

## Arquitetura

### Componentes Principais

#### 1. **Classe Stop**
Representa uma parada de entrega com coordenadas.

```python
from route_optimizer import Stop

stop = Stop(
    id=1,
    latitude=-23.5505,
    longitude=-46.6333,
    address="Rua das Flores, 123",
    packages=5
)

# Calcula distância até outra parada
distance = stop.distance_to(other_stop)  # em km
```

#### 2. **Classe RouteOptimizer**
Otimiza rotas usando múltiplos algoritmos.

```python
from route_optimizer import RouteOptimizer, Stop

# Cria lista de paradas
stops = [
    Stop(1, -23.5505, -46.6333, "Centro", 5),
    Stop(2, -23.5615, -46.6833, "Pinheiros", 3),
    Stop(3, -23.5870, -46.6170, "Vila Mariana", 2),
]

# Cria otimizador
optimizer = RouteOptimizer(stops)

# Otimiza rota
route, distance = optimizer.optimize(method='two_opt')

print(f"Rota: {route}")
print(f"Distância: {distance:.2f} km")
```

## Algoritmos Disponíveis

### 1. Nearest Neighbor (Algoritmo Guloso)

**Características:**
- ⚡ Muito rápido (O(n²))
- 📍 Começa em um ponto e vai para o vizinho mais próximo
- ❌ Não garante solução ótima
- 📊 Qualidade: ~20-30% pior que ótimo

**Uso:**
```python
route, distance = optimizer.nearest_neighbor(start_index=0)
print(f"Distância: {distance:.2f} km")
```

**Quando usar:**
- Rotas muito grandes (>100 paradas)
- Necessidade de resposta rápida
- Baseline para comparação

### 2. Algoritmo 2-opt

**Características:**
- ⚡ Rápido (O(n²) por iteração)
- 🔄 Remove cruzamentos na rota
- ✅ Melhora solução iterativamente
- 📊 Qualidade: ~5-15% pior que ótimo

**Uso:**
```python
# Começa com Nearest Neighbor e melhora
initial_route, _ = optimizer.nearest_neighbor()
route, distance = optimizer.two_opt(initial_route, max_iterations=1000)

# Ou deixa o algoritmo começar do zero
route, distance = optimizer.two_opt(max_iterations=1000)
```

**Como funciona:**
1. Toma uma rota inicial
2. Tenta inverter segmentos da rota
3. Se melhora, mantém a mudança
4. Repete até não haver melhorias

**Quando usar:**
- Rotas de tamanho médio (10-100 paradas)
- Melhor balanço entre qualidade e velocidade
- **Recomendado para produção**

### 3. Algoritmo Genético

**Características:**
- 🐢 Mais lento (O(n²) por geração × gerações)
- 🧬 Simula evolução natural
- ✅ Pode encontrar soluções melhores
- 📊 Qualidade: ~2-10% pior que ótimo

**Uso:**
```python
route, distance = optimizer.genetic_algorithm(
    population_size=100,      # Número de indivíduos
    generations=500,          # Número de gerações
    mutation_rate=0.02,       # Taxa de mutação (0-1)
    elite_size=10             # Indivíduos elite a preservar
)
```

**Parâmetros:**
- `population_size`: Maior = mais exploração, mais lento
- `generations`: Maior = mais iterações, mais lento
- `mutation_rate`: Maior = mais variação, menos convergência
- `elite_size`: Maior = preserva mais boas soluções

**Quando usar:**
- Rotas pequenas (<50 paradas)
- Quando qualidade é crítica
- Tempo de processamento não é limitado

## Uso Prático

### Exemplo Completo

```python
import pandas as pd
from route_optimizer import RouteOptimizer, create_stops_from_dataframe

# Lê dados geocodificados
df = pd.read_excel('entregas_geocodificadas.xlsx')

# Cria paradas
stops = create_stops_from_dataframe(df)

# Cria otimizador
optimizer = RouteOptimizer(stops)

# Otimiza rota
route, distance = optimizer.optimize(method='two_opt', max_iterations=500)

# Obtém detalhes
details = optimizer.get_optimized_route_details()

print(f"Distância total: {details['total_distance']:.2f} km")
print(f"Número de paradas: {details['number_of_stops']}")

# Exibe segmentos
for segment in details['segments']:
    print(f"{segment['from']} → {segment['to']}: {segment['distance']:.2f} km")
```

### Integração com DataFrame

```python
from route_optimizer import create_stops_from_dataframe

# Cria paradas a partir de DataFrame
# Esperado: colunas 'id', 'latitude', 'longitude', 'endereco', 'quantidade_pacotes'
stops = create_stops_from_dataframe(df_geocoded)

# Otimiza
optimizer = RouteOptimizer(stops)
route, distance = optimizer.optimize(method='two_opt')

# Cria DataFrame com rota otimizada
route_df = pd.DataFrame([
    {
        'ordem': i + 1,
        'id': stops[idx].id,
        'endereco': stops[idx].address,
        'latitude': stops[idx].latitude,
        'longitude': stops[idx].longitude,
    }
    for i, idx in enumerate(route)
])

route_df.to_excel('rota_otimizada.xlsx', index=False)
```

## Comparação de Métodos

### Teste com 46 Paradas

| Método | Distância | Tempo | Melhoria |
|--------|-----------|-------|----------|
| Nearest Neighbor | 14.36 km | 0.000s | Base |
| 2-opt | 13.10 km | 0.002s | 8.80% |
| Genético | 18.73 km | 0.250s | -30.40% |

### Recomendações por Tamanho de Rota

| Tamanho | Método Recomendado | Motivo |
|---------|-------------------|--------|
| < 10 | Genético | Pode encontrar ótimo |
| 10-50 | 2-opt | Melhor balanço |
| 50-100 | 2-opt | Rápido e bom |
| > 100 | Nearest Neighbor | Muito rápido |

## Funcionalidades Avançadas

### Comparar Todos os Métodos

```python
comparison = optimizer.compare_methods()

for method, results in comparison.items():
    print(f"{method}: {results['distance']:.2f} km em {results['time']:.3f}s")
```

### Cálculo de Matriz de Distâncias

```python
# A matriz é calculada automaticamente
distance_matrix = optimizer.distance_matrix

# Acessa distância entre parada i e j
dist_i_to_j = distance_matrix[i][j]
```

### Detalhes da Rota

```python
details = optimizer.get_optimized_route_details()

print(f"Rota: {details['route_indices']}")
print(f"Distância: {details['total_distance']:.2f} km")
print(f"Tempo: {details['optimization_time']:.3f}s")

# Segmentos
for segment in details['segments']:
    print(f"{segment['from']} → {segment['to']}: {segment['distance']:.2f} km")
```

## Métricas e Estatísticas

### Distância Total
Soma de todas as distâncias entre paradas consecutivas, incluindo retorno ao ponto de partida.

```python
total_distance = optimizer.best_distance  # em km
```

### Tempo de Otimização
Tempo gasto para calcular a rota otimizada.

```python
optimization_time = optimizer.optimization_time  # em segundos
```

### Melhoria Percentual
Comparação entre rota inicial e otimizada.

```python
initial_distance = 14.36
optimized_distance = 13.10
improvement = ((initial_distance - optimized_distance) / initial_distance * 100)
print(f"Melhoria: {improvement:.2f}%")
```

## Otimizações de Performance

### Para Rotas Grandes (>100 paradas)

```python
# Use Nearest Neighbor com múltiplos pontos de partida
best_route = None
best_distance = float('inf')

for start in range(min(10, len(stops))):
    route, distance = optimizer.nearest_neighbor(start)
    if distance < best_distance:
        best_distance = distance
        best_route = route
```

### Para Rotas Médias (10-100 paradas)

```python
# Use 2-opt com limite de iterações
route, distance = optimizer.two_opt(max_iterations=500)
```

### Para Rotas Pequenas (<10 paradas)

```python
# Use Algoritmo Genético com mais gerações
route, distance = optimizer.genetic_algorithm(
    population_size=200,
    generations=1000,
)
```

## Limitações e Considerações

### Nearest Neighbor
- ✅ Muito rápido
- ❌ Qualidade variável
- ❌ Sensível ao ponto de partida

### 2-opt
- ✅ Bom balanço qualidade/velocidade
- ✅ Determinístico
- ❌ Pode ficar preso em ótimos locais
- ❌ Lento para rotas muito grandes

### Algoritmo Genético
- ✅ Pode encontrar soluções melhores
- ✅ Explora espaço de soluções
- ❌ Não determinístico
- ❌ Lento
- ❌ Requer ajuste de parâmetros

## Troubleshooting

### Erro: "Coordenadas inválidas"

**Causa:** Paradas sem latitude/longitude

**Solução:**
```python
# Filtra apenas paradas geocodificadas
df_valid = df[df['geocodificado'] == True]
stops = create_stops_from_dataframe(df_valid)
```

### Rota muito longa

**Causa:** Algoritmo 2-opt pode ser lento para rotas grandes

**Solução:**
```python
# Use Nearest Neighbor para rotas grandes
if len(stops) > 100:
    route, distance = optimizer.nearest_neighbor()
else:
    route, distance = optimizer.two_opt()
```

### Rota não melhora com 2-opt

**Causa:** Rota inicial já está em ótimo local

**Solução:**
```python
# Tente múltiplos pontos de partida
best_route = None
best_distance = float('inf')

for start in range(len(stops)):
    route, _ = optimizer.nearest_neighbor(start)
    route, distance = optimizer.two_opt(route)
    if distance < best_distance:
        best_distance = distance
        best_route = route
```

## Próximos Passos

### 1. Visualização em Mapa
Exibir rota otimizada em mapa interativo com Google Maps.

### 2. Restrições de Rota
Adicionar restrições como:
- Janelas de tempo
- Capacidade de veículo
- Zonas proibidas

### 3. Multi-Veículo
Otimizar múltiplas rotas para múltiplos veículos.

### 4. Integração com Navegação
Exportar rota para Waze ou Google Maps.

## Referências

- [Traveling Salesman Problem (TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem)
- [2-opt Algorithm](https://en.wikipedia.org/wiki/2-opt)
- [Genetic Algorithm](https://en.wikipedia.org/wiki/Genetic_algorithm)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026
