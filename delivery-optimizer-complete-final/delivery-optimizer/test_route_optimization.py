"""
Script de teste para otimização de rota.
Testa todos os algoritmos de otimização com dados reais.
"""

import pandas as pd
from route_optimizer import RouteOptimizer, create_stops_from_dataframe
import time


def test_route_optimization():
    print("=" * 70)
    print("🗺️  TESTE DE OTIMIZAÇÃO DE ROTA")
    print("=" * 70)
    
    # Lê arquivo com dados geocodificados
    input_file = '/home/ubuntu/delivery-optimizer/output/test_geocoding_result.xlsx'
    
    print(f"\n📂 Lendo arquivo: {input_file}")
    
    try:
        df = pd.read_excel(input_file)
        print(f"✅ Arquivo lido com sucesso!")
        print(f"   Total de paradas: {len(df)}")
        
        # Filtra apenas paradas geocodificadas
        df_geocoded = df[df['geocodificado'] == True].copy()
        print(f"   Paradas geocodificadas: {len(df_geocoded)}")
        
        if len(df_geocoded) < 2:
            print("❌ Não há paradas suficientes para otimizar rota!")
            return False
        
        # Cria lista de paradas
        print(f"\n📍 Criando lista de paradas...")
        stops = create_stops_from_dataframe(df_geocoded)
        print(f"✅ {len(stops)} paradas criadas")
        
        # Cria otimizador
        print(f"\n⚙️  Inicializando otimizador de rotas...")
        optimizer = RouteOptimizer(stops)
        print(f"✅ Matriz de distâncias calculada")
        
        # Testa Nearest Neighbor
        print(f"\n" + "=" * 70)
        print("1️⃣  NEAREST NEIGHBOR (Algoritmo Guloso)")
        print("=" * 70)
        
        start = time.time()
        nn_route, nn_distance = optimizer.nearest_neighbor()
        nn_time = time.time() - start
        
        print(f"✅ Rota calculada em {nn_time:.3f}s")
        print(f"   Distância total: {nn_distance:.2f} km")
        print(f"   Número de paradas: {len(nn_route)}")
        print(f"   Rota (primeiras 5): {nn_route[:5]}")
        
        # Testa 2-opt
        print(f"\n" + "=" * 70)
        print("2️⃣  2-OPT (Otimização Local)")
        print("=" * 70)
        
        start = time.time()
        opt_route, opt_distance = optimizer.two_opt(nn_route, max_iterations=500)
        opt_time = time.time() - start
        
        improvement = ((nn_distance - opt_distance) / nn_distance * 100)
        
        print(f"✅ Rota otimizada em {opt_time:.3f}s")
        print(f"   Distância total: {opt_distance:.2f} km")
        print(f"   Melhoria: {improvement:.2f}%")
        print(f"   Economia: {nn_distance - opt_distance:.2f} km")
        print(f"   Rota (primeiras 5): {opt_route[:5]}")
        
        # Testa Algoritmo Genético (apenas para rotas pequenas)
        if len(stops) <= 30:
            print(f"\n" + "=" * 70)
            print("3️⃣  ALGORITMO GENÉTICO (Otimização Avançada)")
            print("=" * 70)
            
            start = time.time()
            ga_route, ga_distance = optimizer.genetic_algorithm(
                population_size=50,
                generations=300,
                mutation_rate=0.02,
                elite_size=5
            )
            ga_time = time.time() - start
            
            ga_improvement = ((nn_distance - ga_distance) / nn_distance * 100)
            
            print(f"✅ Rota otimizada em {ga_time:.3f}s")
            print(f"   Distância total: {ga_distance:.2f} km")
            print(f"   Melhoria vs NN: {ga_improvement:.2f}%")
            print(f"   Economia: {nn_distance - ga_distance:.2f} km")
            print(f"   Rota (primeiras 5): {ga_route[:5]}")
        else:
            print(f"\n⏭️  Algoritmo Genético: Pulado (rota com {len(stops)} paradas é muito grande)")
        
        # Comparação de métodos
        print(f"\n" + "=" * 70)
        print("📊 COMPARAÇÃO DE MÉTODOS")
        print("=" * 70)
        
        comparison = optimizer.compare_methods()
        
        print(f"\n{'Método':<20} {'Distância (km)':<20} {'Tempo (s)':<15} {'Melhoria':<15}")
        print("-" * 70)
        
        for method, results in comparison.items():
            distance = results['distance']
            method_time = results['time']
            improvement = results.get('improvement', 0)
            
            if improvement:
                improvement_str = f"{improvement:.2f}%"
            else:
                improvement_str = "Base"
            
            print(f"{method:<20} {distance:<20.2f} {method_time:<15.3f} {improvement_str:<15}")
        
        # Detalhes da melhor rota
        print(f"\n" + "=" * 70)
        print("🏆 MELHOR ROTA (2-OPT)")
        print("=" * 70)
        
        optimizer.best_route = opt_route
        optimizer.best_distance = opt_distance
        
        route_details = optimizer.get_optimized_route_details()
        
        print(f"\n📍 Detalhes da rota:")
        print(f"   Distância total: {route_details['total_distance']:.2f} km")
        print(f"   Número de paradas: {route_details['number_of_stops']}")
        print(f"   Tempo de otimização: {route_details['optimization_time']:.3f}s")
        
        print(f"\n🛣️  Segmentos da rota (primeiros 5):")
        print(f"{'De':<30} {'Para':<30} {'Distância (km)':<15}")
        print("-" * 75)
        
        for i, segment in enumerate(route_details['segments'][:5]):
            from_addr = segment['from'][:28]
            to_addr = segment['to'][:28]
            distance = segment['distance']
            print(f"{from_addr:<30} {to_addr:<30} {distance:<15.2f}")
        
        if len(route_details['segments']) > 5:
            print(f"... ({len(route_details['segments']) - 5} segmentos adicionais)")
        
        # Salva rota otimizada em arquivo
        print(f"\n" + "=" * 70)
        print("💾 SALVANDO ROTA OTIMIZADA")
        print("=" * 70)
        
        output_file = '/home/ubuntu/delivery-optimizer/output/rota_otimizada.xlsx'
        
        # Cria DataFrame com rota otimizada
        route_data = []
        for order, stop_idx in enumerate(opt_route, 1):
            stop = stops[stop_idx]
            route_data.append({
                'ordem': order,
                'id_parada': stop.id,
                'endereco': stop.address,
                'latitude': stop.latitude,
                'longitude': stop.longitude,
                'pacotes': stop.packages,
            })
        
        df_route = pd.DataFrame(route_data)
        df_route.to_excel(output_file, index=False)
        
        print(f"✅ Rota salva em: {output_file}")
        
        # Resumo final
        print(f"\n" + "=" * 70)
        print("📈 RESUMO FINAL")
        print("=" * 70)
        print(f"\n✅ Otimização concluída com sucesso!")
        print(f"\n   Rota Original (NN):     {nn_distance:.2f} km")
        print(f"   Rota Otimizada (2-opt): {opt_distance:.2f} km")
        print(f"   Economia:               {nn_distance - opt_distance:.2f} km ({improvement:.2f}%)")
        print(f"   Paradas:                {len(stops)}")
        print(f"   Tempo de processamento: {opt_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_route_optimization()
    exit(0 if success else 1)
