import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import Features from "./components/Features";
import HowItWorks from "./components/HowItWorks";
import LearningPreview from "./components/LearningPreview";
import InterviewPreview from "./components/InterviewPreview";
import Badges from "./components/Badges";
import CTA from "./components/CTA";
import Footer from "./components/Footer";
import "./styles/global.css";

/**
 * Marketing landing page for CodeTutor.
 * This is UI/mockup only — no auth, quiz, or backend logic is wired up here.
 * It does not touch the existing AI chat feature; render it as its own
 * route/page and keep the chat component mounted wherever it lives today.
 */
export default function LandingPage() {
  return (
    <div className="ct-landing">
      <Navbar />
      <Hero />
      <Features />
      <HowItWorks />
      <LearningPreview />
      <InterviewPreview />
      <Badges />
      <CTA />
      <Footer />
    </div>
  );
}
