// Short, honest "About / Privacy / Terms" pages. Plain text only, easy to leave.
import Footer from "../components/Footer.jsx";

const PAGES = {
  about: {
    title: "About Solace",
    intro: "Solace is a student project: a small, calm place to put your thoughts into words.",
    sections: [
      ["What it is", "A chatbot built with React, FastAPI and MongoDB. It is rule-based: it looks for keywords in your message and replies with a response that was written in advance."],
      ["What it is not", "Solace is not a person, a therapist or a doctor, and it does not use AI to understand you. It can miss things or misread a message."],
      ["Why it exists", "To practise building a simple, understandable and kind tool for students, and to keep every part of it explainable."],
    ],
  },
  privacy: {
    title: "Privacy",
    intro: "A plain description of what this project does with your information. It has not been independently audited.",
    sections: [
      ["Your account", "When you register, your name, email and a hashed password (Argon2id, never the password itself) are stored in the project’s MongoDB database."],
      ["Staying signed in", "After you sign in, a login token is kept in your browser so you stay signed in for a short time. Signing out removes it."],
      ["Your messages", "Each message you send goes to the Solace server so it can choose a reply. The server does not save messages to the database. The conversation list in the sidebar exists only in your open tab and is cleared when you refresh or sign out."],
      ["Your browser", "Your theme choice (dark or light) is saved in your browser."],
      ["Please be careful", "This is a student project, so avoid sharing details you would not want anyone to see."],
    ],
  },
  terms: {
    title: "Terms",
    intro: "Short and simple. By using Solace you agree to the following.",
    sections: [
      ["Not professional care", "Solace is not medical advice, therapy or a crisis service, and it does not replace a qualified professional."],
      ["In an emergency", "If you or someone else may be in danger, contact your local emergency service (112 in India, 911 in the US) or a trusted person. In India you can call Tele-MANAS on 14416. In the US you can call or text 988. Elsewhere, findahelpline.com lists services by country."],
      ["Limits", "Replies come from keyword matching, so they may not fit what you meant. Solace is provided as is, with no guarantee that it is always available or error-free."],
      ["Your account", "Keep your password to yourself and use Solace kindly and lawfully."],
    ],
  },
};

function InfoPage({ kind, onNavigate }) {
  const page = PAGES[kind];
  return (
    <>
      <main className="container info">
        <button className="back-link" onClick={() => onNavigate("home")}>
          <span aria-hidden="true">←</span> Back to home
        </button>
        <h1>{page.title}</h1>
        <p className="info-intro">{page.intro}</p>
        {page.sections.map(([heading, text]) => (
          <section key={heading}>
            <h2>{heading}</h2>
            <p>{text}</p>
          </section>
        ))}
      </main>
      <Footer onNavigate={onNavigate} />
    </>
  );
}

export default InfoPage;
