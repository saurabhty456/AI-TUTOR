import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { TOKEN_KEY } from "../context/AuthProvider";
import type { QuizHistoryEntry } from "../data/quizData";
import { formatQuizDate } from "../data/quizData";
import "../components/auth.css";

const API_BASE = "http://127.0.0.1:8000";

export default function DashboardPage() {
  const { currentUser } = useAuth();
  const firstName = currentUser?.name.split(" ")[0] ?? "there";
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

  const stats = useMemo(() => {
    if (results.length === 0) {
      return {
        totalQuizzes: 0,
        averageScore: 0,
        bestScore: 0,
        questionsSolved: 0,
      };
    }

    const totalQuizzes = results.length;
    const averageScore =
      results.reduce((sum, item) => sum + Number(item.score_percentage), 0) /
      totalQuizzes;
    const bestScore = Math.max(...results.map((item) => Number(item.score_percentage)));
    const questionsSolved = results.reduce(
      (sum, item) => sum + item.correct_answers + item.wrong_answers,
      0
    );

    return {
      totalQuizzes,
      averageScore,
      bestScore,
      questionsSolved,
    };
  }, [results]);

  const recentResults = results.slice(0, 4);

  const topicPerformance = useMemo(() => {
    const byTopic = new Map<
      string,
      { totalScore: number; count: number; bestScore: number }
    >();

    for (const result of results) {
      const current = byTopic.get(result.topic) ?? {
        totalScore: 0,
        count: 0,
        bestScore: 0,
      };

      current.totalScore += Number(result.score_percentage);
      current.count += 1;
      current.bestScore = Math.max(current.bestScore, Number(result.score_percentage));
      byTopic.set(result.topic, current);
    }

    return [...byTopic.entries()]
      .map(([topic, statsValue]) => ({
        topic,
        average: Math.round(statsValue.totalScore / statsValue.count),
        best: statsValue.bestScore,
        count: statsValue.count,
      }))
      .sort((a, b) => b.average - a.average);
  }, [results]);

  const statCards = [
    { label: "Total Quizzes", value: stats.totalQuizzes, note: "Completed" },
    { label: "Average Score", value: `${Math.round(stats.averageScore)}%`, note: "Your average" },
    { label: "Best Score", value: `${Math.round(stats.bestScore)}%`, note: "Top result" },
    { label: "Questions Solved", value: stats.questionsSolved, note: "Attempted" },
  ];

  return (
    <main className="dashboard-page">
      <header className="dashboard-header">
        <Link to="/" className="auth-brand">
          <span className="auth-brand__mark">&lt;/&gt;</span>
          <span>CodeTutor</span>
        </Link>
        <span className="dashboard-header__label">Learning workspace</span>
      </header>
      <section className="dashboard-content">
        <div className="dashboard-intro">
          <span className="auth-eyebrow">Your dashboard</span>
          <h1>Welcome back, {firstName}</h1>
          <p>Choose a focused next step and keep your learning momentum moving.</p>
        </div>
        <div className="dashboard-actions">
          <Link to="/quiz" className="dashboard-action dashboard-action--primary">
            <span className="dashboard-action__icon">?</span>
            <span><strong>Start a quiz</strong><small>Test your programming knowledge</small></span>
            <span aria-hidden="true">→</span>
          </Link>
          <Link to="/chat" className="dashboard-action">
            <span className="dashboard-action__icon dashboard-action__icon--teal">&lt;/&gt;</span>
            <span><strong>Ask AI Tutor</strong><small>Work through a concept together</small></span>
            <span aria-hidden="true">→</span>
          </Link>
        </div>

        <div className="dashboard-section-heading">
          <div>
            <span className="auth-eyebrow">At a glance</span>
            <h2>Your progress</h2>
          </div>
          <Link to="/history" className="dashboard-history-link">View All History</Link>
        </div>

        <div className="dashboard-stats">
          {statCards.map((stat) => (
            <article className="dashboard-stat" key={stat.label}>
              <span className="dashboard-stat__value">{loading ? "--" : stat.value}</span>
              <strong>{stat.label}</strong>
              <small>{stat.note}</small>
            </article>
          ))}
        </div>

        <div className="dashboard-panel-group">
          <section className="dashboard-panel">
            <div className="dashboard-panel__header">
              <div>
                <span className="auth-eyebrow">Recent activity</span>
                <h3>Recent quizzes</h3>
              </div>
              <Link to="/history" className="dashboard-panel__link">View all</Link>
            </div>

            {recentResults.length === 0 ? (
              <div className="dashboard-empty">No recent quizzes yet. Start one to see your progress here.</div>
            ) : (
              <ul className="dashboard-list">
                {recentResults.map((result) => (
                  <li key={result.id} className="dashboard-list__item">
                    <div>
                      <strong>{result.topic}</strong>
                      <span>{result.difficulty}</span>
                    </div>
                    <div>
                      <strong>{result.score_percentage}%</strong>
                      <span>
                        {result.correct_answers} / {result.total_questions}
                      </span>
                    </div>
                    <div>
                      <strong>{formatQuizDate(result.completed_at)}</strong>
                      <span>{result.completed_at ? new Date(result.completed_at).toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" }) : ""}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="dashboard-panel">
            <div className="dashboard-panel__header">
              <div>
                <span className="auth-eyebrow">Performance</span>
                <h3>Topic performance</h3>
              </div>
            </div>

            {topicPerformance.length === 0 ? (
              <div className="dashboard-empty">Complete a few quizzes to see performance by topic.</div>
            ) : (
              <ul className="dashboard-topic-list">
                {topicPerformance.map((entry) => (
                  <li key={entry.topic} className="dashboard-topic-item">
                    <div>
                      <strong>{entry.topic}</strong>
                      <span>{entry.count} {entry.count === 1 ? "quiz" : "quizzes"}</span>
                    </div>
                    <div className="dashboard-topic-item__score">
                      <strong>{entry.average}%</strong>
                      <span>Best {entry.best}%</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      </section>
    </main>
  );
}
