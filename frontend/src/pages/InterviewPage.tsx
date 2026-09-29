import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { TOKEN_KEY } from "../context/AuthProvider";
import "../styles/interview.css";

const API_BASE = "http://127.0.0.1:8000";

type SQLTable = {
  name: string;
  columns: [string, string][];
  sample_rows: (string | number | null)[][];
};

type SQLExecution = {
  query?: string;
  correct: boolean;
  visible_passed: boolean;
  hidden_passed: boolean;
  hidden_tests_total: number;
  visible_output: Record<string, string | number | null>[];
  error: string | null;
};

type InterviewQuestion = {
  id: number;
  position: number;
  kind: "dsa" | "sql" | "system_design";
  prompt: string;
  details: {
    title?: string;
    difficulty?: string;
    leetcode_url?: string;
    dialect?: string;
    tables?: SQLTable[];
    expected_output?: Record<string, string | number | null>[];
    execution_enabled?: boolean;
  };
  answer: {
    answer_text: string;
    self_reported_result: string | null;
    sql_execution: SQLExecution | null;
  } | null;
};

type InterviewData = {
  id: number;
  status: string;
  created_at: string;
  questions: InterviewQuestion[];
};

type AnswerDraft = { answer_text: string; self_reported_result: string };
type AnswerMap = Record<number, AnswerDraft>;

type InterviewHistoryItem = {
  id: number;
  status: string;
  created_at: string;
  completed_at: string | null;
  overall_score: number | null;
};

type InterviewResult = {
  interview_id: number;
  overall_score: number;
  dsa_feedback: string;
  sql_feedback: string;
  system_design_feedback: string;
  strengths: string[];
  improvements: string[];
  final_feedback: string;
  evaluated_at: string;
  ai_generated: boolean;
  questions?: {
    position: number;
    kind: InterviewQuestion["kind"];
    prompt: string;
    title: string | null;
    answer_text: string;
    self_reported_result: string | null;
    sql_execution: SQLExecution | null;
  }[];
};

