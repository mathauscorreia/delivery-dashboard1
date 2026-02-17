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
import { Ionicons } from "@expo/vector-icons";
import * as Clipboard from "expo-clipboard";

import { processRoute } from "../utils/routeProcessor";
import { parseXLSXBase64 } from "../utils/excelParser";

export default function Otimizar() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [expandedIndex, setExpandedIndex] = useState(null);

  const toggleExpand = (index) => {
    setExpandedIndex((prev) => (prev === index ? null : index));
  };

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

      const base64 = await FileSystem.readAsStringAsync(fileUri, {
        encoding: "base64",
      });

      const stops = parseXLSXBase64(base64);

      if (!stops || stops.length === 0) {
        Alert.alert("Erro", "Planilha vazia ou inválida.");
        setLoading(false);
        return;
      }

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
      <Text style={styles.title}>Paradas Agrupadas</Text>
      <Text style={styles.subtitle}>
        Visualização das paradas prontas para exportação.
      </Text>

      <TouchableOpacity style={styles.button} onPress={pickFile}>
        <Text style={styles.buttonText}>Selecionar Planilha</Text>
      </TouchableOpacity>

      {loading && <ActivityIndicator size="large" style={{ marginTop: 20 }} />}

      {result && (
        <ScrollView style={styles.resultContainer}>
          {result.groupedStops.map((stop, index) => {
            const firstTwo = stop.packages?.slice(0, 2) || [];
            const remaining = (stop.packageCount || 0) - firstTwo.length;

            return (
              <View key={index} style={styles.card}>
                <TouchableOpacity
                  style={styles.rowHeader}
                  onPress={() => toggleExpand(index)}
                >
                  {/* COLUNA ENDEREÇO */}
                  <View style={{ flex: 2 }}>
                    <Text style={styles.address}>
                      {stop.addressLine1}
                    </Text>

                    {stop.addressLine2 && (
                      <Text style={styles.sub}>
                        {stop.addressLine2}
                      </Text>
                    )}

                    {stop.city && (
                      <Text style={styles.sub}>
                        {stop.city}
                      </Text>
                    )}
                  </View>

                  {/* BADGE VERDE */}
                  <View style={styles.badge}>
                    <Text style={styles.badgeText}>
                      {stop.packageCount}
                    </Text>
                  </View>

                  {/* IDS RESUMIDOS */}
                  <View style={{ flex: 2, marginLeft: 15 }}>
                    {firstTwo.map((pkg, i) => (
                      <Text key={i} style={styles.previewId}>
                        {pkg.id}
                        {i === 0 && firstTwo.length > 1 ? "," : ""}
                      </Text>
                    ))}

                    {remaining > 0 && (
                      <Text style={styles.moreText}>
                        +{remaining}
                      </Text>
                    )}
                  </View>
                </TouchableOpacity>

                {/* EXPANDIDO */}
                {expandedIndex === index && (
                  <View style={styles.expandedContainer}>
                    <Text style={styles.expandedTitle}>
                      Todos os {stop.packageCount} pacotes:
                    </Text>

                    <View style={styles.chipsContainer}>
                      {stop.packages?.map((pkg, i) => (
                        <View key={i} style={styles.chip}>
                          <Text style={styles.chipText}>
                            {pkg.id}
                          </Text>
                        </View>
                      ))}
                    </View>

                    <TouchableOpacity
                      style={styles.copyButton}
                      onPress={async () => {
                        const allIds = stop.packages
                          ?.map((p) => p.id)
                          .join("\n");

                        await Clipboard.setStringAsync(allIds);
                      }}
                    >
                      <Ionicons name="copy-outline" size={16} color="#334155" />
                      <Text style={styles.copyText}>
                        Copiar todos os IDs
                      </Text>
                    </TouchableOpacity>
                  </View>
                )}
              </View>
            );
          })}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: "#f1f5f9",
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#0f172a",
  },
  subtitle: {
    color: "#64748b",
    marginBottom: 20,
  },
  button: {
    backgroundColor: "#2563eb",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
    marginBottom: 20,
  },
  buttonText: {
    color: "#fff",
    fontWeight: "600",
  },
  resultContainer: {
    marginTop: 10,
  },
  card: {
    backgroundColor: "#ffffff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  rowHeader: {
    flexDirection: "row",
    alignItems: "center",
  },
  address: {
    fontWeight: "600",
    fontSize: 15,
    color: "#0f172a",
  },
  sub: {
    color: "#64748b",
    fontSize: 13,
  },
  badge: {
    backgroundColor: "#16a34a",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 20,
    marginLeft: 10,
  },
  badgeText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 12,
  },
  expandedContainer: {
    marginTop: 15,
    backgroundColor: "#f8fafc",
    padding: 15,
    borderRadius: 10,
  },
  expandedTitle: {
    fontWeight: "600",
    marginBottom: 10,
    color: "#0f172a",
  },
  chipsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  chip: {
    borderWidth: 1,
    borderColor: "#93c5fd",
    backgroundColor: "#ffffff",
    borderRadius: 10,
    paddingVertical: 6,
    paddingHorizontal: 12,
    margin: 5,
  },
  chipText: {
    color: "#1e293b",
    fontSize: 12,
  },
  copyButton: {
    marginTop: 15,
    backgroundColor: "#e2e8f0",
    padding: 10,
    borderRadius: 8,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  copyText: {
    color: "#334155",
    fontWeight: "600",
    marginLeft: 5,
  },
  previewId: {
    color: "#1e293b",
    fontSize: 13,
  },
  moreText: {
    color: "#2563eb",
    fontWeight: "600",
    marginTop: 2,
  },
/* ===== RESUMO ===== */

summaryContainer: {
  marginBottom: 20,
},

summaryRow: {
  flexDirection: "row",
  justifyContent: "space-between",
  marginBottom: 15,
},

summaryCard: {
  flex: 1,
  padding: 18,
  borderRadius: 16,
  marginHorizontal: 5,
  backgroundColor: "#ffffff",
  elevation: 2,
},

blueCard: {
  borderColor: "#3b82f6",
  borderWidth: 1,
},

greenCard: {
  borderColor: "#22c55e",
  borderWidth: 1,
},

orangeCard: {
  borderColor: "#f97316",
  borderWidth: 1,
},

summaryLabelBlue: {
  color: "#3b82f6",
  fontWeight: "600",
  fontSize: 14,
},

summaryLabelGreen: {
  color: "#16a34a",
  fontWeight: "600",
  fontSize: 14,
},

summaryLabelOrange: {
  color: "#ea580c",
  fontWeight: "600",
  fontSize: 14,
},

summaryNumberBlue: {
  fontSize: 28,
  fontWeight: "bold",
  color: "#1e3a8a",
  marginTop: 8,
},

summaryNumberGreen: {
  fontSize: 28,
  fontWeight: "bold",
  color: "#166534",
  marginTop: 8,
},

summaryNumberOrange: {
  fontSize: 28,
  fontWeight: "bold",
  color: "#7c2d12",
  marginTop: 8,
},

/* ===== EFICIÊNCIA ===== */

efficiencyCard: {
  backgroundColor: "#ffffff",
  padding: 20,
  borderRadius: 16,
  borderWidth: 1,
  borderColor: "#bfdbfe",
},

efficiencyTitle: {
  fontSize: 16,
  fontWeight: "bold",
  color: "#0f172a",
},

efficiencySub: {
  color: "#64748b",
  marginTop: 6,
  marginBottom: 12,
},

progressContainer: {
  height: 10,
  backgroundColor: "#e2e8f0",
  borderRadius: 20,
  overflow: "hidden",
},

progressBar: {
  height: 10,
  backgroundColor: "#2563eb",
},

progressText: {
  marginTop: 8,
  fontWeight: "600",
  color: "#16a34a",
  alignSelf: "flex-end",
},

});
