# Frontend — Kapruka Gift Concierge UI

A modern **Next.js** chat interface for the Kapruka Gift Concierge AI agent. Features real-time streaming status updates, a rich sidebar with recipient profiles and category navigation, JWT authentication, and markdown-rendered responses with product recommendations.

---

## Project Structure

```
frontend/
├── app/
│   ├── layout.js            # Root layout
│   ├── page.js              # Landing page (redirects to /chat)
│   ├── globals.css           # Global styles and TailwindCSS base
│   ├── chat/
│   │   ├── layout.js        # Chat layout wrapper
│   │   └── page.js          # Main chat page (session init, sidebar + chat area)
│   └── login/
│       └── page.js          # Auth page (sign in / sign up)
│
├── components/
│   ├── chat/
│   │   ├── ChatArea.jsx     # Main chat container (message list, input, SSE handling)
│   │   ├── MessageBubble.jsx # Individual message renderer (markdown, memoized)
│   │   └── WelcomeMessage.jsx # Initial greeting with quick-action suggestions
│   ├── sidebar/
│   │   ├── Sidebar.jsx      # Sidebar container (branding, profile, categories, logout)
│   │   ├── RecipientCard.jsx # Displays recipient preferences & allergies
│   │   └── CategoryGrid.jsx # Gift category quick-nav grid
│   └── ui/                  # shadcn/ui primitive components
│       ├── accordion.jsx
│       ├── avatar.jsx
│       ├── badge.jsx
│       ├── button.jsx
│       ├── card.jsx
│       ├── input.jsx
│       ├── scroll-area.jsx
│       └── separator.jsx
│
├── context/
│   └── AuthContext.js        # React context for auth state 
│
├── lib/
│   └── utils.js              # Utility functions (cn classname merger)
│
├── services/
│   └── api.js                # API service layer 
│
├── components.json           # shadcn/ui configuration
├── next.config.mjs           # Next.js configuration
├── postcss.config.mjs        # PostCSS config (TailwindCSS)
├── package.json              # Dependencies and scripts
└── eslint.config.mjs         # ESLint configuration
```

---

## Features

### Chat Interface
- **Real-time SSE streaming** — Status updates appear live while the agent processes ("Analyzing request...", "Searching catalog...", "Synthesizing response...")
- **Markdown rendering** — Agent responses render rich markdown with links, lists, and formatting
- **Auto-scrolling** — Chat automatically scrolls to the latest message
- **Memoized message bubbles** — `React.memo` prevents re-rendering unchanged messages for performance

### Sidebar
- **Recipient Profile Cards** — Dynamically displays each recipient's preferences and allergies, updated in real-time after each response
- **Category Grid** — Quick-access grid for gift categories (Cakes, Flowers, Electronics, etc.)


### Authentication
- **Split-screen design** — Login/signup page with branded left panel and form on the right
- **JWT token management** — Tokens stored in `localStorage`, auto-attached to requests via axios interceptor
- **Auto-redirect on 401** — Expired tokens trigger automatic logout and redirect to login page

---

## API Integration

The `services/api.js` module handles all backend communication:

| Function | Method | Endpoint | Description |
|---|---|---|---|
| `signUp(email, pass)` | POST | `/auth/signup` | Register a new user |
| `signIn(email, pass)` | POST | `/auth/signin` | Login (returns JWT) |
| `createSession()` | GET | `/chat/session` | Create a new chat session |
| `getProfile()` | GET | `/chat/profile` | Fetch semantic profile |
| `sendMessageStream(...)` | POST | `/chat` | Send message with SSE callbacks |


The function uses the native `fetch` API (not axios) to read the SSE stream via `ReadableStream`, parsing `data:` events as they arrive.

---

## Getting Started

### Prerequisites
- Node.js 20.9+
- Backend API 

### Setup

```bash
# Install dependencies
npm install

# Configure environment
cp .env.sample .env
# Edit .env:
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API base URL | `http://localhost:8000` |


---