async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem(TOKEN_KEY);
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      ...(init.body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init.headers,
    },
  });
  if (!response.ok) {
    let message = "The request could not be completed.";
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) message = payload.detail;
    } catch {
      // Use the generic request message when the response is not JSON.
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

function BrandHeader({ label }: { label: string }) {
  return (
    <header className="interview-header">
      <Link to="/dashboard" className="auth-brand">
        <span className="auth-brand__mark">&lt;/&gt;</span>
        <span>CodeTutor</span>
      </Link>
      <span className="interview-header__label">{label}</span>
    </header>
  );
}

export default function InterviewPage() {
  const navigate = useNavigate();
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  async function startInterview() {
    setStarting(true);
    setError("");
    try {
      const interview = await apiRequest<InterviewData>("/interviews/start", { method: "POST" });
      navigate(`/interview/session/${interview.id}`);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to start an interview.");
    } finally {
      setStarting(false);
    }
  }

  return (
    <main className="interview-page">
      <BrandHeader label="Interview preparation" />
      <section className="interview-shell interview-setup">
        <div className="interview-hero">
          <span className="interview-eyebrow">Structured practice · 4 questions</span>
          <h1>Practice the whole interview.</h1>
          <p>Work through two real LeetCode problems, a medium-to-hard SQL challenge, and a system design prompt. Your responses are saved to your private interview history.</p>
          <button className="interview-button interview-button--primary" type="button" onClick={startInterview} disabled={starting}>
            {starting ? "Preparing your interview..." : "Start interview"}
            <span aria-hidden="true">→</span>
          </button>
          {error && <p className="interview-alert" role="alert">{error}</p>}
        </div>
        <div className="interview-steps" aria-label="Interview format">
          {[
            ["01", "DSA problem", "Approach and self-reported result"],
            ["02", "DSA problem", "Approach and self-reported result"],
            ["03", "SQL challenge", "PostgreSQL editor with test results"],
            ["04", "System design", "Architecture and trade-offs"],
          ].map(([number, title, description]) => (
            <article className="interview-step" key={number}>
              <span>{number}</span><div><strong>{title}</strong><small>{description}</small></div>
            </article>
          ))}
        </div>
        <Link className="interview-text-link" to="/interview/history">View interview history <span aria-hidden="true">→</span></Link>
      </section>
    </main>
  );
}

export function InterviewSessionPage() {
  const { interviewId } = useParams();
  const navigate = useNavigate();
  const [interview, setInterview] = useState<InterviewData | null>(null);
  const [answers, setAnswers] = useState<AnswerMap>({});
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState("");
  const [sqlExecution, setSqlExecution] = useState<SQLExecution | null>(null);

  useEffect(() => {
    if (!interviewId) return;
    apiRequest<InterviewData>(`/interviews/${interviewId}`)
      .then((data) => {
        setInterview(data);
        setAnswers(Object.fromEntries(data.questions.map((question) => [question.id, {
          answer_text: question.answer?.answer_text ?? "",
          self_reported_result: question.answer?.self_reported_result ?? "",
        }])));
        const sqlQuestion = data.questions.find((question) => question.kind === "sql");
        setSqlExecution(sqlQuestion?.answer?.sql_execution ?? null);
      })
      .catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : "Unable to load the interview."))
      .finally(() => setLoading(false));
  }, [interviewId]);

  const question = interview?.questions[step];
  const draft = question ? answers[question.id] ?? { answer_text: "", self_reported_result: "" } : null;

  function updateAnswer(changes: Partial<AnswerDraft>) {
    if (!question) return;
    setAnswers((previous) => ({
      ...previous,
      [question.id]: { ...(previous[question.id] ?? { answer_text: "", self_reported_result: "" }), ...changes },
    }));
  }

  async function persistAnswers() {
    if (!interview) return;
    setSaving(true);
    try {
      await apiRequest(`/interviews/${interview.id}/answers`, {
        method: "POST",
        body: JSON.stringify({ answers: interview.questions.map((item) => ({
          question_id: item.id,
          answer_text: answers[item.id]?.answer_text ?? "",
          self_reported_result: answers[item.id]?.self_reported_result || null,
        })) }),
      });
    } finally {
      setSaving(false);
    }
  }

  async function moveTo(nextStep: number) {
    setError("");
    try {
      await persistAnswers();
      setStep(nextStep);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save your answer.");
    }
  }

  async function executeSQL() {
    if (!interview || !question || !draft) return;
    setExecuting(true);
    setError("");
    try {
      const result = await apiRequest<SQLExecution>(`/interviews/${interview.id}/questions/${question.id}/execute-sql`, {
        method: "POST",
        body: JSON.stringify({ query: draft.answer_text }),
      });
      setSqlExecution(result);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "SQL execution failed.");
    } finally {
      setExecuting(false);
    }
  }

  async function submitInterview() {
    if (!interview) return;
    if (!window.confirm("Submit this interview for AI evaluation? You will not be able to edit it afterward.")) return;
    setEvaluating(true);
    setError("");
    try {
      await persistAnswers();
      await apiRequest<InterviewResult>(`/interviews/${interview.id}/evaluate`, {
        method: "POST",
        body: JSON.stringify({ answers: interview.questions.map((item) => ({
          question_id: item.id,
          answer_text: answers[item.id]?.answer_text ?? "",
          self_reported_result: answers[item.id]?.self_reported_result || null,
        })) }),
      });
      navigate(`/interview/result/${interview.id}`);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to evaluate this interview.");
    } finally {
      setEvaluating(false);
    }
  }

  if (loading) return <main className="interview-page"><BrandHeader label="Interview in progress" /><p className="interview-state">Loading your interview...</p></main>;
  if (error && !interview) return <main className="interview-page"><BrandHeader label="Interview in progress" /><div className="interview-state interview-alert">{error}</div></main>;
  if (!interview || !question || !draft) return <main className="interview-page"><BrandHeader label="Interview in progress" /><p className="interview-state">Interview not found.</p></main>;

  return (
    <main className="interview-page">
      <BrandHeader label={`Interview · ${interview.status === "completed" ? "completed" : "in progress"}`} />
      <section className="interview-shell interview-session">
        <div className="interview-progress-head">
          <Link className="interview-text-link" to="/interview">Exit interview</Link>
          <span>Question {step + 1} <i>/</i> {interview.questions.length}</span>
        </div>
        <div className="interview-progress-track" aria-label={`Question ${step + 1} of ${interview.questions.length}`}>
          {interview.questions.map((item, index) => <span key={item.id} className={index <= step ? "is-active" : ""} />)}
        </div>

        <div className="interview-question-head">
          <div>
            <span className="interview-eyebrow">{question.kind === "system_design" ? "System design" : question.kind === "dsa" ? `DSA question ${step + 1}` : "SQL challenge · Medium to Hard"}</span>
            <h1>{question.kind === "dsa" ? question.details.title : question.kind === "sql" ? "Query the data" : "Design the system"}</h1>
          </div>
          {question.details.difficulty && <span className={`interview-difficulty interview-difficulty--${question.details.difficulty.toLowerCase()}`}>{question.details.difficulty}</span>}
        </div>

        {question.kind === "dsa" && (
          <div className="interview-question-card">
            <p>{question.prompt}</p>
            <a className="interview-external-link" href={question.details.leetcode_url} target="_blank" rel="noreferrer">Open original LeetCode problem <span aria-hidden="true">↗</span></a>
            <label className="interview-field-label" htmlFor="self-report">Your result</label>
            <select id="self-report" value={draft.self_reported_result} onChange={(event) => updateAnswer({ self_reported_result: event.target.value })}>
              <option value="">Select a result</option>
              <option value="Solved">Solved</option>
              <option value="Partially solved">Partially solved</option>
              <option value="Could not solve">Could not solve</option>
            </select>
            <label className="interview-field-label" htmlFor="answer">Approach and complexity</label>
            <textarea id="answer" className="interview-editor interview-editor--answer" value={draft.answer_text} onChange={(event) => updateAnswer({ answer_text: event.target.value })} placeholder="Describe the key idea, correctness, time complexity, and space complexity..." />
          </div>
        )}

        {question.kind === "sql" && (
          <div className="interview-sql-layout">
            <div className="interview-question-card interview-sql-brief">
              <p>{question.prompt}</p>
              <strong>Schema and sample data</strong>
              {question.details.tables?.map((table) => (
                <div className="interview-table-wrap" key={table.name}>
                  <h3>{table.name}</h3>
                  <div className="interview-table-scroll"><table><thead><tr>{table.columns.map(([name, type]) => <th key={name}>{name}<small>{type}</small></th>)}</tr></thead><tbody>{table.sample_rows.map((row, index) => <tr key={`${table.name}-${index}`}>{row.map((value, cellIndex) => <td key={`${table.name}-${index}-${cellIndex}`}>{value ?? "NULL"}</td>)}</tr>)}</tbody></table></div>
                </div>
              ))}
              <strong>Expected output for the sample</strong>
              <ResultTable rows={question.details.expected_output ?? []} />
            </div>
            <div className="interview-sql-editor">
              <div className="interview-editor-title"><label htmlFor="sql-answer">PostgreSQL</label><span>Read-only query</span></div>
              <textarea id="sql-answer" className="interview-editor interview-editor--code" spellCheck={false} value={draft.answer_text} onChange={(event) => updateAnswer({ answer_text: event.target.value })} placeholder="WITH ... AS (...)\nSELECT ..." />
              {!question.details.execution_enabled && <p className="interview-inline-note">SQL execution is unavailable until the isolated sandbox is configured. Your query can still be submitted for AI feedback.</p>}
              <button type="button" className="interview-button interview-button--secondary" disabled={executing || !question.details.execution_enabled || !draft.answer_text.trim()} onClick={executeSQL}>{executing ? "Running tests..." : "Run against sample and hidden tests"}</button>
              {sqlExecution && <div className={`interview-execution ${sqlExecution.correct ? "is-correct" : "is-incorrect"}`}>
                <strong>{sqlExecution.error ? "Query error" : sqlExecution.correct ? "All tests passed" : "Some tests failed"}</strong>
                {sqlExecution.error ? <pre>{sqlExecution.error}</pre> : <><span>Sample: {sqlExecution.visible_passed ? "passed" : "failed"} · Hidden: {sqlExecution.hidden_passed ? "passed" : "failed"}</span><ResultTable rows={sqlExecution.visible_output} /></>}
              </div>}
            </div>
          </div>
        )}

        {question.kind === "system_design" && (
          <div className="interview-question-card">
            <p>{question.prompt}</p>
            <label className="interview-field-label" htmlFor="answer">System design response</label>
            <textarea id="answer" className="interview-editor interview-editor--design" value={draft.answer_text} onChange={(event) => updateAnswer({ answer_text: event.target.value })} placeholder="Start with requirements, then outline components, APIs, data model, scaling, and failure handling..." />
          </div>
        )}

        {error && <p className="interview-alert" role="alert">{error}</p>}
        <div className="interview-nav">
          <button type="button" className="interview-button interview-button--secondary" onClick={() => void moveTo(step - 1)} disabled={step === 0 || saving || evaluating}>{saving ? "Saving..." : "← Back"}</button>
          <span>{saving ? "Saving answers..." : "Answers save as you move between questions"}</span>
          {step < interview.questions.length - 1 ? (
            <button type="button" className="interview-button interview-button--primary" onClick={() => void moveTo(step + 1)} disabled={saving || evaluating}>Next question <span aria-hidden="true">→</span></button>
          ) : (
            <button type="button" className="interview-button interview-button--primary" onClick={() => void submitInterview()} disabled={saving || evaluating}>{evaluating ? "Evaluating..." : "Submit interview"}</button>
          )}
        </div>
      </section>
    </main>
  );
}

