import type { QuizQuestionData } from "../data/quizData";
import ReactMarkdown from "react-markdown";
import "./QuizReview.css";

interface QuizReviewProps {
  questions: QuizQuestionData[];
  userAnswers: (number | null)[];
}

function QuizReview({ questions, userAnswers }: QuizReviewProps) {
  return (
    <div className="quiz-review">
      {questions.map((q, index) => {
        const userIndex = userAnswers[index];
        const isCorrect = userIndex === q.correctIndex;
        const isUnanswered = userIndex === null;

        return (
          <div className="quiz-review__item" key={`${q.id}-${index}`}>
            <div className="quiz-review__head">
              <span>Question {index + 1}</span>
              <span
                className={
                  isCorrect
                    ? "quiz-review__badge quiz-review__badge--correct"
                    : isUnanswered
                      ? "quiz-review__badge quiz-review__badge--unanswered"
                      : "quiz-review__badge quiz-review__badge--incorrect"
                }
              >
                {isCorrect ? "✓ Correct" : isUnanswered ? "— Unanswered" : "✗ Incorrect"}
              </span>
            </div>

            <div className="quiz-review__question">
              <ReactMarkdown
                components={{
                  pre: ({ children }) => (
                    <pre className="quiz-review__code">{children}</pre>
                  ),
                }}
              >
                {q.question}
              </ReactMarkdown>
            </div>

            {q.codeSnippet && !q.question.includes("```") && (
              <pre className="quiz-review__code">
                <code>{q.codeSnippet}</code>
              </pre>
            )}

            <div className="quiz-review__answers">
              <div>
                <span className="quiz-review__label">Your answer</span>
                <p
                  className={
                    isUnanswered
                      ? "quiz-review__answer-text quiz-review__answer-text--unanswered"
                      : isCorrect
                      ? "quiz-review__answer-text quiz-review__answer-text--correct"
                      : "quiz-review__answer-text quiz-review__answer-text--incorrect"
                  }
                >
                  {userIndex !== null ? q.options[userIndex] : "No answer provided"}
                </p>
              </div>
              <div>
                <span className="quiz-review__label">Correct answer</span>
                <p className="quiz-review__answer-text quiz-review__answer-text--correct">
                  {q.options[q.correctIndex]}
                </p>
              </div>
            </div>

            <div className="quiz-review__explanation">
              <span className="quiz-review__label">Explanation</span>
              <p>{q.explanation}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default QuizReview;
