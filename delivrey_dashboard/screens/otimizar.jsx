import React, { useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Dimensions,
  Alert,
} from "react-native";
import * as DocumentPicker from "expo-document-picker";
import * as FileSystem from "expo-file-system/legacy";
import * as XLSX from "xlsx";
import { BarChart } from "react-native-chart-kit";
import { useNavigation } from "@react-navigation/native";

const screenWidth = Dimensions.get("window").width;

export default function Otimizar() {
  const navigation = useNavigation();

  const [paradasOriginais, setParadasOriginais] = useState(0);
  const [paradasAgrupadas, setParadasAgrupadas] = useState(0);
  const [reducao, setReducao] = useState(0);
  const [paradas, setParadas] = useState([]);

  async function handleUpload() {
    try {
        const result = await DocumentPicker.getDocumentAsync({
        type: [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ],
        copyToCacheDirectory: true,
        });

        if (result.canceled) return;

        const fileUri = result.assets[0].uri;

        // LER COMO STRING BINÁRIA
        const fileContent = await FileSystem.readAsStringAsync(fileUri, {
            encoding: "base64",
        });

        const workbook = XLSX.read(fileContent, {
        type: "base64",
        });

        const sheetName = workbook.SheetNames[0];
        const sheet = workbook.Sheets[sheetName];

        const jsonData = XLSX.utils.sheet_to_json(sheet);

        if (!jsonData || jsonData.length === 0) {
        Alert.alert("Arquivo vazio ou formato inválido");
        return;
        }

        processarArquivo(jsonData);
    } catch (error) {
        console.log("ERRO REAL:", error);
        Alert.alert("Erro ao ler arquivo", error.message);
    }
    }

  function processarArquivo(data) {
    setParadasOriginais(data.length);

    const agrupado = {};

    data.forEach((item) => {
        const endereco1 = item["Address Line 1"] || "";
        const endereco2 = item["Address Line 2"] || "";
        const enderecoCompleto = `${endereco1} ${endereco2}`.trim();

        const note = item["Notes"] || "";

        if (!agrupado[enderecoCompleto]) {
        agrupado[enderecoCompleto] = {
            endereco: enderecoCompleto,
            address1: endereco1,
            address2: endereco2,
            latitude: Number(item.Latitude),
            longitude: Number(item.Longitude),
            pacotes: 1,
            notes: [note],
        };
        } else {
        agrupado[enderecoCompleto].pacotes += 1;
        agrupado[enderecoCompleto].notes.push(note);
        }
    });

    const lista = Object.values(agrupado);

    setParadas(lista);
    setParadasAgrupadas(lista.length);

    const reducaoCalculada = Math.round(
        ((data.length - lista.length) / data.length) * 100
    );

    setReducao(reducaoCalculada);

    gerarArquivoRota(lista);
    }

    async function gerarArquivoRota(lista) {
        try {
            const dadosExport = lista.map((item, index) => ({
            Ordem: index + 1,
            Endereco: item.endereco,
            "Address Line 1": item.address1,
            "Address Line 2": item.address2,
            Latitude: item.latitude,
            Longitude: item.longitude,
            Pacotes: item.pacotes,
            Notes: item.notes.join(" | "),
            }));

            const worksheet = XLSX.utils.json_to_sheet(dadosExport);
            const workbook = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(workbook, worksheet, "Rota");

            const wbout = XLSX.write(workbook, {
            type: "base64",
            bookType: "xlsx",
            });

            const fileUri =
            FileSystem.documentDirectory + "rota_spoke.xlsx";

            await FileSystem.writeAsStringAsync(fileUri, wbout, {
            encoding: FileSystem.EncodingType.Base64,
            });

            Alert.alert("Arquivo rota_spoke.xlsx gerado com sucesso!");

        } catch (err) {
            console.log("Erro ao gerar arquivo:", err);
        }
        }


  function irParaMapa() {
    if (paradas.length === 0) {
      Alert.alert("Nenhuma rota gerada ainda");
      return;
    }

    navigation.navigate("Mapa", { rota: paradas });
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.titulo}>SPX Route Grouper</Text>

      <TouchableOpacity style={styles.botaoUpload} onPress={handleUpload}>
        <Text style={styles.botaoTexto}>Fazer Upload do Arquivo</Text>
      </TouchableOpacity>

      {paradasOriginais > 0 && (
        <>
          {/* CARDS */}
          <View style={styles.card}>
            <Text>Paradas Originais</Text>
            <Text style={styles.numero}>{paradasOriginais}</Text>
          </View>

          <View style={[styles.card, { borderColor: "green" }]}>
            <Text>Paradas Agrupadas</Text>
            <Text style={[styles.numero, { color: "green" }]}>
              {paradasAgrupadas}
            </Text>
          </View>

          <View style={[styles.card, { borderColor: "orange" }]}>
            <Text>Redução</Text>
            <Text style={[styles.numero, { color: "orange" }]}>
              {reducao}%
            </Text>
          </View>

          {/* GRÁFICO */}
          <Text style={styles.subtitulo}>Comparação</Text>
          <BarChart
            data={{
              labels: ["Originais", "Agrupadas"],
              datasets: [
                {
                  data: [paradasOriginais, paradasAgrupadas],
                },
              ],
            }}
            width={screenWidth - 20}
            height={220}
            chartConfig={{
              backgroundGradientFrom: "#fff",
              backgroundGradientTo: "#fff",
              decimalPlaces: 0,
              color: () => `#2563eb`,
            }}
            style={{ borderRadius: 10 }}
          />

          {/* LISTA DE PARADAS */}
          <Text style={styles.subtitulo}>Rota Gerada</Text>

          {paradas.map((p, index) => (
            <View key={index} style={styles.itemParada}>
              <Text style={styles.endereco}>{p.endereco}</Text>
              <Text>{p.pacotes} pacotes</Text>
            </View>
          ))}

          <TouchableOpacity style={styles.botaoMapa} onPress={irParaMapa}>
            <Text style={styles.botaoTexto}>Ver rota no mapa</Text>
          </TouchableOpacity>
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 10,
  },
  titulo: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 15,
  },
  botaoUpload: {
    backgroundColor: "#2563eb",
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
  },
  botaoMapa: {
    backgroundColor: "#16a34a",
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
    marginVertical: 20,
  },
  botaoTexto: {
    color: "#fff",
    fontWeight: "bold",
  },
  card: {
    backgroundColor: "#f3f4f6",
    padding: 15,
    borderRadius: 12,
    marginTop: 10,
    borderWidth: 1,
    borderColor: "#2563eb",
  },
  numero: {
    fontSize: 28,
    fontWeight: "bold",
    marginTop: 5,
  },
  subtitulo: {
    fontSize: 18,
    fontWeight: "bold",
    marginVertical: 15,
  },
  itemParada: {
    backgroundColor: "#e5e7eb",
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  endereco: {
    fontWeight: "bold",
  },
});
