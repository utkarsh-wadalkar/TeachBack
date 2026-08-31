import { AlertTriangle, ArrowRight, Check } from "lucide-react";
import type { AttemptResponse } from "../lib/api";
import { Button } from "./Button";
import { EvaluationSection } from "./EvaluationSection";
import { LedgerRow } from "./LedgerRow";
import { MisconceptionCard } from "./MisconceptionCard";
import { ScoreCard } from "./ScoreCard";

interface EvaluationReportProps {
  attempt: AttemptResponse;
  onRetry: () => void;
  onAnswerFollowUp: (question: string) => void;
}

/**
 * The diagnostic report, disclosed progressively: headline understanding
 * first, then the breakdown, then what was right, what needs attention,
 * any misconception, a targeted explanation, and finally the follow-up.
 * Each block is one `.reveal-step` so the report reads top-to-bottom like an
 * examined answer sheet instead of arriving as a wall of text.
 */
export function EvaluationReport({ attempt, onRetry, onAnswerFollowUp }: EvaluationReportProps) {
  const { evaluation, improvement } = attempt;

  return (
    <div aria-live="polite">
      <div className="reveal-step">
        <EvaluationSection eyebrow="Your understanding">
          <ScoreCard understanding={evaluation.understanding} improvement={improvement} />
        </EvaluationSection>
      </div>

      <div className="reveal-step mt-8">
        <EvaluationSection eyebrow="Breakdown">
          <div className="panel-surface divide-y divide-rule/60 rounded-[1.25rem] px-5 py-1">
            <LedgerRow
              label="Conceptual correctness"
              value={`${evaluation.conceptual_correctness}%`}
              glyph={<Check size={13} className="text-correct" aria-hidden />}
            />
            <LedgerRow
              label="Completeness"
              value={`${evaluation.completeness}%`}
              glyph={
                evaluation.completeness >= evaluation.conceptual_correctness ? (
                  <Check size={13} className="text-correct" aria-hidden />
                ) : (
                  <AlertTriangle size={13} className="text-attention" aria-hidden />
                )
              }
            />
            <LedgerRow
              label="Application readiness"
              value={`${evaluation.application_readiness}%`}
              glyph={<AlertTriangle size={13} className="text-attention" aria-hidden />}
            />
          </div>
        </EvaluationSection>
      </div>

      <div className="reveal-step mt-8 grid gap-6 md:grid-cols-2 md:gap-10">
        <EvaluationSection eyebrow="What you got right">
          {evaluation.got_right.length > 0 ? (
            <ul className="space-y-2">
              {evaluation.got_right.map((point) => (
                <li key={point.key} className="flex items-start gap-2.5 text-[14.5px] text-ink-soft">
                  <Check size={15} strokeWidth={2.5} aria-hidden className="mt-0.5 shrink-0 text-correct" />
                  <span>
                    {point.label}
                    <span className="sr-only"> — correct</span>
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[14.5px] text-ink-faint">Nothing yet this time.</p>
          )}
        </EvaluationSection>

        <EvaluationSection eyebrow="What needs attention">
          {evaluation.needs_attention.length > 0 ? (
            <ul className="space-y-2">
              {evaluation.needs_attention.map((point) => (
                <li key={point.key} className="flex items-start gap-2.5 text-[14.5px] text-ink-soft">
                  <AlertTriangle size={15} aria-hidden className="mt-0.5 shrink-0 text-attention" />
                  <span>
                    {point.label}
                    <span className="sr-only"> — needs attention</span>
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-[14.5px] text-correct">Every expected idea was covered.</p>
          )}
        </EvaluationSection>
      </div>

      {evaluation.misconceptions.length > 0 ? (
        <div className="reveal-step mt-8 space-y-4">
          {evaluation.misconceptions.map((m) => (
            <MisconceptionCard
              key={m.code}
              misconception={m}
              action={
                <Button variant="secondary" size="sm" onClick={() => onAnswerFollowUp(evaluation.followup_question)}>
                  Explain this concept
                </Button>
              }
            />
          ))}
        </div>
      ) : null}

      {evaluation.targeted_explanation ? (
        <div className="reveal-step mt-8">
          <EvaluationSection eyebrow="Targeted explanation">
            <div className="border-l-2 border-primary pl-4">
              <p className="max-w-[68ch] text-[15px] leading-relaxed text-ink-soft">
                {evaluation.targeted_explanation}
              </p>
            </div>
          </EvaluationSection>
        </div>
      ) : null}

      {evaluation.followup_question ? (
        <div className="reveal-step mt-8">
          <EvaluationSection eyebrow="Follow-up question">
            <div className="panel-surface rounded-[1.25rem] px-5 py-4">
              <p className="max-w-[68ch] text-[15px] leading-relaxed font-medium text-ink">
                {evaluation.followup_question}
              </p>
              <div className="mt-4 flex flex-wrap gap-2.5">
                <Button onClick={onRetry}>
                  Try again
                  <ArrowRight size={15} aria-hidden />
                </Button>
              </div>
            </div>
          </EvaluationSection>
        </div>
      ) : null}
    </div>
  );
}
