import "./Badges.css";

const BADGES = [
  { icon: "🐍", label: "Python Basics", state: "earned" as const },
  { icon: "🧩", label: "OOP Explorer", state: "earned" as const },
  { icon: "🌳", label: "Tree Traversal", state: "earned" as const },
  { icon: "⚡", label: "7-Day Streak", state: "earned" as const },
  { icon: "🎤", label: "Mock Interview I", state: "locked" as const },
  { icon: "🧠", label: "DSA Level 3", state: "locked" as const },
];

export default function Badges() {
  return (
    <section className="ct-section ct-section--tight">
      <div className="ct-container ct-badges">
        <div className="ct-section-head">
          <span className="ct-eyebrow">Milestones</span>
          <h2 className="ct-h2">Badges that mark real progress</h2>
          <p className="ct-lede">
            Every completed playlist, quiz, and streak earns a badge — a visible
            record of what you've actually learned.
          </p>
        </div>

        <div className="ct-badges__grid">
          {BADGES.map((b) => (
            <div
              key={b.label}
              className={`ct-badge ${b.state === "locked" ? "ct-badge--locked" : ""}`}
            >
              <span className="ct-badge__icon">{b.icon}</span>
              <span className="ct-badge__label">{b.label}</span>
              {b.state === "locked" && <span className="ct-badge__lock">locked</span>}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
