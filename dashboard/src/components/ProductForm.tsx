import { useState } from "react";
import { View, Text } from "react-native";

import Input from "@/components/Input";
import Button from "@/components/Button";

import {
  Product,
  CreateProductData,
} from "@/types/product";

interface ProductFormProps {
  product?: Product;
  onSubmit: (data: CreateProductData) => Promise<void>;
}

export default function ProductForm({
  product,
  onSubmit,
}: ProductFormProps) {
  const [name, setName] = useState(product?.name ?? "");

  const [costPrice, setCostPrice] = useState(
    product?.cost_price ?? ""
  );

  const [sellingPrice, setSellingPrice] = useState(
    product?.selling_price ?? ""
  );

  const [unit, setUnit] = useState(product?.unit ?? "");

  const [stock, setStock] = useState(
    String(product?.stock_quantity ?? 0)
  );

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit() {
    if (
      !name.trim() ||
      !unit.trim() ||
      !costPrice.trim() ||
      !sellingPrice.trim()
    ) {
      setError("Complete all required fields");
      return;
    }

    const validPrice = /^\d+(\.\d{1,2})?$/;

    if (
      !validPrice.test(costPrice.trim()) ||
      !validPrice.test(sellingPrice.trim())
    ) {
      setError("Enter valid non-negative prices");
      return;
    }

    if (
      !product &&
      (!stock.trim() ||
        !Number.isSafeInteger(Number(stock)) ||
        Number(stock) < 0)
    ) {
      setError("Enter a valid stock quantity");
      return;
    }

    try {
      setSubmitting(true);
      setError("");

      await onSubmit({
        name: name.trim(),
        cost_price: costPrice.trim(),
        selling_price: sellingPrice.trim(),
        unit: unit.trim(),
        stock_quantity: Number(stock),
      });
    } catch {
      setError("Failed to save product. Check your details.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <View className="gap-4">
      <Input
        label="Product name"
        value={name}
        onChangeText={setName}
        placeholder="Eg. Rice"
      />

      <Input
        label="Cost price (₹)"
        value={costPrice}
        onChangeText={setCostPrice}
        keyboardType="decimal-pad"
      />

      <Input
        label="Selling price (₹)"
        value={sellingPrice}
        onChangeText={setSellingPrice}
        keyboardType="decimal-pad"
      />

      <Input
        label="Unit"
        value={unit}
        onChangeText={setUnit}
        placeholder="kg, litre, piece, packet"
      />

      {!product && (
        <Input
          label="Initial stock"
          value={stock}
          onChangeText={setStock}
          keyboardType="number-pad"
        />
      )}

      {error ? (
        <Text className="text-red-600">{error}</Text>
      ) : null}

      <Button
        title={product ? "Save changes" : "Add product"}
        onPress={handleSubmit}
        loading={submitting}
      />
    </View>
  );
}