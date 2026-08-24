import "./CTA.css";

export default function CTA() {
  return (
    <section className="ct-section ct-cta" id="get-started">
      <div className="ct-container ct-cta__inner">
        <span className="ct-eyebrow">Ready when you are</span>
        <h2 className="ct-h2">Ready to become a better programmer?</h2>
        <p className="ct-lede" style={{ margin: "16px auto 0" }}>
          Start with your AI tutor, then work your way through quizzes, playlists, and
          interview practice at your own pace.
        </p>
        <a className="ct-btn ct-btn--primary ct-cta__btn" href="#top">
          Start learning
        </a>
      </div>
    </section>
  );
}
