import { useState } from "react";
import { View, Text, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Link, Redirect } from "expo-router";
import { Store } from "lucide-react-native";

import { useAuth } from "@/contexts/AuthContext";
import Button from "@/components/Button";
import Input from "@/components/Input";

export default function LoginScreen() {
  const { login, user } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin() {
    if (!email.trim() || !password) {
      setError("Please enter email and password");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      await login(email.trim(), password);
    } catch {
      setError("Login failed. Check your credentials.");
    } finally {
      setSubmitting(false);
    }
  }

  if (user) return <Redirect href="/shops" />;

  return (
    <SafeAreaView className="flex-1 bg-background">
      <ScrollView
        contentContainerStyle={{ flexGrow: 1 }}
        keyboardShouldPersistTaps="handled"
      >
        <View className="mx-auto w-full max-w-md flex-1 justify-center gap-5 px-6 py-8">
          <View className="mb-6 items-center gap-2">
            <View className="rounded-2xl bg-primary p-4">
              <Store size={32} color="white" />
            </View>

            <Text className="text-3xl font-bold text-primary">
              Gumasta
            </Text>

            <Text className="text-gray-500">
              Manage your shop with ease
            </Text>
          </View>

          <View>
            <Text className="text-2xl font-bold text-gray-900">
              Welcome back
            </Text>

            <Text className="mt-1 text-gray-500">
              Login to your account
            </Text>
          </View>

          <Input
            label="Email"
            placeholder="Enter your email"
            value={email}
            onChangeText={setEmail}
            autoCapitalize="none"
            keyboardType="email-address"
          />

          <Input
            label="Password"
            placeholder="Enter your password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          {error ? (
            <Text className="text-sm text-red-600">
              {error}
            </Text>
          ) : null}

          <Button
            title="Login"
            onPress={handleLogin}
            loading={submitting}
          />

          <View className="flex-row justify-center gap-1">
            <Text className="text-gray-500">
              New to Gumasta?
            </Text>

            <Link
              href="/register"
              className="font-semibold text-primary"
            >
              Create account
            </Link>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}