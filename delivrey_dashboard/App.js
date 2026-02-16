import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

/* TELAS */
import Mapa from './screens/mapa';
import Carregando from './screens/carregando';
import Otimizar from './screens/otimizar';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Carregando" component={Carregando} />
        <Stack.Screen name="Mapa" component={Mapa} />
        <Stack.Screen name="Otimizar" component={Otimizar} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
