import { View, Text } from "react-native";

interface Props {
  label: string;
  value: string;
  color?: string;
}

export default function SummaryCard({
  label,
  value,
  color = "#111827",
}: Props) {
  return (
    <View className="flex-1 gap-2 rounded-xl border border-gray-200 bg-white p-4">
      <Text className="text-sm text-gray-500">
        {label}
      </Text>

      <Text
        className="text-xl font-bold"
        style={{ color }}
      >
        {value}
      </Text>
    </View>
  );
}