import { CornerDownRight, Sparkles, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { AudioRecorder } from "../components/AudioRecorder";
import { Button } from "../components/Button";
import { EvaluationReport } from "../components/EvaluationReport";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import {
  api,
  type AttemptResponse,
} from "../lib/api";

const MAX_CHARS = 1000;

const DEMO_WEAK =
  "Third Normal Form builds on 2NF. A relation is in 3NF when it is already in second normal form, so all partial dependencies have been removed, and every non-key attribute depends on the candidate key. We use functional dependencies to check which attributes determine others. For example, in a STUDENT table, StudentID determines Name and Department.";

const DEMO_STRONG =
  "Third Normal Form builds on 2NF, so the relation must already be in second normal form with all partial dependencies removed. Beyond that, a relation is in 3NF only if there are no transitive dependencies: a non-key attribute must not depend on another non-key attribute, only on the candidate key. We reason about this using functional dependencies. For example, in STUDENT(StudentID, Dept, DeptHead) where StudentID determines Dept and Dept determines DeptHead, DeptHead depends transitively on the key, so it is not in 3NF and must be decomposed.";

interface SessionMeta {
  session_id: number;
  concept_id: number;
  concept_name: string;
  prompt: string;
}

type Phase = "compose" | "evaluating";

/**
 * The heart of the product: prove you understand. A focused composer, an
 * honest "Evaluating…" state, and then the diagnostic report. Attempts stack
 * within the same session so improvement is measured against your own last try.
 */
export function TeachBackPage() {
  const { sessionId } = useParams();
  const location = useLocation();

  const meta: SessionMeta | null =
    (location.state as SessionMeta | null) ??
    (() => {
      const raw = sessionStorage.getItem(`tb-session-${sessionId}`);
      return raw ? (JSON.parse(raw) as SessionMeta) : null;
    })();

  const [phase, setPhase] = useState<Phase>("compose");
  const [text, setText] = useState("");
  const [modality, setModality] = useState<"text" | "audio">("text");
  const [attempts, setAttempts] = useState<AttemptResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [followUpQuote, setFollowUpQuote] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Restore a returning session's attempts after a refresh.
  useEffect(() => {
    const raw = sessionStorage.getItem(`tb-attempts-${sessionId}`);
    if (raw) setAttempts(JSON.parse(raw));
  }, [sessionId]);

  useEffect(() => {
    if (attempts.length > 0) {
      sessionStorage.setItem(`tb-attempts-${sessionId}`, JSON.stringify(attempts));
    }
  }, [attempts, sessionId]);

  const submit = async () => {
    if (!text.trim()) return;
    setPhase("evaluating");
    setError(null);
    try {
      const result = await api.submitAttempt(sessionId!, text.trim(), modality);
      setAttempts((prev) => [...prev, result]);
      setPhase("compose");
      setText("");
      setFollowUpQuote(null);
      window.scrollTo({ top: 0 });
    } catch (err) {
      setError((err as Error).message);
      setPhase("compose");
    }
  };

  const retry = () => {
    setFollowUpQuote(null);
    setText("");
    textareaRef.current?.focus();
    window.scrollTo({ top: document.body.scrollHeight });
  };

  const answerFollowUp = (question: string) => {
    setFollowUpQuote(question);
    textareaRef.current?.focus();
    window.scrollTo({ top: document.body.scrollHeight });
  };

  if (!meta) {
    return (
      <div>
        <p className="mb-4 text-[15px] text-ink-soft">
          This TeachBack session isn't in this browser's memory anymore.
        </p>
        <Link to="/" className="text-sm font-medium text-primary hover:underline">
          Back to the learning path
        </Link>
      </div>
    );
  }

  const latest = attempts.at(-1);
  const canSubmit = text.trim().length > 0 && phase === "compose";

  return (
    <article className="pb-8">
      <PageHeader
        crumbs={[
          { label: "DBMS", to: "/" },
          { label: "Normalization", to: `/concept/${meta.concept_id}` },
        ]}
        title={`${meta.concept_name} — TeachBack`}
        lede="Can you teach this concept? Explain it as if you were teaching a classmate who has just finished the reading."
      />

      {/* Attempt history — small, factual */}
      {attempts.length > 0 ? (
        <ol className="mb-8 flex flex-wrap items-center gap-2" aria-label="Your attempts">
          {attempts.map((a, i) => (
            <li
              key={a.attempt_id}
              className={`rounded-full border px-3 py-1 text-[12.5px] font-medium tabular-nums ${
                i === attempts.length - 1
                  ? "border-primary-line bg-primary-tint text-primary"
                  : "border-rule bg-surface text-ink-faint"
              }`}
            >
              Attempt {a.attempt_number} · {a.evaluation.understanding}%
            </li>
          ))}
        </ol>
      ) : null}

      {latest ? (
        <section aria-label="Your evaluation" className="mb-12 space-y-8">
          <EvaluationReport
            attempt={latest}
            onRetry={retry}
            onAnswerFollowUp={answerFollowUp}
          />
        </section>
      ) : null}

      {/* Composer */}
      <section aria-label="Write your explanation" className={latest ? "border-t border-rule pt-10" : ""}>
        {followUpQuote ? (
          <div className="mb-4 flex items-start justify-between gap-3 rounded-[1.2rem] border border-primary-line bg-primary-tint px-5 py-4">
            <div>
              <p className="eyebrow mb-1 text-primary">Answering the follow-up</p>
              <p className="flex items-start gap-2 text-[14px] leading-relaxed text-ink">
                <CornerDownRight size={14} aria-hidden className="mt-1 shrink-0 text-primary" />
                {followUpQuote}
              </p>
            </div>
            <button
              type="button"
              onClick={() => setFollowUpQuote(null)}
              className="text-ink-faint hover:text-ink transition-colors p-1"
              aria-label="Clear follow-up question"
              title="Clear follow-up"
            >
              <X size={15} />
            </button>
          </div>
        ) : null}

        <div className="mb-2 flex items-center justify-between gap-2">
          <label htmlFor="explanation" className="text-[13px] font-medium text-ink-soft">
            Your explanation of {meta.concept_name}:
          </label>
          <div className="flex items-center gap-1.5 text-[12px]">
            <span className="text-ink-faint hidden sm:inline flex items-center gap-1">
              <Sparkles size={12} className="text-primary" /> Demo samples:
            </span>
            <button
              type="button"
              onClick={() => {
                setText(DEMO_WEAK);
                setModality("text");
              }}
              disabled={phase === "evaluating"}
              className="rounded bg-surface border border-rule px-2 py-0.5 font-medium text-primary hover:border-primary/50 transition-colors disabled:opacity-50"
              title="Load weak explanation (~72% score)"
            >
              Weak (72%)
            </button>
            <button
              type="button"
              onClick={() => {
                setText(DEMO_STRONG);
                setModality("text");
              }}
              disabled={phase === "evaluating"}
              className="rounded bg-surface border border-rule px-2 py-0.5 font-medium text-primary hover:border-primary/50 transition-colors disabled:opacity-50"
              title="Load strong explanation (~86% score)"
            >
              Strong (86%)
            </button>
          </div>
        </div>

        <textarea
          id="explanation"
          ref={textareaRef}
          value={text}
          maxLength={MAX_CHARS}
          onChange={(e) => {
            setText(e.target.value);
            setModality("text");
          }}
          rows={9}
          placeholder={
            followUpQuote
              ? "Take another go — use what the report showed you…"
              : `In your own words: what does ${meta.concept_name.replace(/^Third Normal Form$/, "3NF")} require, and why does it matter?`
          }
          className="w-full resize-y rounded-[1.35rem] border border-rule-strong bg-carbon px-5 py-5 text-[15px] leading-relaxed text-ink placeholder:text-ink-faint focus:border-primary"
          disabled={phase === "evaluating"}
        />

        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <AudioRecorder
              disabled={phase !== "compose"}
              onTranscript={(t) => {
                setText((prev) => (prev.trim() ? `${prev}\n\n${t}` : t));
                setModality("audio");
              }}
              onError={(msg) => setError(msg)}
            />
            <span className="tabular-nums text-[12.5px] text-ink-faint">
              {text.length}/{MAX_CHARS}
            </span>
          </div>

          <Button onClick={submit} disabled={!canSubmit} loading={phase === "evaluating"}>
            Submit explanation
          </Button>
        </div>

        {phase === "evaluating" ? (
          <div className="mt-6 border-t border-rule pt-6">
            <LoadingState label="Evaluating your explanation…" />
          </div>
        ) : null}

        {error ? (
          <p role="alert" className="mt-4 rounded-md border border-misconception-line bg-misconception-bg px-4 py-3 text-[14px] text-misconception">
            {error}
          </p>
        ) : null}

        {attempts.length === 0 && phase === "compose" ? (
          <p className="mt-5 max-w-[60ch] text-[13.5px] leading-relaxed text-ink-faint">
            Write it like you'd say it out loud. Cover what it is, why it exists, and an example —
            the evaluation checks all three.
          </p>
        ) : null}
      </section>
    </article>
  );
}
