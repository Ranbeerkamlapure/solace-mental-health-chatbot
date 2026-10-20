# Solace — Mental Health Support Chatbot 🌿

**A calm, accessible web application for supportive conversations and reflection.**

Solace is a full-stack student project designed to provide a simple space where users can express their feelings and receive supportive replies. A language model on Groq writes those replies. A fixed crisis reply is used for selected high-risk phrases, and a written keyword reply is used only if Groq cannot answer. The app combines a responsive React interface with a FastAPI backend and MongoDB for accounts and saved chats.

> **Important:** Solace is an educational support project, not a medical or mental-health professional service. It does not diagnose conditions, prescribe treatment, or replace professional care or emergency services.

## 🌐 Live Demo

- **Web application:** https://solace-mental-health-chatbot.vercel.app
- **Backend API:** https://solace-backend-x7eo.onrender.com
- **API documentation:** https://solace-backend-x7eo.onrender.com/docs

The backend is hosted on Render's free tier and may take a little time to respond after inactivity.

## ✨ Features

- **User authentication:** Account registration and login.
- **Secure password handling:** Password hashing using Argon2.
- **Token-based authentication:** JWT-protected backend endpoints.
- **Supportive chatbot:** Replies are written by Groq's free API and follow the message and recent turns of the chat.
- **Safety checks:** Selected crisis phrases receive a fixed helpline reply and are not sent to Groq.
- **Saved conversations:** Chats are stored for the signed-in user and can be deleted from the sidebar.
- **Send limits:** One message every 2 seconds, and 100 messages per account per day.
- **Responsive interface:** A calm visual design for desktop and mobile screens.
- **Theme switching:** Dark and light appearance options.
- **Profile page:** View account information and change the display name.
- **Informational pages:** About, Privacy, and Terms.
- **Cloud deployment:** Frontend and backend deployed separately.

## 🛠️ Tech Stack

| Layer            | Technology                   |
| ---------------- | ---------------------------- |
| Frontend         | React, Vite, JavaScript, CSS |
| Backend          | Python, FastAPI              |
| Database         | MongoDB Atlas                |
| Authentication   | JWT                          |
| Password hashing | Argon2                       |
| Chat replies     | Groq API (`openai/gpt-oss-120b`) |
| Frontend hosting | Vercel                       |
| Backend hosting  | Render                       |
| Source control   | Git and GitHub               |

## 🏗️ Architecture

```text
User's Browser
      |
      v
React + Vite Frontend
      |
      | HTTP requests
      v
FastAPI Backend
      |
      +--> Authentication and JWT verification
      |
      +--> Crisis phrase check (fixed helpline reply)
      |
      +--> Groq, for other replies
      |
      +--> Written keyword reply, only if Groq fails
      |
      +--> MongoDB Atlas
             |
             +--> User accounts
             +--> Saved conversations
```

The frontend communicates with the backend through HTTP requests. The backend handles authentication, checks for crisis phrases, asks Groq for a reply, and stores the conversation for that user.

MongoDB Atlas stores account data and saved chats. A message and a few earlier turns are also sent to Groq so the reply can follow the conversation. Groq's free tier is rate-limited.

## 📁 Project Structure

```text
mental-health-chatbot/
├── backend/
│   ├── core/
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── rate_limit.py
│   │   └── security.py
│   ├── models/
│   │   └── user.py
│   ├── routes/
│   │   ├── auth.py
│   │   └── conversations.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── user.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   └── conversation_service.py
│   ├── tests/
│   ├── database.py
│   ├── main.py
│   ├── requirements.txt
│   └── .gitignore
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   ├── config.js
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 🚀 Run Locally

### Prerequisites

- Python and pip
- Node.js and npm
- A MongoDB Atlas cluster or another compatible MongoDB deployment
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Ranbeerkamlapure/solace-mental-health-chatbot.git
cd solace-mental-health-chatbot
```

### 2. Configure the backend

Create a private `backend/.env` file containing the following variables:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB_NAME=Solace
JWT_SECRET=your_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Use your own database connection string and a strong random JWT secret. Never commit real credentials to GitHub.

Create and activate a Python virtual environment, then install the backend dependencies:

```bash
python -m venv .venv
```

Activate it using the command for your operating system.

Windows Command Prompt:

```bat
.venv\Scripts\activate
```

Git Bash:

```bash
source .venv/Scripts/activate
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies and start FastAPI:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend should be available at `http://127.0.0.1:8000`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 3. Configure the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create a `frontend/.env.local` file with:

```env
VITE_API_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

For local development, ensure the backend's `CORS_ORIGINS` includes the frontend origin you use.

## ⚙️ Environment Variables

| Variable                      | Purpose                                            |
| ----------------------------- | -------------------------------------------------- |
| `MONGODB_URI`                 | MongoDB connection string                          |
| `MONGODB_DB_NAME`             | Database name                                      |
| `JWT_SECRET`                  | Secret used to sign authentication tokens          |
| `JWT_ALGORITHM`               | JWT signing algorithm                              |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration duration                          |
| `CORS_ORIGINS`                | Comma-separated list of permitted frontend origins |
| `GROQ_API_KEY`                | Free Groq API key used to write chat replies       |
| `GROQ_MODEL`                  | Groq model id, default `openai/gpt-oss-120b`       |
| `VITE_API_URL`                | Backend URL used by the Vite frontend              |

Variables beginning with `VITE_` are exposed to frontend code. Never place database credentials, JWT secrets, or other private values in frontend environment variables.

## 🔐 Security and Privacy

- Passwords are hashed before storage.
- Protected endpoints require valid authentication.
- Environment files and credentials must remain outside the public repository.
- Conversations are stored for the signed-in user and can be deleted from the chat sidebar.
- A message and a few earlier turns are sent to Groq to write the reply.
- Users should avoid entering highly sensitive personal information.

Crisis checks look for selected phrases and cannot guarantee detection of every crisis situation. If you are in immediate danger, contact local emergency services or a trusted person.

## ⚠️ Current Limitations

- Replies come from Groq when `GROQ_API_KEY` is set. If that call fails, a keyword reply is used instead.
- Crisis handling is a fixed reply for selected phrases, not a clinical assessment.
- Chat sending is limited to one message every 2 seconds and 100 messages per user per day, in the running server process.
- The profile page can change the display name. Email cannot be changed.
- The application is an educational project and has not been presented as a certified clinical or emergency service.

## 🛣️ Potential Improvements

- Add automated frontend tests.
- Keep the send limit in a shared store so it survives more than one server process.
- Expand safety handling and test edge cases.
- Improve accessibility and loading/error states.

## 👨‍💻 Project

Solace is a student-built full-stack web application intended to demonstrate frontend development, REST API integration, authentication, database connectivity, and cloud deployment.

Feedback and suggestions are welcome through GitHub Issues.

---

**Built with care for learning and supportive conversations.**
