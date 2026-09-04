import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./LandingPage";
import ChatPage from "./ChatPage";
import ScorePage from "./ScorePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DashboardPage from "./pages/DashboardPage";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthProvider";

import QuizPage from "./components/QuizPage";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Route>

          <Route path="/chat" element={<ChatPage />} />
          <Route path="/quiz" element={<QuizPage />} />
          <Route path="/score" element={<ScorePage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;