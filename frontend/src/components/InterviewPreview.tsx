import "./InterviewPreview.css";

const COMPANIES = [
  {
    name: "Amazon",
    tag: "Leadership + coding",
    question: "Reverse a linked list in place — walk through your approach out loud.",
  },
  {
    name: "Google",
    tag: "Algorithms",
    question: "Given an array, find the longest increasing subsequence.",
  },
  {
    name: "Microsoft",
    tag: "System design basics",
    question: "How would you design a rate limiter for an API?",
  },
  {
    name: "Meta",
    tag: "Coding + behavioral",
    question: "Detect a cycle in a directed graph, then explain a time you debugged one.",
  },
];

export default function InterviewPreview() {
  return (
    <section className="ct-section ct-section--tight" id="interview-prep">
      <div className="ct-container">
        <div className="ct-section-head">
          <span className="ct-eyebrow">Interview preparation</span>
          <h2 className="ct-h2">Practice with questions companies actually ask</h2>
          <p className="ct-lede">
            Work through commonly reported questions, then switch to AI-led mock
            interviews that push back and follow up like a real interviewer would.
          </p>
        </div>

        <div className="ct-interview__grid">
          {COMPANIES.map((c) => (
            <div className="ct-tab-card ct-interview-card" key={c.name}>
              <div className="ct-tab-card__bar">
                <span className="ct-tab-card__dot" />
                <span className="ct-tab-card__filename">{c.name.toLowerCase()}.interview</span>
              </div>
              <div className="ct-interview-card__body">
                <div className="ct-interview-card__head">
                  <h3>{c.name}</h3>
                  <span className="ct-interview-card__tag">{c.tag}</span>
                </div>
                <p className="ct-tok-str">"{c.question}"</p>
              </div>
            </div>
          ))}
        </div>

        <a className="ct-interview__cta" href="#get-started">
          Start a mock interview →
        </a>
      </div>
    </section>
  );
}
