import api from "./api";
import {
  User,
  RegisterData,
  TokenResponse,
} from "@/types/auth";

export async function register(data: RegisterData) {
  const response = await api.post<User>(
    "/auth/register",
    data
  );

  return response.data;
}

export async function login(
  email: string,
  password: string
) {
  const form = new URLSearchParams();

  form.append("username", email);
  form.append("password", password);

  const response = await api.post<TokenResponse>(
    "/auth/login",
    form.toString(),
    {
      headers: {
        "Content-Type":
          "application/x-www-form-urlencoded",
      },
    }
  );

  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get<User>("/auth/me");

  return response.data;
}