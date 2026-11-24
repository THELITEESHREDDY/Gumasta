import { useState } from "react";
import { View, Text, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";

import Input from "@/components/Input";
import Button from "@/components/Button";
import { createShop } from "@/services/shop";

export default function CreateShopScreen() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [contact, setContact] = useState("");
  const [gstId, setGstId] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleCreate() {
    if (!name.trim() || !address.trim() || !contact.trim()) {
      setError("Complete all required fields");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      await createShop({
        name: name.trim(),
        address: address.trim(),
        contact: contact.trim(),
        gst_id: gstId.trim() || null,
      });

      router.replace("/shops");
    } catch {
      setError("Failed to create shop. Check your details.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <SafeAreaView className="flex-1 bg-background">
      <ScrollView keyboardShouldPersistTaps="handled">
        <View className="mx-auto w-full max-w-xl gap-5 p-6">
          <Text className="text-2xl font-bold">
            Create shop
          </Text>

          <Input
            label="Shop name"
            value={name}
            onChangeText={setName}
            placeholder="Enter shop name"
          />

          <Input
            label="Address"
            value={address}
            onChangeText={setAddress}
            placeholder="Enter shop address"
            multiline
          />

          <Input
            label="Contact number"
            value={contact}
            onChangeText={setContact}
            keyboardType="phone-pad"
          />

          <Input
            label="GST ID (optional)"
            value={gstId}
            onChangeText={setGstId}
            autoCapitalize="characters"
            maxLength={15}
          />

          {error ? (
            <Text className="text-red-600">{error}</Text>
          ) : null}

          <Button
            title="Create shop"
            onPress={handleCreate}
            loading={submitting}
          />

          <Button
            title="Cancel"
            onPress={() => router.back()}
            disabled={submitting}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}