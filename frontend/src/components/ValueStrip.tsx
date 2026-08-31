const VALUES = [
  "AI-powered learning",
  "Topic-based quizzes",
  "Interview preparation",
  "Progress tracking",
];

export default function ValueStrip() {
  return (
    <section className="ct-value">
      <div className="ct-container ct-value__inner">
        <p className="ct-value__heading">
          Everything you need to become a better programmer
        </p>
        <ul className="ct-value__list">
          {VALUES.map((v) => (
            <li key={v}>{v}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
