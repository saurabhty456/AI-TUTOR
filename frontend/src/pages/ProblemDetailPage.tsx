import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/landing.css";
import "./ProblemDetailPage.css";

const API_BASE = "http://127.0.0.1:8000";

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

export default function ProblemDetailPage() {
  const { problemId } = useParams();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!problemId) return;

    setLoading(true);
    setError("");
    fetch(`${API_BASE}/problems/${problemId}`)
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to load problem.");
        return (await response.json()) as Problem;
      })
      .then(setProblem)
      .catch(() => setError("This problem is temporarily unavailable."))
      .finally(() => setLoading(false));
  }, [problemId]);

  return (
    <div className="ct-page problem-detail-page">
      <Navbar />
      <main className="problem-detail-shell">
        {loading ? <p className="problem-detail-state">Loading problem...</p> : null}
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
                <h2 id="practice-heading">Build your solution here next.</h2>
                <p>
                  The CodeTutor editor, hints, and code execution tools will be added in the next phase.
                  For now, use the metadata above to choose your next practice problem.
                </p>
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