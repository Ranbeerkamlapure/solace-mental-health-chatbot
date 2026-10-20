import { Logo } from "../components/Nav.jsx";
import Footer from "../components/Footer.jsx";
import forestImage from "../assets/forest.svg";
import journalImage from "../assets/journal.svg";

// If an image fails to load, hide it: the CSS background behind it is the fallback
const hideImage = (event) => {
  event.currentTarget.style.display = "none";
};

// Landing page for visitors who are not signed in.
// Everything written here describes what Solace really does.

const FEATURES = [
  {
    title: "Empathy first",
    text: "Every reply is written to be warm, gentle and non-judgmental, and many end with an open question so you can keep talking at your own pace.",
  },
  {
    title: "Simple by design",
    text: "A language model reads the message you just sent and writes a short reply. If that service is unavailable, Solace uses a reply written in advance.",
  },
  {
    title: "Safe by design",
    text: "Before anything else, Solace checks for obvious crisis phrases. If it finds one, it shows a fixed message pointing to emergency and crisis support.",
  },
];

const STEPS = [
  {
    title: "You share what’s on your mind",
    text: "Type a message in your own words, whenever you’re ready.",
  },
  {
    title: "Safety phrases are checked first",
    text: "Solace looks for obvious crisis phrases before anything else. If one appears, it replies with a fixed message about emergency and crisis support.",
  },
  {
    title: "A reply is written for this message",
    text: "Otherwise your message, and a few earlier turns from this chat, are sent to Groq so the reply can follow what you actually said.",
  },
  {
    title: "A written reply is the backup",
    text: "If Groq cannot answer, Solace matches keywords such as “stressed” or “lonely” and uses a reply written in advance.",
  },
];

function HomePage({ onNavigate }) {
  return (
    <>
      <main>
        <section className="container hero">
          <h1>
            A quiet place to put words to <em>what you’re feeling.</em>
          </h1>
          <p className="hero-text">
            Solace is a simple, supportive space to talk, reflect, and put your thoughts into words.
          </p>
          <div className="hero-actions">
            <button className="btn btn-primary" onClick={() => onNavigate("register")}>
              Begin a conversation <span aria-hidden="true">→</span>
            </button>
            <a className="btn btn-outline" href="#how-it-works">
              How Solace works
            </a>
          </div>
          <p className="hero-note">
            Solace is not a doctor or therapist. If you’re in immediate danger, contact your local
            emergency service or a trusted person.
          </p>
        </section>

        <section className="container features" aria-label="What makes Solace different">
          {FEATURES.map((feature, index) => (
            <article className="feature" key={feature.title}>
              <span className="eyebrow">0{index + 1}</span>
              <h2>{feature.title}</h2>
              <p>{feature.text}</p>
            </article>
          ))}
        </section>

        <section className="how" id="how-it-works">
          <div className="container story">
            <figure className="story-visual">
              <img
                src={journalImage}
                alt="An illustration of an open journal and a cup of tea by a window"
                onError={hideImage}
              />
              <figcaption className="quote-card on-forest">
                <Logo />
                <blockquote>“I felt like being listened to, without being fixed.”</blockquote>
                <small>Sample reflection · illustrative, not a real review</small>
              </figcaption>
            </figure>

            <div className="story-copy">
              <span className="eyebrow">How Solace works</span>
              <h2 className="how-title">Simple on purpose.</h2>
              <p className="how-intro">
                Solace is a supportive chatbot, not a person or a clinician. This is exactly what
                happens when you send a message.
              </p>
              <ol className="steps">
                {STEPS.map((step, index) => (
                  <li key={step.title}>
                    <span className="step-num">0{index + 1}</span>
                    <div>
                      <h3>{step.title}</h3>
                      <p>{step.text}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </section>

        <section className="nature on-forest">
          <img className="nature-img" src={forestImage} alt="" onError={hideImage} />
          <div className="container nature-inner">
            <h2>Some conversations are easier when nobody’s watching.</h2>
            <p>Take a quiet moment for yourself. Start a conversation whenever you’re ready.</p>
            <button className="btn btn-primary btn-round" onClick={() => onNavigate("register")}>
              Create a free account <span aria-hidden="true">→</span>
            </button>
          </div>
        </section>
      </main>

      <Footer onNavigate={onNavigate} />
    </>
  );
}

export default HomePage;
