import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import "../components/auth.css";

const STATS = [
  { label: "Quizzes completed", value: "--", note: "Coming soon" },
  { label: "Average score", value: "--", note: "Coming soon" },
  { label: "Learning streak", value: "--", note: "Coming soon" },
  { label: "Questions solved", value: "--", note: "Coming soon" },
];

export default function DashboardPage() {
  const { currentUser } = useAuth();
  const firstName = currentUser?.name.split(" ")[0] ?? "there";

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
          <div><span className="auth-eyebrow">At a glance</span><h2>Your progress</h2></div>
          <span className="dashboard-section-heading__future">Stats connect in a future update</span>
        </div>
        <div className="dashboard-stats">
          {STATS.map((stat) => (
            <article className="dashboard-stat" key={stat.label}>
              <span className="dashboard-stat__value">{stat.value}</span>
              <strong>{stat.label}</strong>
              <small>{stat.note}</small>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
