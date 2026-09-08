import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  formatTime,
  getPerformanceMessage,
  type QuizResult,
} from "./data/quizData";
import QuizReview from "./components/QuizReview";
import "./ScorePage.css";

function ScorePage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [reviewOpen, setReviewOpen] = useState(false);

  const result = location.state as (QuizResult & { saveError?: string }) | null;

  if (
    !result ||
    !Array.isArray(result.questions) ||
    !Array.isArray(result.userAnswers) ||
    result.questions.length !== result.userAnswers.length
  ) {
    return (
      <div className="score-page">
        <div className="score-page__empty">
          <h2>No quiz result to show</h2>
          <p>Take a quiz first and your results will appear here.</p>
          <Link to="/quiz" className="score-page__btn score-page__btn--primary">
            Go to Quiz
          </Link>
        </div>
      </div>
    );
  }

  const correct = result.questions.reduce(
    (count, question, index) =>
      result.userAnswers[index] === question.correctIndex ? count + 1 : count,
    0
  );
  const unanswered = result.userAnswers.filter((answer) => answer === null).length;
  const incorrect = result.total - correct - unanswered;
  const percentage = result.total === 0 ? 0 : Math.round((correct / result.total) * 100);

  const handleRetake = () => {
    navigate("/quiz", {
      state: {
        retakeConfig: {
          topicId: result.topicId,
          difficulty: result.difficulty,
          questionCount: result.total,
          timerMinutes: result.timerMinutes,
        },
      },
    });
  };

  const handleChooseAnotherTopic = () => {
    navigate("/quiz");
  };

  return (
    <div className="score-page">
      <div className="score-page__card">
        {result.saveError && (
          <div className="score-page__alert" role="status">
            {result.saveError}
          </div>
        )}
        <span className="score-page__eyebrow">Quiz Complete!</span>
        <h1>{result.topicName}</h1>
        <span className="score-page__difficulty">{result.difficulty}</span>

        <div className="score-page__ring-wrap">
          <div
            className="score-page__ring"
            style={{
              background: `conic-gradient(var(--sp-accent) ${percentage}%, var(--sp-surface-2) ${percentage}% 100%)`,
            }}
          >
            <div className="score-page__ring-inner">
              <span className="score-page__pct">{percentage}%</span>
              <span className="score-page__fraction">
                {correct} / {result.total}
              </span>
            </div>
          </div>
        </div>

        <p className="score-page__message">
          {getPerformanceMessage(percentage)}
        </p>

        <div className="score-page__stats">
          <div className="score-page__stat">
            <span className="score-page__stat-value score-page__stat-value--correct">
              {correct}
            </span>
            <span className="score-page__stat-label">Correct Answers</span>
          </div>
          <div className="score-page__stat">
            <span className="score-page__stat-value score-page__stat-value--incorrect">
              {incorrect}
            </span>
            <span className="score-page__stat-label">Incorrect Answers</span>
          </div>
          <div className="score-page__stat">
            <span className="score-page__stat-value score-page__stat-value--unanswered">
              {unanswered}
            </span>
            <span className="score-page__stat-label">Unanswered</span>
          </div>
          <div className="score-page__stat">
            <span className="score-page__stat-value">{percentage}%</span>
            <span className="score-page__stat-label">Accuracy</span>
          </div>
          <div className="score-page__stat">
            <span className="score-page__stat-value">
              {formatTime(result.timeTakenSeconds)}
            </span>
            <span className="score-page__stat-label">Time Taken</span>
          </div>
        </div>

        <div className="score-page__actions">
          <button
            type="button"
            className="score-page__btn score-page__btn--secondary"
            onClick={() => setReviewOpen((open) => !open)}
          >
            {reviewOpen ? "Hide Review" : "Review Answers"}
          </button>
          <button
            type="button"
            className="score-page__btn score-page__btn--secondary"
            onClick={handleRetake}
          >
            Retake Quiz
          </button>
          <button
            type="button"
            className="score-page__btn score-page__btn--secondary"
            onClick={handleChooseAnotherTopic}
          >
            Choose Another Topic
          </button>
          <Link to="/" className="score-page__btn score-page__btn--primary">
            Back to Home
          </Link>
        </div>

        {reviewOpen && (
          <QuizReview
            questions={result.questions}
            userAnswers={result.userAnswers}
          />
        )}
      </div>
    </div>
  );
}

export default ScorePage;
