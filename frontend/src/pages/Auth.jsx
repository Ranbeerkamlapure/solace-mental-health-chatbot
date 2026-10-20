import { useState } from "react";
import { API_URL } from "../config.js";

const UNAVAILABLE = "The service is temporarily unavailable. Please try again in a moment.";

// POST JSON with a time limit, so the page can never sit on "Please wait..." forever
async function postJson(path, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    return await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}

// One component for both screens. mode is "login" or "register".
function AuthPage({ mode, notice, onNavigate, onLogin }) {
  const isLogin = mode === "login";

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Returns an error message, or "" if everything looks fine
  function validate() {
    if (!isLogin && name.trim().length < 2) {
      return "Name must be at least 2 characters.";
    }
    if (!email.includes("@")) {
      return "Please enter a valid email address.";
    }
    if (!isLogin && password.length < 8) {
      return "Password must be at least 8 characters.";
    }
    if (!password) {
      return "Please enter your password.";
    }
    return "";
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (loading) return; // ignore a second submit while a request is running
    setError("");

    const problem = validate();
    if (problem) {
      setError(problem);
      return;
    }

    setLoading(true);
    try {
      if (isLogin) {
        const res = await postJson("/auth/login", { email: email.trim(), password });

        if (res.ok) {
          const data = await res.json();
          onLogin(data.access_token); // App saves the token and opens the chat
        } else if (res.status === 401) {
          setError("Invalid email or password.");
        } else if (res.status === 422) {
          setError("Please enter a valid email and password.");
        } else if (res.status === 503) {
          setError(UNAVAILABLE);
        } else {
          setError("Something went wrong. Please try again.");
        }
      } else {
        // The backend field is called "username"; the form calls it "Your name"
        const res = await postJson("/auth/register", {
          username: name.trim(),
          email: email.trim(),
          password,
        });

        if (res.status === 201) {
          onNavigate("login", "Account created! Please log in.");
        } else if (res.status === 409) {
          setError("An account with this email already exists.");
        } else if (res.status === 422) {
          setError("Please check your details and try again.");
        } else if (res.status === 503) {
          setError(UNAVAILABLE);
        } else {
          setError("Something went wrong. Please try again.");
        }
      }
    } catch (err) {
      setError(
        err.name === "AbortError"
          ? "The server took too long to respond. Please try again."
          : "Unable to connect to the server.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="auth-inner">
        <h1>{isLogin ? "Welcome back." : "Create your quiet space."}</h1>
        <p className="lead">
          {isLogin
            ? "Sign in to continue your conversation."
            : "Start a simple conversation with Solace."}
        </p>

        {notice && (
          <p className="notice info" role="status">
            {notice}
          </p>
        )}
        {error && (
          <p className="notice error" role="alert">
            {error}
          </p>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {!isLogin && (
            <div className="field">
              <label htmlFor="name">Your name</label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
                maxLength={50}
              />
            </div>
          )}

          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete={isLogin ? "current-password" : "new-password"}
              maxLength={128}
            />
            {!isLogin && <span className="hint">At least 8 characters.</span>}
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Please wait..." : isLogin ? "Sign in" : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          {isLogin ? "Don’t have an account? " : "Already have an account? "}
          <button
            type="button"
            className="text-link"
            onClick={() => onNavigate(isLogin ? "register" : "login")}
          >
            {isLogin ? "Create one" : "Sign in"}
          </button>
        </p>
      </div>
    </main>
  );
}

export default AuthPage;
