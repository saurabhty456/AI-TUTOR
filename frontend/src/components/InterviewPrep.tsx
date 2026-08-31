const COMPANIES = [
  { name: "Amazon", topic: "Arrays & Strings", count: 12 },
  { name: "Google", topic: "Algorithms", count: 15 },
  { name: "Microsoft", topic: "Data Structures", count: 10 },
  { name: "Meta", topic: "Problem Solving", count: 14 },
];

export default function InterviewPrep() {
  return (
    <section className="ct-section" id="interview-prep">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <h2 className="ct-h2">Prepare for technical interviews.</h2>
          <p className="ct-lede">
            Practice with commonly reported interview topics and questions.
          </p>
        </div>

        <div className="ct-interview__grid">
          {COMPANIES.map((c) => (
            <div className="ct-card ct-interview-card" key={c.name}>
              <h3>{c.name}</h3>
              <p className="ct-interview-card__topic">{c.topic}</p>
              <span className="ct-interview-card__count">{c.count} Questions</span>
            </div>
          ))}
        </div>

        <div className="ct-interview__cta">
          <a className="ct-btn ct-btn--primary" href="#get-started">
            Practice with AI
          </a>
        </div>
      </div>
    </section>
  );
}
