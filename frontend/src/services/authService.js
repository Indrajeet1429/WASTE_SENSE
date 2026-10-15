// Browser-only auth: accounts live in this browser only. Replace login/register bodies with
// POST /auth/login and POST /auth/register on FastAPI, then call setToken(response.token).
import { setToken } from "./api";

const USERS = "ws_users", SESSION = "ws_session";
const read = (k) => { try { return JSON.parse(localStorage.getItem(k)); } catch { return null; } };
const write = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch { /* storage unavailable */ } };
const sha = async (s) => {
  try {
    const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`ws::${s}`));
    return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
  } catch { return btoa(s); }
};
const publicUser = (u) => ({ name: u.name, email: u.email, role: u.role });

export const getSession = () => read(SESSION);

export async function login(email, password) {
  const hash = await sha(password);
  const u = (read(USERS) || []).find((x) => x.email === email.trim().toLowerCase() && x.hash === hash);
  if (!u) throw new Error("Email or password is incorrect. Check both and try again.");
  write(SESSION, publicUser(u));
  return publicUser(u);
}
export async function register({ name, email, role, password, confirm }) {
  const users = read(USERS) || [], em = email.trim().toLowerCase();
  if (password.length < 8 || !/\d/.test(password) || !/[A-Za-z]/.test(password)) throw new Error("Use at least 8 characters with a letter and a number.");
  if (password !== confirm) throw new Error("The two passwords do not match.");
  if (users.find((u) => u.email === em)) throw new Error("An account with this email already exists. Sign in instead.");
  const u = { name: name.trim(), email: em, role, hash: await sha(password) };
  users.push(u); write(USERS, users); write(SESSION, publicUser(u));
  return publicUser(u);
}
export function logout() {
  try { localStorage.removeItem(SESSION); } catch { /* ignore */ }
  setToken(null);
}
