import { useEffect, useRef, useState } from "react";

import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import {
  createSpeechRecognition,
  speakText,
  stopSpeaking,
} from "@/services/speech";
import {
  Bot,
  Send,
  RotateCcw,
  Mic,
  MicOff,
} from "lucide-react-native";

import { useShop } from "@/contexts/ShopContext";

import {
  createSession,
  sendMessage,
} from "@/services/voice";

import {
  ChatMessage,
  ConversationStatus,
} from "@/types/voice";

export default function VoiceAssistantScreen() {
  const { selectedShop } = useShop();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [error, setError] = useState("");

  const [status, setStatus] =
    useState<ConversationStatus>("collecting_details");

  const scrollRef = useRef<ScrollView>(null);
  const busyRef = useRef(false);
  const messageId = useRef(0);

  const recognitionRef = useRef<
    ReturnType<typeof createSpeechRecognition>
  >(null);

  const finished = [
    "completed",
    "cancelled",
    "failed",
  ].includes(status);

  function makeMessage(
    role: "user" | "assistant",
    content: string
  ): ChatMessage {
    return {
      id: String(++messageId.current),
      role,
      content,
    };
  }

  // Stop microphone and discard pending transcription
  function stopMicrophone() {
    const recognition = recognitionRef.current;

    if (recognition) {
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;

      recognitionRef.current = null;
      recognition.abort();
    }

    setListening(false);
  }

  // Start a new conversation
  async function startSession() {
    if (!selectedShop || busyRef.current) return;

    stopMicrophone();
    stopSpeaking();

    busyRef.current = true;

    setLoading(true);
    setError("");
    setSessionId(null);
    setMessages([]);
    setInput("");
    setStatus("collecting_details");

    try {
      const result = await createSession(selectedShop.id);

      setSessionId(result.session_id);
      setStatus(result.status);

      setMessages([
        makeMessage("assistant", result.response),
      ]);
      speakText(result.response);
    } catch {
      setError("Unable to start conversation.");
    } finally {
      busyRef.current = false;
      setLoading(false);
    }
  }

  // Initialize conversation
  useEffect(() => {
    startSession();
  }, [selectedShop?.id]);

  // Microphone cleanup
  useEffect(() => {
   return () => {
     stopSpeaking();

    const recognition = recognitionRef.current;

     if (recognition) {
       recognition.onresult = null;
       recognition.onerror = null;
       recognition.onend = null;
       recognition.abort();
       recognitionRef.current = null;
     }
   };
 }, []);

  // Speech-to-text
  function handleMicrophone() {
    if (busyRef.current || finished || !sessionId) return;
    stopSpeaking();
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      return;
    }

    const recognition = createSpeechRecognition();

    if (!recognition) {
      setError("Speech recognition is not supported.");
      return;
    }

    recognitionRef.current = recognition;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;

      setInput(transcript);
    };

    recognition.onerror = (event) => {
      setError(`Microphone error: ${event.error}`);
      setListening(false);
    };

    recognition.onend = () => {
      setListening(false);
      recognitionRef.current = null;
    };

    try {
      setError("");
      recognition.start();
      setListening(true);
    } catch {
      setListening(false);
      recognitionRef.current = null;
      setError("Unable to start microphone.");
    }
  }

  // Send message to agent
  async function handleSend() {
    const message = input.trim();

    if (
      !message ||
      !sessionId ||
      busyRef.current ||
      finished
    ) return;

    stopMicrophone();
    stopSpeaking();

    busyRef.current = true;

    setLoading(true);
    setError("");
    setInput("");

    setMessages((previous) => [
      ...previous,
      makeMessage("user", message),
    ]);

    try {
      const result = await sendMessage(sessionId, message);

      setMessages((previous) => [
        ...previous,
        makeMessage("assistant", result.response),
      ]);

      setStatus(result.status);
      speakText(result.response);
    } catch {
      setError(
        "Unable to verify the response. Check the dashboard before retrying an order."
      );

      setStatus("failed");
    } finally {
      busyRef.current = false;
      setLoading(false);
    }
  }

  return (
    <View className="flex-1 bg-background">

      {/* Header */}
      <View className="flex-row items-center justify-between bg-white p-4 border-b border-gray-200">

        <View className="flex-row items-center gap-3">

          <View className="bg-primary p-3 rounded-full">
            <Bot size={24} color="white" />
          </View>

          <View>
            <Text className="text-lg font-bold">
              Gumasta AI
            </Text>

            <Text className="text-gray-500">
              Order-taking assistant
            </Text>
          </View>

        </View>

        <TouchableOpacity
          onPress={startSession}
          disabled={loading}
        >
          <RotateCcw size={22} color="#166534" />
        </TouchableOpacity>

      </View>

      {/* Conversation */}
      <ScrollView
        ref={scrollRef}
        className="flex-1 p-4"
        keyboardShouldPersistTaps="handled"
        onContentSizeChange={() =>
          scrollRef.current?.scrollToEnd({
            animated: true,
          })
        }
      >

        {messages.map((message) => (
          <View
            key={message.id}
            className={`mb-3 p-4 rounded-2xl max-w-[85%] ${
              message.role === "user"
                ? "self-end bg-primary"
                : "self-start bg-white border border-gray-200"
            }`}
          >
            <Text
              className={
                message.role === "user"
                  ? "text-white text-base"
                  : "text-gray-800 text-base"
              }
            >
              {message.content}
            </Text>
          </View>
        ))}

        {loading && (
          <View className="flex-row items-center gap-2 p-3">
            <ActivityIndicator
              color="#166534"
              size="small"
            />

            <Text className="text-gray-500">
              Processing...
            </Text>
          </View>
        )}

        {!!error && (
          <Text className="text-red-600 p-3">
            {error}
          </Text>
        )}

      </ScrollView>

      {/* Listening indicator */}
      {listening && (
        <View className="flex-row items-center justify-center gap-2 bg-red-50 p-3">

          <View className="h-3 w-3 rounded-full bg-red-600" />

          <Text className="text-red-600 font-medium">
            Listening... Speak now
          </Text>

        </View>
      )}

      {/* Message input */}
      {!finished && (
        <View className="flex-row items-center gap-3 bg-white p-4 border-t border-gray-200">

          {/* Microphone button */}
          <TouchableOpacity
            onPress={handleMicrophone}
            disabled={loading || !sessionId}
            className={`rounded-xl p-4 ${
              listening ? "bg-red-600" : "bg-primary"
            }`}
          >
            {listening ? (
              <MicOff size={22} color="white" />
            ) : (
              <Mic size={22} color="white" />
            )}
          </TouchableOpacity>

          {/* Text input */}
          <TextInput
            value={input}
            onChangeText={setInput}
            placeholder={
              listening
                ? "Listening..."
                : "Type your message..."
            }
            editable={!loading && !!sessionId && !listening}
            onSubmitEditing={handleSend}
            className="flex-1 bg-gray-100 rounded-xl p-4"
          />

          {/* Send button */}
          <TouchableOpacity
            onPress={handleSend}
            disabled={
              loading ||
              listening ||
              !input.trim() ||
              !sessionId
            }
            className={`rounded-xl p-4 ${
              loading ||
              listening ||
              !input.trim() ||
              !sessionId
                ? "bg-gray-400"
                : "bg-primary"
            }`}
          >
            <Send size={22} color="white" />
          </TouchableOpacity>

        </View>
      )}

      {/* Completed conversation */}
      {finished && (
        <TouchableOpacity
          onPress={startSession}
          disabled={loading}
          className="bg-primary m-4 p-4 rounded-xl"
        >
          <Text className="text-white text-center font-bold">
            Start New Conversation
          </Text>
        </TouchableOpacity>
      )}

    </View>
  );
}