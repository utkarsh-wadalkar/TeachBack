import { ArrowRight, BookOpen } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button } from "../components/Button";
import { ConceptBadge } from "../components/ConceptBadge";
import { LoadingState } from "../components/LoadingState";
import { PageHeader } from "../components/PageHeader";
import { QuestionCard } from "../components/QuestionCard";
import { api, type LearningContent, type PyqOut, type StartSessionResponse } from "../lib/api";

/**
 * The reading experience: typography and spacing do the hierarchy work —
 * no paragraph gets its own card. Ends with the call to prove understanding.
 */
export function LearningPage() {
  const { conceptId } = useParams();
  const navigate = useNavigate();
  const [content, setContent] = useState<LearningContent | null>(null);
  const [pyqs, setPyqs] = useState<PyqOut[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    api
      .learning(conceptId!)
      .then((data) => {
        if (cancelled) return;
        setContent(data);
        return api
          .pyqsForConcept(conceptId!)
          .then((p) => {
            if (!cancelled) setPyqs(p);
          })
          .catch(() => undefined); // PYQs are optional on this page
      })
      .catch((err: Error) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, [conceptId]);

  const startTeachback = async () => {
    if (!content) return;
    setStarting(true);
    try {
      const session: StartSessionResponse = await api.startSession(content.concept_id);
      sessionStorage.setItem(`tb-session-${session.session_id}`, JSON.stringify(session));
      navigate(`/session/${session.session_id}`, { state: session });
    } catch (err) {
      setError((err as Error).message);
      setStarting(false);
    }
  };

  if (error)
    return (
      <div role="alert" className="rounded-lg border border-misconception-line bg-misconception-bg px-5 py-4 text-[14.5px] text-misconception">
        {error}
      </div>
    );
  if (!content) return <LoadingState label="Loading the concept…" centered />;

  const b = content.breadcrumb;

  return (
    <article className="pb-8">
      <PageHeader
        crumbs={[
          { label: b.university },
          { label: b.subject, to: "/" },
          { label: b.topic, to: "/" },
        ]}
        title={content.name}
        meta={
          <span className="rounded-md border border-rule bg-surface px-2 py-1 text-[12px] font-medium tracking-[0.06em] text-ink-soft uppercase">
            {content.code}
          </span>
        }
      />

      {/* Reading column */}
      <div className="max-w-[70ch]">
        <p className="border-l border-primary pl-5 text-[17px] leading-relaxed font-medium text-ink">{content.summary}</p>

        {content.key_idea ? (
          <section aria-labelledby="key-idea" className="mt-9">
            <p id="key-idea" className="eyebrow mb-2 text-primary">
              Key idea
            </p>
            <p className="border-l-2 border-primary pl-4 text-[15.5px] leading-relaxed font-medium text-ink">
              {content.key_idea}
            </p>
          </section>
        ) : null}

        {content.explanation ? (
          <section aria-labelledby="explanation" className="prose-learning mt-9">
            <p id="explanation" className="eyebrow mb-2">
              Explanation
            </p>
            <div className="[&_p]:!text-ink-soft">
              {content.explanation.split("\n\n").map((para, i) => (
                <p key={i}>{para}</p>
              ))}
            </div>
          </section>
        ) : null}

        {content.example ? (
          <section aria-labelledby="example" className="panel-surface mt-9 rounded-[1.35rem] px-6 py-5">
            <p id="example" className="eyebrow mb-2 flex items-center gap-1.5">
              <BookOpen size={13} aria-hidden />
              Example
            </p>
            <div className="max-w-[68ch] text-[14.5px] leading-relaxed text-ink-soft">
              {content.example.split("\n\n").map((para, i) => (
                <p key={i}>{para}</p>
              ))}
            </div>
          </section>
        ) : null}

        {content.common_mistake ? (
          <section aria-labelledby="common-mistake" className="mt-8">
            <div className="rounded-[1.2rem] border border-attention-line border-l-4 border-l-attention bg-attention-bg px-5 py-4">
              <p id="common-mistake" className="eyebrow mb-1.5 text-attention">
                Common mistake
              </p>
              <p className="max-w-[64ch] text-[14.5px] leading-relaxed text-ink-soft">
                {content.common_mistake}
              </p>
            </div>
          </section>
        ) : null}
      </div>

      {/* Siblings */}
      <section aria-labelledby="in-topic" className="mt-12">
        <h2 id="in-topic" className="eyebrow mb-3">
          In this topic
        </h2>
        <ul className="panel-surface divide-y divide-rule rounded-[1.35rem] px-3 py-1.5">
          {content.siblings.map((sibling) => (
            <li key={sibling.id}>
              <ConceptBadge
                name={sibling.name}
                code={sibling.code}
                teachbackEnabled={sibling.teachback_enabled}
                mastery={sibling.mastery ?? undefined}
                to={`/concept/${sibling.id}`}
                state={
                  sibling.id === content.concept_id
                    ? "active"
                    : sibling.mastery != null
                      ? "attempted"
                      : "upcoming"
                }
              />
            </li>
          ))}
        </ul>
      </section>

      {/* The call to action — one rule, one question, one button */}
      <section aria-labelledby="ready" className="panel-surface mt-12 rounded-[1.45rem] px-6 py-7 sm:px-8">
        <p className="eyebrow mb-2 text-primary">Diagnostic gate</p>
        <h2 id="ready" className="display-type text-[26px]">
          Ready to explain it?
        </h2>
        <p className="mt-1.5 max-w-[60ch] text-[14.5px] leading-relaxed text-ink-soft">
          Put the reading away. Explain {content.name} in your own words — TeachBack will show you
          exactly where your understanding is solid and where it isn't.
        </p>
        {content.teachback_enabled ? (
          <Button onClick={startTeachback} loading={starting} className="mt-5">
            Start TeachBack
            <ArrowRight size={15} aria-hidden />
          </Button>
        ) : (
          <p className="mt-5 text-[14px] text-ink-faint">
            TeachBack for this concept is coming soon.
          </p>
        )}
      </section>

      {/* PYQs — understanding connects to application */}
      {pyqs.length > 0 ? (
        <section aria-labelledby="pyq-heading" className="mt-14">
          <h2 id="pyq-heading" className="mb-1 text-[18px] font-semibold tracking-[-0.01em]">
            Previous year questions
          </h2>
          <p className="mb-5 max-w-[60ch] text-[14px] leading-relaxed text-ink-faint">
            From actual SPPU end-semester papers. Apply what you learned.
          </p>
          <div className="space-y-4">
            {pyqs.map((pyq) => (
              <QuestionCard key={pyq.id} pyq={pyq} />
            ))}
          </div>
        </section>
      ) : null}
    </article>
  );
}
