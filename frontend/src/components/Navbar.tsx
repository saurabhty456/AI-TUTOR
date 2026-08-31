import { useEffect, useState } from "react";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "How It Works", href: "#how-it-works" },
  { label: "Interview Prep", href: "#interview-prep" },
  { label: "Learning Paths", href: "#learning-paths" },
];

export default function Navbar() {
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

          <a href="/chat" className="ct-btn ct-btn--primary">
            Get Started
          </a>
        </div>
      </div>
    </header>
  );
}