/**
 * Typed API client — a 1:1 mirror of the backend's Pydantic response schemas.
 * Every component consumes these types; nothing hand-rolls fetch calls.
 */

const BASE = import.meta.env.VITE_API_URL ?? "/api";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, init);
  } catch {
    throw new ApiError("Cannot reach the TeachBack server. Is the backend running?", 0);
  }
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      /* non-JSON error body — keep the generic message */
    }
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as T;
}

const jsonBody = (payload: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

// ---------------------------------------------------------------------------
// Types mirroring app/schemas/*
// ---------------------------------------------------------------------------

export interface ConceptPoint {
  key: string;
  label: string;
}

export interface MisconceptionOut {
  code: string;
  title: string;
  description: string;
  why_it_matters: string;
}

export interface EvaluationResult {
  understanding: number;
  conceptual_correctness: number;
  completeness: number;
  application_readiness: number;
  got_right: ConceptPoint[];
  needs_attention: ConceptPoint[];
  misconceptions: MisconceptionOut[];
  targeted_explanation: string;
  followup_question: string;
}

export interface Improvement {
  previous_understanding: number;
  current_understanding: number;
  delta: number;
  message: string;
}

export interface MasteryOut {
  concept_id: number;
  score: number;
  best_score: number;
  attempts_count: number;
}

export interface StartSessionResponse {
  session_id: number;
  concept_id: number;
  concept_name: string;
  prompt: string;
  attempt_number: number;
}

export interface AttemptResponse {
  attempt_id: number;
  attempt_number: number;
  evaluation: EvaluationResult;
  improvement: Improvement | null;
  mastery: MasteryOut;
}

export interface ConceptNode {
  id: number;
  code: string;
  name: string;
  order: number;
  teachback_enabled: boolean;
  mastery?: number | null;
}

export interface TopicNode {
  id: number;
  code: string;
  name: string;
  concepts: ConceptNode[];
}

export interface UnitNode {
  id: number;
  number: number;
  name: string;
  topics: TopicNode[];
}

export interface SubjectNode {
  id: number;
  code: string;
  name: string;
  units: UnitNode[];
}

export interface SemesterNode {
  id: number;
  number: number;
  name: string;
  subjects: SubjectNode[];
}

export interface PatternNode {
  id: number;
  code: string;
  name: string;
  semesters: SemesterNode[];
}

export interface ProgrammeNode {
  id: number;
  code: string;
  name: string;
  patterns: PatternNode[];
}

export interface UniversityNode {
  id: number;
  code: string;
  name: string;
  programmes: ProgrammeNode[];
}

export interface CurriculumTree {
  universities: UniversityNode[];
}

export interface Breadcrumb {
  university: string;
  programme: string;
  pattern: string;
  semester: string;
  subject: string;
  unit: string;
  topic: string;
}

export interface LearningContent {
  concept_id: number;
  code: string;
  name: string;
  summary: string;
  key_idea: string;
  explanation: string;
  example: string;
  common_mistake: string;
  teachback_enabled: boolean;
  breadcrumb: Breadcrumb;
  mastery: number | null;
  siblings: ConceptNode[];
}

export interface PyqOut {
  id: number;
  code: string;
  question: string;
  marks: number;
  year: string;
  source: Record<string, string | number>;
  concepts_tested: string[];
}

export interface PyqAttemptResponse {
  pyq_id: number;
  evaluation: EvaluationResult;
}

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------

export const api = {
  curriculum: () => request<CurriculumTree>("/curriculum"),

  learning: (conceptId: number | string) =>
    request<LearningContent>(`/learning/${conceptId}`),

  startSession: (conceptId: number) =>
    request<StartSessionResponse>("/teachback/sessions", jsonBody({ concept_id: conceptId })),

  submitAttempt: (
    sessionId: number | string,
    responseText: string,
    modality: "text" | "audio" = "text",
  ) =>
    request<AttemptResponse>(
      `/teachback/sessions/${sessionId}/attempts`,
      jsonBody({ response_text: responseText, modality }),
    ),

  transcribe: async (audio: Blob): Promise<string> => {
    const form = new FormData();
    const ext = audio.type.includes("mp4") ? "mp4" : audio.type.includes("ogg") ? "ogg" : "webm";
    form.append("file", audio, `answer.${ext}`);
    const data = await request<{ text: string }>("/teachback/transcribe", {
      method: "POST",
      body: form,
    });
    return data.text;
  },

  pyqsForConcept: (conceptId: number | string) =>
    request<PyqOut[]>(`/pyq/concepts/${conceptId}`),

  pyq: (pyqId: number | string) => request<PyqOut>(`/pyq/${pyqId}`),

  attemptPyq: (pyqId: number | string, responseText: string) =>
    request<PyqAttemptResponse>(`/pyq/${pyqId}/attempts`, jsonBody({ response_text: responseText })),
};
