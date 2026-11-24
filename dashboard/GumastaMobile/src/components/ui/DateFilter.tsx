
import { useState } from "react";
import { View, Text, Pressable, Platform } from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";

interface DateFilterProps {
  label: string;
  date: Date;
  onChange: (date: Date) => void;
}

export default function DateFilter({
  label,
  date,
  onChange,
}: DateFilterProps) {
  const [showPicker, setShowPicker] = useState(false);

  const formattedDate = date.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });

  return (
    <View style={{ flex: 1, gap: 6 }}>
      <Text style={{ fontSize: 12, color: "#6B7280" }}>{label}</Text>

      <Pressable
        onPress={() => setShowPicker(true)}
        style={{
          borderWidth: 1,
          borderColor: "#E5E7EB",
          borderRadius: 10,
          padding: 12,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "#FFFFFF",
        }}
      >
        <Text style={{ color: "#111827", fontSize: 13 }}>
          {formattedDate}
        </Text>
        <Text>📅</Text>
      </Pressable>

      {showPicker && (
        <DateTimePicker
          value={date}
          mode="date"
          display={Platform.OS === "ios" ? "spinner" : "default"}
          onChange={(_, selectedDate) => {
            setShowPicker(Platform.OS === "ios");

            if (selectedDate) {
              onChange(selectedDate);
            }
          }}
        />
      )}
    </View>
  );
}
