import "./Footer.css";

const COLUMNS = [
  {
    heading: "Product",
    links: ["Features", "How it works", "Interview prep"],
  },
  {
    heading: "Learn",
    links: ["Python", "JavaScript", "Java", "DSA"],
  },
  {
    heading: "Company",
    links: ["About", "Contact"],
  },
];

export default function Footer() {
  return (
    <footer className="ct-footer" id="about">
      <div className="ct-container ct-footer__inner">
        <div className="ct-footer__brand">
          <a className="ct-nav__brand" href="#top">
            <span className="ct-nav__brand-mark">&lt;/&gt;</span>
            CodeTutor
          </a>
          <p>Your AI programming tutor — for learning, practicing, and interviewing.</p>
        </div>

        <div className="ct-footer__cols">
          {COLUMNS.map((col) => (
            <div key={col.heading}>
              <h4>{col.heading}</h4>
              <ul>
                {col.links.map((link) => (
                  <li key={link}>
                    <a href="#top">{link}</a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="ct-container ct-footer__bottom">
        <span>© {new Date().getFullYear()} CodeTutor. All rights reserved.</span>
      </div>
    </footer>
  );
}
