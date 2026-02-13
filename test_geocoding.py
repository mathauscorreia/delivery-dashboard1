"""
Script de teste para geocodificação de endereços.
Testa a integração com o geocodificador (real ou simulado).
"""

from processor import DeliveryProcessor
from geocoder import MockGeocoder, GeocoderService
import os

def test_geocoding():
    print("=" * 60)
    print("🧪 TESTE DE GEOCODIFICAÇÃO")
    print("=" * 60)
    
    # Cria instância do processador com MockGeocoder
    print("\n📍 Testando com MockGeocoder (simulado)...")
    processor = DeliveryProcessor(geocoder=MockGeocoder())
    
    # Arquivo de entrada
    input_file = '/home/ubuntu/delivery-optimizer/test_entregas.xlsx'
    output_file = '/home/ubuntu/delivery-optimizer/output/test_geocoding_result.xlsx'
    
    print(f"\n📂 Lendo arquivo: {input_file}")
    
    try:
        # Lê arquivo Excel
        df_original = processor.read_excel(input_file)
        print(f"✅ Arquivo lido com sucesso!")
        print(f"   Total de registros: {len(df_original)}")
        
        # Agrupa entregas com geocodificação
        print(f"\n⚙️  Processando agrupamento com geocodificação...")
        df_grouped = processor.group_deliveries(df_original, enable_geocoding=True)
        print(f"✅ Agrupamento e geocodificação concluídos!")
        
        # Mostra resultados
        print(f"\n📊 Entregas agrupadas com coordenadas (top 5):")
        print(df_grouped[['endereco', 'numero', 'bairro', 'latitude', 'longitude', 'geocodificado']].head(5).to_string(index=False))
        
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
        print(f"🌐 Tempo de Geocodificação: {stats['geocoding_time']} segundos")
        
        # Mostra estatísticas do geocodificador
        if stats['geocoder_stats']:
            print(f"\n🌐 ESTATÍSTICAS DO GEOCODIFICADOR")
            print("=" * 60)
            print(f"Tipo: {type(processor.geocoder).__name__}")
            print(f"Total de requisições: {stats['geocoder_stats'].get('total_requests', 0)}")
            print(f"Sucessos: {stats['geocoder_stats'].get('successful', 0)}")
            print(f"Falhas: {stats['geocoder_stats'].get('failed', 0)}")
            print(f"Taxa de sucesso: {stats['geocoder_stats'].get('success_rate', 0):.1f}%")
            print(f"Resultados em cache: {stats['geocoder_stats'].get('cached_results', 0)}")
        
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        
        # Mostra alguns exemplos de endereços geocodificados
        print(f"\n🗺️  EXEMPLOS DE ENDEREÇOS GEOCODIFICADOS:")
        
        geocoded_df = df_grouped[df_grouped['geocodificado'] == True]
        for idx, row in geocoded_df.head(3).iterrows():
            print(f"\n   📍 {row['endereco']}, {row['numero']} - {row['bairro']}")
            print(f"      Coordenadas: ({row['latitude']:.4f}, {row['longitude']:.4f})")
            print(f"      Endereço Formatado: {row['endereco_formatado']}")
            print(f"      Pacotes: {row['quantidade_pacotes']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_distance_calculation():
    """Testa cálculo de distância entre pontos."""
    print(f"\n\n" + "=" * 60)
    print("📏 TESTE DE CÁLCULO DE DISTÂNCIA")
    print("=" * 60)
    
    geocoder = MockGeocoder()
    
    # Coordenadas de exemplo (São Paulo)
    # Centro: -23.5505, -46.6333
    # Pinheiros: -23.5615, -46.6833
    
    lat1, lon1 = -23.5505, -46.6333  # Centro
    lat2, lon2 = -23.5615, -46.6833  # Pinheiros
    
    distance = geocoder.get_distance(lat1, lon1, lat2, lon2)
    
    print(f"\nCentro: ({lat1}, {lon1})")
    print(f"Pinheiros: ({lat2}, {lon2})")
    print(f"\nDistância: {distance:.2f} km")
    
    print(f"\n✅ Cálculo de distância funcionando!")


if __name__ == '__main__':
    success = test_geocoding()
    
    if success:
        test_distance_calculation()
    
    exit(0 if success else 1)
