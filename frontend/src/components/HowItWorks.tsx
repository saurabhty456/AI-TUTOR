import "./HowItWorks.css";

const STEPS = [
  { cmd: "ask", title: "Ask", desc: "Post a question or paste code that's not working." },
  { cmd: "learn", title: "Learn", desc: "Get a clear, step-by-step explanation from your tutor." },
  { cmd: "practice", title: "Practice", desc: "Reinforce it with a quiz or a mock interview question." },
  { cmd: "improve", title: "Improve", desc: "Track the result and move to the next topic." },
];

export default function HowItWorks() {
  return (
    <section className="ct-section ct-section--tight" id="how-it-works">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <span className="ct-eyebrow">The loop</span>
          <h2 className="ct-h2">One command chain, repeated until it clicks</h2>
        </div>

        <div className="ct-tab-card ct-pipeline">
          <div className="ct-tab-card__bar">
            <span className="ct-tab-card__dot" />
            <span className="ct-tab-card__filename">learning-loop.sh</span>
          </div>
          <div className="ct-pipeline__body">
            {STEPS.map((step, i) => (
              <div className="ct-pipeline__step" key={step.cmd}>
                <div className="ct-pipeline__cmd">
                  <span className="ct-tok-fn">{step.cmd}</span>
                  <span className="ct-pipeline__title">{step.title}</span>
                </div>
                <p>{step.desc}</p>
                {i < STEPS.length - 1 && <span className="ct-pipeline__pipe">|</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
