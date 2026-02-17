import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from "react-native";

import * as DocumentPicker from "expo-document-picker";
import * as FileSystem from "expo-file-system/legacy";

import { processRoute } from "../utils/routeProcessor";
import { parseXLSXBase64 } from "../utils/excelParser";

export default function Otimizar() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  async function pickFile() {
    try {
      const res = await DocumentPicker.getDocumentAsync({
        type: [
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
          "application/vnd.ms-excel",
        ],
        copyToCacheDirectory: true,
      });

      if (res.canceled) return;

      setLoading(true);

      const fileUri = res.assets[0].uri;

      // 🔥 LER BASE64 (FORMA CORRETA NO RN)
      const base64 = await FileSystem.readAsStringAsync(fileUri, {
        encoding: "base64",
      });

      // 🔥 PARSE IGUAL AO WEB
      const stops = parseXLSXBase64(base64);

      if (!stops || stops.length === 0) {
        Alert.alert("Erro", "Planilha vazia ou inválida.");
        setLoading(false);
        return;
      }

      // 🔥 PROCESSAMENTO ORIGINAL
      const processed = processRoute(stops);

      setResult(processed);
      setLoading(false);
    } catch (error) {
      console.log(error);
      Alert.alert("Erro", "Erro ao processar arquivo.");
      setLoading(false);
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>SPX Route Optimizer</Text>

      <TouchableOpacity style={styles.button} onPress={pickFile}>
        <Text style={styles.buttonText}>Selecionar Planilha</Text>
      </TouchableOpacity>

      {loading && (
        <ActivityIndicator size="large" style={{ marginTop: 20 }} />
      )}

      {result && (
        <ScrollView style={styles.resultContainer}>
          <Text style={styles.stat}>
            Paradas Originais: {result.originalCount}
          </Text>
          <Text style={styles.stat}>
            Paradas Agrupadas: {result.groupedCount}
          </Text>
          <Text style={styles.stat}>
            Redução: {result.reductionPercentage}%
          </Text>

          <View style={{ marginTop: 20 }}>
            {result.groupedStops.map((stop, index) => (
              <View key={index} style={styles.card}>
                <Text style={styles.address}>
                  {stop.addressLine1}
                </Text>

                {stop.addressLine2 ? (
                  <Text style={styles.sub}>
                    {stop.addressLine2}
                  </Text>
                ) : null}

                {stop.notes ? (
                  <Text style={styles.sub}>
                    {stop.notes}
                  </Text>
                ) : null}

                <Text style={styles.count}>
                  Pacotes: {stop.packageCount}
                </Text>
              </View>
            ))}
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#0f172a",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#fff",
    marginBottom: 20,
    textAlign: "center",
  },
  button: {
    backgroundColor: "#2563eb",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontWeight: "bold",
  },
  resultContainer: {
    marginTop: 20,
  },
  stat: {
    color: "#fff",
    fontSize: 16,
    marginBottom: 5,
  },
  card: {
    backgroundColor: "#1e293b",
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
  },
  address: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 16,
  },
  sub: {
    color: "#cbd5e1",
  },
  count: {
    marginTop: 5,
    color: "#38bdf8",
    fontWeight: "bold",
  },
});
