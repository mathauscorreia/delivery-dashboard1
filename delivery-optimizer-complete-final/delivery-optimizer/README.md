# 🚚 Delivery Optimizer - Sistema de Otimização de Entregas

Sistema inteligente de agrupamento de entregas com normalização automática de endereços, desenvolvido para motoristas SPX.

## 📋 Visão Geral

O **Delivery Optimizer** é uma aplicação web que processa planilhas de entregas e agrupa automaticamente pacotes destinados ao mesmo endereço, mesmo quando há variações na forma como o endereço foi escrito. O sistema normaliza endereços, remove duplicatas e gera uma nova planilha otimizada, economizando tempo e reduzindo o número de paradas.

### 🎯 Principais Funcionalidades

- ✅ **Normalização Inteligente de Endereços**
  - Converte variações de logradouros (Rua/R., Avenida/Av., Travessa/Tv., etc)
  - Remove diferenças de maiúsculas/minúsculas
  - Elimina espaços duplicados
  - Padroniza complementos (Apartamento/Apto/Ap)
  - Trata campos vazios e números sem número (s/n)

- ⚡ **Performance Otimizada**
  - Processa 80+ entregas em menos de 0.05 segundos
  - Algoritmo eficiente baseado em Pandas
  - Funciona 100% offline, sem dependência de APIs externas

- 📊 **Estatísticas Detalhadas**
  - Total de paradas originais vs otimizadas
  - Quantidade de paradas economizadas
  - Percentual de economia
  - Tempo estimado economizado (3 min/parada)
  - Tempo de processamento

- 🎨 **Interface Moderna**
  - Design responsivo com Bootstrap 5
  - Upload via drag-and-drop
  - Feedback visual em tempo real
  - Gráficos e métricas interativas

- 🗺️ **Geocodificação Inteligente**
  - Validação automática de endereços
  - Obtenção de coordenadas (latitude/longitude)
  - Suporte a Google Maps API ou MockGeocoder
  - Cálculo de distâncias entre pontos
  - Cache de resultados para otimizar performance

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11**
- **Flask 3.0** - Framework web
- **Pandas 2.1** - Processamento de dados
- **Openpyxl 3.1** - Leitura/escrita de Excel

### Frontend
- **HTML5 / CSS3**
- **Bootstrap 5.3** - Framework UI
- **JavaScript (Vanilla)** - Interatividade

### Banco de Dados
- **SQLite** (opcional, preparado para histórico)

## 📂 Estrutura do Projeto

```
delivery-optimizer/
├── app.py                 # Aplicação Flask principal
├── normalizer.py          # Módulo de normalização de endereços
├── processor.py           # Módulo de processamento e agrupamento
├── requirements.txt       # Dependências Python
├── test_data.py          # Gerador de dados de teste
├── test_processor.py     # Script de teste automatizado
├── README.md             # Este arquivo
├── templates/
│   └── index.html        # Interface web
├── static/
│   ├── css/              # Estilos customizados (se necessário)
│   └── js/               # Scripts customizados (se necessário)
├── uploads/              # Arquivos enviados (temporário)
├── output/               # Planilhas otimizadas geradas
└── test_entregas.xlsx    # Planilha de exemplo para testes
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### Passo 1: Instalar Dependências

```bash
cd delivery-optimizer
pip install -r requirements.txt
```

Ou, se estiver usando o ambiente do sistema:

```bash
sudo pip3 install -r requirements.txt
```

### Passo 2: Iniciar o Servidor

```bash
python3.11 app.py
```

Você verá a mensagem:

```
============================================================
🚚 DELIVERY OPTIMIZER - Sistema de Otimização de Entregas
============================================================

✅ Servidor iniciado com sucesso!
📍 Acesse: http://127.0.0.1:5000

