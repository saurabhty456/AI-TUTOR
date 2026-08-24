import "./Hero.css";

export default function Hero() {
  return (
    <section className="ct-hero" id="top">
      <div className="ct-container ct-hero__inner">
        <div className="ct-hero__copy">
          <span className="ct-eyebrow">AI programming tutor, always on</span>
          <h1 className="ct-hero__headline">
            Master programming with <span>your AI tutor</span>
          </h1>
          <p className="ct-hero__sub">
            Ask questions, work through algorithms, and debug real code with an AI
            that explains its reasoning. Then put it to the test — quizzes,
            interview practice, and a learning path that tracks every step forward.
          </p>
          <div className="ct-hero__actions">
            <a className="ct-btn ct-btn--primary" href="#get-started">
              Start learning
            </a>
            <a className="ct-btn ct-btn--ghost" href="#features">
              Explore features
            </a>
          </div>

          <dl className="ct-hero__stats">
            <div>
              <dt>Topics covered</dt>
              <dd>Python · JS · Java · DSA</dd>
            </div>
            <div>
              <dt>Practice mode</dt>
              <dd>Quizzes + mock interviews</dd>
            </div>
            <div>
              <dt>Always visible</dt>
              <dd>Progress, streaks, badges</dd>
            </div>
          </dl>
        </div>

        <div className="ct-hero__visual" aria-hidden="true">
          <div className="ct-tab-card ct-editor">
            <div className="ct-tab-card__bar">
              <span className="ct-tab-card__dot" style={{ background: "#f5a3a3" }} />
              <span className="ct-tab-card__dot" style={{ background: "#f5d68e" }} />
              <span className="ct-tab-card__dot" style={{ background: "#8ee6b0" }} />
              <span className="ct-tab-card__filename">tutor-session.py — CodeTutor</span>
            </div>

            <div className="ct-editor__body">
              <div className="ct-editor__gutter">
                {Array.from({ length: 12 }, (_, i) => (
                  <span key={i}>{i + 1}</span>
                ))}
              </div>

              <div className="ct-editor__code">
                <p className="ct-editor__line">
                  <span className="ct-tok-comment"># you asked:</span>
                </p>
                <p className="ct-editor__line ct-editor__msg ct-editor__msg--user">
                  "Why is my recursive fibonacci so slow?"
                </p>
                <p className="ct-editor__line">&nbsp;</p>
                <p className="ct-editor__line">
                  <span className="ct-tok-comment"># tutor:</span>
                </p>
                <p className="ct-editor__line ct-editor__msg ct-editor__msg--ai">
                  <span className="ct-tok-key">def</span> explain():
                </p>
                <p className="ct-editor__line ct-editor__msg ct-editor__msg--ai ct-indent">
                  <span className="ct-tok-str">"You're recomputing the same calls."</span>
                </p>
                <p className="ct-editor__line ct-editor__msg ct-editor__msg--ai ct-indent">
                  <span className="ct-tok-key">return</span> <span className="ct-tok-fn">memoize</span>(fib)
                </p>
                <p className="ct-editor__line">&nbsp;</p>
                <p className="ct-editor__line ct-editor__typing">
                  <span className="ct-tok-comment"># typing…</span>
                </p>
              </div>
            </div>
          </div>

          <div className="ct-hero__floatcard ct-hero__floatcard--score">
            <span className="ct-hero__floatcard-label">Quiz score</span>
            <span className="ct-hero__floatcard-value">92%</span>
          </div>
          <div className="ct-hero__floatcard ct-hero__floatcard--badge">
            <span>🏅</span>
            <span>DSA Level 2 unlocked</span>
          </div>
        </div>
      </div>
    </section>
  );
}
