import ReactMarkdown from "react-markdown";
import type { QuizQuestionData } from "../data/quizData";
import "./QuizQuestion.css";

interface QuizQuestionProps {
  question: QuizQuestionData;
  questionNumber: number;
  totalQuestions: number;
  selectedIndex: number | null;
  onSelect: (index: number) => void;
}

const LETTERS = ["A", "B", "C", "D"];

function QuizQuestion({
  question,
  questionNumber,
  totalQuestions,
  selectedIndex,
  onSelect,
}: QuizQuestionProps) {
  const answered = selectedIndex !== null;
  const isCorrect = selectedIndex === question.correctIndex;

  const optionState = (index: number) => {
    if (!answered) return "";
    if (index === question.correctIndex) return "quiz-option--correct";
    if (index === selectedIndex) return "quiz-option--incorrect";
    return "quiz-option--muted";
  };

  return (
    <div className="quiz-question">
      <span className="quiz-question__counter">
        Question {questionNumber} of {totalQuestions}
      </span>

      <div className="quiz-question__text">
        <ReactMarkdown
          components={{
            pre: ({ children }) => (
              <pre className="quiz-question__code">{children}</pre>
            ),
          }}
        >
          {question.question}
        </ReactMarkdown>
      </div>

      {!question.question.includes("```") && question.codeSnippet && (
        <pre className="quiz-question__code">
          <code>{question.codeSnippet}</code>
        </pre>
      )}

      <div className="quiz-question__options" role="group" aria-label="Answer options">
        {question.options.map((option, index) => (
          <button
            key={option}
            type="button"
            className={`quiz-option ${optionState(index)}`}
            onClick={() => onSelect(index)}
            disabled={answered}
            aria-pressed={selectedIndex === index}
          >
            <span className="quiz-option__letter">{LETTERS[index]}</span>
            <span>{option}</span>
          </button>
        ))}
      </div>

      {answered && (
        <div
          className={`quiz-question__feedback ${
            isCorrect
              ? "quiz-question__feedback--correct"
              : "quiz-question__feedback--incorrect"
          }`}
          role="status"
        >
          <span className="quiz-question__feedback-title">
            {isCorrect ? "✓ Correct!" : "✗ Incorrect"}
          </span>
          <p>{question.explanation}</p>
        </div>
      )}
    </div>
  );
}

export default QuizQuestion;
