const FEEDBACK = [
  { text: "Good problem decomposition", positive: true },
  { text: "Correct complexity analysis", positive: true },
  { text: "Explain edge cases more clearly", positive: false },
];

export default function AIInterview() {
  return (
    <section className="ct-section ct-section--muted">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <h2 className="ct-h2">Practice mock interviews with AI</h2>
        </div>

        <div className="ct-card ct-mock">
          <div className="ct-mock__chrome">
            <span className="ct-preview__dot" />
            <span className="ct-preview__dot" />
            <span className="ct-preview__dot" />
            <span className="ct-mock__chrome-title">AI Interviewer</span>
          </div>

          <div className="ct-mock__body">
            <p className="ct-mock__prompt">
              "Tell me how you would approach this problem."
            </p>

            <div className="ct-mock__answer-area" aria-hidden="true">
              Student response area
            </div>

            <button type="button" className="ct-btn ct-btn--primary" disabled>
              Submit Answer
            </button>

            <div className="ct-mock__feedback">
              <span className="ct-mock__feedback-label">AI Feedback</span>
              <ul>
                {FEEDBACK.map((f) => (
                  <li key={f.text} className={f.positive ? "ct-mock__feedback--good" : ""}>
                    <span>{f.positive ? "✓" : "○"}</span> {f.text}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
