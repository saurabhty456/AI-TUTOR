import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./LandingPage";
import ChatPage from "./ChatPage";
import ScorePage from "./ScorePage";

import QuizPage from "./components/QuizPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing page */}
        <Route path="/" element={<LandingPage />} />

        {/* AI Tutor */}
        <Route path="/chat" element={<ChatPage />} />

        {/* Quiz */}
        <Route path="/quiz" element={<QuizPage />} />

        {/* Quiz Score */}
        <Route path="/score" element={<ScorePage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;