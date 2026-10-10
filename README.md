# Solace — Mental Health Support Chatbot 🌿

**A calm, accessible web application for supportive conversations and reflection.**

Solace is a full-stack student project designed to provide a simple space where users can express their feelings and receive supportive, rule-based chatbot responses. It combines a responsive React interface with a FastAPI backend and MongoDB-backed user authentication.

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
- **Supportive chatbot:** Locally implemented, rule-based responses without a paid external AI API.
- **Safety checks:** Keyword-based checks for selected high-risk messages.
- **Responsive interface:** A calm visual design for desktop and mobile screens.
- **Theme switching:** Dark and light appearance options.
- **Profile page:** View account information.
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
      +--> Keyword-based safety checks
      |
      +--> Rule-based chatbot responses
      |
      +--> MongoDB Atlas
             |
             +--> User account data
```

The frontend communicates with the backend through HTTP requests. The backend handles authentication, validates protected requests, applies the chatbot's safety checks, and returns responses.

MongoDB Atlas stores user account data. Chat conversations currently exist only in frontend application state and are not persistently saved to the database.

## 📁 Project Structure

```text
mental-health-chatbot/
├── backend/
│   ├── core/
│   │   ├── config.py
│   │   ├── deps.py
│   │   └── security.py
│   ├── models/
│   │   └── user.py
│   ├── routes/
│   │   └── auth.py
│   ├── schemas/
│   │   ├── auth.py
│   │   └── user.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── chat_service.py
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
| `VITE_API_URL`                | Backend URL used by the Vite frontend              |

Variables beginning with `VITE_` are exposed to frontend code. Never place database credentials, JWT secrets, or other private values in frontend environment variables.

## 🔐 Security and Privacy

- Passwords are hashed before storage.
- Protected endpoints require valid authentication.
- Environment files and credentials must remain outside the public repository.
- Conversations are not currently persisted across page refreshes.
- Users should avoid entering highly sensitive personal information.

The chatbot's keyword-based safety checks are limited and cannot guarantee detection of every crisis situation. If you are in immediate danger, contact local emergency services or a trusted person.

## ⚠️ Current Limitations

- Chatbot replies use predefined, rule-based logic rather than a large language model.
- Chat history is not persisted across refreshes or sessions.
- The profile page does not currently support editing account information.
- Safety checks are based on selected keywords and are not a clinical assessment.
- The application is an educational project and has not been presented as a certified clinical or emergency service.

## 🛣️ Potential Improvements

- Persist conversations with appropriate privacy controls.
- Add automated backend and frontend tests.
- Improve rate limiting and abuse protection.
- Add account profile editing.
- Expand safety handling and test edge cases.
- Improve accessibility and loading/error states.

## 👨‍💻 Project

Solace is a student-built full-stack web application intended to demonstrate frontend development, REST API integration, authentication, database connectivity, and cloud deployment.

Feedback and suggestions are welcome through GitHub Issues.

---

**Built with care for learning and supportive conversations.**
