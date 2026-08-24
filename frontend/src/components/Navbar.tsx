import { useEffect, useState } from "react";
import "./Navbar.css";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "How it works", href: "#how-it-works" },
  { label: "Interview prep", href: "#interview-prep" },
  { label: "About", href: "#about" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`ct-nav ${scrolled ? "ct-nav--scrolled" : ""}`}>
      <div className="ct-container ct-nav__inner">
        <a className="ct-nav__brand" href="#top">
          <span className="ct-nav__brand-mark">&lt;/&gt;</span>
          CodeTutor
        </a>

        <nav className="ct-nav__links" aria-label="Primary">
          {NAV_LINKS.map((link) => (
            <a key={link.href} href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>

        <div className="ct-nav__actions">
          <a className="ct-btn ct-btn--primary ct-nav__cta" href="#get-started">
            Get started
          </a>
          <button
            className="ct-nav__menu-btn"
            aria-label="Toggle navigation menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </div>

      {menuOpen && (
        <div className="ct-nav__mobile">
          {NAV_LINKS.map((link) => (
            <a key={link.href} href={link.href} onClick={() => setMenuOpen(false)}>
              {link.label}
            </a>
          ))}
          <a className="ct-btn ct-btn--primary" href="#get-started" onClick={() => setMenuOpen(false)}>
            Get started
          </a>
        </div>
      )}
    </header>
  );
}
