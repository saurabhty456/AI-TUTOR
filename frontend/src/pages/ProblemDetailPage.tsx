import Editor, { type OnMount } from "@monaco-editor/react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { TOKEN_KEY } from "../context/AuthProvider";
import "../styles/landing.css";
import "./ProblemDetailPage.css";

const API_BASE = "http://127.0.0.1:8000";
const STARTER_CODE = "def solution():\n    pass";

const LANGUAGES = [
  { value: "python", label: "Python" },
] as const;

type ProblemNavigation = {
  id: number;
  title: string;
  position: number;
};

type Problem = {
  id: number;
  playlist_id: number;
  leetcode_id: number;
  title: string;
  leetcode_url: string;
  difficulty: string;
  acceptance_rate: number;
  frequency: number;
  is_premium: boolean;
  position: number;
  playlist_name: string;
  playlist_slug: string;
  company_name: string;
  previous_problem: ProblemNavigation | null;
  next_problem: ProblemNavigation | null;
};

type CodeRunResponse = {
  status: "success" | "error" | "timeout";
  stdout: string;
  stderr: string;
  executionTimeMs: number;
};

type CodeSubmitTestCase = {
  position: number;
  isSample: boolean;
  passed: boolean;
  input: string | null;
  expectedOutput: string | null;
  actualOutput: string | null;
  error: string | null;
};

type CodeSubmitResponse = {
  status: "accepted" | "wrong_answer" | "runtime_error" | "timeout";
  passed: number;
  total: number;
  executionTimeMs: number;
  testCases: CodeSubmitTestCase[];
};

