export type ConversationStatus =
  | "collecting_details"
  | "awaiting_confirmation"
  | "placing_order"
  | "completed"
  | "cancelled"
  | "failed";

export interface VoiceSession {
  session_id: string;
  response: string;
  status: ConversationStatus;
  order_id?: string | null;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}