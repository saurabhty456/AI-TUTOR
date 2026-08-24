import "./Features.css";

const FEATURES = [
  {
    file: "tutor.ts",
    icon: "💬",
    title: "AI Tutor",
    desc: "Ask about any concept, algorithm, or bug. The tutor explains the reasoning, not just the fix.",
  },
  {
    file: "quiz.ts",
    icon: "✅",
    title: "AI Quizzes",
    desc: "Test yourself on Python, JavaScript, Java, and DSA topics, with scores after every attempt.",
  },
  {
    file: "progress.ts",
    icon: "📈",
    title: "Progress Tracking",
    desc: "See completed topics, quiz history, and how your skills are building over time.",
  },
  {
    file: "interview.ts",
    icon: "🎯",
    title: "Interview Preparation",
    desc: "Practice real technical interview questions asked by major companies, with AI-led mock rounds.",
  },
  {
    file: "playlists.ts",
    icon: "🧭",
    title: "Learning Playlists",
    desc: "Follow structured paths like Python → Basics → Functions → OOP → DSA, in the right order.",
  },
  {
    file: "badges.ts",
    icon: "🏅",
    title: "Badges & Achievements",
    desc: "Earn recognition as you finish playlists, quizzes, and learning milestones.",
  },
];

export default function Features() {
  return (
    <section className="ct-section" id="features">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <span className="ct-eyebrow">Everything in one workspace</span>
          <h2 className="ct-h2">Built like the tools you'll actually use</h2>
          <p className="ct-lede">
            One tutor, one workspace — for learning concepts, testing yourself, and getting
            interview-ready.
          </p>
        </div>

        <div className="ct-features__grid">
          {FEATURES.map((f) => (
            <div className="ct-tab-card ct-feature-card" key={f.title}>
              <div className="ct-tab-card__bar">
                <span className="ct-tab-card__dot" />
                <span className="ct-tab-card__filename">{f.file}</span>
              </div>
              <div className="ct-feature-card__body">
                <span className="ct-feature-card__icon">{f.icon}</span>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
