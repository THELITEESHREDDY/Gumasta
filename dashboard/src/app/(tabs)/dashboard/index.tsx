import { useState, useCallback } from "react";

import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";

import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter, useFocusEffect } from "expo-router";
import { RefreshCw } from "lucide-react-native";

import { useShop } from "@/contexts/ShopContext";

import {
  getDashboardSummary,
  getDashboardOrders,
  getDashboardTransactions,
} from "@/services/dashboard";

import {
  DashboardSummary,
  DashboardOrder,
  DashboardTransaction,
} from "@/types/dashboard";

import {
  formatCurrency,
  formatDateTime,
  today,
  isValidDate,
} from "@/utils/format";

import Button from "@/components/Button";
import Input from "@/components/Input";
import SummaryCard from "@/components/SummaryCards";
import PaymentBadge from "@/components/PaymentBadge";

type ActiveTab = "orders" | "transactions";

const PAGE_SIZE = 20;

export default function DashboardScreen() {
  const router = useRouter();
  const { selectedShop } = useShop();

  const [summary, setSummary] =
    useState<DashboardSummary | null>(null);

  const [orders, setOrders] =
    useState<DashboardOrder[]>([]);

  const [transactions, setTransactions] =
    useState<DashboardTransaction[]>([]);

  const [orderTotal, setOrderTotal] = useState(0);
  const [transactionTotal, setTransactionTotal] = useState(0);

  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(today);
  const [search, setSearch] = useState("");

  const [filters, setFilters] = useState(() => ({
    start_date: today(),
    end_date: today(),
    search: "",
  }));

  const [activeTab, setActiveTab] =
    useState<ActiveTab>("orders");

  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState("");
  const [filterError, setFilterError] = useState("");

  const loadDashboard = useCallback(async () => {
    if (!selectedShop) return;

    try {
      setLoading(true);
      setError("");

      const [summaryData, orderData, transactionData] =
        await Promise.all([
          getDashboardSummary(selectedShop.id, {
            start_date: filters.start_date,
            end_date: filters.end_date,
          }),

          getDashboardOrders(selectedShop.id, {
            ...filters,
            limit: PAGE_SIZE,
            offset: 0,
          }),

          getDashboardTransactions(selectedShop.id, {
            ...filters,
            limit: PAGE_SIZE,
            offset: 0,
          }),
        ]);

      setSummary(summaryData);
      setOrders(orderData.items);
      setTransactions(transactionData.items);
      setOrderTotal(orderData.total);
      setTransactionTotal(transactionData.total);

    } catch {
      setError("Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }, [selectedShop?.id, filters]);

  useFocusEffect(
    useCallback(() => {
      loadDashboard();
    }, [loadDashboard])
  );

  function applyFilters() {
    if (
      !isValidDate(startDate) ||
      !isValidDate(endDate)
    ) {
      setFilterError("Use valid YYYY-MM-DD dates");
      return;
    }

    if (startDate > endDate) {
      setFilterError("Start date cannot exceed end date");
      return;
    }

    setFilterError("");

    setFilters({
      start_date: startDate,
      end_date: endDate,
      search: search.trim(),
    });
  }

  function resetFilters() {
    const date = today();

    setStartDate(date);
    setEndDate(date);
    setSearch("");
    setFilterError("");

    setFilters({
      start_date: date,
      end_date: date,
      search: "",
    });
  }

  async function loadMore() {
    if (!selectedShop || loadingMore || loading) return;

    try {
      setLoadingMore(true);
      setError("");

      if (activeTab === "orders") {
        const response = await getDashboardOrders(
          selectedShop.id,
          {
            ...filters,
            limit: PAGE_SIZE,
            offset: orders.length,
          }
        );

        setOrders((previous) => [
          ...previous,
          ...response.items,
        ]);

        setOrderTotal(response.total);
      } else {
        const response = await getDashboardTransactions(
          selectedShop.id,
          {
            ...filters,
            limit: PAGE_SIZE,
            offset: transactions.length,
          }
        );

        setTransactions((previous) => [
          ...previous,
          ...response.items,
        ]);

        setTransactionTotal(response.total);
      }
    } catch {
      setError("Failed to load more records");
    } finally {
      setLoadingMore(false);
    }
  }

  function openOrder(orderId: string) {
    router.push({
      pathname: "/dashboard/orders/[id]",
      params: { id: orderId },
    });
  }

  const hasMore =
    activeTab === "orders"
      ? orders.length < orderTotal
      : transactions.length < transactionTotal;

  return (
    <SafeAreaView className="flex-1 bg-background">
      <ScrollView keyboardShouldPersistTaps="handled">
        <View className="mx-auto w-full max-w-3xl gap-5 p-5">

          {/* Header */}

          <View className="flex-row items-center justify-between">
            <View className="flex-1">
              <Text className="text-sm text-gray-500">
                Welcome back
              </Text>

              <Text className="text-2xl font-bold text-primary">
                {selectedShop?.name}
              </Text>
            </View>

            <TouchableOpacity
              onPress={loadDashboard}
              disabled={loading || loadingMore}
              className="rounded-xl bg-white p-3"
            >
              <RefreshCw size={22} color="#166534" />
            </TouchableOpacity>
          </View>

          {/* Summary */}

          {summary && (
            <View className="gap-3">
              <View className="flex-row gap-3">
                <SummaryCard
                  label="Total sales"
                  value={formatCurrency(summary.total_sales)}
                />

                <SummaryCard
                  label="Amount received"
                  value={formatCurrency(summary.amount_received)}
                  color="#16A34A"
                />
              </View>

              <View className="flex-row gap-3">
                <SummaryCard
                  label="Outstanding (all time)"
                  value={formatCurrency(summary.outstanding_amount)}
                  color="#DC2626"
                />

                <SummaryCard
                  label="Total orders"
                  value={String(summary.total_orders)}
                />
              </View>

              <Text className="text-xs text-gray-500">
                Reporting period: {summary.start_date} to{" "}
                {summary.end_date}
              </Text>
            </View>
          )}

          <Button
            title="+ New order"
            onPress={() =>
              router.push("/dashboard/orders/create")
            }
          />

          {/* Filters */}

          <View className="gap-3 rounded-xl border border-gray-200 bg-white p-4">

            <Text className="text-lg font-bold">
              Filters
            </Text>

            <View className="flex-row gap-3">
              <View className="flex-1">
                <Input
                  label="Start date"
                  value={startDate}
                  onChangeText={setStartDate}
                  placeholder="YYYY-MM-DD"
                />
              </View>

              <View className="flex-1">
                <Input
                  label="End date"
                  value={endDate}
                  onChangeText={setEndDate}
                  placeholder="YYYY-MM-DD"
                />
              </View>
            </View>

            <Input
              label="Search customer"
              value={search}
              onChangeText={setSearch}
              placeholder="Name or mobile number"
              maxLength={100}
            />

            {filterError ? (
              <Text className="text-red-600">
                {filterError}
              </Text>
            ) : null}

            <View className="flex-row gap-3">
              <View className="flex-1">
                <Button
                  title="Apply filters"
                  onPress={applyFilters}
                  disabled={loading || loadingMore}
                />
              </View>

              <TouchableOpacity
                onPress={resetFilters}
                disabled={loading || loadingMore}
                className="flex-1 items-center justify-center rounded-xl border border-gray-200"
              >
                <Text className="font-semibold text-gray-600">
                  Reset
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Orders / Transactions toggle */}

          <View className="flex-row rounded-xl bg-gray-200 p-1">
            {(["orders", "transactions"] as const).map(
              (tab) => (
                <TouchableOpacity
                  key={tab}
                  onPress={() => setActiveTab(tab)}
                  disabled={loadingMore}
                  className={`flex-1 items-center rounded-lg p-3 ${
                    activeTab === tab ? "bg-white" : ""
                  }`}
                >
                  <Text
                    className={`font-semibold capitalize ${
                      activeTab === tab
                        ? "text-primary"
                        : "text-gray-500"
                    }`}
                  >
                    {tab}
                  </Text>
                </TouchableOpacity>
              )
            )}
          </View>

          {error ? (
            <View className="gap-3">
              <Text className="text-red-600">{error}</Text>

              <Button
                title="Refresh dashboard"
                onPress={loadDashboard}
                disabled={loading || loadingMore}
              />
            </View>
          ) : null}

          {loading ? (
            <ActivityIndicator color="#166534" />
          ) : activeTab === "orders" ? (
            <>
              <Text className="text-sm text-gray-500">
                Showing {orders.length} of {orderTotal} orders
              </Text>

              {orders.length === 0 && (
                <Text className="py-8 text-center text-gray-500">
                  No orders found
                </Text>
              )}

              {orders.map((order) => (
                <TouchableOpacity
                  key={order.order_id}
                  onPress={() => openOrder(order.order_id)}
                  className="gap-3 rounded-xl border border-gray-200 bg-white p-4"
                >
                  <View className="flex-row justify-between">
                    <View className="flex-1">
                      <Text className="text-base font-semibold">
                        {order.customer_name}
                      </Text>

                      <Text className="text-sm text-gray-500">
                        {order.customer_mobile}
                      </Text>
                    </View>

                    <Text className="text-lg font-bold">
                      {formatCurrency(order.total_amount)}
                    </Text>
                  </View>

                  <PaymentBadge
                    status={order.payment_status}
                  />

                  <View className="flex-row border-t border-gray-100 pt-3">
                    <View className="flex-1">
                      <Text className="text-xs text-gray-500">
                        Amount received
                      </Text>

                      <Text className="font-bold text-green-600">
                        {formatCurrency(order.amount_paid)}
                      </Text>
                    </View>

                    <View className="flex-1">
                      <Text className="text-xs text-gray-500">
                        Outstanding
                      </Text>

                      <Text className="font-bold text-red-600">
                        {formatCurrency(order.amount_due)}
                      </Text>
                    </View>
                  </View>

                  <Text className="text-xs text-gray-400">
                    {formatDateTime(order.created_at)}
                  </Text>
                </TouchableOpacity>
              ))}
            </>
          ) : (
            <>
              <Text className="text-sm text-gray-500">
                Showing {transactions.length} of{" "}
                {transactionTotal} transactions
              </Text>

              {transactions.length === 0 && (
                <Text className="py-8 text-center text-gray-500">
                  No transactions found
                </Text>
              )}

              {transactions.map((transaction) => (
                <TouchableOpacity
                  key={transaction.payment_id}
                  onPress={() => openOrder(transaction.order_id)}
                  className="gap-3 rounded-xl border border-gray-200 bg-white p-4"
                >
                  <View className="flex-row justify-between">
                    <View className="flex-1">
                      <Text className="font-semibold">
                        {transaction.customer_name}
                      </Text>

                      <Text className="text-sm text-gray-500">
                        {transaction.customer_mobile}
                      </Text>
                    </View>

                    <Text className="text-lg font-bold text-green-600">
                      + {formatCurrency(transaction.amount)}
                    </Text>
                  </View>

                  <Text className="capitalize text-gray-600">
                    {transaction.payment_method.replace(/_/g, " ")}
                  </Text>

                  {transaction.reference && (
                    <Text className="text-sm text-gray-500">
                      Ref: {transaction.reference}
                    </Text>
                  )}

                  <Text className="text-xs text-gray-400">
                    {formatDateTime(transaction.created_at)}
                  </Text>
                </TouchableOpacity>
              ))}
            </>
          )}

          {!loading && hasMore && (
            <Button
              title="Load more"
              onPress={loadMore}
              loading={loadingMore}
            />
          )}

        </View>
      </ScrollView>
    </SafeAreaView>
  );
}