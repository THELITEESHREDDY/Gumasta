import { useState } from "react";
import { View, Text } from "react-native";
import axios from "axios";

import Input from "@/components/Input";
import Button from "@/components/Button";
import { Customer, CustomerData } from "@/types/customer";

interface Props {
  customer?: Customer;
  onSubmit: (data: CustomerData) => Promise<void>;
  onCancel: () => void;
}

export default function CustomerForm({
  customer,
  onSubmit,
  onCancel,
}: Props) {
  const [name, setName] = useState(customer?.name ?? "");
  const [mobile, setMobile] = useState(customer?.mobile ?? "");

  const [alternateMobile, setAlternateMobile] = useState(
    customer?.alternate_mobile ?? ""
  );

  const [address, setAddress] = useState(
    customer?.address ?? ""
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    const mobileRegex = /^\+?[0-9]{10,15}$/;

    if (!name.trim() || !mobileRegex.test(mobile.trim())) {
      setError("Enter a valid name and mobile number");
      return;
    }

    if (
      alternateMobile.trim() &&
      !mobileRegex.test(alternateMobile.trim())
    ) {
      setError("Invalid alternate mobile number");
      return;
    }

    try {
      setLoading(true);
      setError("");

      await onSubmit({
        name: name.trim(),
        mobile: mobile.trim(),
        alternate_mobile: alternateMobile.trim() || null,
        address: address.trim() || null,
      });
    } catch (err) {
      const detail = axios.isAxiosError(err)
        ? err.response?.data?.detail
        : null;

      setError(
        typeof detail === "string"
          ? detail
          : "Failed to save customer"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <View className="gap-4">
      <Text className="text-xl font-bold">
        {customer ? "Edit customer" : "Add customer"}
      </Text>

      <Input
        label="Customer name"
        value={name}
        onChangeText={setName}
        maxLength={100}
      />

      <Input
        label="Mobile number"
        value={mobile}
        onChangeText={setMobile}
        keyboardType="phone-pad"
      />

      <Input
        label="Alternate mobile (optional)"
        value={alternateMobile}
        onChangeText={setAlternateMobile}
        keyboardType="phone-pad"
      />

      <Input
        label="Address (optional)"
        value={address}
        onChangeText={setAddress}
        multiline
      />

      {error ? (
        <Text className="text-red-600">{error}</Text>
      ) : null}

      <Button
        title={customer ? "Save changes" : "Add customer"}
        onPress={handleSubmit}
        loading={loading}
      />

      <Button
        title="Cancel"
        onPress={onCancel}
        disabled={loading}
      />
    </View>
  );
}