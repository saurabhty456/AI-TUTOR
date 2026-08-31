const BADGES = [
  { icon: "🏆", title: "First Steps", desc: "Complete your first quiz." },
  { icon: "🔥", title: "Consistency", desc: "Maintain a 7-day learning streak." },
  { icon: "🧠", title: "Algorithm Master", desc: "Complete the algorithms playlist." },
  { icon: "💻", title: "Python Foundations", desc: "Complete the Python fundamentals path." },
  { icon: "🎯", title: "Interview Ready", desc: "Complete interview preparation milestones." },
];

export default function Badges() {
  return (
    <section className="ct-section">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <h2 className="ct-h2">Make progress feel rewarding.</h2>
        </div>

        <div className="ct-badges__grid">
          {BADGES.map((b) => (
            <div className="ct-card ct-badge" key={b.title}>
              <span className="ct-badge__icon">{b.icon}</span>
              <h3>{b.title}</h3>
              <p>{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