function ResultTable({ rows }: { rows: Record<string, string | number | null>[] }) {
  if (!rows.length) return <p className="interview-inline-note">No rows returned.</p>;
  const columns = Object.keys(rows[0]);
  return <div className="interview-table-scroll"><table><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{row[column] ?? "NULL"}</td>)}</tr>)}</tbody></table></div>;
}

export function InterviewHistoryPage() {
  const [items, setItems] = useState<InterviewHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiRequest<InterviewHistoryItem[]>("/interviews/history")
      .then(setItems)
      .catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : "Unable to load interview history."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="interview-page">
      <BrandHeader label="Interview history" />
      <section className="interview-shell interview-history">
        <div className="interview-history-head"><div><span className="interview-eyebrow">Your practice record</span><h1>Interview history</h1></div><Link className="interview-button interview-button--secondary" to="/interview">New interview</Link></div>
        {loading ? <p className="interview-state">Loading your interviews...</p> : error ? <p className="interview-alert" role="alert">{error}</p> : items.length === 0 ? (
          <div className="interview-empty"><strong>No interviews completed yet.</strong><p>Your completed interviews and scores will appear here.</p><Link className="interview-button interview-button--primary" to="/interview">Start your first interview</Link></div>
        ) : (
          <div className="interview-history-list">{items.map((item) => <Link className="interview-history-row" key={item.id} to={item.status === "completed" ? `/interview/result/${item.id}` : `/interview/session/${item.id}`}>
            <span className="interview-history-date">{new Date(item.created_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}</span>
            <span className="interview-history-name"><strong>Technical interview</strong><small>{item.status === "completed" ? "Completed" : "In progress"}</small></span>
            <span className="interview-history-score">{item.overall_score === null ? "Resume →" : `${Math.round(item.overall_score)}%`}</span>
          </Link>)}</div>
        )}
      </section>
    </main>
  );
}

