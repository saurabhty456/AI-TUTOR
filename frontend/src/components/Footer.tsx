const LINKS = [
  { label: "Features", href: "#features" },
  { label: "Learning Paths", href: "#learning-paths" },
  { label: "Interview Prep", href: "#interview-prep" },
  { label: "About", href: "#about" },
  { label: "Contact", href: "#contact" },
];

export default function Footer() {
  return (
    <footer className="ct-footer">
      <div className="ct-container ct-footer__inner">
        <div className="ct-footer__brand">
          <span className="ct-nav__brand">
            <span className="ct-nav__mark">CT</span>
            CodeTutor
          </span>
          <p>Learn. Practice. Master.</p>
        </div>

        <nav className="ct-footer__links" aria-label="Footer">
          {LINKS.map((link) => (
            <a key={link.href} href={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
      </div>

      <div className="ct-container ct-footer__bottom">
        <span>© {new Date().getFullYear()} CodeTutor. All rights reserved.</span>
      </div>
    </footer>
  );
}
