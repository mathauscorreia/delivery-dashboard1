"""
Script de teste do pipeline completo.
Testa normalização → geocodificação → otimização de rota.
"""

from processor_with_routing import DeliveryProcessorWithRouting
from geocoder import MockGeocoder
import time


def test_complete_pipeline():
    print("=" * 80)
    print("🚚 TESTE DO PIPELINE COMPLETO")
    print("=" * 80)
    
    input_file = '/home/ubuntu/delivery-optimizer/test_entregas.xlsx'
    output_file = '/home/ubuntu/delivery-optimizer/output/pipeline_completo.xlsx'
    
    print(f"\n📂 Arquivo de entrada: {input_file}")
    
    try:
        # Cria processador com MockGeocoder
        print(f"\n⚙️  Inicializando processador...")
        geocoder = MockGeocoder()
        processor = DeliveryProcessorWithRouting(geocoder=geocoder)
        print(f"✅ Processador inicializado")
        
        # Executa pipeline completo
        print(f"\n🚀 Executando pipeline completo...")
        print(f"   1. Leitura de arquivo")
        print(f"   2. Normalização de endereços")
        print(f"   3. Geocodificação")
        print(f"   4. Agrupamento de entregas")
        print(f"   5. Otimização de rota")
        
        pipeline_start = time.time()
        
        results = processor.process_complete_pipeline(
            file_path=input_file,
            route_method='two_opt',
            output_excel=output_file
        )
        
        pipeline_time = time.time() - pipeline_start
        
        print(f"\n✅ Pipeline concluído em {pipeline_time:.3f}s")
        
        # Exibe resultados
        print(f"\n" + "=" * 80)
        print("📊 RESULTADOS DO PIPELINE")
        print("=" * 80)
        
        print(f"\n📦 AGRUPAMENTO DE ENTREGAS")
        print(f"   Entregas originais:  {results['original_count']}")
        print(f"   Paradas agrupadas:   {results['grouped_count']}")
        print(f"   Economia de paradas: {results['original_count'] - results['grouped_count']}")
        
        stats = results['statistics']
        print(f"\n📈 ESTATÍSTICAS")
        print(f"   Percentual de economia: {stats['percentage_saved']:.2f}%")
        print(f"   Tempo economizado: {stats['time_saved_minutes']} minutos")
        print(f"   Tempo de processamento: {stats['processing_time']:.3f}s")
        print(f"   Tempo de geocodificação: {stats['geocoding_time']:.3f}s")
        
        route_stats = results['route_statistics']
        if route_stats:
            print(f"\n🗺️  OTIMIZAÇÃO DE ROTA")
            print(f"   Distância total: {route_stats['total_distance_km']:.2f} km")
            print(f"   Número de paradas: {route_stats['number_of_stops']}")
            print(f"   Tempo de otimização: {route_stats['optimization_time']:.3f}s")
            print(f"   Método: {route_stats['optimization_method']}")
        
        print(f"\n⏱️  TEMPO TOTAL DO PIPELINE: {results['total_pipeline_time']:.3f}s")
        
        # Exibe amostra dos dados
        print(f"\n" + "=" * 80)
        print("📋 AMOSTRA DOS DADOS PROCESSADOS (Primeiras 5 paradas)")
        print("=" * 80)
        
        df = results['dataframe']
        
        print(f"\nColunas disponíveis: {list(df.columns)}")
        
        # Seleciona colunas relevantes
        cols_to_show = ['ordem_rota', 'endereco', 'numero', 'bairro', 'quantidade_pacotes', 
                       'latitude', 'longitude']
        
        available_cols = [col for col in cols_to_show if col in df.columns]
        
        print(f"\n{df[available_cols].head(5).to_string(index=False)}")
        
        # Detalhes da rota
        print(f"\n" + "=" * 80)
        print("🛣️  DETALHES DA ROTA OTIMIZADA")
        print("=" * 80)
        
        route_details = processor.get_route_details()
        
        if route_details:
            print(f"\n📍 Rota:")
            print(f"   Distância total: {route_details['total_distance']:.2f} km")
            print(f"   Número de paradas: {route_details['number_of_stops']}")
            print(f"   Tempo de otimização: {route_details['optimization_time']:.3f}s")
            
            print(f"\n🛣️  Primeiros 5 segmentos da rota:")
            print(f"{'De':<35} {'Para':<35} {'Distância (km)':<15}")
            print("-" * 85)
            
            for segment in route_details['segments'][:5]:
                from_addr = segment['from'][:33]
                to_addr = segment['to'][:33]
                distance = segment['distance']
                print(f"{from_addr:<35} {to_addr:<35} {distance:<15.2f}")
            
            if len(route_details['segments']) > 5:
                print(f"... ({len(route_details['segments']) - 5} segmentos adicionais)")
        
        # Comparação de métodos
        print(f"\n" + "=" * 80)
        print("📊 COMPARAÇÃO DE MÉTODOS DE OTIMIZAÇÃO")
        print("=" * 80)
        
        comparison = processor.compare_route_methods()
        
        if comparison:
            print(f"\n{'Método':<20} {'Distância (km)':<20} {'Tempo (s)':<15} {'Melhoria':<15}")
            print("-" * 70)
            
            for method, results_method in comparison.items():
                distance = results_method['distance']
                method_time = results_method['time']
                improvement = results_method.get('improvement', 0)
                
                if improvement:
                    improvement_str = f"{improvement:.2f}%"
                else:
                    improvement_str = "Base"
                
                print(f"{method:<20} {distance:<20.2f} {method_time:<15.3f} {improvement_str:<15}")
        
        # Resumo final
        print(f"\n" + "=" * 80)
        print("✅ RESUMO FINAL")
        print("=" * 80)
        
        print(f"\n✨ Pipeline executado com sucesso!")
        print(f"\n   Arquivo salvo em: {output_file}")
        print(f"   Total de paradas otimizadas: {results['grouped_count']}")
        print(f"   Distância total da rota: {route_stats.get('total_distance_km', 0):.2f} km")
        print(f"   Tempo total: {results['total_pipeline_time']:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_complete_pipeline()
    exit(0 if success else 1)
