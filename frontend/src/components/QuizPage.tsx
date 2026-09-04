import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  TOPICS,
  formatTime,
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

type Phase = "topics" | "setup" | "loading" | "quiz";

interface RetakeState {
  retakeConfig: {
    topicId: string;
    difficulty: Difficulty;
    questionCount: number;
    timerMinutes: number;
  };
}

interface ApiQuizQuestion {
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
}

function normalizeDifficulty(value: string): Difficulty {
  const normalized = value.toLowerCase();
  if (normalized === "easy") return "Easy";
  if (normalized === "hard") return "Hard";
  return "Medium";
}

function mapApiQuestions(
  questions: ApiQuizQuestion[],
  difficulty: Difficulty,
  topicId: string
): QuizQuestionData[] {
  return questions.map((question, index) => {
    const cleanedQuestion = question.question.trim();

    return {
      id: `${topicId}-${difficulty.toLowerCase()}-${index}-${cleanedQuestion
        .slice(0, 24)
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")}`,
      question: cleanedQuestion,
      options: question.options,
      correctIndex: question.correctIndex,
      explanation: question.explanation,
      difficulty,
    };
  });
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
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [submitDialogOpen, setSubmitDialogOpen] = useState(false);

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

  async function beginQuiz(topic: Topic, quizConfig: QuizConfig) {
    if (isGenerating) return;

    setGenerationError(null);
    setSelectedTopic(topic);
    setConfig(quizConfig);
    setCurrentIndex(0);
    setQuestions([]);
    setUserAnswers([]);
    setTimeRemaining(
      quizConfig.timerMinutes > 0 ? quizConfig.timerMinutes * 60 : null
    );
    setPhase("loading");
    setIsGenerating(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/quiz/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic.name,
          difficulty: quizConfig.difficulty.toLowerCase(),
          number_of_questions: quizConfig.questionCount,
        }),
      });

      if (!response.ok) {
        let message = "We couldn’t generate the quiz right now. Please try again.";

        try {
          const payload = await response.json();
          if (typeof payload?.detail === "string" && payload.detail.trim()) {
            message = payload.detail;
          }
        } catch {
          // Ignore malformed error payloads and fall back to the generic message.
        }

        throw new Error(message);
      }

      const data = (await response.json()) as {
        topic?: string;
        difficulty?: string;
        number_of_questions?: number;
        questions?: ApiQuizQuestion[];
      };

      const generatedQuestions = mapApiQuestions(
        data.questions ?? [],
        normalizeDifficulty(data.difficulty ?? quizConfig.difficulty),
        topic.id
      );

      if (generatedQuestions.length === 0) {
        throw new Error("The quiz generator returned no questions. Please try again.");
      }

      setQuestions(generatedQuestions);
      setUserAnswers(new Array(generatedQuestions.length).fill(null));
      setCurrentIndex(0);
      setTimeRemaining(
        quizConfig.timerMinutes > 0 ? quizConfig.timerMinutes * 60 : null
      );
      quizStartRef.current = Date.now();
      setPhase("quiz");
    } catch (error) {
      const message =
        error instanceof Error && error.message
          ? error.message
          : "We couldn’t generate the quiz right now. Please try again.";

      setGenerationError(message);
      setSelectedTopic(topic);
      setConfig(null);
      setQuestions([]);
      setUserAnswers([]);
      setCurrentIndex(0);
      setTimeRemaining(null);
      setPhase("setup");
    } finally {
      setIsGenerating(false);
    }
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
      setSubmitDialogOpen(true);
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
      setGenerationError(null);
      setPhase("topics");
      setSelectedTopic(null);
      setConfig(null);
      setQuestions([]);
      setUserAnswers([]);
      setTimeRemaining(null);
      setIsGenerating(false);
      setSubmitDialogOpen(false);
    }
  }

  function finishQuiz() {
    if (!selectedTopic || !config) return;

    const score = userAnswers.reduce<number>((total, answer, i) => {
      return answer === questions[i]?.correctIndex ? total + 1 : total;
    }, 0);
    const unanswered = userAnswers.filter((answer) => answer === null).length;
    const percentage = Math.round((score / questions.length) * 100);

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
      percentage,
      unanswered,
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
          isLoading={isGenerating}
          errorMessage={generationError}
        />
      </div>
    );
  }

  if (phase === "loading" && selectedTopic) {
    return (
      <div className="quiz-app">
        <div className="quiz-loading" aria-live="polite">
          <div className="quiz-loading__card">
            <div className="quiz-loading__spinner" aria-hidden="true" />
            <h2>Generating your quiz...</h2>
            <p>
              We’re creating a personalized {selectedTopic.name} quiz for you.
            </p>
          </div>
        </div>
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
              >
                {currentIndex === questions.length - 1
                  ? "Submit Quiz"
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

        {submitDialogOpen && (
          <div className="quiz-submit-dialog" role="presentation">
            <div
              className="quiz-submit-dialog__backdrop"
              onClick={() => setSubmitDialogOpen(false)}
            />
            <section
              className="quiz-submit-dialog__content"
              role="dialog"
              aria-modal="true"
              aria-labelledby="quiz-submit-title"
            >
              <h2 id="quiz-submit-title">Submit your quiz?</h2>
              <p className="quiz-submit-dialog__summary">
                You have answered {userAnswers.filter((answer) => answer !== null).length} of {questions.length} questions.
              </p>
              <div className="quiz-submit-dialog__counts">
                <span>Answered <strong>{userAnswers.filter((answer) => answer !== null).length}</strong></span>
                <span>Unanswered <strong>{userAnswers.filter((answer) => answer === null).length}</strong></span>
              </div>
              <div className="quiz-submit-dialog__actions">
                <button
                  type="button"
                  className="quiz-runner__nav-btn"
                  onClick={() => setSubmitDialogOpen(false)}
                >
                  Continue Quiz
                </button>
                <button
                  type="button"
                  className="quiz-runner__nav-btn quiz-runner__nav-btn--primary"
                  onClick={finishQuiz}
                >
                  Submit Quiz
                </button>
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

export default QuizPage;
