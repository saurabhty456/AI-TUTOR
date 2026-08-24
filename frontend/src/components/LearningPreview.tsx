import "./LearningPreview.css";

const PLAYLISTS = [
  {
    title: "Python",
    path: ["Basics", "Functions", "OOP", "DSA"],
    progress: 62,
  },
  {
    title: "JavaScript",
    path: ["Fundamentals", "Async", "DOM", "Projects"],
    progress: 38,
  },
  {
    title: "Data Structures & Algorithms",
    path: ["Arrays", "Trees", "Graphs", "Dynamic Programming"],
    progress: 21,
  },
];

export default function LearningPreview() {
  return (
    <section className="ct-section">
      <div className="ct-container ct-learning">
        <div className="ct-learning__intro">
          <span className="ct-eyebrow">Structured paths</span>
          <h2 className="ct-h2">Learning playlists that build in order</h2>
          <p className="ct-lede">
            Each path breaks a subject into an ordered sequence, so you always know what
            comes next — and can see exactly how far you've gotten.
          </p>
        </div>

        <div className="ct-learning__list">
          {PLAYLISTS.map((p) => (
            <div className="ct-tab-card ct-playlist" key={p.title}>
              <div className="ct-tab-card__bar">
                <span className="ct-tab-card__dot" />
                <span className="ct-tab-card__filename">{p.title.toLowerCase().replace(/[^a-z]+/g, "-")}.path</span>
                <span className="ct-playlist__pct">{p.progress}%</span>
              </div>
              <div className="ct-playlist__body">
                <h3>{p.title}</h3>
                <div className="ct-playlist__steps">
                  {p.path.map((step, i) => (
                    <span key={step} className="ct-playlist__step">
                      {step}
                      {i < p.path.length - 1 && <span className="ct-playlist__arrow">→</span>}
                    </span>
                  ))}
                </div>
                <div className="ct-playlist__bar">
                  <div className="ct-playlist__bar-fill" style={{ width: `${p.progress}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
