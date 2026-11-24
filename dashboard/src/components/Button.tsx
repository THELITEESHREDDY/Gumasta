import {
  TouchableOpacity,
  Text,
  ActivityIndicator,
} from "react-native";

interface ButtonProps {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
}

export default function Button({
  title,
  onPress,
  loading = false,
  disabled = false,
}: ButtonProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={loading || disabled}
      className={`items-center rounded-xl bg-primary p-4 ${
        loading || disabled ? "opacity-50" : ""
      }`}
    >
      {loading ? (
        <ActivityIndicator color="white" />
      ) : (
        <Text className="text-base font-semibold text-white">
          {title}
        </Text>
      )}
    </TouchableOpacity>
  );
}