import { Redirect } from "expo-router";
import { useAuth } from "@/contexts/AuthContext";
import { useShop } from "@/contexts/ShopContext";

export default function Index() {
  const { user } = useAuth();
  const { selectedShop } = useShop();

  if (!user) {
    return <Redirect href="/login" />;
  }

  if (!selectedShop) {
    return <Redirect href="/shops" />;
  }

  return <Redirect href="/dashboard" />;
}