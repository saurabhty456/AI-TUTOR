import { createContext, useContext } from "react";
import type { Credentials, SignupDetails, User } from "./AuthContextTypes";

export type AuthContextValue = {
  currentUser: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (credentials: Credentials) => Promise<void>;
  signup: (details: SignupDetails) => Promise<void>;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
