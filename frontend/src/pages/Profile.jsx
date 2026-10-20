import { useState, useEffect } from "react";
import { API_URL } from "../config.js";

function ProfilePage({ token, theme, onToggleTheme, onSessionExpired }) {
  const [profile, setProfile] = useState(null); // { username, email, created_at }
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");
  const [saving, setSaving] = useState(false);

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
          const data = await res.json();
          setProfile(data);
          setName(data.username);
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

  const trimmedName = name.trim().replace(/\s+/g, " ");
  const nameChanged = profile && trimmedName !== profile.username;
  const nameValid = trimmedName.length >= 2 && trimmedName.length <= 50;

  async function saveName(event) {
    event.preventDefault();
    if (!nameChanged || !nameValid || saving) return;
    setSaving(true);
    setError("");
    setSaved("");
    try {
      const res = await fetch(`${API_URL}/auth/me`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ username: trimmedName }),
      });
      if (res.status === 401) {
        onSessionExpired();
        return;
      }
      if (res.ok) {
        const data = await res.json();
        setProfile(data);
        setName(data.username);
        setSaved("Name saved.");
      } else {
        setError("That name couldn’t be saved. Use 2 to 50 characters.");
      }
    } catch {
      setError("Unable to connect to the server.");
    } finally {
      setSaving(false);
    }
  }

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
            <form onSubmit={saveName}>
              <div className="field">
                <label htmlFor="profile-name">Name</label>
                <input
                  id="profile-name"
                  type="text"
                  value={name}
                  onChange={(event) => {
                    setName(event.target.value);
                    setSaved("");
                  }}
                  maxLength={50}
                />
              </div>
              <div className="field">
                <label htmlFor="profile-email">Email</label>
                <input id="profile-email" type="email" value={profile.email} readOnly />
              </div>
              <div className="field">
                <span className="field-label">Member since</span>
                <span className="field-value">{memberSince}</span>
              </div>
              <button className="btn btn-primary" type="submit" disabled={!nameChanged || !nameValid || saving}>
                {saving ? "Saving..." : "Save changes"}
              </button>
              {saved && <p className="hint">{saved}</p>}
              {nameChanged && !nameValid && (
                <p className="hint">Use 2 to 50 characters.</p>
              )}
            </form>
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
              Conversations are saved to your account and stay available after a refresh. You can
              delete a conversation from the chat sidebar.
            </li>
            <li>Your name, email and a securely hashed password are stored so you can sign in.</li>
            <li>A sign-in token is kept in this browser until you sign out.</li>
            <li>
              To write a reply, your message and a few earlier turns from this chat are also sent
              to Groq (groq.com).
            </li>
          </ul>
        </section>
      </div>
    </main>
  );
}

export default ProfilePage;