⚡ Aguardando upload de planilhas...
```

### Passo 3: Acessar a Interface

Abra seu navegador e acesse:

```
http://127.0.0.1:5000
```

## 📝 Como Usar

### 1. Preparar Planilha de Entregas

Sua planilha Excel (.xlsx ou .xls) deve conter as seguintes colunas:

| Coluna      | Obrigatória | Descrição                          |
|-------------|-------------|------------------------------------|
| `endereco`  | ✅ Sim      | Endereço completo (rua/avenida)    |
| `numero`    | ✅ Sim      | Número do endereço                 |
| `bairro`    | ✅ Sim      | Nome do bairro                     |
| `complemento` | ❌ Não    | Apartamento, bloco, casa, etc      |
| `id`        | ❌ Não      | ID da entrega (gerado se ausente)  |

**Exemplo:**

| id | endereco           | numero | complemento | bairro      |
|----|--------------------|--------|-------------|-------------|
| 1  | Rua das Flores     | 123    | Apto 101    | Centro      |
| 2  | R. das Flores      | 123    | Apto 102    | centro      |
| 3  | Avenida Paulista   | 1000   |             | Bela Vista  |

### 2. Upload da Planilha

1. Clique na área de upload ou arraste o arquivo
2. Selecione sua planilha (.xlsx ou .xls)
3. Clique em **"Processar Entregas"**

### 3. Visualizar Resultados

Após o processamento, você verá:

- 📦 **Paradas Originais**: Total de entregas na planilha
- ✅ **Paradas Otimizadas**: Total após agrupamento
- 💰 **Paradas Economizadas**: Quantidade reduzida
- 📊 **Percentual de Economia**: % de otimização
- ⏱️ **Tempo Economizado**: Estimativa em minutos

### 4. Baixar Planilha Otimizada

Clique em **"Baixar Planilha Otimizada"** para fazer download do arquivo Excel processado.

A planilha otimizada conterá:

| Coluna              | Descrição                                    |
|---------------------|----------------------------------------------|
| `endereco`          | Endereço normalizado                         |
| `numero`            | Número normalizado                           |
| `complemento`       | Complementos agrupados (separados por vírgula) |
| `bairro`            | Bairro normalizado                           |
| `quantidade_pacotes`| Número de pacotes neste endereço             |
| `ids_agrupados`     | IDs das entregas agrupadas                   |

## 🧪 Testes

### Gerar Planilha de Teste

```bash
python3.11 test_data.py
```

Isso criará `test_entregas.xlsx` com 85 entregas de exemplo contendo variações intencionais para testar a normalização.

### Executar Teste Automatizado

```bash
python3.11 test_processor.py
```

Este script testa o processamento completo e exibe estatísticas detalhadas.

### Testar Geocodificação

```bash
python3.11 test_geocoding.py
```

Este script testa a geocodificação com MockGeocoder e exibe:
- Coordenadas obtidas para cada parada
- Taxa de sucesso da geocodificação
- Cálculo de distância entre pontos
- Arquivo Excel com coordenadas

**Resultado esperado:**

```
📈 ESTATÍSTICAS DO PROCESSAMENTO
============================================================
📦 Paradas Originais:      85
✅ Paradas Otimizadas:     46
💰 Paradas Economizadas:   39
📊 Percentual de Economia: 45.88%
⏱️  Tempo Economizado:      117 minutos
⚡ Tempo de Processamento: 0.045 segundos
============================================================

✅ VERIFICAÇÃO DE REQUISITOS:
   ✅ Performance: 0.045s < 3s (PASSOU)
   ✅ Agrupamento: 39 paradas economizadas (PASSOU)
   ✅ Economia: 45.88% (PASSOU)
