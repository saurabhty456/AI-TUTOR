const STEPS = [
  {
    number: "01",
    title: "ASK",
    desc: "Ask your AI tutor anything about programming.",
  },
  {
    number: "02",
    title: "LEARN",
    desc: "Understand the concept through clear explanations and examples.",
  },
  {
    number: "03",
    title: "PRACTICE",
    desc: "Take quizzes and solve interview questions.",
  },
  {
    number: "04",
    title: "MASTER",
    desc: "Track your progress and complete learning paths.",
  },
];

export default function HowItWorks() {
  return (
    <section className="ct-section ct-section--muted" id="how-it-works">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <h2 className="ct-h2">Learn. Practice. Improve.</h2>
        </div>

        <div className="ct-steps">
          {STEPS.map((step) => (
            <div className="ct-step" key={step.number}>
              <span className="ct-step__number">{step.number}</span>
              <h3 className="ct-step__title">{step.title}</h3>
              <p>{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
