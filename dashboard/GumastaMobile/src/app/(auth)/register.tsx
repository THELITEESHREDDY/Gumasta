import { View, Text, Pressable } from "react-native";
import { router } from "expo-router";

export default function RegisterScreen() {
  return (
    <View>
      <Pressable onPress={() => router.back()}>
        <Text>Go Back</Text>
      </Pressable>

      <Text>Gumasta Register</Text>
    </View>
  );
}