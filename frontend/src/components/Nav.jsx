// Small logo + the top navigation bar (used on every page)

export function Logo() {
  // Two simple leaves (one large, one smaller) in the sage accent colour
  return (
    <svg className="logo-mark" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 21c0-7.5 3.2-13 8.5-15.5 0 7.5-3.2 13-8.5 15.5z" fill="currentColor" />
      <path d="M12 16C6.6 16 4 12.2 4 8.5c4.8 0 8 2.7 8 7.5z" fill="currentColor" opacity="0.6" />
    </svg>
  );
}

function ThemeButton({ theme, onToggleTheme }) {
  const next = theme === "dark" ? "light" : "dark";
  return (
    <button
      className="icon-button"
      onClick={onToggleTheme}
      aria-label={`Switch to ${next} theme`}
      title={`Switch to ${next} theme`}
    >
      <svg
        viewBox="0 0 24 24"
        width="18"
        height="18"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
      >
        {theme === "dark" ? (
          <>
            <circle cx="12" cy="12" r="4" />
            <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
          </>
        ) : (
          <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" />
        )}
      </svg>
    </button>
  );
}

function Nav({ loggedIn, page, onNavigate, theme, onToggleTheme, onSignOut }) {
  return (
    <header className="nav">
      <button
        className="brand"
        onClick={() => onNavigate(loggedIn ? "chat" : "home")}
        aria-label="Solace home"
      >
        <Logo />
        <span>Solace</span>
      </button>

      <nav className="nav-links" aria-label="Main">
        {loggedIn ? (
          <>
            <button
              className="nav-link"
              aria-current={page === "chat" ? "page" : undefined}
              onClick={() => onNavigate("chat")}
            >
              Chat
            </button>
            <button
              className="nav-link"
              aria-current={page === "profile" ? "page" : undefined}
              onClick={() => onNavigate("profile")}
            >
              Profile
            </button>
            <ThemeButton theme={theme} onToggleTheme={onToggleTheme} />
            <button className="btn btn-outline btn-small" onClick={onSignOut}>
              Sign out
            </button>
          </>
        ) : (
          <>
            <ThemeButton theme={theme} onToggleTheme={onToggleTheme} />
            <button
              className="nav-link"
              aria-current={page === "login" ? "page" : undefined}
              onClick={() => onNavigate("login")}
            >
              Sign in
            </button>
            <button className="btn btn-primary btn-small" onClick={() => onNavigate("register")}>
              Get started
            </button>
          </>
        )}
      </nav>
    </header>
  );
}

export default Nav;
