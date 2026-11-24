
import { Tabs } from "expo-router";
import {
  LayoutDashboard,
  ChartNoAxesCombined,
  UserRound,
} from "lucide-react-native";

export default function TabsLayout() {
  return (
    <Tabs
      
        screenOptions={{
            headerShown: false,

            tabBarActiveTintColor: "#2563EB",
            tabBarInactiveTintColor: "#9CA3AF",

            tabBarStyle: {
                height: 65,
                paddingBottom: 8,
                paddingTop: 6,
                backgroundColor: "#FFFFFF",
                borderTopWidth: 1,
                borderTopColor: "#E5E7EB",
            },

            tabBarLabelStyle: {
                fontSize: 11,
                fontWeight: "600",
            },

            tabBarIconStyle: {
                marginTop: 2,
            },
        }}

    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: "Dashboard",
          tabBarIcon: ({ color, size }) => (
            <LayoutDashboard color={color} size={size} />
          ),
        }}
      />

      <Tabs.Screen
        name="analysis"
        options={{
          title: "Analysis",
          tabBarIcon: ({ color, size }) => (
            <ChartNoAxesCombined color={color} size={size} />
          ),
        }}
      />

      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color, size }) => (
            <UserRound color={color} size={size} />
          ),
        }}
      />
    </Tabs>
  );
}
