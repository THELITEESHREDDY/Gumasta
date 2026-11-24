import {
  View,
  Text,
  TextInput,
  TextInputProps,
} from "react-native";

interface InputProps extends TextInputProps {
  label: string;
}

export default function Input({
  label,
  ...props
}: InputProps) {
  return (
    <View className="gap-2">
      <Text className="text-sm font-medium text-gray-700">
        {label}
      </Text>

      <TextInput
        {...props}
        placeholderTextColor="#9CA3AF"
        className="rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900"
      />
    </View>
  );
}