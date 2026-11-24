import { useState } from "react";
import { View, Text, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Link, Redirect } from "expo-router";

import Input from "@/components/Input";
import Button from "@/components/Button";
import { register } from "@/services/auth";
import { useAuth } from "@/contexts/AuthContext";

export default function RegisterScreen() {
  const { login, user } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleRegister() {
    if (
      !name.trim() ||
      !email.trim() ||
      !mobile.trim() ||
      password.length < 8
    ) {
      setError(
        "Complete all fields. Password must have at least 8 characters."
      );
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      await register({
        name: name.trim(),
        email: email.trim(),
        mobile: mobile.trim(),
        password,
      });

      await login(email.trim(), password);
    } catch {
      setError(
        "Registration failed. Check your details or try logging in."
      );
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
          <Text className="text-3xl font-bold text-primary">
            Gumasta
          </Text>

          <View>
            <Text className="text-2xl font-bold text-gray-900">
              Create account
            </Text>

            <Text className="mt-1 text-gray-500">
              Start managing your business
            </Text>
          </View>

          <Input
            label="Full name"
            placeholder="Enter your name"
            value={name}
            onChangeText={setName}
          />

          <Input
            label="Email"
            placeholder="Enter your email"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />

          <Input
            label="Mobile number"
            placeholder="Enter mobile number"
            value={mobile}
            onChangeText={setMobile}
            keyboardType="phone-pad"
          />

          <Input
            label="Password"
            placeholder="Minimum 8 characters"
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
            title="Create account"
            onPress={handleRegister}
            loading={submitting}
          />

          <View className="flex-row justify-center gap-1">
            <Text className="text-gray-500">
              Already registered?
            </Text>

            <Link
              href="/login"
              className="font-semibold text-primary"
            >
              Login
            </Link>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}