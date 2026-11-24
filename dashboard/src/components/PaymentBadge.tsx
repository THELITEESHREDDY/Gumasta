import { View, Text } from "react-native";
import { PaymentStatus } from "@/types/payment";

const styles = {
  paid: {
    background: "bg-green-100",
    text: "text-green-700",
    label: "Paid",
  },
  partially_paid: {
    background: "bg-amber-100",
    text: "text-amber-700",
    label: "Partially paid",
  },
  unpaid: {
    background: "bg-red-100",
    text: "text-red-700",
    label: "Unpaid",
  },
  cancelled: {
    background: "bg-gray-200",
    text: "text-gray-600",
    label: "Cancelled",
  },
};

export default function PaymentBadge({
  status,
}: {
  status: PaymentStatus;
}) {
  const style = styles[status];

  return (
    <View
      className={`self-start rounded-full px-3 py-1 ${style.background}`}
    >
      <Text
        className={`text-xs font-semibold ${style.text}`}
      >
        {style.label}
      </Text>
    </View>
  );
}