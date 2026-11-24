import { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";

import { useLocalSearchParams } from "expo-router";
import axios from "axios";

import { useShop } from "@/contexts/ShopContext";

import { getOrder, cancelOrder } from "@/services/order";
import { getCustomer } from "@/services/customer";

import {
  getPayments,
  getPaymentSummary,
  createPayment,
} from "@/services/payments";

import { OrderDetail } from "@/types/order";

import {
  Payment,
  PaymentSummary,
  PaymentMethod,
} from "@/types/payment";

import Input from "@/components/Input";
import Button from "@/components/Button";

const methods: PaymentMethod[] = [
  "cash",
  "upi",
  "card",
  "bank_transfer",
];

export default function OrderDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { selectedShop } = useShop();

  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [summary, setSummary] = useState<PaymentSummary | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [customerName, setCustomerName] = useState("");

  const [amount, setAmount] = useState("");
  const [method, setMethod] = useState<PaymentMethod>("cash");
  const [reference, setReference] = useState("");

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [confirmCancel, setConfirmCancel] = useState(false);

  async function loadOrder() {
    if (!selectedShop || !id) return;

    try {
      setLoading(true);
      setError("");

      const [orderData, summaryData, paymentData] =
        await Promise.all([
          getOrder(selectedShop.id, id),
          getPaymentSummary(selectedShop.id, id),
          getPayments(selectedShop.id, id),
        ]);

      const customer = await getCustomer(
        selectedShop.id,
        orderData.customer_id
      );

      setOrder(orderData);
      setSummary(summaryData);
      setPayments(paymentData);
      setCustomerName(customer.name);
      setAmount(summaryData.amount_due);
    } catch {
      setError("Failed to load order details");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadOrder();
  }, [selectedShop?.id, id]);

  async function handlePayment() {
    if (!selectedShop || !id || !summary || busy) return;

    if (
      !/^\d+(\.\d{1,2})?$/.test(amount.trim()) ||
      Number(amount) <= 0 ||
      Number(amount) > Number(summary.amount_due)
    ) {
      setError("Enter a valid amount within the outstanding balance");
      return;
    }

    try {
      setBusy(true);
      setError("");

      await createPayment(selectedShop.id, id, {
        amount: amount.trim(),
        payment_method: method,
        reference: reference.trim() || null,
      });

      setReference("");
      await loadOrder();
    } catch (err) {
      const detail = axios.isAxiosError(err)
        ? err.response?.data?.detail
        : null;

      setError(
        typeof detail === "string"
          ? detail
          : "Payment failed. Refresh before retrying."
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleCancel() {
    if (!selectedShop || !id || busy) return;

    try {
      setBusy(true);
      setError("");

      await cancelOrder(selectedShop.id, id);

      setConfirmCancel(false);
      await loadOrder();
    } catch {
      setError("Failed to cancel order");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <View className="flex-1 items-center justify-center">
        <ActivityIndicator color="#166534" />
      </View>
    );
  }

  if (!order || !summary) {
    return (
      <View className="gap-4 p-5">
        <Text className="text-red-600">{error}</Text>
        <Button title="Retry" onPress={loadOrder} />
      </View>
    );
  }

  return (
    <ScrollView
      className="flex-1 bg-background"
      keyboardShouldPersistTaps="handled"
    >
      <View className="mx-auto w-full max-w-xl gap-5 p-5">

        <View className="gap-3 rounded-xl bg-white p-5">
          <Text className="text-lg font-semibold">
            {customerName}
          </Text>

          <Text className="text-gray-500">Order total</Text>

          <Text className="text-3xl font-bold">
            ₹{summary.total_amount}
          </Text>

          <View className="flex-row border-t border-gray-200 pt-3">
            <View className="flex-1">
              <Text className="text-gray-500">Amount paid</Text>

              <Text className="text-xl font-bold text-green-600">
                ₹{summary.amount_paid}
              </Text>
            </View>

            <View className="flex-1">
              <Text className="text-gray-500">Amount due</Text>

              <Text className="text-xl font-bold text-red-600">
                ₹{summary.amount_due}
              </Text>
            </View>
          </View>

          <Text className="font-semibold capitalize text-gray-600">
            {summary.payment_status.replace(/_/g, " ")}
          </Text>
        </View>

        <Text className="text-xl font-bold">Order items</Text>

        <View className="gap-3 rounded-xl bg-white p-4">
          {order.order_items.map((item) => (
            <View
              key={item.id}
              className="flex-row justify-between"
            >
              <Text>
                {item.product_name} × {item.quantity}
              </Text>

              <Text className="font-semibold">
                ₹{item.subtotal}
              </Text>
            </View>
          ))}
        </View>

        {error ? (
          <View className="gap-2">
            <Text className="text-red-600">{error}</Text>
            <Button title="Refresh order" onPress={loadOrder} disabled={busy} />
          </View>
        ) : null}

        {order.status !== "cancelled" &&
          Number(summary.amount_due) > 0 && (
            <View className="gap-4">
              <Text className="text-xl font-bold">
                Record payment
              </Text>

              <Input
                label="Amount (₹)"
                value={amount}
                onChangeText={setAmount}
                keyboardType="decimal-pad"
              />

              <View className="flex-row flex-wrap gap-2">
                {methods.map((item) => (
                  <TouchableOpacity
                    key={item}
                    disabled={busy}
                    onPress={() => setMethod(item)}
                    className={`rounded-lg border px-4 py-3 ${
                      method === item
                        ? "border-primary bg-primary"
                        : "border-gray-200 bg-white"
                    }`}
                  >
                    <Text
                      className={`capitalize ${
                        method === item
                          ? "text-white"
                          : "text-gray-700"
                      }`}
                    >
                      {item.replace(/_/g, " ")}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>

              <Input
                label="Reference (optional)"
                value={reference}
                onChangeText={setReference}
              />

              <Button
                title="Record payment"
                onPress={handlePayment}
                loading={busy}
                disabled={!!error}
              />
            </View>
          )}

        <Text className="text-xl font-bold">
          Payment history
        </Text>

        {payments.length === 0 ? (
          <Text className="text-gray-500">
            No payments recorded
          </Text>
        ) : (
          payments.map((payment) => (
            <View
              key={payment.id}
              className="flex-row justify-between rounded-xl bg-white p-4"
            >
              <View>
                <Text className="font-semibold capitalize">
                  {payment.payment_method.replace(/_/g, " ")}
                </Text>

                {payment.reference ? (
                  <Text className="text-gray-500">
                    {payment.reference}
                  </Text>
                ) : null}
              </View>

              <Text className="font-bold text-green-600">
                + ₹{payment.amount}
              </Text>
            </View>
          ))
        )}

        {order.status !== "cancelled" &&
          payments.length === 0 && (
            confirmCancel ? (
              <View className="gap-3">
                <Text className="text-red-600">
                  Cancel this order and restore its stock?
                </Text>

                <Button
                  title="Confirm cancellation"
                  onPress={handleCancel}
                  loading={busy}
                />

                <Button
                  title="Keep order"
                  onPress={() => setConfirmCancel(false)}
                  disabled={busy}
                />
              </View>
            ) : (
              <TouchableOpacity
                disabled={busy}
                onPress={() => setConfirmCancel(true)}
                className="items-center rounded-xl border border-red-200 p-4"
              >
                <Text className="font-semibold text-red-600">
                  Cancel order
                </Text>
              </TouchableOpacity>
            )
          )}

      </View>
    </ScrollView>
  );
}