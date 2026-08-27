import { Mic, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";

interface AudioRecorderProps {
  onTranscript: (text: string) => void;
  onError: (message: string) => void;
  disabled?: boolean;
}

type RecorderState = "idle" | "recording" | "transcribing";

/**
 * Press-to-record answer capture. Records with MediaRecorder, sends the blob
 * to /teachback/transcribe, and returns the transcript to the composer.
 * Hidden entirely when the browser has no recording support.
 */
export function AudioRecorder({ onTranscript, onError, disabled = false }: AudioRecorderProps) {
  const [state, setState] = useState<RecorderState>("idle");
  const [supported, setSupported] = useState(true);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    setSupported(
      typeof window !== "undefined" &&
        typeof MediaRecorder !== "undefined" &&
        Boolean(navigator.mediaDevices?.getUserMedia),
    );
    return () => {
      // If the component unmounts mid-recording, release the microphone.
      if (recorderRef.current?.state === "recording") {
        recorderRef.current.stop();
        recorderRef.current.stream.getTracks().forEach((t) => t.stop());
      }
    };
  }, []);

  if (!supported) return null;

  const start = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        setState("transcribing");
        try {
          const text = await api.transcribe(blob);
          if (text.trim()) onTranscript(text.trim());
          else onError("We couldn't hear anything in that recording. Try again a little closer.");
        } catch {
          onError("Transcription failed. You can still type your explanation below.");
        } finally {
          setState("idle");
        }
      };
      recorder.start();
      recorderRef.current = recorder;
      setState("recording");
    } catch {
      onError("Microphone access was blocked. Allow it in your browser, or type your answer.");
    }
  };

  const stop = () => {
    recorderRef.current?.stop();
  };

  if (state === "transcribing") {
    return (
      <span className="inline-flex h-10 items-center gap-2 rounded-md border border-rule bg-surface px-4 text-sm text-ink-soft">
        <span className="rec-dot h-2 w-2 rounded-full bg-misconception" aria-hidden />
        Transcribing your recording…
      </span>
    );
  }

  return (
    <button
      type="button"
      onClick={state === "recording" ? stop : start}
      disabled={disabled}
      className={`inline-flex h-10 items-center gap-2 rounded-md border px-4 text-sm font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
        state === "recording"
          ? "border-misconception-line bg-misconception-bg text-misconception hover:bg-misconception-line/30"
          : "border-rule-strong bg-surface text-ink hover:border-ink-faint"
      }`}
      aria-pressed={state === "recording"}
    >
      {state === "recording" ? (
        <>
          <Square size={13} fill="currentColor" aria-hidden />
          <span className="rec-dot h-2 w-2 rounded-full bg-misconception" aria-hidden />
          Stop recording
        </>
      ) : (
        <>
          <Mic size={15} aria-hidden />
          Record answer
        </>
      )}
    </button>
  );
}
