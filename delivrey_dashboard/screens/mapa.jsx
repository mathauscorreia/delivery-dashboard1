import React, { useEffect, useState, useRef } from "react";
import { StyleSheet, View, ActivityIndicator, Alert } from "react-native";
import MapView, { Marker, Polyline } from "react-native-maps";
import * as Location from "expo-location";
import { useRoute } from "@react-navigation/native";

export default function Mapa() {
  const [location, setLocation] = useState(null);
  const [loading, setLoading] = useState(true);

  const route = useRoute();
  const rota = route.params?.rota || [];

  const mapRef = useRef(null);

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

  // Ajusta zoom automaticamente quando rota chegar
  useEffect(() => {
    if (rota.length > 0 && mapRef.current) {
      const coordinates = rota.map((p) => ({
        latitude: Number(p.latitude),
        longitude: Number(p.longitude),
      }));

      mapRef.current.fitToCoordinates(coordinates, {
        edgePadding: { top: 100, right: 50, bottom: 100, left: 50 },
        animated: true,
      });
    }
  }, [rota]);

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
      followsUserLocation={false}
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

      {/* LINHA DA ROTA */}
      {rota.length > 1 && (
        <Polyline
          coordinates={rota.map((p) => ({
            latitude: Number(p.latitude),
            longitude: Number(p.longitude),
          }))}
          strokeWidth={4}
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