export function InterviewResultPage() {
  const { interviewId } = useParams();
  const [result, setResult] = useState<InterviewResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!interviewId) return;
    apiRequest<InterviewResult>(`/interviews/${interviewId}/result`)
      .then(setResult)
      .catch((requestError: unknown) => setError(requestError instanceof Error ? requestError.message : "Unable to load the result."))
      .finally(() => setLoading(false));
  }, [interviewId]);

  if (loading) return <main className="interview-page"><BrandHeader label="Interview result" /><p className="interview-state">Loading your result...</p></main>;
  if (error || !result) return <main className="interview-page"><BrandHeader label="Interview result" /><p className="interview-state interview-alert" role="alert">{error || "Result not found."}</p></main>;

  const score = Math.round(result.overall_score);
  const feedback = [
    ["DSA", result.dsa_feedback],
    ["SQL", result.sql_feedback],
    ["System design", result.system_design_feedback],
  ];

  return (
    <main className="interview-page">
      <BrandHeader label="Interview result" />
      <section className="interview-shell interview-result">
        <div className="interview-result-top"><div><span className="interview-eyebrow">Technical interview · AI evaluation</span><h1>Interview result</h1><p>Evaluation generated by AI</p></div><div className="interview-score" style={{ "--score": `${score}%` } as React.CSSProperties}><strong>{score}<small>%</small></strong><span>Overall score</span></div></div>
        <article className="interview-result-summary"><span>Final feedback</span><p>{result.final_feedback}</p></article>
        <div className="interview-feedback-grid">{feedback.map(([title, text]) => <article className="interview-feedback-card" key={title}><span>{title}</span><p>{text}</p></article>)}</div>
        <div className="interview-result-lists">
          <article><h2>Strengths</h2>{result.strengths.length ? <ul>{result.strengths.map((item) => <li key={item}>{item}</li>)}</ul> : <p>No strengths were returned.</p>}</article>
          <article><h2>Areas to improve</h2>{result.improvements.length ? <ul>{result.improvements.map((item) => <li key={item}>{item}</li>)}</ul> : <p>No improvement areas were returned.</p>}</article>
        </div>
        <section className="interview-answer-review">
          <h2>Submitted answers</h2>
          {result.questions?.map((item) => <article key={item.position}>
            <div><span>Question {item.position} · {item.kind.replace("_", " ")}</span><strong>{item.title || item.prompt}</strong></div>
            <p>{item.answer_text || "No written answer submitted."}</p>
            {item.self_reported_result && <small>Self-reported: {item.self_reported_result}</small>}
            {item.kind === "sql" && item.sql_execution && <small>SQL tests: {item.sql_execution.correct ? "all passed" : "not all passed"}{item.sql_execution.error ? ` · ${item.sql_execution.error}` : ""}</small>}
          </article>)}
        </section>
        <div className="interview-result-actions"><Link className="interview-button interview-button--secondary" to="/interview/history">Interview history</Link><Link className="interview-button interview-button--primary" to="/interview">Practice again <span aria-hidden="true">→</span></Link></div>
        <p className="interview-ai-disclaimer">AI-generated feedback · Use as a practice guide, not a hiring decision.</p>
      </section>
    </main>
  );
}
