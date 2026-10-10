// Site footer (signed-out pages). Every link uses the app's own navigation: onNavigate(page, message, sectionId)
import { Logo } from "./Nav.jsx";

function Footer({ onNavigate }) {
  return (
    <footer className="footer on-forest">
      <div className="footer-inner">
        <div className="footer-about">
          <button className="brand" onClick={() => onNavigate("home")} aria-label="Solace home">
            <Logo />
            <span>Solace</span>
          </button>
          <p>A quiet space to reflect, find perspective, and take things one step at a time.</p>
        </div>

        <nav aria-label="Explore">
          <h2>Explore</h2>
          <ul>
            <li><button onClick={() => onNavigate("home")}>Home</button></li>
            <li><button onClick={() => onNavigate("home", "", "how-it-works")}>How Solace works</button></li>
            <li><button onClick={() => onNavigate("login")}>Sign in</button></li>
            <li><button onClick={() => onNavigate("register")}>Create an account</button></li>
          </ul>
        </nav>

        <nav aria-label="Information">
          <h2>Information</h2>
          <ul>
            <li><button onClick={() => onNavigate("about")}>About Solace</button></li>
            <li><button onClick={() => onNavigate("privacy")}>Privacy</button></li>
            <li><button onClick={() => onNavigate("terms")}>Terms</button></li>
          </ul>
        </nav>
      </div>

      <div className="footer-bottom">
        <p>© 2026 Solace. Built with care.</p>
        <p>
          Solace is a supportive student project and not a replacement for professional
          mental-health care.
        </p>
      </div>
    </footer>
  );
}

export default Footer;
