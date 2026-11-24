import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";

export default function LoginScreen() {
  return (
    <View>
      <Text>Gumasta Login</Text>
      
      
      <Pressable
        onPress={() => router.push("/(tabs)/dashboard")}
      >
        <Text>Go to Dashboard</Text>
      </Pressable>

      <Pressable
        onPress={() => router.push("/(auth)/register")}
      >
        <Text>Don't have an account? Register</Text>
      </Pressable>
    
    </View>
  );
}