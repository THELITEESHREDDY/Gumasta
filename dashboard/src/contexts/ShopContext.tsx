import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { Shop } from "@/types/shop";
import { useAuth } from "./AuthContext";

interface ShopContextType {
  selectedShop: Shop | null;
  selectShop: (shop: Shop) => void;
  clearShop: () => void;
}

const ShopContext = createContext<ShopContextType | null>(
  null
);

export function ShopProvider({
  children,
}: {
  children: ReactNode;
}) {
  const { user } = useAuth();

  const [selectedShop, setSelectedShop] =
    useState<Shop | null>(null);

  useEffect(() => {
    setSelectedShop(null);
  }, [user?.id]);

  function selectShop(shop: Shop) {
    setSelectedShop(shop);
  }

  function clearShop() {
    setSelectedShop(null);
  }

  return (
    <ShopContext.Provider
      value={{ selectedShop, selectShop, clearShop }}
    >
      {children}
    </ShopContext.Provider>
  );
}

export function useShop() {
  const context = useContext(ShopContext);

  if (!context) {
    throw new Error(
      "useShop must be used inside ShopProvider"
    );
  }

  return context;
}