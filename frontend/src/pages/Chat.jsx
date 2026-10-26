import { useState, useEffect, useRef } from "react";
import { API_URL } from "../config.js";

const SUGGESTIONS = ["I'm feeling stressed", "I'm feeling lonely", "I need some motivation"];

// conversations = [{ id, title, messages: [{ role: "user" | "ai" | "error", content }] }]
// Saved chats come from the server. A message with role "error" stays in this tab only.
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
  const [chatsLoading, setChatsLoading] = useState(true);
  const bottomRef = useRef(null);

  useEffect(() => {
    let ignore = false;

    async function loadChats() {
      try {
        const response = await fetch(`${API_URL}/conversations`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (ignore) return;
        if (response.status === 401) {
          onSessionExpired();
          return;
        }
        if (response.ok) {
          const data = await response.json();
          setConversations(data);
          setActiveId((current) => current ?? data[0]?.id ?? null);
        }
      } catch {
        // The sidebar keeps whatever is already on screen.
      } finally {
        if (!ignore) setChatsLoading(false);
      }
    }

    loadChats();
    return () => {
      ignore = true;
    };
  }, [token, setConversations, setActiveId]);

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

  async function deleteConversation(id) {
    if (String(id).startsWith("local-")) {
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeId === id) setActiveId(null);
      return;
    }
    if (!window.confirm("Delete this conversation? This cannot be undone.")) return;

    try {
      const response = await fetch(`${API_URL}/conversations/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status === 401) {
        onSessionExpired();
        return;
      }
      if (response.ok) {
        setConversations((prev) => prev.filter((c) => c.id !== id));
        if (activeId === id) setActiveId(null);
      }
    } catch {
      // Leave the conversation in the list if the server could not be reached.
    }
  }

  async function sendMessage(text) {
    const userText = text.trim();
    if (!userText || loading) return;

    const creating = activeId === null || String(activeId).startsWith("local-");
    let id = activeId;
    if (id === null) {
      id = `local-${Date.now()}`;
      const title = userText.length > 40 ? `${userText.slice(0, 40)}…` : userText;
      setConversations((prev) => [{ id, title, messages: [] }, ...prev]);
      setActiveId(id);
    }

    addMessage(id, "user", userText);
    setMessage("");
    setLoading(true);
    setPendingId(id);

    const url = creating
      ? `${API_URL}/conversations`
      : `${API_URL}/conversations/${id}/messages`;

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: userText }),
      });

      if (response.status === 401) {
        onSessionExpired();
        return;
      }

      if (response.ok) {
        const saved = await response.json();
        setConversations((prev) => [saved, ...prev.filter((c) => c.id !== id && c.id !== saved.id)]);
        setActiveId(saved.id);
      } else if (response.status === 422) {
        addMessage(id, "error", "That message couldn't be sent. Please try a shorter one.");
      } else if (response.status === 429) {
        const data = await response.json().catch(() => ({}));
        addMessage(id, "error", data.detail || "Please wait a moment and try again.");
      } else if (response.status === 503) {
        const data = await response.json().catch(() => ({}));
        addMessage(
          id,
          "error",
          data.detail || "Chat replies are temporarily unavailable. Please try again in a moment.",
        );
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
          {chatsLoading ? (
            <p className="sidebar-empty">Loading chats...</p>
          ) : conversations.length === 0 ? (
            <p className="sidebar-empty">No conversations yet.</p>
          ) : visible.length === 0 ? (
            <p className="sidebar-empty">No chats match your search.</p>
          ) : (
            visible.map((c) => (
              <div key={c.id} className={`conversation-row ${c.id === activeId ? "active" : ""}`}>
                <button className="conversation-item" onClick={() => openConversation(c.id)}>
                  {c.title}
                </button>
                <button
                  className="conversation-delete"
                  aria-label={`Delete ${c.title}`}
                  onClick={() => deleteConversation(c.id)}
                >
                  Delete
                </button>
              </div>
            ))
          )}
        </div>

        <p className="sidebar-note">Chats are saved to your account. You can delete one at any time.</p>
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
