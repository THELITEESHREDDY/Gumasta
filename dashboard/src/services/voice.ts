import axios from "axios";

import { getToken } from "@/services/storage";
import { VoiceSession } from "@/types/voice";

const voiceApi = axios.create({
  baseURL: process.env.EXPO_PUBLIC_VOICE_API_URL,
  timeout: 60000,
});

voiceApi.interceptors.request.use(async (config) => {
  const token = await getToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export async function createSession(
  shopId: string
): Promise<VoiceSession> {
  const response = await voiceApi.post("/sessions", {
    shop_id: shopId,
  });

  return response.data;
}

export async function sendMessage(
  sessionId: string,
  message: string
): Promise<VoiceSession> {
  const response = await voiceApi.post(
    `/sessions/${sessionId}/message`,
    { message }
  );

  return response.data;
}