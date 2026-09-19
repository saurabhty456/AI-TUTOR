import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { TOKEN_KEY } from "../context/AuthProvider";
import type { QuizHistoryEntry } from "../data/quizData";
import { formatQuizDate, formatQuizTime } from "../data/quizData";

const API_BASE = "http://127.0.0.1:8000";

type CodeSubmission = {
  id: number;
  problemId: number;
  problemTitle: string;
  status: string;
  language: string;
  passedTests: number;
  totalTests: number;
  executionTimeMs: number;
  createdAt: string;
};

export default function HistoryPage() {
  const [results, setResults] = useState<QuizHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [submissions, setSubmissions] = useState<CodeSubmission[]>([]);

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
      setLoading(false);
      setResults([]);
      return;
    }

    fetch(`${API_BASE}/quiz/results`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("Unable to load your quiz history.");
        }
        return (await response.json()) as QuizHistoryEntry[];
      })
      .then((data) => setResults(Array.isArray(data) ? data : []))
      .catch(() => setResults([]))
      .finally(() => setLoading(false));

    fetch(`${API_BASE}/code/submissions`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (response) => response.ok ? (await response.json()) as CodeSubmission[] : [])
      .then(setSubmissions)
      .catch(() => setSubmissions([]));
  }, []);

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <Link to="/" className="auth-brand">
          <span className="auth-brand__mark">&lt;/&gt;</span>
          <span>CodeTutor</span>
        </Link>
        <span className="dashboard-header__label">Quiz history</span>
      </header>

      <section className="history-page__content">
        <div className="history-page__header">
          <div>
            <span className="auth-eyebrow">Your progress</span>
            <h1>Quiz History</h1>
          </div>
          <Link to="/dashboard" className="dashboard-panel__link">Back to dashboard</Link>
        </div>

        {loading ? (
          <div className="dashboard-empty">Loading your history...</div>
        ) : results.length === 0 ? (
          <div className="history-page__empty">
            <h2>No quiz history yet.</h2>
            <p>No quiz history yet. Take your first quiz to start tracking your progress.</p>
            <Link to="/quiz" className="dashboard-action dashboard-action--primary history-page__cta">
              <span className="dashboard-action__icon">?</span>
              <span><strong>Start a quiz</strong><small>Build your progress</small></span>
              <span aria-hidden="true">→</span>
            </Link>
          </div>
        ) : (
          <div className="history-list">
            {results.map((result) => (
              <article key={result.id} className="history-item">
                <div className="history-item__topline">
                  <div>
                    <span className="history-item__topic">{result.topic}</span>
                    <span className="history-item__difficulty">{result.difficulty}</span>
                  </div>
                  <span className="history-item__score">{result.score_percentage}%</span>
                </div>

                <div className="history-item__meta">
                  <span>
                    {result.correct_answers} / {result.total_questions}
                  </span>
                  <span>
                    {formatQuizDate(result.completed_at)}
                  </span>
                  <span>{formatQuizTime(result.completed_at)}</span>
                </div>

                <div className="history-item__stats">
                  <span>Correct: {result.correct_answers}</span>
                  <span>Wrong: {result.wrong_answers}</span>
                  <span>Unanswered: {result.unanswered_questions}</span>
                </div>
              </article>
            ))}
          </div>
        )}

        <div className="history-page__coding-heading">
          <div>
            <span className="auth-eyebrow">Your progress</span>
            <h2>Coding Submission History</h2>
          </div>
        </div>
        {submissions.length === 0 ? (
          <div className="dashboard-empty">No coding submissions yet. Submit a solution from a problem page to see it here.</div>
        ) : (
          <div className="code-history-list">
            {submissions.map((submission) => (
              <article className="code-history-item" key={submission.id}>
                <div><strong>{submission.problemTitle}</strong><span>{submission.status === "accepted" ? "Accepted" : submission.status === "wrong_answer" ? "Wrong Answer" : submission.status === "timeout" ? "Time Limit Exceeded" : "Runtime Error"}</span></div>
                <span>{submission.language}</span>
                <span>{submission.passedTests}/{submission.totalTests} tests</span>
                <span>{submission.executionTimeMs} ms</span>
                <time dateTime={submission.createdAt}>{new Date(submission.createdAt).toLocaleString()}</time>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
