const PATHS = [
  {
    title: "Python Fundamentals",
    progress: 68,
    done: ["Variables", "Conditions", "Loops", "Functions"],
    todo: ["Object-Oriented Programming", "Data Structures"],
  },
  {
    title: "Data Structures & Algorithms",
    progress: 42,
    done: ["Arrays", "Strings", "Linked Lists"],
    todo: ["Stacks & Queues", "Trees", "Graphs"],
  },
];

export default function LearningPaths() {
  return (
    <section className="ct-section" id="learning-paths">
      <div className="ct-container">
        <div className="ct-section-head ct-section-head--center">
          <h2 className="ct-h2">Structured learning paths, start to finish</h2>
          <p className="ct-lede">
            Follow a clear sequence of topics and always know exactly where you
            left off.
          </p>
        </div>

        <div className="ct-paths__grid">
          {PATHS.map((path) => (
            <div className="ct-card ct-path-card" key={path.title}>
              <div className="ct-path-card__head">
                <h3>{path.title}</h3>
                <span className="ct-path-card__pct">{path.progress}%</span>
              </div>

              <div className="ct-path-card__bar">
                <div
                  className="ct-path-card__bar-fill"
                  style={{ width: `${path.progress}%` }}
                />
              </div>

              <ul className="ct-path-card__list">
                {path.done.map((item) => (
                  <li key={item} className="ct-path-card__item ct-path-card__item--done">
                    <span>✓</span> {item}
                  </li>
                ))}
                {path.todo.map((item) => (
                  <li key={item} className="ct-path-card__item">
                    <span>○</span> {item}
                  </li>
                ))}
              </ul>

              <a className="ct-btn ct-btn--secondary ct-path-card__btn" href="#get-started">
                Continue Learning
              </a>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
