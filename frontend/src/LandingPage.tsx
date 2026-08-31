import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import ValueStrip from "./components/ValueStrip";
import Features from "./components/Features";
import HowItWorks from "./components/HowItWorks";
import LearningPaths from "./components/LearningPaths";
import QuizPreview from "./components/QuizPreview";
import InterviewPrep from "./components/InterviewPrep";
import AIInterview from "./components/AIInterview";
import Badges from "./components/Badges";
import CTA from "./components/CTA";
import Footer from "./components/Footer";
import "./styles/landing.css";

/**
 * CodeTutor marketing landing page.
 * UI only — no auth, quiz, badge, or interview backend logic here.
 * Does not touch the existing AI chat component.
 */
export default function LandingPage() {
  return (
    <div className="ct-page">
      <Navbar />
      <Hero />
      <ValueStrip />
      <Features />
      <HowItWorks />
      <LearningPaths />
      <QuizPreview />
      <InterviewPrep />
      <AIInterview />
      <Badges />
      <CTA />
      <Footer />
    </div>
  );
}
