"""
Script para gerar dados de teste para o sistema de otimização de entregas.
Cria uma planilha Excel com endereços variados para testar normalização e agrupamento.
"""

import pandas as pd
import random

# Dados de teste com variações intencionais para testar normalização
test_deliveries = [
    # Mesmo endereço com variações
    {'id': 1, 'endereco': 'Rua das Flores', 'numero': '123', 'complemento': 'Apto 101', 'bairro': 'Centro'},
    {'id': 2, 'endereco': 'R. das Flores', 'numero': '123', 'complemento': 'Apto 102', 'bairro': 'centro'},
    {'id': 3, 'endereco': 'R das Flores', 'numero': '123', 'complemento': 'Ap 103', 'bairro': 'CENTRO'},
    
    # Avenida com variações
    {'id': 4, 'endereco': 'Avenida Paulista', 'numero': '1000', 'complemento': '', 'bairro': 'Bela Vista'},
    {'id': 5, 'endereco': 'Av. Paulista', 'numero': '1000', 'complemento': 'Loja 5', 'bairro': 'Bela Vista'},
    {'id': 6, 'endereco': 'Av Paulista', 'numero': '1000', 'complemento': '', 'bairro': 'bela vista'},
    
    # Travessa com variações
    {'id': 7, 'endereco': 'Travessa do Comércio', 'numero': '45', 'complemento': '', 'bairro': 'Sé'},
    {'id': 8, 'endereco': 'Tv. do Comércio', 'numero': '45', 'complemento': 'Casa 2', 'bairro': 'Sé'},
    {'id': 9, 'endereco': 'Tv do Comércio', 'numero': '45', 'complemento': '', 'bairro': 'sé'},
    
    # Alameda
    {'id': 10, 'endereco': 'Alameda Santos', 'numero': '2000', 'complemento': 'Bloco A', 'bairro': 'Jardins'},
    {'id': 11, 'endereco': 'Al. Santos', 'numero': '2000', 'complemento': 'Bloco B', 'bairro': 'Jardins'},
    
    # Praça
    {'id': 12, 'endereco': 'Praça da República', 'numero': 's/n', 'complemento': '', 'bairro': 'República'},
    {'id': 13, 'endereco': 'Pç. da República', 'numero': 'SN', 'complemento': '', 'bairro': 'República'},
    
    # Estrada
    {'id': 14, 'endereco': 'Estrada do M Boi Mirim', 'numero': '5000', 'complemento': '', 'bairro': 'Jardim Ângela'},
    {'id': 15, 'endereco': 'Est. do M Boi Mirim', 'numero': '5000', 'complemento': 'Casa 1', 'bairro': 'Jardim Ângela'},
    
    # Endereços únicos (não devem ser agrupados)
    {'id': 16, 'endereco': 'Rua Augusta', 'numero': '500', 'complemento': '', 'bairro': 'Consolação'},
    {'id': 17, 'endereco': 'Rua Oscar Freire', 'numero': '300', 'complemento': '', 'bairro': 'Jardins'},
    {'id': 18, 'endereco': 'Avenida Rebouças', 'numero': '1500', 'complemento': '', 'bairro': 'Pinheiros'},
    {'id': 19, 'endereco': 'Rua da Consolação', 'numero': '2000', 'complemento': '', 'bairro': 'Consolação'},
    {'id': 20, 'endereco': 'Avenida Faria Lima', 'numero': '3000', 'complemento': '', 'bairro': 'Itaim Bibi'},
    
    # Mais variações do mesmo endereço
    {'id': 21, 'endereco': 'RUA DAS FLORES', 'numero': '123', 'complemento': 'APTO 104', 'bairro': 'Centro'},
    {'id': 22, 'endereco': 'r.  das   flores', 'numero': '123', 'complemento': '', 'bairro': 'centro'},
    
    # Números com variações
    {'id': 23, 'endereco': 'Rua Vergueiro', 'numero': '1000', 'complemento': '', 'bairro': 'Vila Mariana'},
    {'id': 24, 'endereco': 'R. Vergueiro', 'numero': '1000', 'complemento': 'Apto 501', 'bairro': 'Vila Mariana'},
    {'id': 25, 'endereco': 'Rua Vergueiro', 'numero': '1001', 'complemento': '', 'bairro': 'Vila Mariana'},
    
    # Sem número
    {'id': 26, 'endereco': 'Rua dos Pinheiros', 'numero': 's/n', 'complemento': '', 'bairro': 'Pinheiros'},
    {'id': 27, 'endereco': 'R. dos Pinheiros', 'numero': 'sem número', 'complemento': '', 'bairro': 'Pinheiros'},
    {'id': 28, 'endereco': 'Rua dos Pinheiros', 'numero': '', 'complemento': '', 'bairro': 'pinheiros'},
    
    # Complementos variados
    {'id': 29, 'endereco': 'Avenida Ipiranga', 'numero': '200', 'complemento': 'Apartamento 10', 'bairro': 'República'},
    {'id': 30, 'endereco': 'Av. Ipiranga', 'numero': '200', 'complemento': 'Apto 11', 'bairro': 'República'},
    {'id': 31, 'endereco': 'Av Ipiranga', 'numero': '200', 'complemento': 'Ap 12', 'bairro': 'república'},
    
    # Mais endereços para atingir 80+
    {'id': 32, 'endereco': 'Rua Haddock Lobo', 'numero': '595', 'complemento': '', 'bairro': 'Cerqueira César'},
    {'id': 33, 'endereco': 'R. Haddock Lobo', 'numero': '595', 'complemento': 'Loja 1', 'bairro': 'Cerqueira César'},
    {'id': 34, 'endereco': 'Avenida Brigadeiro Faria Lima', 'numero': '2000', 'complemento': '', 'bairro': 'Jardim Paulistano'},
    {'id': 35, 'endereco': 'Av. Brig. Faria Lima', 'numero': '2000', 'complemento': 'Sala 100', 'bairro': 'Jardim Paulistano'},
    {'id': 36, 'endereco': 'Rua Estados Unidos', 'numero': '1500', 'complemento': '', 'bairro': 'Jardim América'},
    {'id': 37, 'endereco': 'R. Estados Unidos', 'numero': '1500', 'complemento': 'Apto 201', 'bairro': 'Jardim América'},
    {'id': 38, 'endereco': 'Avenida São João', 'numero': '1000', 'complemento': '', 'bairro': 'Centro'},
    {'id': 39, 'endereco': 'Av. São João', 'numero': '1000', 'complemento': '', 'bairro': 'centro'},
    {'id': 40, 'endereco': 'Rua Pamplona', 'numero': '145', 'complemento': '', 'bairro': 'Jardim Paulista'},
    {'id': 41, 'endereco': 'R. Pamplona', 'numero': '145', 'complemento': 'Conj 12', 'bairro': 'Jardim Paulista'},
    {'id': 42, 'endereco': 'Avenida Angélica', 'numero': '2000', 'complemento': '', 'bairro': 'Consolação'},
    {'id': 43, 'endereco': 'Av. Angélica', 'numero': '2000', 'complemento': '', 'bairro': 'Consolação'},
    {'id': 44, 'endereco': 'Rua Bela Cintra', 'numero': '500', 'complemento': '', 'bairro': 'Consolação'},
    {'id': 45, 'endereco': 'R. Bela Cintra', 'numero': '500', 'complemento': 'Apto 301', 'bairro': 'consolação'},
    {'id': 46, 'endereco': 'Avenida Nove de Julho', 'numero': '3000', 'complemento': '', 'bairro': 'Jardins'},
    {'id': 47, 'endereco': 'Av. 9 de Julho', 'numero': '3000', 'complemento': '', 'bairro': 'Jardins'},
    {'id': 48, 'endereco': 'Rua Iguatemi', 'numero': '100', 'complemento': '', 'bairro': 'Itaim Bibi'},
    {'id': 49, 'endereco': 'R. Iguatemi', 'numero': '100', 'complemento': 'Bloco 1', 'bairro': 'Itaim Bibi'},
    {'id': 50, 'endereco': 'Avenida Europa', 'numero': '500', 'complemento': '', 'bairro': 'Jardim Europa'},
    {'id': 51, 'endereco': 'Av. Europa', 'numero': '500', 'complemento': '', 'bairro': 'Jardim Europa'},
    {'id': 52, 'endereco': 'Rua Joaquim Floriano', 'numero': '800', 'complemento': '', 'bairro': 'Itaim Bibi'},
    {'id': 53, 'endereco': 'R. Joaquim Floriano', 'numero': '800', 'complemento': 'Sala 50', 'bairro': 'Itaim Bibi'},
    {'id': 54, 'endereco': 'Avenida Cidade Jardim', 'numero': '400', 'complemento': '', 'bairro': 'Jardim Paulistano'},
    {'id': 55, 'endereco': 'Av. Cidade Jardim', 'numero': '400', 'complemento': '', 'bairro': 'Jardim Paulistano'},
    {'id': 56, 'endereco': 'Rua Funchal', 'numero': '500', 'complemento': '', 'bairro': 'Vila Olímpia'},
    {'id': 57, 'endereco': 'R. Funchal', 'numero': '500', 'complemento': 'Andar 5', 'bairro': 'Vila Olímpia'},
    {'id': 58, 'endereco': 'Avenida Juscelino Kubitschek', 'numero': '1500', 'complemento': '', 'bairro': 'Itaim Bibi'},
    {'id': 59, 'endereco': 'Av. JK', 'numero': '1500', 'complemento': '', 'bairro': 'Itaim Bibi'},
    {'id': 60, 'endereco': 'Rua Gomes de Carvalho', 'numero': '1000', 'complemento': '', 'bairro': 'Vila Olímpia'},
    {'id': 61, 'endereco': 'R. Gomes de Carvalho', 'numero': '1000', 'complemento': 'Sala 200', 'bairro': 'Vila Olímpia'},
    {'id': 62, 'endereco': 'Avenida Santo Amaro', 'numero': '5000', 'complemento': '', 'bairro': 'Brooklin'},
    {'id': 63, 'endereco': 'Av. Santo Amaro', 'numero': '5000', 'complemento': '', 'bairro': 'Brooklin'},
    {'id': 64, 'endereco': 'Rua Pedroso Alvarenga', 'numero': '1000', 'complemento': '', 'bairro': 'Itaim Bibi'},
    {'id': 65, 'endereco': 'R. Pedroso Alvarenga', 'numero': '1000', 'complemento': 'Apto 101', 'bairro': 'Itaim Bibi'},
    {'id': 66, 'endereco': 'Avenida Ibirapuera', 'numero': '2000', 'complemento': '', 'bairro': 'Moema'},
    {'id': 67, 'endereco': 'Av. Ibirapuera', 'numero': '2000', 'complemento': '', 'bairro': 'Moema'},
    {'id': 68, 'endereco': 'Rua Vieira de Morais', 'numero': '500', 'complemento': '', 'bairro': 'Campo Belo'},
    {'id': 69, 'endereco': 'R. Vieira de Morais', 'numero': '500', 'complemento': 'Casa 3', 'bairro': 'Campo Belo'},
    {'id': 70, 'endereco': 'Avenida Moreira Guimarães', 'numero': '1000', 'complemento': '', 'bairro': 'Indianópolis'},
    {'id': 71, 'endereco': 'Av. Moreira Guimarães', 'numero': '1000', 'complemento': '', 'bairro': 'Indianópolis'},
    {'id': 72, 'endereco': 'Rua Domingos de Morais', 'numero': '2000', 'complemento': '', 'bairro': 'Vila Mariana'},
    {'id': 73, 'endereco': 'R. Domingos de Morais', 'numero': '2000', 'complemento': 'Loja 10', 'bairro': 'Vila Mariana'},
    {'id': 74, 'endereco': 'Avenida Lins de Vasconcelos', 'numero': '1500', 'complemento': '', 'bairro': 'Cambuci'},
    {'id': 75, 'endereco': 'Av. Lins de Vasconcelos', 'numero': '1500', 'complemento': '', 'bairro': 'Cambuci'},
    {'id': 76, 'endereco': 'Rua Tutóia', 'numero': '800', 'complemento': '', 'bairro': 'Paraíso'},
    {'id': 77, 'endereco': 'R. Tutóia', 'numero': '800', 'complemento': 'Apto 202', 'bairro': 'Paraíso'},
    {'id': 78, 'endereco': 'Avenida Brigadeiro Luís Antônio', 'numero': '2000', 'complemento': '', 'bairro': 'Bela Vista'},
    {'id': 79, 'endereco': 'Av. Brig. Luís Antônio', 'numero': '2000', 'complemento': '', 'bairro': 'Bela Vista'},
    {'id': 80, 'endereco': 'Rua Avanhandava', 'numero': '100', 'complemento': '', 'bairro': 'Bela Vista'},
    {'id': 81, 'endereco': 'R. Avanhandava', 'numero': '100', 'complemento': 'Sala 5', 'bairro': 'Bela Vista'},
    {'id': 82, 'endereco': 'Avenida Pacaembu', 'numero': '1000', 'complemento': '', 'bairro': 'Pacaembu'},
    {'id': 83, 'endereco': 'Av. Pacaembu', 'numero': '1000', 'complemento': '', 'bairro': 'Pacaembu'},
    {'id': 84, 'endereco': 'Rua Cardeal Arcoverde', 'numero': '500', 'complemento': '', 'bairro': 'Pinheiros'},
    {'id': 85, 'endereco': 'R. Cardeal Arcoverde', 'numero': '500', 'complemento': 'Apto 303', 'bairro': 'Pinheiros'},
]

# Cria DataFrame
df = pd.DataFrame(test_deliveries)

# Salva em Excel
output_file = '/home/ubuntu/delivery-optimizer/test_entregas.xlsx'
df.to_excel(output_file, index=False, sheet_name='Entregas')

print(f"✅ Planilha de teste criada com sucesso!")
print(f"📁 Arquivo: {output_file}")
print(f"📊 Total de entregas: {len(df)}")
print(f"\n🔍 Resumo dos dados:")
print(f"   - Endereços únicos esperados após agrupamento: ~42")
print(f"   - Economia esperada: ~50%")
print(f"\n💡 Casos de teste incluídos:")
print(f"   ✓ Variações de tipo de logradouro (Rua/R., Avenida/Av., etc)")
print(f"   ✓ Diferenças de maiúsculas/minúsculas")
print(f"   ✓ Espaços duplicados")
print(f"   ✓ Complementos variados")
print(f"   ✓ Números sem número (s/n, SN, vazio)")
print(f"   ✓ Abreviações diferentes")