```

## 🔍 Como Funciona a Normalização

### Exemplos de Normalização

#### 1. Tipo de Logradouro

| Original            | Normalizado |
|---------------------|-------------|
| Rua das Flores      | r das flores |
| R. das Flores       | r das flores |
| R das Flores        | r das flores |
| Avenida Paulista    | av paulista |
| Av. Paulista        | av paulista |
| Travessa do Comércio| tv do comércio |

#### 2. Maiúsculas/Minúsculas

| Original     | Normalizado  |
|--------------|--------------|
| CENTRO       | centro       |
| Centro       | centro       |
| centro       | centro       |

#### 3. Números

| Original      | Normalizado |
|---------------|-------------|
| 123           | 123         |
| s/n           | s/n         |
| sem número    | s/n         |
| (vazio)       | s/n         |

#### 4. Complementos

| Original           | Normalizado |
|--------------------|-------------|
| Apartamento 101    | ap 101      |
| Apto 101           | ap 101      |
| Bloco A            | bl a        |
| Casa 2             | cs 2        |

### Critério de Agrupamento

Duas entregas são agrupadas quando possuem:
- ✅ Mesmo endereço normalizado
- ✅ Mesmo número normalizado
- ✅ Mesmo bairro normalizado

**Nota:** Complementos diferentes **não impedem** o agrupamento. Eles são apenas concatenados na planilha final.

## 📊 Casos de Uso

### Exemplo Real

**Entrada (3 entregas):**

| id | endereco          | numero | complemento | bairro |
|----|-------------------|--------|-------------|--------|
| 1  | Rua das Flores    | 123    | Apto 101    | Centro |
| 2  | R. das Flores     | 123    | Apto 102    | centro |
| 3  | RUA DAS FLORES    | 123    | Apto 103    | CENTRO |

**Saída (1 parada):**

| endereco       | numero | complemento              | bairro | quantidade_pacotes | ids_agrupados |
|----------------|--------|--------------------------|--------|--------------------|---------------|
| r das flores   | 123    | ap101, ap102, ap103      | centro | 3                  | 1, 2, 3       |

**Resultado:**
- ✅ 3 entregas → 1 parada
- 💰 2 paradas economizadas (66.67%)
- ⏱️ 6 minutos economizados

## 🗺️ Geocodificação (IMPLEMENTADO ✅)

O sistema agora inclui geocodificação completa:

### Recursos Implementados
- ✅ **GeocoderService**: Integração com Google Maps Geocoding API
- ✅ **MockGeocoder**: Geocodificador simulado para testes
- ✅ **Coordenadas**: Latitude e longitude para cada parada
- ✅ **Validação**: Verificação automática de endereços
- ✅ **Distâncias**: Cálculo de distância entre pontos (Haversine)
- ✅ **Cache**: Otimização de performance com cache de resultados
- ✅ **Estatísticas**: Relatório detalhado de geocodificação

**Veja `GEOCODING.md` para documentação completa!**

## 🗺️ Otimização de Rota (IMPLEMENTADO ✅)

O sistema inclui algoritmos avançados de otimização de rota:

### Algoritmos Disponíveis
- ✅ **Nearest Neighbor**: Rápido (guloso), ideal para rotas grandes
- ✅ **2-opt**: Otimizado, remove cruzamentos, recomendado para produção
- ✅ **Algoritmo Genético**: Avançado, busca global, para rotas pequenas

### Resultados (46 Paradas)
- **Nearest Neighbor**: 14.36 km
- **2-opt**: 13.10 km (8.80% de melhoria)
- **Algoritmo Genético**: 18.73 km

**Veja `ROUTE_OPTIMIZATION.md` para documentação completa!**

## 🚀 Evolução Futura

O sistema está preparado para as seguintes melhorias:

### 🗺️ Visualização em Mapa Interativo
- Mapa com todas as paradas geocodificadas
- Exibição da rota otimizada
- Integração com Google Maps
- Clusters de entregas por região

### 📱 Versão Mobile (PWA)
- Aplicativo instalável
- Funciona offline
- Notificações push
- Sincronização em nuvem

### 📈 Dashboard e Histórico
- Histórico de otimizações
- Gráficos de performance
- Estatísticas acumuladas
- Comparação entre períodos

### ☁️ Versão SaaS
- Multi-usuário
- Autenticação e autorização
- API REST
- Planos de assinatura

## 🔧 Configuração Avançada

### Alterar Porta do Servidor

Edite `app.py` na última linha:

```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Altere 5000 para 8080
```

### Ajustar Tamanho Máximo de Upload

Edite `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Personalizar Estimativa de Tempo

Edite `processor.py` no método `get_statistics()`:

```python
time_saved_minutes = stops_saved * 5  # Altere 3 para 5 minutos
```

## 🐛 Solução de Problemas

### Erro: "Colunas obrigatórias ausentes"

**Causa:** Sua planilha não possui as colunas `endereco`, `numero` ou `bairro`.

**Solução:** Renomeie as colunas da sua planilha para corresponder aos nomes esperados (tudo em minúsculas).

### Erro: "Formato de arquivo não permitido"

**Causa:** Arquivo enviado não é .xlsx ou .xls.

**Solução:** Converta sua planilha para formato Excel (.xlsx).

### Servidor não inicia

**Causa:** Porta 5000 já está em uso.

**Solução:** 
1. Feche outros aplicativos usando a porta 5000
2. Ou altere a porta no `app.py` (veja Configuração Avançada)

### Performance lenta

**Causa:** Planilha muito grande (>10.000 linhas).

**Solução:** O sistema foi otimizado para até 1.000 entregas. Para volumes maiores, considere dividir a planilha ou aguardar a versão otimizada para big data.

## 📄 Licença

Este projeto foi desenvolvido para uso interno de motoristas SPX. Todos os direitos reservados.

## 👨‍💻 Desenvolvimento

Desenvolvido com Python, Flask, Pandas e Bootstrap.

### Contribuindo

Para reportar bugs ou sugerir melhorias, entre em contato com a equipe de desenvolvimento.

---

**Versão:** 1.0.0  
**Última atualização:** Fevereiro 2026  
**Status:** ✅ Produção
