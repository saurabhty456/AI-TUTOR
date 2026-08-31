export default function Hero() {
  return (
    <section className="ct-hero" id="top">
      <div className="ct-container ct-hero__grid">
        <div className="ct-hero__copy">
          <h1 className="ct-hero__headline">
            Master Programming with Your <span>AI Tutor</span>
          </h1>
          <p className="ct-hero__sub">
            Learn programming concepts, practice with AI-powered quizzes, prepare
            for technical interviews, and track your progress — all in one place.
          </p>
          <div className="ct-hero__actions">
            <a className="ct-btn ct-btn--primary" href="/chat">
  Start Learning
</a>
<a className="ct-btn ct-btn--secondary" href="/quiz">
  Take a Quiz
</a>
            <a className="ct-btn ct-btn--secondary" href="#features">
              Explore Features
            </a>
          </div>
        </div>

        <div className="ct-hero__preview" aria-hidden="true">
          <div className="ct-preview">
            <div className="ct-preview__chrome">
              <span className="ct-preview__dot" />
              <span className="ct-preview__dot" />
              <span className="ct-preview__dot" />
              <span className="ct-preview__title">AI Tutor</span>
            </div>

            <div className="ct-preview__chat">
              <div className="ct-preview__bubble ct-preview__bubble--user">
                Explain binary search in simple terms.
              </div>
              <div className="ct-preview__bubble ct-preview__bubble--ai">
                Binary search is an efficient way to find an item in a sorted
                list by repeatedly dividing the search area in half.
              </div>
            </div>

            <div className="ct-preview__stats">
              <div className="ct-preview__stat">
                <span className="ct-preview__stat-label">Quiz Score</span>
                <span className="ct-preview__stat-value">8/10</span>
              </div>
              <div className="ct-preview__stat">
                <span className="ct-preview__stat-label">Progress</span>
                <span className="ct-preview__stat-value">68%</span>
              </div>
              <div className="ct-preview__stat">
                <span className="ct-preview__stat-label">Interview</span>
                <span className="ct-preview__stat-value">Ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
