const OPTIONS = ["O(n)", "O(log n)", "O(n²)", "O(1)"];

export default function QuizPreview() {
  return (
    <section className="ct-section ct-section--muted">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <h2 className="ct-h2">Turn learning into practice.</h2>
        </div>

        <div className="ct-quiz">
          <div className="ct-card ct-quiz__card">
            <span className="ct-quiz__label">Binary Search Quiz</span>
            <p className="ct-quiz__question">
              What is the time complexity of binary search?
            </p>
            <div className="ct-quiz__options">
              {OPTIONS.map((opt, i) => (
                <button
                  type="button"
                  key={opt}
                  className={`ct-quiz__option ${i === 1 ? "ct-quiz__option--correct" : ""}`}
                  disabled
                >
                  {opt}
                </button>
              ))}
            </div>
          </div>

          <div className="ct-card ct-quiz__result">
            <span className="ct-quiz__label">Score</span>
            <div className="ct-quiz__result-value">
              <span className="ct-quiz__result-number">8 / 10</span>
              <span className="ct-quiz__result-pct">80%</span>
            </div>
            <p className="ct-quiz__result-msg">Great job! Keep practicing.</p>
            <a className="ct-btn ct-btn--primary" href="#get-started">
              Take a Quiz
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
