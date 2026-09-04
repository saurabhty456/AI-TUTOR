import { Link } from "react-router-dom";
import type { ReactNode } from "react";
import "./auth.css";

interface AuthLayoutProps {
  eyebrow: string;
  title: string;
  description: string;
  children: ReactNode;
  footer: ReactNode;
}

export default function AuthLayout({
  eyebrow,
  title,
  description,
  children,
  footer,
}: AuthLayoutProps) {
  return (
    <main className="auth-page">
      <div className="auth-page__glow auth-page__glow--one" />
      <div className="auth-page__glow auth-page__glow--two" />
      <Link to="/" className="auth-brand">
        <span className="auth-brand__mark">&lt;/&gt;</span>
        <span>CodeTutor</span>
      </Link>
      <section className="auth-shell">
        <div className="auth-shell__intro">
          <span className="auth-eyebrow">{eyebrow}</span>
          <h1>{title}</h1>
          <p>{description}</p>
          <div className="auth-shell__signal">
            <span className="auth-shell__signal-dot" />
            AI-powered learning, built for momentum.
          </div>
        </div>
        <div className="auth-card">
          {children}
          <div className="auth-card__footer">{footer}</div>
        </div>
      </section>
    </main>
  );
}
