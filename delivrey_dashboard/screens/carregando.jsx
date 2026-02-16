import { StatusBar } from 'expo-status-bar';
import { useEffect, useRef } from 'react';
import { StyleSheet, Text, View, Image, Animated } from 'react-native';
import cores from './style/cores';

export default function CarregandoApp({ navigation }) {

  const progress = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    // Anima a barra por 5 segundos
    Animated.timing(progress, {
      toValue: 1,
      duration: 3000,
      useNativeDriver: false,
    }).start(() => {
      navigation.replace('Otimizar');
    });
  }, []);

  const larguraBarra = progress.interpolate({
    inputRange: [0, 1],
    outputRange: ['0%', '100%'],
  });

  return (
    <View style={styles.container}>
      <Image
        source={require('../img/icone.png')}
        style={styles.image}
        resizeMode="contain"
      />
      <Text style={styles.text}>Carregando...</Text>

      {/* Barra de progresso */}
      <View style={styles.progressContainer}>
        <Animated.View style={[styles.progressBar, { width: larguraBarra }]} />
      </View>

      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: cores.FundoDeTela,
    alignItems: 'center',
    justifyContent: 'center',
  },
  image: {
    width: 200,
    height: 200,
    marginBottom: 20,
    borderRadius: 20,
  },
  text: {
    fontSize: 18,
    color: cores.TextoPrincipal,
    marginBottom: 30,
  },
  progressContainer: {
    width: '70%',
    height: 10,
    backgroundColor: '#ddd',
    borderRadius: 10,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: cores.TextoPrincipal,
  },
});
