const FEATURES = [
  {
    icon: "💬",
    title: "AI Programming Tutor",
    desc: "Get clear explanations for programming concepts, algorithms, debugging and code.",
  },
  {
    icon: "✅",
    title: "AI-Powered Quizzes",
    desc: "Test your understanding with topic-based quizzes and instant results.",
  },
  {
    icon: "📈",
    title: "Progress Tracking",
    desc: "Track your scores, completed topics and overall learning progress.",
  },
  {
    icon: "🎯",
    title: "Interview Preparation",
    desc: "Practice commonly reported technical interview questions and prepare with AI.",
  },
  {
    icon: "🧭",
    title: "Learning Playlists",
    desc: "Follow structured learning paths from fundamentals to advanced topics.",
  },
  {
    icon: "🏅",
    title: "Badges & Achievements",
    desc: "Earn badges as you complete quizzes, playlists and learning milestones.",
  },
];

export default function Features() {
  return (
    <section className="ct-section" id="features">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <h2 className="ct-h2">One platform. Every step of your learning journey.</h2>
        </div>

        <div className="ct-features__grid">
          {FEATURES.map((f) => (
            <div className="ct-card ct-feature-card" key={f.title}>
              <span className="ct-feature-card__icon">{f.icon}</span>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
