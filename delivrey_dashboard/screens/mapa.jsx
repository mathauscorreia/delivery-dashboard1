import React, { useEffect, useState, useRef } from "react";
import { StyleSheet, View, ActivityIndicator, Alert } from "react-native";
import MapView, { Marker, Polyline } from "react-native-maps";
import * as Location from "expo-location";
import { useRoute } from "@react-navigation/native";
import { decode } from "@mapbox/polyline";

export default function Mapa() {
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rotaReal, setRotaReal] = useState([]);

  const route = useRoute();
  const rota = route.params?.rota || [];

  const mapRef = useRef(null);

  // 🔥 BUSCAR ROTA REAL
  async function buscarRotaGoogle() {
    try {
      if (rota.length < 2) return;

      const origin = `${rota[0].latitude},${rota[0].longitude}`;
      const destination = `${rota[rota.length - 1].latitude},${rota[rota.length - 1].longitude}`;

      const waypoints = rota
        .slice(1, rota.length - 1)
        .map(p => `${p.latitude},${p.longitude}`)
        .join("|");

      const apiKey = "SUA_API_KEY_AQUI";

      const url = `https://maps.googleapis.com/maps/api/directions/json?origin=${origin}&destination=${destination}&waypoints=${waypoints}&key=${apiKey}`;

      const response = await fetch(url);
      const data = await response.json();

      if (!data.routes || data.routes.length === 0) {
        Alert.alert("Não foi possível gerar rota real");
        return;
      }

      const points = decode(data.routes[0].overview_polyline.points);

      const coords = points.map(point => ({
        latitude: point[0],
        longitude: point[1],
      }));

      setRotaReal(coords);

    } catch (error) {
      console.log("Erro rota Google:", error);
      Alert.alert("Erro ao buscar rota");
    }
  }

  // 🔥 LOCALIZAÇÃO
  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Permissão de localização negada");
        return;
      }

      const currentLocation = await Location.getCurrentPositionAsync({});
      setLocation(currentLocation.coords);
      setLoading(false);

      Location.watchPositionAsync(
        {
          accuracy: Location.Accuracy.High,
          timeInterval: 3000,
          distanceInterval: 1,
        },
        (newLocation) => {
          setLocation(newLocation.coords);
        }
      );
    })();
  }, []);

  // 🔥 QUANDO RECEBER ROTA → BUSCA ROTA REAL
  useEffect(() => {
    if (rota.length > 1) {
      buscarRotaGoogle();
    }
  }, [rota]);

  // 🔥 AJUSTAR ZOOM
  useEffect(() => {
    if (rotaReal.length > 0 && mapRef.current) {
      mapRef.current.fitToCoordinates(rotaReal, {
        edgePadding: { top: 100, right: 50, bottom: 100, left: 50 },
        animated: true,
      });
    }
  }, [rotaReal]);

  if (loading || !location) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <MapView
      ref={mapRef}
      style={styles.map}
      showsUserLocation={true}
      initialRegion={{
        latitude: location.latitude,
        longitude: location.longitude,
        latitudeDelta: 0.02,
        longitudeDelta: 0.02,
      }}
    >
      {/* SUA LOCALIZAÇÃO */}
      <Marker
        coordinate={{
          latitude: location.latitude,
          longitude: location.longitude,
        }}
        title="Você está aqui"
        pinColor="blue"
      />

      {/* MARCADORES DAS PARADAS */}
      {rota.map((p, index) => (
        <Marker
          key={index}
          coordinate={{
            latitude: Number(p.latitude),
            longitude: Number(p.longitude),
          }}
          title={`Parada ${index + 1}`}
          description={`${p.endereco} - ${p.pacotes} pacotes`}
          pinColor="red"
        />
      ))}

      {/* 🔥 ROTA REAL */}
      {rotaReal.length > 0 && (
        <Polyline
          coordinates={rotaReal}
          strokeWidth={5}
          strokeColor="#2563eb"
        />
      )}
    </MapView>
  );
}

const styles = StyleSheet.create({
  map: {
    flex: 1,
  },
  loading: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
});
