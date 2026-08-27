import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type CurriculumTree, type TopicNode } from "./api";

interface CurriculumState {
  tree: CurriculumTree | null;
  /** The Normalization topic — the MVP's one active topic. */
  topic: TopicNode | null;
  loading: boolean;
  error: string | null;
}

const CurriculumContext = createContext<CurriculumState>({
  tree: null,
  topic: null,
  loading: true,
  error: null,
});

export function CurriculumProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<CurriculumState>({
    tree: null,
    topic: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let cancelled = false;
    api
      .curriculum()
      .then((tree) => {
        if (cancelled) return;
        const semester = tree.universities[0]?.programmes[0]?.patterns[0]?.semesters[0];
        const subject = semester?.subjects.find((s) => s.code === "DBMS") ?? semester?.subjects[0];
        const topic = subject?.units.flatMap((u) => u.topics).find((t) => t.concepts.length > 0);
        setState({ tree, topic: topic ?? null, loading: false, error: null });
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setState((s) => ({ ...s, loading: false, error: err.message }));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return <CurriculumContext.Provider value={state}>{children}</CurriculumContext.Provider>;
}

export function useCurriculum() {
  return useContext(CurriculumContext);
}
