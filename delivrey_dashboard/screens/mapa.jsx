import React, { useEffect, useState, useRef } from "react";
import {
  StyleSheet,
  View,
  ActivityIndicator,
  Text,
  TouchableOpacity,
  Alert,
} from "react-native";
import MapView, { Marker, Polyline } from "react-native-maps";
import * as Location from "expo-location";
import { useRoute } from "@react-navigation/native";
import { decode } from "@mapbox/polyline";
import { getDistance } from "geolib";

export default function Mapa() {
  const route = useRoute();
  const paradasOriginais = route.params?.rota || [];

  const [location, setLocation] = useState(null);
  const [rotaReal, setRotaReal] = useState([]);
  const [paradas, setParadas] = useState([]);
  const [paradaAtual, setParadaAtual] = useState(0);
  const [distancia, setDistancia] = useState(0);
  const [duracao, setDuracao] = useState(0);
  const [loading, setLoading] = useState(true);

  const mapRef = useRef(null);
  const apiKey = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImI3MDYwY2M0YmE0YjRhMjY5NGIyMjEwZGVkODU1YzVhIiwiaCI6Im11cm11cjY0In0=";

  // 🚀 GERAR ROTA
  async function gerarRota(inicio) {
    try {
      const coords = [
        [inicio.longitude, inicio.latitude],
        ...paradas.map(p => [Number(p.longitude), Number(p.latitude)]),
      ];

      const response = await fetch(
        "https://api.openrouteservice.org/v2/directions/driving-car",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: apiKey,
          },
          body: JSON.stringify({
            coordinates: coords,
            optimize_waypoints: true,
          }),
        }
      );

      const data = await response.json();
      const rota = data.routes[0];

      setDistancia((rota.summary.distance / 1000).toFixed(2));
      setDuracao(Math.round(rota.summary.duration / 60));

      const decoded = decode(rota.geometry);
      const poly = decoded.map(p => ({
        latitude: p[0],
        longitude: p[1],
      }));

      setRotaReal(poly);

      mapRef.current?.fitToCoordinates(poly, {
        edgePadding: { top: 100, right: 50, bottom: 250, left: 50 },
        animated: true,
      });

    } catch (err) {
      console.log("Erro rota:", err);
    }
  }

  // 📍 TRACKING EM TEMPO REAL
  async function iniciarTracking() {
    await Location.watchPositionAsync(
      {
        accuracy: Location.Accuracy.High,
        distanceInterval: 5,
      },
      (pos) => {
        const novaLoc = pos.coords;
        setLocation(novaLoc);

        // 🔥 verificar desvio da rota
        if (rotaReal.length > 0) {
          const distanciaRota = getDistance(novaLoc, rotaReal[0]);

          if (distanciaRota > 80) {
            console.log("Desviou da rota — recalculando");
            gerarRota(novaLoc);
          }
        }
      }
    );
  }

  // 📍 INICIALIZAR
  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permissão negada");
        return;
      }

      const loc = await Location.getCurrentPositionAsync({});
      setLocation(loc.coords);
      setParadas(paradasOriginais);
      setLoading(false);
      gerarRota(loc.coords);
      iniciarTracking();
    })();
  }, []);

  // ✅ CONCLUIR PARADA
  function concluirParada() {
    if (paradas.length === 0) return;

    const novas = [...paradas];
    novas.shift(); // remove primeira parada

    setParadas(novas);
    setParadaAtual(paradaAtual + 1);

    if (novas.length > 0) {
      gerarRota(location);
    } else {
      Alert.alert("🎉 Todas entregas concluídas!");
      setRotaReal([]);
    }
  }

  if (loading || !location) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <MapView
        ref={mapRef}
        style={styles.map}
        showsUserLocation
        followsUserLocation
      >
        {paradas.map((p, index) => (
            <Marker
              key={index}
              coordinate={{
                latitude: Number(p.latitude),
                longitude: Number(p.longitude),
              }}
              pinColor={index === 0 ? "green" : "red"}
              title={`Parada ${index + 1}`}
              description={`📍 ${p.address1} ${p.address2}

            📦 Pacotes: ${p.pacotes}

            📝 Pedidos:
            ${p.notes.join("\n")}`}
            />
        ))}

        {rotaReal.length > 0 && (
          <Polyline
            coordinates={rotaReal}
            strokeWidth={6}
            strokeColor="#2563eb"
          />
        )}
      </MapView>

      {/* 🔥 PAINEL PROFISSIONAL */}
      <View style={styles.painel}>
        <Text style={styles.titulo}>🚚 Entrega em andamento</Text>
        <Text>📍 Próxima: {paradas[0]?.endereco || "Finalizado"}</Text>
        <Text>📏 {distancia} km restantes</Text>
        <Text>⏱️ {duracao} min estimados</Text>

        {paradas.length > 0 && (
          <TouchableOpacity style={styles.botao} onPress={concluirParada}>
            <Text style={styles.botaoTexto}>✅ Concluir Parada</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  map: { flex: 1 },
  loading: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  painel: {
    position: "absolute",
    bottom: 0,
    width: "100%",
    backgroundColor: "#fff",
    padding: 20,
    borderTopLeftRadius: 25,
    borderTopRightRadius: 25,
    elevation: 10,
  },
  titulo: {
    fontSize: 18,
    fontWeight: "bold",
    marginBottom: 5,
  },
  botao: {
    backgroundColor: "#16a34a",
    padding: 15,
    borderRadius: 12,
    marginTop: 10,
    alignItems: "center",
  },
  botaoTexto: {
    color: "#fff",
    fontWeight: "bold",
  },
});
