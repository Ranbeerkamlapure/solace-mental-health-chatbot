import { useState, useEffect } from "react";
import "./App.css";
import Nav from "./components/Nav.jsx";
import HomePage from "./pages/Home.jsx";
import AuthPage from "./pages/Auth.jsx";
import ChatPage from "./pages/Chat.jsx";
import ProfilePage from "./pages/Profile.jsx";
import InfoPage from "./pages/Info.jsx";

// Pages: "home", "login", "register", "about", "privacy", "terms" (signed out)   |   "chat", "profile" (signed in)
function App() {
  const [token, setToken] = useState(() => localStorage.getItem("token"));
  const [page, setPage] = useState(() => (localStorage.getItem("token") ? "chat" : "home"));
  const [notice, setNotice] = useState(""); // message shown on the login page
  const [theme, setTheme] = useState(() =>
    localStorage.getItem("theme") === "light" ? "light" : "dark",
  );

  // Chat conversations live here so they survive switching between Chat and Profile
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);

  // Apply the theme: CSS reads [data-theme="light"] on the <html> element
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  function toggleTheme() {
    setTheme(theme === "dark" ? "light" : "dark");
  }

  // go("home", "", "how-it-works") opens the page, then scrolls to that section id
  function go(newPage, message = "", section = "") {
    setPage(newPage);
    setNotice(message);
    if (section) {
      setTimeout(() => document.getElementById(section)?.scrollIntoView(), 50);
    } else {
      window.scrollTo(0, 0);
    }
  }

  function clearConversations() {
    setConversations([]);
    setActiveId(null);
  }

  function handleLogin(newToken) {
    localStorage.setItem("token", newToken);
    clearConversations();
    setToken(newToken);
    go("chat");
  }

  function handleLogout() {
    localStorage.removeItem("token");
    clearConversations();
    setToken(null);
    go("home");
  }

  function handleSessionExpired() {
    localStorage.removeItem("token");
    clearConversations();
    setToken(null);
    go("login", "Your session expired. Please log in again.");
  }

  const loggedIn = Boolean(token);

  let content;
  if (loggedIn && page === "profile") {
    content = (
      <ProfilePage
        token={token}
        theme={theme}
        onToggleTheme={toggleTheme}
        onSessionExpired={handleSessionExpired}
      />
    );
  } else if (loggedIn) {
    content = (
      <ChatPage
        token={token}
        conversations={conversations}
        setConversations={setConversations}
        activeId={activeId}
        setActiveId={setActiveId}
        onNavigate={go}
        onSessionExpired={handleSessionExpired}
      />
    );
  } else if (page === "login" || page === "register") {
    content = (
      <AuthPage key={page} mode={page} notice={notice} onNavigate={go} onLogin={handleLogin} />
    );
  } else if (page === "about" || page === "privacy" || page === "terms") {
    content = <InfoPage key={page} kind={page} onNavigate={go} />;
  } else {
    content = <HomePage onNavigate={go} />;
  }

  return (
    <div className={loggedIn ? "app-shell" : "site"}>
      <Nav
        loggedIn={loggedIn}
        page={page}
        onNavigate={go}
        theme={theme}
        onToggleTheme={toggleTheme}
        onSignOut={handleLogout}
      />
      {content}
    </div>
  );
}

export default App;
