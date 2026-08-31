import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "../components/Button";
import { EvaluationReport } from "../components/EvaluationReport";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { api, type EvaluationResult, type PyqOut } from "../lib/api";

/**
 * A previous-year question, attempted under exam conditions. The evaluation
 * reuses the same diagnostic report — understanding connects to application.
 */
export function PYQPage() {
  const { pyqId } = useParams();
  const [pyq, setPyq] = useState<PyqOut | null>(null);
  const [text, setText] = useState("");
  const [phase, setPhase] = useState<"compose" | "evaluating">("compose");
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    api
      .pyq(pyqId!)
      .then((data) => !cancelled && setPyq(data))
      .catch((err: Error) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [pyqId]);

  const submit = async () => {
    if (!text.trim() || !pyq) return;
    setPhase("evaluating");
    try {
      const result = await api.attemptPyq(pyq.id, text.trim());
      setEvaluation(result.evaluation);
      window.scrollTo({ top: 0 });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPhase("compose");
    }
  };

  if (error && !pyq)
    return (
      <div role="alert" className="rounded-lg border border-misconception-line bg-misconception-bg px-5 py-4 text-[14.5px] text-misconception">
        {error}
      </div>
    );
  if (!pyq) return <LoadingState label="Loading the question…" centered />;

  const sourceParts = [
    pyq.source.university,
    pyq.source.subject,
    pyq.year || pyq.source.year,
    pyq.source.exam,
  ]
    .filter(Boolean)
    .map(String);
  sourceParts.push(`${pyq.marks} marks`);

  return (
    <article className="pb-8">
      <PageHeader
        crumbs={[{ label: "Learning path", to: "/" }, { label: "PYQ" }]}
        title="Previous year question"
        meta={
          <span className="text-[13px] text-ink-faint">{sourceParts.join(" • ")}</span>
        }
      />

      {/* The paper */}
      <section aria-label="The question" className="panel-surface rounded-[1.45rem] px-6 py-6 sm:px-8">
        <p className="eyebrow mb-4">Question · Q{pyq.code.split("-").at(-1)}</p>
        <p className="max-w-[70ch] text-[17px] leading-relaxed font-medium text-ink">{pyq.question}</p>

        <div className="mt-6 border-t border-rule pt-4">
          <p className="eyebrow mb-2">Concepts tested</p>
          <ul className="flex flex-wrap gap-x-5 gap-y-1.5">
            {pyq.concepts_tested.map((name) => (
              <li key={name} className="text-[13.5px] text-ink-soft">
                {name}
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Answer area */}
      <section aria-label="Your answer" className="mt-8">
        {evaluation ? (
          <>
            <div aria-live="polite" className="space-y-8">
              <EvaluationReport
                attempt={{
                  attempt_id: pyq.id,
                  attempt_number: 1,
                  evaluation,
                  improvement: null,
                  mastery: { concept_id: 0, score: evaluation.understanding, best_score: evaluation.understanding, attempts_count: 1 },
                }}
                onRetry={() => {
                  setEvaluation(null);
                  setText("");
                }}
                onAnswerFollowUp={() => {
                  setEvaluation(null);
                  setText("");
                }}
              />
            </div>
            <div className="mt-10 border-t border-rule pt-6">
              <Link to="/" className="text-sm font-medium text-primary hover:underline">
                Back to the learning path
              </Link>
            </div>
          </>
        ) : (
          <>
            <label htmlFor="pyq-answer" className="sr-only">
              Your answer
            </label>
            <textarea
              id="pyq-answer"
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={9}
              maxLength={1000}
              placeholder="Answer as you would in the examination hall — definition, reasoning, and a worked example."
              className="w-full resize-y rounded-[1.35rem] border border-rule-strong bg-carbon px-5 py-5 text-[15px] leading-relaxed text-ink placeholder:text-ink-faint focus:border-primary"
              disabled={phase === "evaluating"}
            />
            <div className="mt-3 flex items-center justify-between gap-3">
              <span className="tabular-nums text-[12.5px] text-ink-faint">{text.length}/1000</span>
              <Button onClick={submit} disabled={!text.trim()} loading={phase === "evaluating"}>
                Submit answer
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
          </>
        )}
      </section>
    </article>
  );
}
