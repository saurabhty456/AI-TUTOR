import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  TOPICS,
  formatTime,
  generateQuizQuestions,
  getTopicById,
  type Difficulty,
  type QuizConfig,
  type QuizQuestionData,
  type QuizResult,
  type Topic,
} from "../data/quizData";
import TopicSelection from "./TopicSelection";
import QuizSetup from "./QuizSetup";
import QuizQuestion from "./QuizQuestion";
import "./QuizPage.css";

type Phase = "topics" | "setup" | "quiz";

interface RetakeState {
  retakeConfig: {
    topicId: string;
    difficulty: Difficulty;
    questionCount: number;
    timerMinutes: number;
  };
}

function QuizPage() {
  const navigate = useNavigate();
  const location = useLocation();

  const [phase, setPhase] = useState<Phase>("topics");
  const [selectedTopic, setSelectedTopic] = useState<Topic | null>(null);
  const [config, setConfig] = useState<QuizConfig | null>(null);
  const [questions, setQuestions] = useState<QuizQuestionData[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<(number | null)[]>([]);
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);

  const quizStartRef = useRef<number>(Date.now());
  const hasHandledRetake = useRef(false);

  // Handle a "Retake Quiz" navigation from the score page — jump straight
  // into a fresh quiz for the same topic/settings, skipping setup.
  useEffect(() => {
    if (hasHandledRetake.current) return;
    const state = location.state as RetakeState | null;
    if (state?.retakeConfig) {
      hasHandledRetake.current = true;
      const { topicId, difficulty, questionCount, timerMinutes } =
        state.retakeConfig;
      const topic = getTopicById(topicId);
      if (topic) {
        beginQuiz(topic, {
          difficulty,
          questionCount: questionCount as QuizConfig["questionCount"],
          timerMinutes: timerMinutes as QuizConfig["timerMinutes"],
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state]);

  // Countdown timer — only runs while in the quiz phase with a timer set.
  useEffect(() => {
    if (phase !== "quiz" || timeRemaining === null) return;

    if (timeRemaining <= 0) {
      finishQuiz();
      return;
    }

    const id = window.setTimeout(() => {
      setTimeRemaining((t) => (t !== null ? t - 1 : null));
    }, 1000);

    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phase, timeRemaining]);

  function beginQuiz(topic: Topic, quizConfig: QuizConfig) {
    const generated = generateQuizQuestions(
      topic,
      quizConfig.difficulty,
      quizConfig.questionCount
    );
    setSelectedTopic(topic);
    setConfig(quizConfig);
    setQuestions(generated);
    setUserAnswers(new Array(generated.length).fill(null));
    setCurrentIndex(0);
    setTimeRemaining(
      quizConfig.timerMinutes > 0 ? quizConfig.timerMinutes * 60 : null
    );
    quizStartRef.current = Date.now();
    setPhase("quiz");
  }

  function handleSelectTopic(topic: Topic) {
    setSelectedTopic(topic);
    setPhase("setup");
  }

  function handleBackToTopics() {
    setSelectedTopic(null);
    setPhase("topics");
  }

  function handleSelectAnswer(index: number) {
    if (userAnswers[currentIndex] !== null) return;
    const next = [...userAnswers];
    next[currentIndex] = index;
    setUserAnswers(next);
  }

  function handlePrev() {
    setCurrentIndex((i) => Math.max(0, i - 1));
  }

  function handleNext() {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((i) => i + 1);
    } else {
      finishQuiz();
    }
  }

  function handleJumpTo(index: number) {
    setCurrentIndex(index);
  }

  function handleExitQuiz() {
    const confirmed = window.confirm(
      "Are you sure you want to exit? Your progress will be lost."
    );
    if (confirmed) {
      setPhase("topics");
      setSelectedTopic(null);
      setConfig(null);
      setQuestions([]);
      setUserAnswers([]);
      setTimeRemaining(null);
    }
  }

  function finishQuiz() {
    if (!selectedTopic || !config) return;

    const score = userAnswers.reduce<number>((total, answer, i) => {
      return answer === questions[i]?.correctIndex ? total + 1 : total;
    }, 0);

    const timeTakenSeconds =
      config.timerMinutes > 0
        ? config.timerMinutes * 60 - (timeRemaining ?? 0)
        : Math.round((Date.now() - quizStartRef.current) / 1000);

    const result: QuizResult = {
      topicId: selectedTopic.id,
      topicName: selectedTopic.name,
      difficulty: config.difficulty,
      timerMinutes: config.timerMinutes,
      questions,
      userAnswers,
      score,
      total: questions.length,
      timeTakenSeconds,
      completedAt: new Date().toISOString(),
    };

    navigate("/score", { state: result });
  }

  if (phase === "topics") {
    return (
      <div className="quiz-app">
        <TopicSelection topics={TOPICS} onSelectTopic={handleSelectTopic} />
      </div>
    );
  }

  if (phase === "setup" && selectedTopic) {
    return (
      <div className="quiz-app">
        <QuizSetup
          topic={selectedTopic}
          onStart={(cfg) => beginQuiz(selectedTopic, cfg)}
          onBack={handleBackToTopics}
        />
      </div>
    );
  }

  // phase === "quiz"
  if (!selectedTopic || !config || questions.length === 0) {
    return (
      <div className="quiz-app">
        <TopicSelection topics={TOPICS} onSelectTopic={handleSelectTopic} />
      </div>
    );
  }

  const progressPct = ((currentIndex + 1) / questions.length) * 100;
  const isTimerLow = timeRemaining !== null && timeRemaining <= 60;

  return (
    <div className="quiz-app">
      <div className="quiz-runner">
        <header className="quiz-runner__header">
          <div className="quiz-runner__header-top">
            <a className="quiz-runner__brand" href="/">
              <span className="quiz-runner__mark">CT</span>
              CodeTutor
            </a>

            <div className="quiz-runner__meta">
              <span className="quiz-runner__topic">{selectedTopic.name}</span>
              <span className="quiz-runner__difficulty">
                {config.difficulty}
              </span>
            </div>

            <button
              type="button"
              className="quiz-runner__exit"
              onClick={handleExitQuiz}
            >
              Exit Quiz
            </button>
          </div>

          <div className="quiz-runner__progress-row">
            <span className="quiz-runner__progress-label">
              Question {currentIndex + 1} of {questions.length}
            </span>

            <div className="quiz-runner__progress-bar">
              <div
                className="quiz-runner__progress-fill"
                style={{ width: `${progressPct}%` }}
              />
            </div>

            {timeRemaining !== null && (
              <span
                className={`quiz-runner__timer ${
                  isTimerLow ? "quiz-runner__timer--warning" : ""
                }`}
              >
                Timer: {formatTime(timeRemaining)}
              </span>
            )}
          </div>
        </header>

        <div className="quiz-runner__body">
          <main className="quiz-runner__main">
            <QuizQuestion
              key={currentIndex}
              question={questions[currentIndex]}
              questionNumber={currentIndex + 1}
              totalQuestions={questions.length}
              selectedIndex={userAnswers[currentIndex]}
              onSelect={handleSelectAnswer}
            />

            <div className="quiz-runner__controls">
              <button
                type="button"
                className="quiz-runner__nav-btn"
                onClick={handlePrev}
                disabled={currentIndex === 0}
              >
                ← Previous
              </button>

              <button
                type="button"
                className="quiz-runner__nav-btn quiz-runner__nav-btn--primary"
                onClick={handleNext}
                disabled={userAnswers[currentIndex] === null}
              >
                {currentIndex === questions.length - 1
                  ? "Finish Quiz"
                  : "Next Question →"}
              </button>
            </div>
          </main>

          <aside className="quiz-runner__navigator" aria-label="Question navigator">
            <span className="quiz-runner__navigator-label">Questions</span>
            <div className="quiz-runner__navigator-grid">
              {questions.map((_, index) => {
                const isAnswered = userAnswers[index] !== null;
                const isCurrent = index === currentIndex;
                return (
                  <button
                    key={index}
                    type="button"
                    className={`quiz-runner__nav-dot ${
                      isCurrent ? "quiz-runner__nav-dot--current" : ""
                    } ${isAnswered ? "quiz-runner__nav-dot--answered" : ""}`}
                    onClick={() => handleJumpTo(index)}
                    aria-current={isCurrent}
                    aria-label={`Question ${index + 1}${
                      isAnswered ? ", answered" : ", unanswered"
                    }`}
                  >
                    {isAnswered && !isCurrent ? "✓" : index + 1}
                  </button>
                );
              })}
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}

export default QuizPage;
