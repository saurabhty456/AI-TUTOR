import { useState } from "react";
import LandingPage from "./LandingPage";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";

import "./App.css";

type Message = {
  role: "user" | "model";
  content: string;
};

function App() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<Message[]>([]);

  const askTutor = async () => {
    if (!question.trim()) return;

    const currentQuestion = question;

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: currentQuestion,
          history: history,
        }),
      });

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
          role: "model",
          content: "Sorry, something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return <LandingPage />;
}

export default App;