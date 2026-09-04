import { useEffect, useState, type ReactNode } from "react";
import { AuthContext } from "./AuthContext";
import type { Credentials, SignupDetails, User } from "./AuthContextTypes";

const API_BASE = "http://127.0.0.1:8000";
export const TOKEN_KEY = "codetutor-access-token";

type AuthResponse = {
  access_token: string;
  token_type: string;
  user: User;
};

async function readError(response: Response, fallback: string): Promise<Error> {
  try {
    const payload = (await response.json()) as { detail?: string };
    if (typeof payload.detail === "string" && payload.detail.trim()) {
      return new Error(payload.detail);
    }
  } catch {
    // Keep backend and network details out of the UI.
  }
  return new Error(fallback);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem(TOKEN_KEY)));

  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return;

    fetch(`${API_BASE}/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(async (response) => {
        if (!response.ok) throw await readError(response, "Your session has expired.");
        return response.json() as Promise<User>;
      })
      .then(setCurrentUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_KEY);
        setCurrentUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function saveAuthResponse(response: Response, fallback: string) {
    if (!response.ok) throw await readError(response, fallback);
    const payload = (await response.json()) as AuthResponse;
    localStorage.setItem(TOKEN_KEY, payload.access_token);
    setCurrentUser(payload.user);
  }

  async function login(credentials: Credentials) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(credentials),
    });
    await saveAuthResponse(response, "Unable to sign in right now. Please try again.");
  }

  async function signup(details: SignupDetails) {
    const response = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(details),
    });
    await saveAuthResponse(response, "Unable to create your account right now. Please try again.");
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setCurrentUser(null);
  }

  return (
    <AuthContext.Provider value={{ currentUser, isAuthenticated: currentUser !== null, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
