type SpeechRecognitionResult = {
  results: ArrayLike<
    ArrayLike<{ transcript: string }>
  >;
};

interface BrowserSpeechRecognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;

  onresult: ((event: SpeechRecognitionResult) => void) | null;
  onerror: ((event: { error: string }) => void) | null;
  onend: (() => void) | null;

  start(): void;
  stop(): void;
  abort(): void;
}

type SpeechRecognitionConstructor =
  new () => BrowserSpeechRecognition;

export function createSpeechRecognition() {
  if (typeof window === "undefined") {
    return null;
  }

  const browser = window as unknown as {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  };

  const Recognition =
    browser.SpeechRecognition ||
    browser.webkitSpeechRecognition;

  if (!Recognition) return null;

  const recognition = new Recognition();

  recognition.lang = "en-IN";
  recognition.continuous = false;
  recognition.interimResults = false;

  return recognition;
}

export function speakText(text: string) {
  if (
    typeof window === "undefined" ||
    !("speechSynthesis" in window)
  ) {
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);

  utterance.lang = "en-IN";
  utterance.rate = 0.95;
  utterance.pitch = 1;
  utterance.volume = 1;

  window.speechSynthesis.speak(utterance);
}

// Stop text-to-speech
export function stopSpeaking() {
  if (
    typeof window !== "undefined" &&
    "speechSynthesis" in window
  ) {
    window.speechSynthesis.cancel();
  }
}