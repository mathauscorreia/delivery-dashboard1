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
import { exportToSpoke, exportDetailedReport } from "../utils/excelExporter";

export default function Otimizar() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [fileBase64, setFileBase64] = useState(null);


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

    const fileUri = res.assets[0].uri;
    const name = res.assets[0].name;

    setFileName(name);

    const base64 = await FileSystem.readAsStringAsync(fileUri, {
      encoding: "base64",
    });

    setFileBase64(base64);
  } catch (error) {
    Alert.alert("Erro", "Erro ao selecionar arquivo.");
  }
}

function handleProcess() {
  if (!fileBase64) {
    Alert.alert("Selecione uma planilha primeiro.");
    return;
  }

  try {
    setLoading(true);

    const stops = parseXLSXBase64(fileBase64);

    if (!stops || stops.length === 0) {
      Alert.alert("Erro", "Planilha vazia ou inválida.");
      setLoading(false);
      return;
    }

    const processed = processRoute(stops);
    setResult(processed);
    setLoading(false);
  } catch (error) {
    Alert.alert("Erro", "Erro ao processar arquivo.");
    setLoading(false);
  }
}

async function handleExportSpoke() {
  if (!result) return;
  await exportToSpoke(result.groupedStops);
}

async function handleExportDetailed() {
  if (!result) return;

  await exportDetailedReport(
    result.groupedStops,
    result.originalCount,
    result.groupedCount,
    result.reductionPercentage
  );
}

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Paradas Agrupadas</Text>
      <Text style={styles.subtitle}>
        Visualização das paradas prontas para exportação.
      </Text>

      {/* ===== CARD UPLOAD ===== */}

      <View style={styles.uploadContainer}>
        <Text style={styles.uploadTitle}>1. Carregar Arquivo SPX</Text>
        <Text style={styles.uploadSubtitle}>
          Faça upload do arquivo XLSX exportado do SPX Motorista
        </Text>

        <TouchableOpacity
          style={styles.uploadArea}
          onPress={pickFile}
          activeOpacity={0.8}
        >
          <Ionicons name="document-outline" size={42} color="#2563eb" />

          {fileName ? (
            <>
              <Text style={styles.fileName}>{fileName}</Text>

              <View style={styles.loadedBadge}>
                <Ionicons name="checkmark-circle" size={16} color="#16a34a" />
                <Text style={styles.loadedText}>Arquivo carregado</Text>
              </View>
            </>
          ) : (
            <Text style={styles.selectText}>Toque para selecionar a planilha</Text>
          )}
        </TouchableOpacity>

        {fileName && (
          <TouchableOpacity
            style={styles.processButton}
            onPress={handleProcess}
            activeOpacity={0.8}
          >
            <Ionicons name="cube-outline" size={18} color="#fff" />
            <Text style={styles.processButtonText}>Processar e Agrupar</Text>
          </TouchableOpacity>
        )}
      </View>


      {loading && <ActivityIndicator size="large" style={{ marginTop: 20 }} />}

      {result && (
        <ScrollView style={styles.resultContainer}>

          {/* ===== RELATÓRIO GERAL ===== */}
          <View style={styles.summaryContainer}>
            <View style={styles.summaryRow}>
              <View style={[styles.summaryCard, styles.blueCard]}>
                <Text style={styles.summaryLabelBlue}>Paradas Originais</Text>
                <Text style={styles.summaryNumberBlue}>
                  {result.originalCount}
                </Text>
              </View>

              <View style={[styles.summaryCard, styles.greenCard]}>
                <Text style={styles.summaryLabelGreen}>Paradas Agrupadas</Text>
                <Text style={styles.summaryNumberGreen}>
                  {result.groupedCount}
                </Text>
              </View>

              <View style={[styles.summaryCard, styles.orangeCard]}>
                <Text style={styles.summaryLabelOrange}>Redução</Text>
                <Text style={styles.summaryNumberOrange}>
                  {result.reductionPercentage}%
                </Text>
              </View>
            </View>

            <View style={styles.efficiencyCard}>
              <Text style={styles.efficiencyTitle}>
                Eficiência do Agrupamento
              </Text>

              <Text style={styles.efficiencySub}>
                {result.originalCount - result.groupedCount} paradas eliminadas através do agrupamento
              </Text>

              <View style={styles.progressContainer}>
                <View
                  style={[
                    styles.progressBar,
                    { width: `${result.reductionPercentage}%` },
                  ]}
                />
              </View>

              <Text style={styles.progressText}>
                {result.reductionPercentage}%
              </Text>
            </View>
          </View>
              {/* ===== LISTA DE RUAS ===== */}
              {result.groupedStops.map((stop, index) => (
                <View key={index} style={styles.cardContainer}>
                  
                  {/* HEADER */}
                  <TouchableOpacity
                    style={styles.cardHeader}
                    onPress={() => toggleExpand(index)}
                    activeOpacity={0.7}
                  >
                    <View style={styles.leftSection}>

                      <View style={styles.arrowContainer}>
                        <Text style={styles.arrow}>
                          {expandedIndex === index ? "▴" : "▾"}
                        </Text>
                      </View>

                      <View style={styles.indexContainer}>
                        <Text style={styles.indexNumber}>
                          {index + 1}
                        </Text>
                      </View>

                      <View style={styles.addressContainer}>
                        <Text style={styles.city}>
                          {stop.name} | {stop.addressLine2} | {stop.city}
                        </Text>
                      </View>

                    </View>

                    <View style={styles.rightSection}>
                      <View style={styles.badgeCircle}>
                        <Text style={styles.badgeText}>
                          {stop.packageIds?.length || 0}
                        </Text>
                      </View>

                      <View style={styles.idsPreview}>
                        {(stop.packageIds || []).slice(0, 2).map((id, i) => (
                          <Text key={i} style={styles.idText}>
                            {id}
                          </Text>
                        ))}

                        {(stop.packageIds?.length || 0) > 2 && (
                          <Text style={styles.moreText}>
                            +{stop.packageIds.length - 2}
                          </Text>
                        )}
                      </View>
                    </View>
                  </TouchableOpacity>

                  {/* EXPANDIDO */}
                  {expandedIndex === index && (
                    <View style={styles.expandedContainer}>
                      <Text style={styles.expandedTitle}>
                        Todos os {stop.packageIds?.length || 0} pacotes:
                      </Text>

                      <View style={styles.chipsContainer}>
                        {(stop.packageIds || []).map((id, i) => (
                          <View key={i} style={styles.chip}>
                            <Text style={styles.chipText}>{id}</Text>
                          </View>
                        ))}
                      </View>

                      <TouchableOpacity
                        style={styles.copyButton}
                        onPress={() =>
                          Clipboard.setStringAsync(stop.packageIds.join(", "))
                        }
                      >
                        <Ionicons name="copy-outline" size={16} color="#334155" />
                        <Text style={styles.copyText}>
                          Copiar todos os IDs
                        </Text>
                      </TouchableOpacity>
                    </View>
                  )}
                </View>
              ))}
                    {/* ===== EXPORTAÇÃO ===== */}
                    <View style={styles.exportContainer}>
                      <Text style={styles.exportTitle}>3. Exportar para Spoke</Text>
                      <Text style={styles.exportSubtitle}>
                        Baixe o arquivo otimizado pronto para importação no aplicativo Spoke
                      </Text>

                      <View style={styles.exportButtonsRow}>
                        <TouchableOpacity
                          style={styles.exportPrimaryButton}
                          onPress={handleExportSpoke}
                        >
                          <Ionicons name="download-outline" size={18} color="#fff" />
                          <Text style={styles.exportPrimaryText}>Exportar para Spoke</Text>
                        </TouchableOpacity>

                        <TouchableOpacity
                          style={styles.exportSecondaryButton}
                          onPress={handleExportDetailed}
                        >
                          <Ionicons name="document-text-outline" size={18} color="#334155" />
                          <Text style={styles.exportSecondaryText}>Relatório Completo</Text>
                        </TouchableOpacity>
                      </View>
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
  },

  blueCard: { borderWidth: 1, borderColor: "#3b82f6" },
  greenCard: { borderWidth: 1, borderColor: "#22c55e" },
  orangeCard: { borderWidth: 1, borderColor: "#f97316" },

  summaryLabelBlue: { color: "#3b82f6", fontWeight: "600" },
  summaryLabelGreen: { color: "#16a34a", fontWeight: "600" },
  summaryLabelOrange: { color: "#ea580c", fontWeight: "600" },

  summaryNumberBlue: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#1e3a8a",
    marginTop: 8,
  },

  summaryNumberGreen: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#166534",
    marginTop: 8,
  },

  summaryNumberOrange: {
    fontSize: 26,
    fontWeight: "bold",
    color: "#7c2d12",
    marginTop: 8,
  },

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
    height: 8,
    backgroundColor: "#e2e8f0",
    borderRadius: 20,
    overflow: "hidden",
  },

  progressBar: {
    height: 8,
    backgroundColor: "#2563eb",
  },

  progressText: {
    marginTop: 8,
    fontWeight: "600",
    color: "#16a34a",
    alignSelf: "flex-end",
  },

  /* ===== CARD LISTA ===== */

  cardContainer: {
    backgroundColor: "#ffffff",
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    overflow: "hidden",
  },

  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    padding: 16,
  },

  leftSection: {
    flexDirection: "row",
    alignItems: "center",
    flex: 1,
  },

  arrowContainer: {
  width: 22,
  alignItems: "center",
  paddingTop: 4,
},
indexContainer: {
  width: 28,
  alignItems: "center",
  paddingTop: 2,
},

  arrow: {
    fontSize: 14,
    marginRight: 8,
    color: "#64748b",
  },

  indexNumber: {
    width: 24,
    color: "#64748b",
  },

  addressContainer: {
    flex: 1,
  },

  street: {
    fontSize: 15,
    fontWeight: "600",
    color: "#0f172a",
  },

  complement: {
    fontSize: 14,
    color: "#64748b",
  },

  city: {
    fontSize: 14,
    color: "#0f172a",
    fontWeight: "500",
  },

  rightSection: {
    alignItems: "flex-end",
  },

  badgeCircle: {
    backgroundColor: "#16a34a",
    width: 28,
    height: 28,
    borderRadius: 20,
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 6,
  },

  badgeText: {
    color: "#fff",
    fontWeight: "600",
  },

  idsPreview: {
    alignItems: "flex-end",
  },

  idText: {
    fontSize: 13,
    color: "#475569",
  },

  moreText: {
    fontSize: 13,
    color: "#2563eb",
    fontWeight: "600",
  },

  /* ===== EXPANDIDO ===== */

  expandedContainer: {
    backgroundColor: "#f8fafc",
    padding: 16,
  },

  expandedTitle: {
    fontWeight: "600",
    marginBottom: 12,
  },

  chipsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
  },

  chip: {
    borderWidth: 1,
    borderColor: "#93c5fd",
    backgroundColor: "#eff6ff",
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 10,
    marginRight: 10,
    marginBottom: 10,
  },

  chipText: {
    color: "#1d4ed8",
    fontSize: 13,
    fontWeight: "500",
  },

  copyButton: {
    marginTop: 12,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#e2e8f0",
    padding: 12,
    borderRadius: 8,
  },

  copyText: {
    marginLeft: 6,
    fontWeight: "600",
    color: "#334155",
  },

  /* ===== UPLOAD CARD ===== */

