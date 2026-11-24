import {
  createContext,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";

import { User } from "@/types/auth";
import * as authService from "@/services/auth";
import * as storage from "@/services/storage";
import { setAuthToken } from "@/services/api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (
    email: string,
    password: string
  ) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(
  null
);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    restoreSession();
  }, []);

  async function restoreSession() {
    try {
      const token = await storage.getToken();

      if (!token) return;

      setAuthToken(token);

      const currentUser =
        await authService.getCurrentUser();

      setUser(currentUser);
    } catch {
      setAuthToken(null);
      await storage.removeToken();
    } finally {
      setLoading(false);
    }
  }

  async function login(
    email: string,
    password: string
  ) {
    const response = await authService.login(
      email,
      password
    );

    setAuthToken(response.access_token);

    try {
      const currentUser =
        await authService.getCurrentUser();

      await storage.saveToken(response.access_token);

      setUser(currentUser);
    } catch (error) {
      setAuthToken(null);
      await storage.removeToken();
      throw error;
    }
  }

  async function logout() {
    await storage.removeToken();
    setAuthToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}