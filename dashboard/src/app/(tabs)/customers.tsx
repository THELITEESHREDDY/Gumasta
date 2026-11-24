import { useState, useCallback } from "react";

import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  ScrollView,
  ActivityIndicator,
} from "react-native";

import { SafeAreaView } from "react-native-safe-area-context";
import { useFocusEffect } from "expo-router";
import { Plus, Search, ChevronRight } from "lucide-react-native";

import { useShop } from "@/contexts/ShopContext";
import { Customer, CustomerData } from "@/types/customer";

import {
  getCustomers,
  createCustomer,
  updateCustomer,
} from "@/services/customer";

import CustomerForm from "@/components/CustomerForm";
import Button from "@/components/Button";

export default function CustomersScreen() {
  const { selectedShop } = useShop();

  const [customers, setCustomers] = useState<Customer[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editingCustomer, setEditingCustomer] =
    useState<Customer | undefined>();

  const loadCustomers = useCallback(async () => {
    if (!selectedShop) return;

    try {
      setLoading(true);
      setError("");

      setCustomers(await getCustomers(selectedShop.id));
    } catch {
      setError("Failed to load customers");
    } finally {
      setLoading(false);
    }
  }, [selectedShop?.id]);

  useFocusEffect(
    useCallback(() => {
      loadCustomers();
    }, [loadCustomers])
  );

  function openCreate() {
    setEditingCustomer(undefined);
    setShowForm(true);
  }

  function openEdit(customer: Customer) {
    setEditingCustomer(customer);
    setShowForm(true);
  }

  function closeForm() {
    setShowForm(false);
    setEditingCustomer(undefined);
  }

  async function handleSave(data: CustomerData) {
    if (!selectedShop) {
      throw new Error("No shop selected");
    }

    if (editingCustomer) {
      await updateCustomer(
        selectedShop.id,
        editingCustomer.id,
        data
      );
    } else {
      await createCustomer(selectedShop.id, data);
    }

    closeForm();
    await loadCustomers();
  }

  const query = search.trim().toLowerCase();

  const filteredCustomers = customers.filter(
    (customer) =>
      customer.name.toLowerCase().includes(query) ||
      customer.mobile.includes(query) ||
      customer.alternate_mobile?.includes(query)
  );

  if (showForm) {
    return (
      <SafeAreaView className="flex-1 bg-background">
        <ScrollView keyboardShouldPersistTaps="handled">
          <View className="mx-auto w-full max-w-xl p-5">
            <CustomerForm
              customer={editingCustomer}
              onSubmit={handleSave}
              onCancel={closeForm}
            />
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView className="flex-1 bg-background">
      <View className="mx-auto w-full max-w-3xl flex-1 gap-4 p-5">

        <View className="flex-row items-center justify-between">
          <Text className="text-2xl font-bold">
            Customers
          </Text>

          <TouchableOpacity
            onPress={openCreate}
            className="flex-row items-center gap-2 rounded-xl bg-primary px-4 py-3"
          >
            <Plus size={18} color="white" />

            <Text className="font-semibold text-white">
              Add customer
            </Text>
          </TouchableOpacity>
        </View>

        <View className="flex-row items-center gap-3 rounded-xl border border-gray-200 bg-white px-4 py-3">
          <Search size={20} color="#9CA3AF" />

          <TextInput
            value={search}
            onChangeText={setSearch}
            placeholder="Search name or mobile..."
            className="flex-1 text-base"
          />
        </View>

        {loading ? (
          <ActivityIndicator color="#166534" />
        ) : error ? (
          <View className="gap-3">
            <Text className="text-red-600">{error}</Text>
            <Button title="Retry" onPress={loadCustomers} />
          </View>
        ) : (
          <>
            <Text className="text-sm text-gray-500">
              {filteredCustomers.length} customers
            </Text>

            <FlatList
              data={filteredCustomers}
              keyExtractor={(item) => item.id}
              contentContainerStyle={{ gap: 12 }}
              ListEmptyComponent={
                <Text className="py-10 text-center text-gray-500">
                  No customers found
                </Text>
              }
              renderItem={({ item }) => (
                <TouchableOpacity
                  onPress={() => openEdit(item)}
                  className="flex-row items-center gap-4 rounded-xl border border-gray-200 bg-white p-4"
                >
                  <View className="h-12 w-12 items-center justify-center rounded-full bg-green-100">
                    <Text className="text-lg font-bold text-primary">
                      {item.name.slice(0, 2).toUpperCase()}
                    </Text>
                  </View>

                  <View className="flex-1">
                    <Text className="text-base font-semibold">
                      {item.name}
                    </Text>

                    <Text className="mt-1 text-gray-500">
                      {item.mobile}
                    </Text>

                    {item.address ? (
                      <Text
                        numberOfLines={1}
                        className="mt-1 text-sm text-gray-400"
                      >
                        {item.address}
                      </Text>
                    ) : null}
                  </View>

                  <ChevronRight size={20} color="#9CA3AF" />
                </TouchableOpacity>
              )}
            />
          </>
        )}
      </View>
    </SafeAreaView>
  );
}