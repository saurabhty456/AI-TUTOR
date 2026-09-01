import { useState } from "react";
import type {
  Difficulty,
  QuestionCount,
  QuizConfig,
  Topic,
  TimerMinutes,
} from "../data/quizData";
import "./QuizSetup.css";

interface QuizSetupProps {
  topic: Topic;
  onStart: (config: QuizConfig) => void;
  onBack: () => void;
  isLoading?: boolean;
  errorMessage?: string | null;
}

const DIFFICULTIES: Difficulty[] = ["Easy", "Medium", "Hard"];
const QUESTION_COUNTS: QuestionCount[] = [5, 10, 15];
const TIMER_OPTIONS: { label: string; value: TimerMinutes }[] = [
  { label: "No Timer", value: 0 },
  { label: "10 minutes", value: 10 },
  { label: "15 minutes", value: 15 },
  { label: "20 minutes", value: 20 },
];

function QuizSetup({
  topic,
  onStart,
  onBack,
  isLoading = false,
  errorMessage,
}: QuizSetupProps) {
  const [difficulty, setDifficulty] = useState<Difficulty>("Medium");
  const [questionCount, setQuestionCount] = useState<QuestionCount>(10);
  const [timerMinutes, setTimerMinutes] = useState<TimerMinutes>(0);

  return (
    <div className="quiz-setup">
      <div className="quiz-setup__card">
        <button type="button" className="quiz-setup__back" onClick={onBack}>
          ← Choose a different topic
        </button>

        <span className="quiz-setup__icon" aria-hidden="true">
          {topic.icon}
        </span>
        <h2>{topic.name}</h2>
        <p className="quiz-setup__desc">{topic.description}</p>

        <div className="quiz-setup__group">
          <span className="quiz-setup__label">Difficulty</span>
          <div className="quiz-setup__options">
            {DIFFICULTIES.map((d) => (
              <button
                key={d}
                type="button"
                className={`quiz-setup__pill ${
                  difficulty === d ? "quiz-setup__pill--active" : ""
                }`}
                onClick={() => setDifficulty(d)}
                aria-pressed={difficulty === d}
              >
                {d}
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-setup__group">
          <span className="quiz-setup__label">Number of Questions</span>
          <div className="quiz-setup__options">
            {QUESTION_COUNTS.map((c) => (
              <button
                key={c}
                type="button"
                className={`quiz-setup__pill ${
                  questionCount === c ? "quiz-setup__pill--active" : ""
                }`}
                onClick={() => setQuestionCount(c)}
                aria-pressed={questionCount === c}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="quiz-setup__group">
          <span className="quiz-setup__label">Timer</span>
          <div className="quiz-setup__options">
            {TIMER_OPTIONS.map((t) => (
              <button
                key={t.value}
                type="button"
                className={`quiz-setup__pill ${
                  timerMinutes === t.value ? "quiz-setup__pill--active" : ""
                }`}
                onClick={() => setTimerMinutes(t.value)}
                aria-pressed={timerMinutes === t.value}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {errorMessage && (
          <p className="quiz-setup__error" role="alert">
            {errorMessage}
          </p>
        )}

        <button
          type="button"
          className="quiz-setup__start-btn"
          onClick={() => onStart({ difficulty, questionCount, timerMinutes })}
          disabled={isLoading}
        >
          {isLoading ? "Generating Quiz..." : "Start Quiz"}
        </button>
      </div>
    </div>
  );
}

export default QuizSetup;
