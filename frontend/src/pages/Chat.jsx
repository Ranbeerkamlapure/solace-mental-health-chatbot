import { useState, useEffect, useRef } from "react";
import { API_URL } from "../config.js";

const SUGGESTIONS = ["I'm feeling stressed", "I'm feeling lonely", "I need some motivation"];

// conversations = [{ id, title, messages: [{ role: "user" | "ai" | "error", content }] }]
// They live in React state only (no database), so they disappear on refresh or sign out.
function ChatPage({
  token,
  conversations,
  setConversations,
  activeId,
  setActiveId,
  onNavigate,
  onSessionExpired,
}) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingId, setPendingId] = useState(null); // which conversation is waiting for a reply
  const [search, setSearch] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false); // only used on small screens
  const bottomRef = useRef(null);

  const active = conversations.find((c) => c.id === activeId);
  const messages = active ? active.messages : [];

  // Scroll down when a new message arrives
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages.length, loading, activeId]);

  // Search by title or by anything said in the conversation
  const query = search.trim().toLowerCase();
  const visible = conversations.filter(
    (c) =>
      !query ||
      c.title.toLowerCase().includes(query) ||
      c.messages.some((m) => m.content.toLowerCase().includes(query)),
  );

  function startNewConversation() {
    setActiveId(null); // the conversation is created when the first message is sent
    setSidebarOpen(false);
  }

  function openConversation(id) {
    setActiveId(id);
    setSidebarOpen(false);
  }

  function addMessage(id, role, content) {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, messages: [...c.messages, { role, content }] } : c)),
    );
  }

  async function sendMessage(text) {
    const userText = text.trim();
    if (!userText || loading) return;

    // Which conversation is this message for? Create one if needed.
    let id = activeId;
    if (id === null) {
      id = Date.now();
      const title = userText.length > 40 ? userText.slice(0, 40) + "…" : userText;
      setConversations((prev) => [{ id, title, messages: [] }, ...prev]);
      setActiveId(id);
    }

    addMessage(id, "user", userText);
    setMessage("");
    setLoading(true);
    setPendingId(id);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userText }),
      });

      if (response.status === 401) {
        onSessionExpired(); // token missing or expired -> back to sign in
        return;
      }

      if (response.ok) {
        const data = await response.json();
        addMessage(id, "ai", data.response);
      } else if (response.status === 422) {
        addMessage(id, "error", "That message couldn't be sent. Please try a shorter one.");
      } else {
        addMessage(id, "error", "Something went wrong. Please try again.");
      }
    } catch {
      addMessage(id, "error", "Unable to connect to the server.");
    } finally {
      setLoading(false);
      setPendingId(null);
    }
  }

  function handleSubmit(e) {
    e.preventDefault(); // pressing Enter in the input submits this form
    sendMessage(message);
  }

  return (
    <div className="chat-layout">
      {sidebarOpen && <div className="backdrop" onClick={() => setSidebarOpen(false)} />}

      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`} aria-label="Conversations">
        <button className="btn btn-outline new-chat" onClick={startNewConversation}>
          + New conversation
        </button>

        <input
          type="search"
          className="search"
          placeholder="Search chats"
          aria-label="Search chats"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <div className="conversation-list">
          {conversations.length === 0 ? (
            <p className="sidebar-empty">No conversations yet.</p>
          ) : visible.length === 0 ? (
            <p className="sidebar-empty">No chats match your search.</p>
          ) : (
            visible.map((c) => (
              <button
                key={c.id}
                className={`conversation-item ${c.id === activeId ? "active" : ""}`}
                onClick={() => openConversation(c.id)}
              >
                {c.title}
              </button>
            ))
          )}
        </div>

        <p className="sidebar-note">Chats are kept only while this page is open.</p>
        <button className="sidebar-link" onClick={() => onNavigate("profile")}>
          Settings &amp; Privacy
        </button>
      </aside>

      <section className="conversation">
        <div className="conversation-header">
          <button
            className="btn btn-outline btn-small menu-button"
            onClick={() => setSidebarOpen(true)}
          >
            Chats
          </button>
          <h1 className="conversation-title">{active ? active.title : "New conversation"}</h1>
        </div>

        <div className="conversation-body">
          <div className="conversation-inner">
            {messages.length === 0 ? (
              <div className="welcome">
                <h2>Hi, I’m Solace 👋</h2>
                <p>How are you feeling today?</p>
                <div className="suggestions">
                  {SUGGESTIONS.map((text) => (
                    <button key={text} className="chip" onClick={() => sendMessage(text)}>
                      {text}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="messages" aria-live="polite">
                {messages.map((msg, index) =>
                  msg.role === "user" ? (
                    <div key={index} className="msg msg-user">
                      {msg.content}
                    </div>
                  ) : (
                    <div
                      key={index}
                      className={`msg msg-solace ${msg.role === "error" ? "msg-error" : ""}`}
                    >
                      <div className="msg-label">Solace</div>
                      <div className="msg-text">{msg.content}</div>
                    </div>
                  ),
                )}
                {loading && pendingId === activeId && (
                  <div className="msg msg-solace">
                    <div className="msg-label">Solace</div>
                    <div className="msg-text thinking">Solace is thinking...</div>
                  </div>
                )}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        <div className="composer-wrap">
          <form className="composer" onSubmit={handleSubmit}>
            <input
              type="text"
              placeholder="Share what's on your mind..."
              aria-label="Your message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              maxLength={1000}
            />
            <button type="submit" className="send-button" disabled={loading || !message.trim()}>
              Send <span aria-hidden="true">→</span>
            </button>
          </form>
          <p className="disclaimer">
            Solace is not a doctor or therapist. If you’re in immediate danger, contact your local
            emergency service.
          </p>
        </div>
      </section>
    </div>
  );
}

export default ChatPage;
