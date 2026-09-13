import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import "../styles/landing.css";
import "../styles/playlists.css";

const API_BASE = "http://127.0.0.1:8000";

type PlaylistSummary = {
  id: number;
  name: string;
  slug: string;
  company_name: string;
  description: string;
  total_problems: number;
};

export default function PlaylistListPage() {
  const [playlists, setPlaylists] = useState<PlaylistSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/playlists`)
      .then(async (response) => {
        if (!response.ok) throw new Error("Unable to load playlists.");
        return (await response.json()) as PlaylistSummary[];
      })
      .then((data) => setPlaylists(Array.isArray(data) ? data : []))
      .catch(() => setError("Playlists are temporarily unavailable."))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="ct-page playlist-page">
      <Navbar />
      <main className="playlist-shell">
        <div className="playlist-hero">
          <span className="playlist-eyebrow">Interview preparation</span>
          <h1>Company-wise DSA playlists</h1>
          <p>Practice the questions that show up most often in real technical interviews.</p>
        </div>

        {loading ? <p className="playlist-state">Loading playlists...</p> : null}
        {error ? <p className="playlist-state playlist-state--error">{error}</p> : null}
        {!loading && !error ? (
          <section className="playlist-grid" aria-label="Company playlists">
            {playlists.map((playlist) => (
              <article className="playlist-card" key={playlist.id}>
                <div className="playlist-card__mark">{playlist.company_name.slice(0, 1)}</div>
                <div className="playlist-card__body">
                  <span className="playlist-card__label">{playlist.company_name}</span>
                  <h2>{playlist.name}</h2>
                  <p>{playlist.description}</p>
                  <div className="playlist-card__footer">
                    <span>{playlist.total_problems} Problems</span>
                    <Link to={`/playlists/${playlist.slug}`} className="ct-btn ct-btn--primary">
                      Open playlist <span aria-hidden="true">→</span>
                    </Link>
                  </div>
                </div>
              </article>
            ))}
          </section>
        ) : null}
      </main>
      <Footer />
    </div>
  );
}