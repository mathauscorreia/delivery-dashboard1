"""
Script de teste para otimização de rota com múltiplos veículos.
Testa atribuição de paradas respeitando capacidade de cada veículo.
"""

import pandas as pd
from multi_vehicle_optimizer import (
    MultiVehicleOptimizer, 
    create_stops_from_dataframe,
    create_vehicles_from_config
)
import time


def test_multi_vehicle_optimization():
    print("=" * 80)
    print("🚚 TESTE DE OTIMIZAÇÃO MULTI-VEÍCULO")
    print("=" * 80)
    
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
            print("❌ Não há paradas suficientes!")
            return False
        
        # Cria lista de paradas
        print(f"\n📍 Criando lista de paradas...")
        stops = create_stops_from_dataframe(df_geocoded)
        print(f"✅ {len(stops)} paradas criadas")
        
        # Calcula total de pacotes
        total_packages = sum(stop.packages for stop in stops)
        print(f"   Total de pacotes: {total_packages}")
        
        # Define frota de veículos
        print(f"\n🚗 Configurando frota de veículos...")
        
        vehicles_config = [
            {'id': 1, 'name': 'Veículo 1 (Moto)', 'capacity': 15},
            {'id': 2, 'name': 'Veículo 2 (Carro)', 'capacity': 25},
            {'id': 3, 'name': 'Veículo 3 (Carro)', 'capacity': 25},
            {'id': 4, 'name': 'Veículo 4 (Van)', 'capacity': 40},
        ]
        
        vehicles = create_vehicles_from_config(vehicles_config)
        total_capacity = sum(v.capacity for v in vehicles)
        
        print(f"✅ Frota configurada:")
        for v in vehicles:
            print(f"   {v.name}: {v.capacity} pacotes")
        print(f"   Capacidade total: {total_capacity} pacotes")
        
        if total_capacity < total_packages:
            print(f"\n⚠️  AVISO: Capacidade total ({total_capacity}) < Pacotes ({total_packages})")
            print(f"   Alguns pacotes não poderão ser entregues!")
        
        # Cria otimizador
        print(f"\n⚙️  Inicializando otimizador...")
        optimizer = MultiVehicleOptimizer(stops, vehicles)
        print(f"✅ Matriz de distâncias calculada")
        
        # Testa atribuição gulosa
        print(f"\n" + "=" * 80)
        print("1️⃣  ATRIBUIÇÃO GULOSA (Greedy)")
        print("=" * 80)
        
        start = time.time()
        greedy_result = optimizer.greedy_assignment()
        greedy_time = time.time() - start
        
        print(f"✅ Atribuição concluída em {greedy_time:.3f}s")
        print(f"   Distância total: {greedy_result['total_distance']:.2f} km")
        print(f"   Paradas não atribuídas: {greedy_result['unassigned_count']}")
        
        # Exibe detalhes dos veículos
        print(f"\n📊 Detalhes dos veículos:")
        print(f"{'Veículo':<30} {'Paradas':<10} {'Carga':<15} {'Utilização':<15} {'Distância':<15}")
        print("-" * 85)
        
        for vehicle_id, route_info in greedy_result['routes'].items():
            vehicle_name = route_info['vehicle_name']
            stops_count = route_info['stops_count']
            load = route_info['load']
            capacity = route_info['capacity']
            utilization = route_info['utilization']
            distance = route_info['distance']
            
            print(f"{vehicle_name:<30} {stops_count:<10} {load}/{capacity:<13} {utilization:<14.1f}% {distance:<15.2f}")
        
        # Otimiza rotas
        print(f"\n" + "=" * 80)
        print("2️⃣  OTIMIZAÇÃO DE ROTAS (2-opt)")
        print("=" * 80)
        
        start = time.time()
        optimizer.optimize_routes(method='two_opt')
        optimization_time = time.time() - start
        
        optimized_result = optimizer._get_routes_dict()
        
        print(f"✅ Otimização concluída em {optimization_time:.3f}s")
        print(f"   Distância total: {optimized_result['total_distance']:.2f} km")
        
        improvement = ((greedy_result['total_distance'] - optimized_result['total_distance']) / 
                      greedy_result['total_distance'] * 100)
        print(f"   Melhoria: {improvement:.2f}%")
        
        # Testa atribuição por clustering
        print(f"\n" + "=" * 80)
        print("3️⃣  ATRIBUIÇÃO POR CLUSTERING")
        print("=" * 80)
        
        start = time.time()
        cluster_result = optimizer.cluster_first_assignment()
        cluster_time = time.time() - start
        
        print(f"✅ Atribuição concluída em {cluster_time:.3f}s")
        print(f"   Distância total: {cluster_result['total_distance']:.2f} km")
        print(f"   Paradas não atribuídas: {cluster_result['unassigned_count']}")
        
        # Otimiza rotas do clustering
        optimizer.optimize_routes(method='two_opt')
        cluster_optimized = optimizer._get_routes_dict()
        
        print(f"   Distância após otimização: {cluster_optimized['total_distance']:.2f} km")
        
        # Comparação de métodos
        print(f"\n" + "=" * 80)
        print("📊 COMPARAÇÃO DE MÉTODOS")
        print("=" * 80)
        
        comparison = optimizer.compare_assignment_methods()
        
        print(f"\n{'Método':<25} {'Distância (km)':<20} {'Não Atribuídas':<20} {'Tempo (s)':<15}")
        print("-" * 80)
        
        print(f"{'Greedy':<25} {comparison['greedy']['total_distance']:<20.2f} {comparison['greedy']['unassigned']:<20} {comparison['greedy']['time']:<15.3f}")
        print(f"{'Cluster First':<25} {comparison['cluster_first']['total_distance']:<20.2f} {comparison['cluster_first']['unassigned']:<20} {comparison['cluster_first']['time']:<15.3f}")
        
        print(f"\n{'Método':<25} {'Distância (km)':<20} {'Melhoria':<20}")
        print("-" * 65)
        
        print(f"{'Greedy + 2-opt':<25} {comparison['greedy_optimized']['total_distance']:<20.2f} {comparison['greedy_optimized']['improvement']:<20.2f}%")
        print(f"{'Cluster + 2-opt':<25} {comparison['cluster_first_optimized']['total_distance']:<20.2f} {comparison['cluster_first_optimized']['improvement']:<20.2f}%")
        
        # Estatísticas finais
        print(f"\n" + "=" * 80)
        print("📈 ESTATÍSTICAS FINAIS")
        print("=" * 80)
        
        stats = optimizer.get_statistics()
        
        print(f"\n🚗 Frota:")
        print(f"   Total de veículos: {stats['total_vehicles']}")
        print(f"   Total de paradas: {stats['total_stops']}")
        print(f"   Paradas não atribuídas: {stats['unassigned_stops']}")
        
        print(f"\n📦 Carga:")
        print(f"   Capacidade total: {stats['total_capacity']} pacotes")
        print(f"   Carga total: {stats['total_load']} pacotes")
        print(f"   Utilização geral: {stats['overall_utilization']:.1f}%")
        
        print(f"\n🛣️  Rotas:")
        print(f"   Distância total: {stats['total_distance_km']:.2f} km")
        print(f"   Distância média por veículo: {stats['average_distance_per_vehicle']:.2f} km")
        print(f"   Tempo de otimização: {stats['optimization_time']:.3f}s")
        
        print(f"\n📊 Detalhamento por veículo:")
        print(f"{'Veículo':<25} {'Paradas':<10} {'Carga':<15} {'Utilização':<15} {'Distância':<15}")
        print("-" * 80)
        
        for vehicle_info in stats['vehicles']:
            vehicle_name = vehicle_info['name']
            stops = vehicle_info['stops']
            load = vehicle_info['load']
            capacity = vehicle_info['capacity']
            utilization = vehicle_info['utilization']
            distance = vehicle_info['distance']
            
            print(f"{vehicle_name:<25} {stops:<10} {load}/{capacity:<13} {utilization:<14.1f}% {distance:<15.2f}")
        
        # Detalhes completos da melhor rota
        print(f"\n" + "=" * 80)
        print("🏆 DETALHES DAS ROTAS OTIMIZADAS")
        print("=" * 80)
        
        detailed = optimizer.get_detailed_routes()
        
        for vehicle_id, vehicle_detail in detailed.items():
            print(f"\n🚗 {vehicle_detail['vehicle_name']}")
            print(f"   Capacidade: {vehicle_detail['capacity']} pacotes")
            print(f"   Carga: {vehicle_detail['load']} pacotes ({vehicle_detail['utilization']:.1f}%)")
            print(f"   Distância total: {vehicle_detail['total_distance']:.2f} km")
            print(f"   Paradas: {len(vehicle_detail['stops'])}")
            
            if vehicle_detail['stops']:
                print(f"\n   Rota (primeiras 5 paradas):")
                print(f"   {'Ordem':<8} {'Endereço':<35} {'Pacotes':<10} {'Dist. Próx.':<12}")
                print(f"   {'-'*65}")
                
                for stop in vehicle_detail['stops'][:5]:
                    order = stop['order']
                    address = stop['address'][:33]
                    packages = stop['packages']
                    distance_to_next = stop['distance_to_next']
                    
                    print(f"   {order:<8} {address:<35} {packages:<10} {distance_to_next:<12.2f} km")
                
                if len(vehicle_detail['stops']) > 5:
                    print(f"   ... ({len(vehicle_detail['stops']) - 5} paradas adicionais)")
        
        # Salva resultado em arquivo
        print(f"\n" + "=" * 80)
        print("💾 SALVANDO RESULTADO")
        print("=" * 80)
        
        output_file = '/home/ubuntu/delivery-optimizer/output/multi_vehicle_routes.xlsx'
        
        # Cria DataFrame com rotas
        routes_data = []
        for vehicle_id, vehicle_detail in detailed.items():
            for stop in vehicle_detail['stops']:
                routes_data.append({
                    'veiculo_id': vehicle_id,
                    'veiculo_nome': vehicle_detail['vehicle_name'],
                    'ordem': stop['order'],
                    'endereco': stop['address'],
                    'latitude': stop['latitude'],
                    'longitude': stop['longitude'],
                    'pacotes': stop['packages'],
                    'distancia_proxima_parada': stop['distance_to_next'],
                })
        
        df_routes = pd.DataFrame(routes_data)
        df_routes.to_excel(output_file, index=False)
        
        print(f"✅ Rotas salvas em: {output_file}")
        
        print(f"\n✨ Teste concluído com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_multi_vehicle_optimization()
    exit(0 if success else 1)
