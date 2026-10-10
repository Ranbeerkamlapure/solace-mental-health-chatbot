import { useState, useEffect } from "react";
import { API_URL } from "../config.js";

function ProfilePage({ token, theme, onToggleTheme, onSessionExpired }) {
  const [profile, setProfile] = useState(null); // { username, email, created_at }
  const [error, setError] = useState("");

  // Ask the backend who is signed in: GET /auth/me (the same JWT as /chat)
  useEffect(() => {
    let ignore = false; // don't update state if this page was closed meanwhile

    async function loadProfile() {
      try {
        const res = await fetch(`${API_URL}/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (ignore) return;

        if (res.status === 401) {
          onSessionExpired();
        } else if (res.ok) {
          setProfile(await res.json());
        } else {
          setError("Something went wrong. Please try again.");
        }
      } catch {
        if (!ignore) setError("Unable to connect to the server.");
      }
    }

    loadProfile();
    return () => {
      ignore = true;
    };
    // Runs once per token. (onSessionExpired is not listed on purpose, so it can't re-trigger the request.)
  }, [token]);

  const memberSince = profile
    ? new Date(profile.created_at).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "";

  return (
    <main className="page-scroll">
      <div className="page">
        <h1>Profile</h1>
        <p className="lead">Your account and preferences.</p>

        {error && (
          <p className="notice error" role="alert">
            {error}
          </p>
        )}
        {!profile && !error && <p className="hint">Loading your account...</p>}

        {profile && (
          <section className="panel">
            <h2 className="eyebrow">Account</h2>
            <div className="field">
              <label htmlFor="profile-name">Name</label>
              <input id="profile-name" type="text" value={profile.username} readOnly />
            </div>
            <div className="field">
              <label htmlFor="profile-email">Email</label>
              <input id="profile-email" type="email" value={profile.email} readOnly />
            </div>
            <div className="field">
              <span className="field-label">Member since</span>
              <span className="field-value">{memberSince}</span>
            </div>
            <button className="btn btn-primary" disabled>
              Save changes
            </button>
            <p className="hint">Editing your details isn’t available yet.</p>
          </section>
        )}

        <section className="panel">
          <h2 className="eyebrow">Preferences</h2>
          <div className="setting-row">
            <div>
              <div className="setting-title">Appearance</div>
              <p className="hint">Currently using the {theme} theme. Saved in this browser.</p>
            </div>
            <button className="btn btn-outline btn-small" onClick={onToggleTheme}>
              Switch to {theme === "dark" ? "light" : "dark"}
            </button>
          </div>
        </section>

        <section className="panel">
          <h2 className="eyebrow">Privacy &amp; data</h2>
          <ul className="privacy-list">
            <li>
              Solace’s server does not store your messages. Conversations stay in this browser tab
              and disappear when you refresh or sign out.
            </li>
            <li>Your name, email and a securely hashed password are stored so you can sign in.</li>
            <li>A sign-in token is kept in this browser until you sign out.</li>
            <li>
              Replies come from Solace’s own keyword rules. Your messages are not sent to any
              external AI service.
            </li>
          </ul>
        </section>
      </div>
    </main>
  );
}

export default ProfilePage;