uploadContainer: {
  backgroundColor: "#ffffff",
  padding: 20,
  borderRadius: 20,
  marginBottom: 20,
},

uploadTitle: {
  fontSize: 16,
  fontWeight: "bold",
  color: "#0f172a",
},

uploadSubtitle: {
  color: "#64748b",
  marginBottom: 15,
},

uploadArea: {
  borderWidth: 2,
  borderColor: "#93c5fd",
  borderStyle: "dashed",
  borderRadius: 16,
  paddingVertical: 40,
  alignItems: "center",
  justifyContent: "center",
  backgroundColor: "#f8fafc",
},

selectText: {
  marginTop: 10,
  color: "#64748b",
},

fileName: {
  marginTop: 15,
  fontSize: 15,
  fontWeight: "600",
  color: "#1e3a8a",
  textAlign: "center",
},

loadedBadge: {
  flexDirection: "row",
  alignItems: "center",
  marginTop: 10,
  backgroundColor: "#dcfce7",
  paddingHorizontal: 12,
  paddingVertical: 6,
  borderRadius: 20,
},

loadedText: {
  marginLeft: 6,
  color: "#16a34a",
  fontWeight: "600",
},

processButton: {
  marginTop: 20,
  backgroundColor: "#2563eb",
  paddingVertical: 14,
  borderRadius: 12,
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  elevation: 2,
},

