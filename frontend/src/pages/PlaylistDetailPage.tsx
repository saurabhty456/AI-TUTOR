import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import { TOKEN_KEY } from "../context/AuthProvider";
import "../styles/landing.css";
import "../styles/playlists.css";

const API_BASE = "http://127.0.0.1:8000";

type Problem = {
  id: number;
  leetcode_id: number;
  title: string;
  leetcode_url: string;
  difficulty: string;
  acceptance_rate: number;
  frequency: number;
  is_premium: boolean;
  position: number;
};

type Playlist = {
  name: string;
  company_name: string;
  description: string;
  total_problems: number;
  problems: Problem[];
};

type ProblemProgress = {
  problemId: number;
  solved: boolean;
  attempted: boolean;
};

export default function PlaylistDetailPage() {
  const { slug } = useParams();
  const [playlist, setPlaylist] = useState<Playlist | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [problemProgress, setProblemProgress] = useState<Record<number, ProblemProgress>>({});
  const [showProgress, setShowProgress] = useState(false);

  useEffect(() => {
    if (!slug) return;
    const token = localStorage.getItem(TOKEN_KEY);
    setShowProgress(Boolean(token));
    Promise.all([
      fetch(`${API_BASE}/playlists/${slug}`).then(async (response) => {
        if (!response.ok) throw new Error("Unable to load playlist.");
        return (await response.json()) as Playlist;
      }),
      token
        ? fetch(`${API_BASE}/code/playlists/${slug}/progress`, { headers: { Authorization: `Bearer ${token}` } })
            .then(async (response) => response.ok ? (await response.json()) as ProblemProgress[] : [])
        : Promise.resolve([] as ProblemProgress[]),
    ])
      .then(([playlistData, progressData]) => {
        setPlaylist(playlistData);
        setProblemProgress(Object.fromEntries(progressData.map((item) => [item.problemId, item])));
      })
      .catch(() => setError("This playlist is temporarily unavailable."))
      .finally(() => setLoading(false));
  }, [slug]);

  return (
    <div className="ct-page playlist-page">
      <Navbar />
      <main className="playlist-shell playlist-shell--detail">
        <Link to="/playlists" className="playlist-back">← All playlists</Link>
        {loading ? <p className="playlist-state">Loading playlist...</p> : null}
        {error ? <p className="playlist-state playlist-state--error">{error}</p> : null}
        {playlist ? (
          <>
            <header className="playlist-detail-head">
              <div>
                <span className="playlist-eyebrow">{playlist.company_name} interview prep</span>
                <h1>{playlist.name}</h1>
                <p>{playlist.description}</p>
              </div>
              <strong className="playlist-total">{playlist.total_problems}<small>Problems</small></strong>
            </header>

            <section className="problem-list" aria-label={`${playlist.name} problems`}>
              {playlist.problems.map((problem) => (
                <Link to={`/problems/${problem.id}`} className="problem-row" key={problem.id}>
                  <span className="problem-row__number">{String(problem.position).padStart(2, "0")}</span>
                  <div className="problem-row__title">
                    <h2>{problem.title}</h2>
                    <span>LeetCode #{problem.leetcode_id}</span>
                  </div>
                  <span className={`difficulty difficulty--${problem.difficulty.toLowerCase()}`}>
                    {problem.difficulty}
                  </span>
                  <span className="problem-row__frequency">Frequency <strong>{problem.frequency}%</strong></span>
                  {problem.is_premium ? <span className="premium-badge">Premium</span> : null}
                  {showProgress ? (
                    <span className={`problem-row__status problem-row__status--${problemProgress[problem.id]?.solved ? "solved" : problemProgress[problem.id]?.attempted ? "attempted" : "unattempted"}`}>
                      {problemProgress[problem.id]?.solved ? "✓ Solved" : problemProgress[problem.id]?.attempted ? "● Attempted" : "○ Not Attempted"}
                    </span>
                  ) : null}
                </Link>
              ))}
            </section>
          </>
        ) : null}
      </main>
      <Footer />
    </div>
  );
}