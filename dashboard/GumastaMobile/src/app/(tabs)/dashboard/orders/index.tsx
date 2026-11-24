
import { useMemo, useState } from "react";
import {
  View,
  Text,
  TextInput,
  Pressable,
  ScrollView,
  StyleSheet,
} from "react-native";
import { router } from "expo-router";
import { Search, CalendarDays, ChevronRight } from "lucide-react-native";

type OrderStatus = "Pending" | "Completed" | "Cancelled";

type CustomerOrder = {
  id: string;
  customerName: string;
  customerPhone: string;
  date: string;
  amount: number;
  status: OrderStatus;
};

function formatDate(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function getDateDaysAgo(days: number) {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return formatDate(date);
}

// Temporary local data. Replace with API data later.
const sampleOrders: CustomerOrder[] = [
  {
    id: "ORD001",
    customerName: "Rahul Sharma",
    customerPhone: "9876543210",
    date: getDateDaysAgo(0),
    amount: 2450,
    status: "Pending",
  },
  {
    id: "ORD002",
    customerName: "Amit Kumar",
    customerPhone: "9876501234",
    date: getDateDaysAgo(0),
    amount: 5200,
    status: "Completed",
  },
  {
    id: "ORD003",
    customerName: "Priya Singh",
    customerPhone: "9876512345",
    date: getDateDaysAgo(1),
    amount: 1800,
    status: "Pending",
  },
  {
    id: "ORD004",
    customerName: "Vikram Patel",
    customerPhone: "9876523456",
    date: getDateDaysAgo(2),
    amount: 3600,
    status: "Cancelled",
  },
  {
    id: "ORD005",
    customerName: "Sneha Verma",
    customerPhone: "9876534567",
    date: getDateDaysAgo(5),
    amount: 4200,
    status: "Completed",
  },
];

export default function OrdersScreen() {
  const today = formatDate(new Date());

  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(today);
  const [search, setSearch] = useState("");

  const filteredOrders = useMemo(() => {
    return sampleOrders.filter((order) => {
      const matchesDate =
        order.date >= startDate && order.date <= endDate;

      const searchText = search.trim().toLowerCase();

      const matchesSearch =
        order.customerName.toLowerCase().includes(searchText) ||
        order.customerPhone.includes(searchText) ||
        order.id.toLowerCase().includes(searchText);

      return matchesDate && matchesSearch;
    });
  }, [startDate, endDate, search]);

  const getStatusStyle = (status: OrderStatus) => {
    switch (status) {
      case "Pending":
        return styles.pending;
      case "Completed":
        return styles.completed;
      case "Cancelled":
        return styles.cancelled;
    }
  };

  const openOrder = (orderId: string) => {
    router.push({
      pathname: "/(tabs)/dashboard/orders/[orderId]",
      params: { orderId },
    });
  };

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      keyboardShouldPersistTaps="handled"
    >
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.heading}>Customer Orders</Text>
          <Text style={styles.subtitle}>
            View and manage all your customer orders
          </Text>
        </View>
      </View>

      {/* Search */}
      <View style={styles.searchContainer}>
        <Search size={19} color="#6B7280" />
        <TextInput
          style={styles.searchInput}
          placeholder="Search customer or order ID"
          placeholderTextColor="#9CA3AF"
          value={search}
          onChangeText={setSearch}
        />
      </View>

      {/* Date Filters */}
      <View style={styles.filterCard}>
        <View style={styles.filterHeading}>
          <CalendarDays size={18} color="#2563EB" />
          <Text style={styles.filterTitle}>Filter by date</Text>
        </View>

        <View style={styles.dateRow}>
          <View style={styles.dateField}>
            <Text style={styles.fieldLabel}>Start date</Text>
            <TextInput
              style={styles.dateInput}
              value={startDate}
              onChangeText={setStartDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor="#9CA3AF"
              autoCapitalize="none"
            />
          </View>

          <View style={styles.dateField}>
            <Text style={styles.fieldLabel}>End date</Text>
            <TextInput
              style={styles.dateInput}
              value={endDate}
              onChangeText={setEndDate}
              placeholder="YYYY-MM-DD"
              placeholderTextColor="#9CA3AF"
              autoCapitalize="none"
            />
          </View>
        </View>

        <Pressable
          onPress={() => {
            setStartDate(today);
            setEndDate(today);
          }}
        >
          <Text style={styles.resetText}>Reset to today</Text>
        </Pressable>
      </View>

      {/* Orders Count */}
      <View style={styles.listHeading}>
        <Text style={styles.sectionTitle}>Orders</Text>
        <Text style={styles.orderCount}>
          {filteredOrders.length} found
        </Text>
      </View>

      {/* Order List */}
      {filteredOrders.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyTitle}>No orders found</Text>
          <Text style={styles.emptySubtitle}>
            Try changing the date range or search term.
          </Text>
        </View>
      ) : (
        filteredOrders.map((order) => (
          <Pressable
            key={order.id}
            style={styles.orderCard}
            onPress={() => openOrder(order.id)}
          >
            <View style={styles.orderTop}>
              <View style={styles.customerInfo}>
                <Text style={styles.customerName}>
                  {order.customerName}
                </Text>
                <Text style={styles.customerPhone}>
                  {order.customerPhone}
                </Text>
              </View>

              <View style={[styles.statusBadge, getStatusStyle(order.status)]}>
                <Text style={styles.statusText}>{order.status}</Text>
              </View>
            </View>

            <View style={styles.orderBottom}>
              <View>
                <Text style={styles.orderId}>{order.id}</Text>
                <Text style={styles.orderDate}>{order.date}</Text>
              </View>

              <View style={styles.amountContainer}>
                <Text style={styles.amount}>
                  ₹{order.amount.toLocaleString("en-IN")}
                </Text>
                <ChevronRight size={19} color="#9CA3AF" />
              </View>
            </View>
          </Pressable>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
  },
  content: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 22,
  },
  heading: {
    fontSize: 24,
    fontWeight: "700",
    color: "#111827",
  },
  subtitle: {
    fontSize: 13,
    color: "#6B7280",
    marginTop: 5,
  },
  searchContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#E5E7EB",
    borderRadius: 12,
    paddingHorizontal: 13,
    marginBottom: 18,
  },
  searchInput: {
    flex: 1,
    height: 48,
    marginLeft: 10,
    fontSize: 14,
    color: "#111827",
  },
  filterCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 15,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    marginBottom: 24,
  },
  filterHeading: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 15,
  },
  filterTitle: {
    fontSize: 15,
    fontWeight: "600",
    color: "#111827",
  },
  dateRow: {
    flexDirection: "row",
    gap: 12,
  },
  dateField: {
    flex: 1,
  },
  fieldLabel: {
    fontSize: 12,
    color: "#6B7280",
    marginBottom: 7,
  },
  dateInput: {
    height: 43,
    borderWidth: 1,
    borderColor: "#E5E7EB",
    borderRadius: 9,
    paddingHorizontal: 9,
    color: "#111827",
    fontSize: 13,
  },
  resetText: {
    color: "#2563EB",
    fontSize: 13,
    fontWeight: "600",
    marginTop: 13,
    alignSelf: "flex-end",
  },
  listHeading: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827",
  },
  orderCount: {
    fontSize: 13,
    color: "#6B7280",
  },
  orderCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 13,
    padding: 15,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  orderTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  customerInfo: {
    flex: 1,
  },
  customerName: {
    fontSize: 15,
    fontWeight: "600",
    color: "#111827",
  },
  customerPhone: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
  },
  pending: {
    backgroundColor: "#FEF3C7",
  },
  completed: {
    backgroundColor: "#DCFCE7",
  },
  cancelled: {
    backgroundColor: "#FEE2E2",
  },
  statusText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#374151",
  },
  orderBottom: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-end",
    borderTopWidth: 1,
    borderTopColor: "#F3F4F6",
    marginTop: 15,
    paddingTop: 12,
  },
  orderId: {
    fontSize: 12,
    fontWeight: "600",
    color: "#374151",
  },
  orderDate: {
    fontSize: 11,
    color: "#9CA3AF",
    marginTop: 4,
  },
  amountContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
  },
  amount: {
    fontSize: 15,
    fontWeight: "700",
    color: "#111827",
  },
  emptyState: {
    backgroundColor: "#FFFFFF",
    padding: 30,
    borderRadius: 13,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#E5E7EB",
  },
  emptyTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#111827",
  },
  emptySubtitle: {
    fontSize: 13,
    color: "#6B7280",
    textAlign: "center",
    marginTop: 7,
  },
});
