import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { TOKEN_KEY } from "../context/AuthProvider";
import type { QuizHistoryEntry } from "../data/quizData";
import { formatQuizDate, formatQuizTime } from "../data/quizData";

const API_BASE = "http://127.0.0.1:8000";

export default function HistoryPage() {
  const [results, setResults] = useState<QuizHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

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
      </section>
    </main>
  );
}
