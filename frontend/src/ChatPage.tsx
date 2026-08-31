import { useState, type ReactNode } from "react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

import "katex/dist/katex.min.css";
import "./ChatPage.css";

type Message = {
  role: "user" | "model";
  content: string;
};

const SUGGESTED_QUESTIONS = [
  "Explain binary search",
  "Teach me recursion",
  "Help me debug this code",
  "Explain time complexity",
];

type CodeBlockProps = {
  className?: string;
  children?: ReactNode;
};

/*
 * ReactMarkdown no longer reliably provides the old `inline` prop.
 *
 * Therefore:
 * - Inline code: no language class + no newline
 * - Block code: language class OR multiline content
 */
function CodeBlock({ className, children }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const code = String(children ?? "").replace(/\n$/, "");

  const isBlockCode =
    Boolean(className) || code.includes("\n");

  if (!isBlockCode) {
    return (
      <code className="inline-code">
        {children}
      </code>
    );
  }

  const language =
    /language-([\w-]+)/.exec(className || "")?.[1];

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(code);

      setCopied(true);

      setTimeout(() => {
        setCopied(false);
      }, 1500);
    } catch (error) {
      console.error("Could not copy code:", error);
    }
  };

  return (
    <div className="code-block">
      <div className="code-block__header">
        <span className="code-block__language">
          {language || "code"}
        </span>

        <button
          type="button"
          className="code-block__copy"
          onClick={handleCopy}
        >
          {copied ? "✓ Copied" : "Copy"}
        </button>
      </div>

      <pre className="code-block__pre">
        <code className={className}>
          {code}
        </code>
      </pre>
    </div>
  );
}

function ChatPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<Message[]>([]);
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  const askTutor = async (overrideText?: string) => {
    const currentQuestion = (
      overrideText ?? question
    ).trim();

    if (!currentQuestion || loading) return;

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: currentQuestion,
            history: history,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      setHistory((previousHistory) => [
        ...previousHistory,
        {
          role: "user",
          content: currentQuestion,
        },
        {
          role: "model",
          content: data.answer,
        },
      ]);
    } catch (error) {
      console.error(error);

      setHistory((previousHistory) => [
        ...previousHistory,
        {
          role: "user",
          content: currentQuestion,
        },
        {
          role: "model",
          content:
            "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askTutor();
    }
  };

  const clearChat = () => {
    if (loading) return;

    setHistory([]);
  };

  const toggleTheme = () => {
    setTheme((currentTheme) =>
      currentTheme === "dark"
        ? "light"
        : "dark"
    );
  };

  return (
    <div
      className={`chat-page chat-page--${theme}`}
    >
      {/* =========================
          NAVBAR
      ========================== */}

      <header className="chat-nav">
        <a
          href="/"
          className="chat-nav__brand"
        >
          <span className="chat-nav__mark">
            CT
          </span>

          <span className="chat-nav__brand-text">
            CodeTutor
          </span>
        </a>

        <div className="chat-nav__actions">
          <a
            href="/"
            className="chat-nav__home"
          >
            <span>←</span>
            <span>Back to Home</span>
          </a>

          <button
            type="button"
            className="chat-nav__button"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            title="Toggle dark/light mode"
          >
            {theme === "dark" ? "☀️" : "🌙"}
          </button>

          <button
            type="button"
            className="chat-nav__clear"
            onClick={clearChat}
            disabled={
              history.length === 0 ||
              loading
            }
          >
            <span>🗑</span>
            <span>Clear Chat</span>
          </button>
        </div>
      </header>

      {/* =========================
          CHAT AREA
      ========================== */}

      <main className="chat-main">
        <div className="chat-scroll">
          {/* EMPTY STATE */}

          {history.length === 0 && (
            <section className="chat-welcome">
              <div className="chat-welcome__icon">
                <span>✦</span>
              </div>

              <h1>
                What do you want to learn today?
              </h1>

              <p>
                Ask your AI programming tutor
                anything about coding, algorithms,
                debugging, data structures, or
                computer science.
              </p>

              <div className="chat-suggestions">
                {SUGGESTED_QUESTIONS.map(
                  (questionText) => (
                    <button
                      key={questionText}
                      type="button"
                      className="chat-suggestion"
                      onClick={() =>
                        askTutor(questionText)
                      }
                      disabled={loading}
                    >
                      <span>
                        {questionText}
                      </span>

                      <span className="chat-suggestion__arrow">
                        →
                      </span>
                    </button>
                  )
                )}
              </div>
            </section>
          )}

          {/* CONVERSATION */}

          <div className="chat-conversation">
            {history.map(
              (message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`chat-row chat-row--${message.role}`}
                >
                  <div className="chat-message">
                    <div className="chat-message__header">
                      <div
                        className={`chat-avatar chat-avatar--${message.role}`}
                      >
                        {message.role ===
                        "user"
                          ? "You"
                          : "AI"}
                      </div>

                      <span className="chat-author">
                        {message.role ===
                        "user"
                          ? "You"
                          : "AI Tutor"}
                      </span>
                    </div>

                    <div className="chat-content">
                      <ReactMarkdown
                        remarkPlugins={[
                          remarkGfm,
                          remarkMath,
                        ]}
                        rehypePlugins={[
                          rehypeKatex,
                        ]}
                        components={{
                          code({
                            className,
                            children,
                          }) {
                            return (
                              <CodeBlock
                                className={
                                  className
                                }
                              >
                                {children}
                              </CodeBlock>
                            );
                          },
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                </div>
              )
            )}

            {/* THINKING */}

            {loading && (
              <div className="chat-row chat-row--model">
                <div className="chat-message">
                  <div className="chat-message__header">
                    <div className="chat-avatar chat-avatar--model">
                      AI
                    </div>

                    <span className="chat-author">
                      AI Tutor
                    </span>
                  </div>

                  <div className="chat-thinking">
                    <span />
                    <span />
                    <span />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* =========================
          INPUT
      ========================== */}

      <footer className="chat-input-area">
        <div className="chat-input-container">
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about programming..."
            rows={1}
            disabled={loading}
            aria-label="Ask programming question"
          />

          <button
            type="button"
            className="chat-send-btn"
            onClick={() => askTutor()}
            disabled={
              loading ||
              !question.trim()
            }
            aria-label="Send message"
          >
            {loading ? (
              <span className="send-spinner">
                ...
              </span>
            ) : (
              <>
                <span>Send</span>
                <span className="send-arrow">
                  ↑
                </span>
              </>
            )}
          </button>
        </div>

        <p className="chat-input-hint">
          Enter to send · Shift + Enter for
          new line
        </p>
      </footer>
    </div>
  );
}

export default ChatPage;