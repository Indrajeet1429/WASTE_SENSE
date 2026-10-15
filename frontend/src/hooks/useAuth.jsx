import { createContext, useContext, useMemo, useState } from "react";
import * as auth from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(auth.getSession());
  const value = useMemo(() => ({
    user,
    login: async (email, password) => setUser(await auth.login(email, password)),
    register: async (data) => setUser(await auth.register(data)),
    logout: () => { auth.logout(); setUser(null); },
  }), [user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export const useAuth = () => useContext(AuthContext);