export default function ProblemDetailPage() {
  const { problemId } = useParams();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [language, setLanguage] = useState<(typeof LANGUAGES)[number]["value"]>("python");
  const [code, setCode] = useState(STARTER_CODE);
  const [output, setOutput] = useState(
    "Run your code to see the sandbox output here."
  );
  const [executionStatus, setExecutionStatus] = useState<CodeRunResponse["status"] | "idle">("idle");
  const [executionTimeMs, setExecutionTimeMs] = useState<number | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<CodeSubmitResponse | null>(null);
  const [submitError, setSubmitError] = useState("");

  const handleEditorMount: OnMount = (editor) => {
    editor.focus();
  };

  const handleReset = () => {
    setCode(STARTER_CODE);
    setOutput("Editor reset to the original starter code.");
    setExecutionStatus("idle");
    setExecutionTimeMs(null);
    setSubmitResult(null);
    setSubmitError("");
  };

  const handleSubmit = async () => {
    if (isRunning || isSubmitting) return;

    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setSubmitError("Sign in to submit your solution for evaluation.");
      setSubmitResult(null);
      return;
    }

    setIsSubmitting(true);
    setSubmitResult(null);
    setSubmitError("");
    try {
      const response = await fetch(`${API_BASE}/code/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ problemId: problem?.id, language, code }),
      });
      if (!response.ok) {
        throw new Error(response.status === 401 ? "Sign in to submit your solution for evaluation." : "Unable to evaluate this submission.");
      }
      setSubmitResult((await response.json()) as CodeSubmitResponse);
    } catch (submissionError) {
      setSubmitError(submissionError instanceof Error ? submissionError.message : "Unable to evaluate this submission.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRun = async () => {
    if (isRunning) return;

    setIsRunning(true);
    setExecutionStatus("idle");
    setExecutionTimeMs(null);
    setOutput("Sending code to the secure sandbox...");

    try {
      const response = await fetch(`${API_BASE}/code/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language, code }),
      });
      const result = (await response.json()) as CodeRunResponse;
      if (!response.ok && !result.status) throw new Error("The execution service returned an invalid response.");

      setExecutionStatus(result.status);
      setExecutionTimeMs(result.executionTimeMs);
      const outputParts = [
        result.stdout ? `stdout:\n${result.stdout}` : "",
        result.stderr ? `stderr:\n${result.stderr}` : "",
      ].filter(Boolean);
      setOutput(outputParts.join("\n\n") || "The sandbox returned no output.");
    } catch {
      setExecutionStatus("error");
      setExecutionTimeMs(null);
      setOutput("Unable to reach the secure code execution service.");
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    if (!problemId) return;

    fetch(`${API_BASE}/problems/${problemId}`)
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to load problem.");
        return (await response.json()) as Problem;
      })
      .then(setProblem)
      .catch(() => setError("This problem is temporarily unavailable."))
      .finally(() => setLoading(false));
  }, [problemId]);

  const isProblemLoading = loading || !problem || problem.id !== Number(problemId);

  return (
    <div className="ct-page problem-detail-page">
      <Navbar />
      <main className="problem-detail-shell">
        {isProblemLoading ? <p className="problem-detail-state">Loading problem...</p> : null}
        {error ? <p className="problem-detail-state problem-detail-state--error">{error}</p> : null}
        {problem ? (
          <>
            <Link to={`/playlists/${problem.playlist_slug}`} className="problem-detail-back">
              ← Back to {problem.playlist_name}
            </Link>

            <header className="problem-detail-hero">
              <div className="problem-detail-hero__copy">
                <span className="problem-detail-eyebrow">
                  {problem.company_name} / {problem.playlist_name}
                </span>
                <h1>{problem.title}</h1>
                <div className="problem-detail-tags">
                  <span className={`problem-detail-difficulty problem-detail-difficulty--${problem.difficulty.toLowerCase()}`}>
                    {problem.difficulty}
                  </span>
                  {problem.is_premium ? <span className="problem-detail-premium">Premium</span> : null}
                  <span className="problem-detail-number">Problem {String(problem.position).padStart(2, "0")}</span>
                </div>
              </div>
              <div className="problem-detail-hero__meta">
                <div><strong>{problem.acceptance_rate}%</strong><span>Acceptance</span></div>
                <div><strong>{problem.frequency}%</strong><span>Frequency</span></div>
              </div>
            </header>

            <section className="problem-detail-practice" aria-labelledby="practice-heading">
              <div>
                <span className="problem-detail-eyebrow">Practice workspace</span>
                <h2 id="practice-heading">Write your solution.</h2>
                <p>Run your code in the secure sandbox, or submit it against CodeTutor-authored test cases.</p>
              </div>
              <a
                href={problem.leetcode_url}
                target="_blank"
                rel="noopener noreferrer"
                className="problem-detail-link"
              >
                Open on LeetCode <span aria-hidden="true">↗</span>
              </a>
            </section>

            <section className="code-workspace" aria-label="Code practice editor">
              <div className="code-workspace__toolbar">
                <label className="code-workspace__language">
                  <span>Language</span>
                  <select
                    value={language}
                    onChange={(event) => setLanguage(event.target.value as typeof language)}
                    aria-label="Programming language"
                  >
                    {LANGUAGES.map((item) => (
                      <option key={item.value} value={item.value}>{item.label}</option>
                    ))}
                  </select>
                </label>
                <div className="code-workspace__actions">
                  <button type="button" className="code-workspace__button code-workspace__button--secondary" onClick={handleReset} disabled={isRunning || isSubmitting}>
                    Reset Code
                  </button>
                  <button type="button" className="code-workspace__button code-workspace__button--primary" onClick={handleRun} disabled={isRunning || isSubmitting}>
                    {isRunning ? "Running..." : "Run Code"} {!isRunning ? <span aria-hidden="true">▶</span> : null}
                  </button>
                  <button type="button" className="code-workspace__button code-workspace__button--submit" onClick={handleSubmit} disabled={isRunning || isSubmitting}>
                    {isSubmitting ? "Evaluating..." : "Submit"} {!isSubmitting ? <span aria-hidden="true">✓</span> : null}
                  </button>
                </div>
              </div>

              <div className="code-workspace__editor">
                <Editor
                  height="500px"
                  language={language}
                  theme="vs-dark"
                  value={code}
                  onChange={(value) => setCode(value ?? "")}
                  onMount={handleEditorMount}
                  loading={<div className="code-workspace__loading">Loading editor...</div>}
                  options={{
                    automaticLayout: true,
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: "on",
                    folding: true,
                    scrollBeyondLastLine: false,
                    padding: { top: 18, bottom: 18 },
                    tabSize: 4,
                  }}
                />
              </div>

              <section className="code-workspace__panel" aria-labelledby="console-heading">
                <div className="code-workspace__panel-heading">
                  <span id="console-heading">Console</span>
                  <span className={`code-workspace__panel-status code-workspace__panel-status--${executionStatus}`}>
                    {executionStatus === "idle" ? "Ready" : executionStatus}
                  </span>
                </div>
                <p className={executionStatus === "error" || executionStatus === "timeout" ? "code-workspace__output--error" : ""}>{output}</p>
                {executionTimeMs !== null ? <small className="code-workspace__timing">Completed in {executionTimeMs} ms</small> : null}
              </section>

              <section className="code-workspace__panel" aria-labelledby="tests-heading">
                <div className="code-workspace__panel-heading">
                  <span id="tests-heading">Test Cases</span>
                  <span className="code-workspace__panel-status">CodeTutor judge</span>
                </div>
                {!submitResult && !submitError ? <p>Submit your solution to evaluate it against CodeTutor-authored test cases.</p> : null}
                {submitError ? <p className="code-workspace__output--error">{submitError}</p> : null}
                {submitResult ? (
                  <div className="judge-result">
                    <div className={`judge-result__verdict judge-result__verdict--${submitResult.status}`}>
                      <strong>{submitResult.status === "accepted" ? "Accepted" : submitResult.status === "wrong_answer" ? "Wrong Answer" : submitResult.status === "timeout" ? "Time Limit Exceeded" : "Runtime Error"}</strong>
                      <span>Passed: {submitResult.passed} / {submitResult.total}</span>
                      <span>Execution time: {submitResult.executionTimeMs} ms</span>
                    </div>
                    <div className="judge-result__cases">
                      {submitResult.testCases.map((testCase) => (
                        <article className={`judge-case judge-case--${testCase.passed ? "passed" : "failed"}`} key={testCase.position}>
                          <div className="judge-case__heading">
                            <strong>Test Case #{testCase.position}</strong>
                            <span>{testCase.passed ? "Passed" : "Failed"}</span>
                          </div>
                          {testCase.isSample ? (
                            <div className="judge-case__values">
                              <span><b>Input</b><code>{testCase.input}</code></span>
                              <span><b>Expected Output</b><code>{testCase.expectedOutput}</code></span>
                              <span><b>Your Output</b><code>{testCase.actualOutput ?? testCase.error ?? "No output"}</code></span>
                            </div>
                          ) : <p>Hidden test data is protected. {testCase.error ?? "Result recorded."}</p>}
                        </article>
                      ))}
                    </div>
                  </div>
                ) : null}
              </section>
            </section>

            <nav className="problem-detail-navigation" aria-label="Problem navigation">
              {problem.previous_problem ? (
                <Link to={`/problems/${problem.previous_problem.id}`} className="problem-detail-nav-card">
                  <span>← Previous problem</span>
                  <strong>{problem.previous_problem.title}</strong>
                  <small>Problem {String(problem.previous_problem.position).padStart(2, "0")}</small>
                </Link>
              ) : <span />}
              {problem.next_problem ? (
                <Link to={`/problems/${problem.next_problem.id}`} className="problem-detail-nav-card problem-detail-nav-card--next">
                  <span>Next problem →</span>
                  <strong>{problem.next_problem.title}</strong>
                  <small>Problem {String(problem.next_problem.position).padStart(2, "0")}</small>
                </Link>
              ) : <span />}
            </nav>
          </>
        ) : null}
      </main>
      <Footer />
    </div>
  );
}