processButtonText: {
  color: "#fff",
  fontWeight: "600",
  marginLeft: 8,
},
/* ===== EXPORTAÇÃO ===== */

exportContainer: {
  backgroundColor: "#ffffff",
  padding: 20,
  borderRadius: 20,
  marginTop: 20,
  marginBottom: 40,
  borderWidth: 1,
  borderColor: "#bbf7d0",
},

exportTitle: {
  fontSize: 16,
  fontWeight: "bold",
  color: "#166534",
},

exportSubtitle: {
  color: "#64748b",
  marginTop: 5,
  marginBottom: 15,
},

exportButtonsRow: {
  flexDirection: "row",
  justifyContent: "space-between",
},

exportPrimaryButton: {
  flex: 1,
  backgroundColor: "#16a34a",
  paddingVertical: 14,
  borderRadius: 12,
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
  marginRight: 10,
},

exportPrimaryText: {
  color: "#fff",
  fontWeight: "600",
  marginLeft: 8,
},

exportSecondaryButton: {
  flex: 1,
  borderWidth: 1,
  borderColor: "#cbd5e1",
  paddingVertical: 14,
  borderRadius: 12,
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "center",
},

exportSecondaryText: {
  color: "#334155",
  fontWeight: "600",
  marginLeft: 8,
},

});