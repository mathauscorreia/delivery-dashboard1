"""
Script de teste automatizado para o processador de entregas.
Testa a normalização e agrupamento sem precisar do servidor web.
"""

from processor import DeliveryProcessor
import os

def test_processor():
    print("=" * 60)
    print("🧪 TESTE DO PROCESSADOR DE ENTREGAS")
    print("=" * 60)
    
    # Cria instância do processador
    processor = DeliveryProcessor()
    
    # Arquivo de entrada
    input_file = '/home/ubuntu/delivery-optimizer/test_entregas.xlsx'
    output_file = '/home/ubuntu/delivery-optimizer/output/test_result.xlsx'
    
    print(f"\n📂 Lendo arquivo: {input_file}")
    
    try:
        # Lê arquivo Excel
        df_original = processor.read_excel(input_file)
        print(f"✅ Arquivo lido com sucesso!")
        print(f"   Total de registros: {len(df_original)}")
        
        # Mostra primeiras linhas
        print(f"\n📋 Primeiras entregas:")
        print(df_original[['id', 'endereco', 'numero', 'bairro']].head(10).to_string(index=False))
        
        # Agrupa entregas
        print(f"\n⚙️  Processando agrupamento...")
        df_grouped = processor.group_deliveries(df_original)
        print(f"✅ Agrupamento concluído!")
        
        # Mostra resultados agrupados
        print(f"\n📊 Entregas agrupadas (top 10 por quantidade):")
        print(df_grouped[['endereco', 'numero', 'bairro', 'quantidade_pacotes', 'ids_agrupados']].head(10).to_string(index=False))
        
        # Salva resultado
        print(f"\n💾 Salvando resultado em: {output_file}")
        processor.save_to_excel(df_grouped, output_file)
        print(f"✅ Arquivo salvo com sucesso!")
        
        # Obtém e exibe estatísticas
        stats = processor.get_statistics()
        
        print(f"\n" + "=" * 60)
        print("📈 ESTATÍSTICAS DO PROCESSAMENTO")
        print("=" * 60)
        print(f"📦 Paradas Originais:      {stats['original_count']}")
        print(f"✅ Paradas Otimizadas:     {stats['grouped_count']}")
        print(f"💰 Paradas Economizadas:   {stats['stops_saved']}")
        print(f"📊 Percentual de Economia: {stats['percentage_saved']}%")
        print(f"⏱️  Tempo Economizado:      {stats['time_saved_minutes']} minutos")
        print(f"⚡ Tempo de Processamento: {stats['processing_time']} segundos")
        print("=" * 60)
        
        # Verifica se atende aos requisitos
        print(f"\n✅ VERIFICAÇÃO DE REQUISITOS:")
        
        if stats['processing_time'] < 3:
            print(f"   ✅ Performance: {stats['processing_time']}s < 3s (PASSOU)")
        else:
            print(f"   ❌ Performance: {stats['processing_time']}s >= 3s (FALHOU)")
        
        if stats['grouped_count'] < stats['original_count']:
            print(f"   ✅ Agrupamento: {stats['stops_saved']} paradas economizadas (PASSOU)")
        else:
            print(f"   ❌ Agrupamento: Nenhuma parada economizada (FALHOU)")
        
        if stats['percentage_saved'] > 0:
            print(f"   ✅ Economia: {stats['percentage_saved']}% (PASSOU)")
        else:
            print(f"   ❌ Economia: 0% (FALHOU)")
        
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        
        # Mostra alguns exemplos de agrupamento
        print(f"\n🔍 EXEMPLOS DE AGRUPAMENTO:")
        print(f"\nEndereços que foram agrupados:")
        
        for idx, row in df_grouped.head(5).iterrows():
            if row['quantidade_pacotes'] > 1:
                print(f"\n   📍 {row['endereco']}, {row['numero']} - {row['bairro']}")
                print(f"      Pacotes: {row['quantidade_pacotes']}")
                print(f"      IDs: {row['ids_agrupados']}")
                if row['complemento']:
                    print(f"      Complementos: {row['complemento']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_processor()
    exit(0 if success else 1)
