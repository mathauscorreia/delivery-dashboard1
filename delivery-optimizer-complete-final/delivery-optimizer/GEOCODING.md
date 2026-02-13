# 🗺️ Guia de Geocodificação - Delivery Optimizer

## Visão Geral

O Delivery Optimizer inclui um sistema de geocodificação que valida endereços e obtém coordenadas de latitude/longitude para cada parada otimizada. Isso permite:

- ✅ Validação automática de endereços
- 📍 Obtenção de coordenadas geográficas
- 🗺️ Integração com mapas
- 📏 Cálculo de distâncias entre pontos
- 🚀 Preparação para otimização de rotas baseada em proximidade

## Arquitetura

### Componentes

#### 1. **GeocoderService** (Google Maps API)
Integração com Google Maps Geocoding API para geocodificação real.

**Características:**
- Requisições HTTP para Google Maps API
- Cache de resultados para otimizar performance
- Rate limiting automático
- Tratamento de erros robusto

**Uso:**
```python
from geocoder import GeocoderService

geocoder = GeocoderService(api_key="sua_chave_api")
result = geocoder.geocode({
    'endereco': 'Rua das Flores',
    'numero': '123',
    'complemento': 'Apto 101',
    'bairro': 'Centro'
})

print(result)
# {
#     'latitude': -23.5505,
#     'longitude': -46.6333,
#     'formatted_address': 'Rua das Flores, 123 - Centro, São Paulo, SP, Brasil',
#     'place_id': 'ChIJ...',
#     'status': 'OK'
# }
```

#### 2. **MockGeocoder** (Simulado)
Geocodificador simulado para testes sem necessidade de API key.

**Características:**
- Coordenadas pré-definidas para bairros conhecidos
- Variação aleatória para simular endereços diferentes
- Sem requisições HTTP
- Perfeito para desenvolvimento e testes

**Uso:**
```python
from geocoder import MockGeocoder

geocoder = MockGeocoder()
result = geocoder.geocode({
    'endereco': 'Avenida Paulista',
    'numero': '1000',
    'complemento': '',
    'bairro': 'Bela Vista'
})

print(result)
# {
#     'latitude': -23.5505,
#     'longitude': -46.6333,
#     'formatted_address': 'Avenida Paulista, 1000 - Bela Vista, Sao Paulo, SP',
#     'place_id': 'mock_12345',
#     'status': 'OK'
# }
```

### Integração com Processor

O `DeliveryProcessor` integra automaticamente a geocodificação:

```python
from processor import DeliveryProcessor
from geocoder import MockGeocoder

# Cria processador com geocodificador
processor = DeliveryProcessor(geocoder=MockGeocoder())

# Lê planilha
df = processor.read_excel('entregas.xlsx')

# Agrupa e geocodifica
df_grouped = processor.group_deliveries(df, enable_geocoding=True)

# Resultado inclui coordenadas
print(df_grouped[['endereco', 'latitude', 'longitude']])
```

## Configuração

### Usar Google Maps API

#### 1. Obter API Key

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a API de Geocoding
4. Crie uma chave de API (tipo: Chave de API)
5. Configure restrições de chave (opcional, mas recomendado)

#### 2. Configurar Variável de Ambiente

```bash
export GOOGLE_MAPS_API_KEY="sua_chave_aqui"
python3.11 app.py
```

Ou defina no código:

```python
from geocoder import GeocoderService
from processor import DeliveryProcessor

geocoder = GeocoderService(api_key="sua_chave_aqui")
processor = DeliveryProcessor(geocoder=geocoder)
```

### Usar MockGeocoder (Padrão)

Nenhuma configuração necessária! O MockGeocoder é usado por padrão:

```bash
python3.11 app.py
```

## Dados de Saída

### Colunas Adicionadas

Quando a geocodificação está ativada, a planilha otimizada inclui:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `latitude` | Float | Latitude da parada |
| `longitude` | Float | Longitude da parada |
| `endereco_formatado` | String | Endereço formatado pela API |
| `geocodificado` | Boolean | Se foi geocodificado com sucesso |

### Exemplo de Saída

```
endereco              numero  bairro      latitude   longitude   geocodificado
Rua das Flores       123     Centro      -23.5579   -46.6384    True
Avenida Paulista     1000    Bela Vista  -23.5466   -46.6418    True
Rua Vergueiro        1000    Vila Mariana -23.5870  -46.6170    True
```

## Funcionalidades Avançadas

### Cálculo de Distância

Calcule distâncias entre duas coordenadas usando a fórmula de Haversine:

