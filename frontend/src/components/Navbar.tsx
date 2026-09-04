import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Interview Prep", href: "#interview-prep" },
  { label: "Learning Paths", href: "#learning-paths" },
];

export default function Navbar() {
  const { currentUser, isAuthenticated, logout } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("codetutor-theme") === "dark";
  });

  useEffect(() => {
    const theme = darkMode ? "dark" : "light";

    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("codetutor-theme", theme);
  }, [darkMode]);

  return (
    <header className="ct-nav">
      <div className="ct-container ct-nav__inner">
        {/* Logo */}
        <a href="#top" className="ct-brand">
          <span className="ct-brand__mark">&lt;/&gt;</span>
          <span className="ct-brand__name">CodeTutor</span>
        </a>

        {/* Navigation */}
        <nav className="ct-nav__links">
          {NAV_LINKS.map((link) => (
            <a key={link.href} href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>

        {/* Actions */}
        <div className="ct-nav__actions">
          <button
            type="button"
            className="ct-theme-toggle"
            onClick={() => setDarkMode((previous) => !previous)}
            aria-label={
              darkMode
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
            title={
              darkMode
                ? "Switch to light mode"
                : "Switch to dark mode"
            }
          >
            {darkMode ? "☀️" : "🌙"}
          </button>

          {isAuthenticated ? (
            <div className="ct-profile">
              <button
                type="button"
                className="ct-profile__button"
                onClick={() => setProfileOpen((open) => !open)}
                aria-expanded={profileOpen}
                aria-haspopup="menu"
              >
                <span className="ct-profile__avatar">
                  {currentUser?.name.charAt(0).toUpperCase()}
                </span>
                <span>{currentUser?.name.split(" ")[0]}</span>
                <span aria-hidden="true">⌄</span>
              </button>
                <div className="ct-nav__auth-links">
                  <Link to="/dashboard">Dashboard</Link>
                  <Link to="/quiz">Quiz</Link>
                  <Link to="/chat">Chat</Link>
                </div>
              {profileOpen && (
                <div className="ct-profile__menu" role="menu">
                  <Link to="/dashboard" role="menuitem">Dashboard</Link>
                  <button type="button" onClick={logout} role="menuitem">Log out</button>
                </div>
              )}
            </div>
          ) : (
            <>
              <Link to="/login" className="ct-nav__login">Login</Link>
              <Link to="/signup" className="ct-btn ct-btn--primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}