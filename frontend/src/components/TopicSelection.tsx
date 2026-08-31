import { Link } from "react-router-dom";
import type { Topic } from "../data/quizData";
import "./TopicSelection.css";

interface TopicSelectionProps {
  topics: Topic[];
  onSelectTopic: (topic: Topic) => void;
}

function TopicSelection({ topics, onSelectTopic }: TopicSelectionProps) {
  return (
    <div className="topic-selection">
      <div className="topic-selection__header">
        <Link to="/" className="topic-selection__back">
          ← Back to Home
        </Link>
        <h1>Test Your Programming Skills</h1>
        <p>
          Pick a topic to start a quiz. Choose your difficulty and question
          count next, then track your score and review every answer
          afterward.
        </p>
      </div>

      <div className="topic-grid">
        {topics.map((topic) => (
          <div className="topic-card" key={topic.id}>
            <span className="topic-card__icon" aria-hidden="true">
              {topic.icon}
            </span>
            <h3>{topic.name}</h3>
            <p>{topic.description}</p>

            <div className="topic-card__meta">
              <span>{topic.questions.length} Questions</span>
              <span className="topic-card__dot" aria-hidden="true">
                •
              </span>
              <span>Easy · Medium · Hard</span>
            </div>

            <button
              type="button"
              className="topic-card__btn"
              onClick={() => onSelectTopic(topic)}
            >
              Start Quiz
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TopicSelection;