```python
from geocoder import MockGeocoder

geocoder = MockGeocoder()

# Coordenadas
lat1, lon1 = -23.5505, -46.6333  # Centro
lat2, lon2 = -23.5615, -46.6833  # Pinheiros

# Calcula distância em km
distance = geocoder.get_distance(lat1, lon1, lat2, lon2)
print(f"Distância: {distance:.2f} km")  # Distância: 5.24 km
```

### Geocodificação em Lote

Geocodifique múltiplos endereços de uma vez:

```python
from geocoder import MockGeocoder

geocoder = MockGeocoder()

addresses = [
    {'endereco': 'Rua A', 'numero': '100', 'complemento': '', 'bairro': 'Centro'},
    {'endereco': 'Rua B', 'numero': '200', 'complemento': '', 'bairro': 'Pinheiros'},
    {'endereco': 'Rua C', 'numero': '300', 'complemento': '', 'bairro': 'Jardins'},
]

results = geocoder.geocode_batch(addresses, show_progress=True)
```

### Estatísticas de Geocodificação

Obtenha estatísticas do processamento:

```python
from processor import DeliveryProcessor
from geocoder import MockGeocoder

processor = DeliveryProcessor(geocoder=MockGeocoder())
df = processor.read_excel('entregas.xlsx')
df_grouped = processor.group_deliveries(df, enable_geocoding=True)

stats = processor.get_statistics()

print(f"Geocodificador: {stats['geocoder_stats']['total_requests']} requisições")
print(f"Taxa de sucesso: {stats['geocoder_stats']['success_rate']:.1f}%")
print(f"Tempo de geocodificação: {stats['geocoding_time']:.3f}s")
```

## Casos de Uso

### 1. Validação de Endereços

Verifique se um endereço é válido:

```python
result = geocoder.geocode(address_data)
if result and result['status'] == 'OK':
    print("Endereço válido!")
else:
    print("Endereço inválido ou não encontrado")
```

### 2. Integração com Google Maps

Use as coordenadas para exibir mapa:

```html
<iframe width="400" height="300" style="border:0" 
  src="https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q=lat:{latitude},lng:{longitude}">
</iframe>
```

### 3. Otimização de Rota

Use distâncias para ordenar paradas:

```python
from geocoder import MockGeocoder

geocoder = MockGeocoder()

# Calcula matriz de distâncias
for i, row1 in df_grouped.iterrows():
    for j, row2 in df_grouped.iterrows():
        dist = geocoder.get_distance(
            row1['latitude'], row1['longitude'],
            row2['latitude'], row2['longitude']
        )
        print(f"Distância {i} → {j}: {dist:.2f} km")
```

## Limitações e Considerações

### MockGeocoder
- ✅ Sem custos
- ✅ Sem limite de requisições
- ✅ Perfeito para testes
- ❌ Coordenadas aproximadas
- ❌ Sem validação real de endereços

### Google Maps API
- ✅ Coordenadas precisas
- ✅ Validação real de endereços
- ✅ Endereços formatados
- ❌ Requer API key
- ❌ Custos por requisição (após limite gratuito)
- ❌ Rate limiting

### Cotas Gratuitas (Google Maps)
- 25.000 requisições/dia gratuitas
- Depois: $0.005 por requisição (até 100.000/dia)

## Troubleshooting

### Erro: "API key not valid"

**Causa:** Chave de API inválida ou não configurada

**Solução:**
```bash
export GOOGLE_MAPS_API_KEY="sua_chave_correta"
python3.11 app.py
```

### Erro: "ZERO_RESULTS"

**Causa:** Endereço não encontrado

**Solução:**
- Verifique se o endereço está correto
- Adicione mais informações (número, bairro)
- Use MockGeocoder para testes

### Erro: "OVER_QUERY_LIMIT"

**Causa:** Limite de requisições excedido

**Solução:**
- Aguarde antes de fazer mais requisições
- Aumente o `RATE_LIMIT_DELAY` em `geocoder.py`
- Considere usar cache

### Coordenadas Nulas

**Causa:** Geocodificação desativada ou falhou

**Solução:**
```python
# Ative geocodificação
df_grouped = processor.group_deliveries(df, enable_geocoding=True)

# Verifique se está ativada
print(df_grouped['geocodificado'].value_counts())
```

## Próximos Passos

### 1. Otimização de Rota com Distâncias
Implemente algoritmo de rota otimizada usando as distâncias geocodificadas.

### 2. Visualização em Mapa
Crie mapa interativo mostrando todas as paradas com suas coordenadas.

### 3. Integração com Waze/Google Maps
Exporte rotas otimizadas para aplicativos de navegação.

### 4. Cálculo de Tempo de Viagem
Use Google Maps Distance Matrix API para tempo real de viagem.

## Referências

- [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding)
- [Fórmula de Haversine](https://en.wikipedia.org/wiki/Haversine_formula)
- [Google Cloud Console](https://console.cloud.google.com/)

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026
