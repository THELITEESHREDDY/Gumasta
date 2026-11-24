import { View, ScrollView } from "react-native";
import { useRouter } from "expo-router";

import ProductForm from "@/components/ProductForm";
import { useShop } from "@/contexts/ShopContext";
import { createProduct } from "@/services/product";
import { CreateProductData } from "@/types/product";

export default function CreateProductScreen() {
  const router = useRouter();
  const { selectedShop } = useShop();

  async function handleCreate(data: CreateProductData) {
    if (!selectedShop) {
      throw new Error("No shop selected");
    }

    await createProduct(selectedShop.id, data);

    router.back();
  }

  return (
    <ScrollView
      className="flex-1 bg-background"
      keyboardShouldPersistTaps="handled"
    >
      <View className="mx-auto w-full max-w-xl p-5">
        <ProductForm onSubmit={handleCreate} />
      </View>
    </ScrollView>
  );
}