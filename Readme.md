<div align="center">

# 🤖 Agent7

### A personal LinkedIn AI agent you talk to through WhatsApp

Discover jobs and internships, generate comments and posts, publish to LinkedIn after your approval, and let the agent remember your conversations.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-orange)
![Gemma](https://img.shields.io/badge/Model-Gemma%203%204B-green)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Business%20API-25D366?logo=whatsapp&logoColor=white)
![LinkedIn](https://img.shields.io/badge/LinkedIn-API-0A66C2?logo=linkedin&logoColor=white)
![Status](https://img.shields.io/badge/Status-Learning%20Project-purple)

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Why I Built Agent7](#-why-i-built-agent7)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [WhatsApp Webhook Setup](#-whatsapp-webhook-setup)
- [Running Agent7](#-running-agent7)
- [Usage Examples](#-usage-examples)
- [Safety & Approval Flow](#-safety--approval-flow)
- [Security Best Practices](#-security-best-practices)
- [Troubleshooting](#-troubleshooting)
- [Roadmap](#-roadmap)
- [What I Learned](#-what-i-learned)
- [Contributing](#-contributing)
- [License](#-license)
- [About the Author](#-about-the-author)

---

## 🚀 Overview

**Agent7** is a personal AI assistant built around my LinkedIn workflow. I send a message on **WhatsApp**, and Agent7 understands the request, routes it to the right component, performs the task, replies, and remembers useful context.

> The goal is not just to build a chatbot, but a **useful personal AI agent that performs real tasks through connected tools and services.**

```text
"Find AI internships"
        ↓
     Agent7
        ↓
    Jobs Agent
        ↓
Job / Internship Results
```

```text
"Write a LinkedIn post about AI Agents"
        ↓
     Agent7
        ↓
    Post Agent
        ↓
Research + AI-Generated Draft
        ↓
    "OK, SHARE"
        ↓
    LinkedIn API
        ↓
  Post Published
```

---

## 🎯 Why I Built Agent7

I wanted to understand how AI agents actually work by building one myself. Instead of studying concepts in isolation, I connected them in a single practical project:

- LLMs and prompt engineering
- APIs and webhooks
- Tool calling and automation
- Memory systems
- Web research
- Agent-based architecture

Agent7 is my way of **learning by building**.

---

## ✨ Features

### 1. 💬 WhatsApp AI Interface
WhatsApp is the main interface. Rather than switching between apps, I send Agent7 a message and it routes the request to the right functionality.

```text
Find AI Engineer internships
Create a LinkedIn post about AI Agents
Write a comment for this LinkedIn post
```

### 2. 💼 Jobs & Internship Search
A dedicated **Jobs Agent** finds relevant opportunities. Its logic is kept separate from the rest of the system.

```text
Find AI internships
Find Python developer internships
Find AI Engineer jobs
Find GenAI internships
```

### 3. 💬 LinkedIn Comment Generation
Send a LinkedIn post URL and the **Comment Agent** generates a comment. Comments aim to avoid generic AI-sounding text and instead be:

- Natural
- Short
- Professional
- Relevant
- Human-like

### 4. 📝 LinkedIn Post Generation
The **Post Agent** researches a topic and produces a draft. The draft is stored as a **pending post** until you explicitly approve it.

### 5. 🚀 Direct LinkedIn Publishing
After reviewing a draft, reply `OK, SHARE` and Agent7 sends the approved post to the LinkedIn integration. Nothing is published automatically.

### 6. 🧠 Memory
A dedicated `memory` module lets Agent7 keep context across conversations instead of treating each message independently.

```text
User:    My name is Durgaprasad.
Agent7:  Nice to meet you, Durgaprasad.

(later)

User:    What is my name?
Agent7:  Uses stored conversation context when available.
```

### 7. 🤖 Local LLM with Ollama
Agent7 runs **Gemma 3 4B** locally through **Ollama**, so conversational requests do not need to go to a cloud LLM API.

### 8. 🌐 Web Research with Tavily
The Post Agent can use **Tavily** to gather current information before generating content, going beyond the model's built-in knowledge.

```text
Topic → Tavily Search → Relevant Information → LLM → LinkedIn Post
```

---

## 🔄 How It Works

Agent7 is built around one simple principle:

```text
Understand → Route → Process → Respond → Remember
```

| Step | Description |
| ---- | ----------- |
| **Understand** | Receive the WhatsApp message and work out what the user wants |
| **Route** | Send the request to the Post, Jobs, or Comment agent |
| **Process** | Run the task using the LLM, research tools, and APIs |
| **Respond** | Return the result over WhatsApp |
| **Remember** | Save useful context through the memory system |

---

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │     WhatsApp     │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   Agent7 Core    │
                         │  Flask Backend   │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌─────────────┐     ┌─────────────┐     ┌──────────────┐
       │ Post Agent  │     │ Jobs Agent  │     │ Comment Agent│
       └──────┬──────┘     └─────────────┘     └──────────────┘
              │
              ▼
       ┌─────────────┐
       │   Tavily    │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐        ┌─────────────┐
       │   Ollama    │◄──────►│   Memory    │
       │ Gemma 3 4B  │        │   System    │
       └─────────────┘        └─────────────┘

       ┌─────────────┐
       │Integrations │
       │ connect.py  │
       └──────┬──────┘
              │
              ▼
       ┌─────────────┐
       │ LinkedIn API│
       └─────────────┘
```

---

## 📁 Project Structure

```text
Agent7/
│
├── backend/
│   ├── app.py                  # Flask app + WhatsApp webhook + routing
│   ├── pending_posts.json      # Drafts awaiting approval
│   └── memory_sessions.json    # Persisted memory sessions
│
├── posts/
│   └── post_agent.py           # Research + post generation
│
├── comments/
│   └── comment_agent.py        # LinkedIn comment generation
│
├── jobs/
│   └── jobs_agent.py           # Job & internship search
│
├── memory/
│   ├── __init__.py
│   ├── conversation_agent.py
│   ├── conversation_memory.py
│   ├── memory_context.py
│   ├── memory_manager.py
│   └── memory_service.py
│
├── integrations/
│   └── connect.py              # LinkedIn API integration
│
├── .env                        # Secrets (never commit)
├── requirements.txt
└── README.md
```

---

## 🔧 Tech Stack

| Technology | Purpose |
| ---------- | ------- |
| **Python** | Main programming language |
| **Flask** | Backend and webhook server |
| **Ollama** | Local LLM runtime |
| **Gemma 3 4B** | Local language model |
| **WhatsApp Business API** | User interface |
| **Meta Developers** | WhatsApp integration |
| **LinkedIn API** | LinkedIn operations |
| **Tavily** | Web research |
| **JSON** | Lightweight persistent storage |
| **GitHub** | Version control |
| **Docker** | Containerization and deployment learning |

---

## ✅ Prerequisites

Before you start, make sure you have:

- **Python 3.10+**
- **[Ollama](https://ollama.com)** installed and running
- A **Meta Developers** account with a WhatsApp Business app
- A **LinkedIn developer app** and access token
- A **[Tavily](https://tavily.com)** API key
- A public HTTPS URL for the webhook (for local development, a tunneling tool such as ngrok works)

---

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Agent7
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**3. Activate it**

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

**5. Pull the local model**

```bash
ollama pull gemma3:4b
```

---

## 🔐 Configuration

Create a `.env` file in the project root:

```env
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_VERSION=202603

WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_verify_token

TAVILY_API_KEY=your_tavily_api_key
```

| Variable | Description |
| -------- | ----------- |
| `LINKEDIN_ACCESS_TOKEN` | OAuth access token used to publish posts |
| `LINKEDIN_VERSION` | LinkedIn API version header value |
| `WHATSAPP_ACCESS_TOKEN` | Token for sending messages via the WhatsApp Business API |
| `WHATSAPP_PHONE_NUMBER_ID` | ID of the WhatsApp business phone number |
| `WHATSAPP_VERIFY_TOKEN` | A string you choose; used to verify the webhook with Meta |
| `TAVILY_API_KEY` | API key for web research |

> ⚠️ **Never commit real keys or tokens.** Add `.env` to `.gitignore`.

---

## 📡 WhatsApp Webhook Setup

1. Start Agent7 (see below) and expose it through a public HTTPS URL.
2. In the **Meta Developers** dashboard, open your app's **WhatsApp → Configuration** section.
3. Set the **Callback URL** to your public webhook endpoint exposed by `backend/app.py`.
4. Set the **Verify token** to the same value as `WHATSAPP_VERIFY_TOKEN` in your `.env`.
5. Subscribe to the **messages** webhook field.
6. Send a message to your WhatsApp business number to test.

---

## ▶️ Running Agent7

Make sure Ollama is running, then start the backend:

```bash
python backend/app.py
```

Now message your WhatsApp number and Agent7 will respond.

---

## 💡 Usage Examples

### Find jobs

```text
User:    Find AI Engineer internships
Agent7:  Searches via the Jobs Agent → processes results → returns opportunities
```

### Generate a LinkedIn post

```text
User:    Create a LinkedIn post about AI Agents
Agent7:  Researches topic → generates content → returns draft
```

The draft stays **pending** until you approve it.

### Publish the post

```text
User:    OK, SHARE
Agent7:  Pending post → LinkedIn integration → LinkedIn API → Post published
```

### Generate a comment

```text
User:    https://www.linkedin.com/posts/example
Agent7:  LinkedIn post → Comment Agent → generated comment
```

### Use memory

```text
User:    My name is Durgaprasad.
User:    What is my name?
Agent7:  Your name is Durgaprasad.
```

---

## 🔒 Safety & Approval Flow

Important actions require explicit user confirmation. Creating a post and publishing a post are **separate steps**:

```text
Generate → Review → Approve → Publish
```

This prevents a generated draft from being published accidentally. Agent7 only publishes when you send the approval message.

---

## 🛡️ Security Best Practices

- Store all keys and tokens in environment variables, never in source code.
- Keep `.env` in `.gitignore`.
- Rotate any token that may have been exposed.
- Restrict who can message the bot (authentication is on the roadmap).
- Review generated content before approving a publish.
- Treat `pending_posts.json` and `memory_sessions.json` as private data and avoid committing them.

---

## 🩺 Troubleshooting

| Problem | Things to check |
| ------- | --------------- |
| Webhook verification fails | `WHATSAPP_VERIFY_TOKEN` matches the value entered in Meta; the callback URL is public HTTPS |
| No reply on WhatsApp | The server is running, the webhook is subscribed to `messages`, and `WHATSAPP_ACCESS_TOKEN` is valid |
| Model errors | Ollama is running and `gemma3:4b` has been pulled (`ollama list`) |
| Research not working | `TAVILY_API_KEY` is set and valid |
| LinkedIn publish fails | Access token is valid and not expired, required permissions are granted, and `LINKEDIN_VERSION` is current |
| Memory not persisting | The app can read and write `backend/memory_sessions.json` |

---

## 🗺️ Roadmap

- [ ] Better intent classification
- [ ] More advanced tool calling
- [ ] Improved long-term memory
- [ ] More LinkedIn automation
- [ ] Scheduled posts
- [ ] Better job filtering
- [ ] Resume-based job matching
- [ ] Email integration
- [ ] More external tools
- [ ] Better error handling
- [ ] Authentication
- [ ] Production database
- [ ] Cloud deployment
- [ ] Monitoring and logging
- [ ] More autonomous agent workflows

---

## 📚 What I Learned

Building Agent7 taught me far more than how to make a chatbot:

- Building APIs and working with webhooks
- Connecting external services (LinkedIn, WhatsApp)
- Running local LLMs with Ollama
- Prompt engineering and agent architecture
- Memory systems and web research
- Backend development and JSON persistence
- Environment variables and API authentication
- Debugging, Docker, Git and GitHub

The biggest lesson: **the model is only one part of the system.** The real application comes from connecting:

```text
LLM + Tools + APIs + Memory + Logic + User Interface
```

I don't claim to know everything. I'm learning, building, getting stuck, fixing errors, and improving the project step by step.

---

## 🤝 Contributing

Contributions, ideas, and feedback are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📜 License

This project is created for learning, experimentation, and personal development. Please check the repository for the applicable license and usage terms.

---

## 👨‍💻 About the Author

I'm **Durgaprasad**, a CSE student learning and building in AI Engineering. My current focus:

- Artificial Intelligence
- Machine Learning
- Generative AI
- AI Agents
- MCP
- Backend development
- Automation
- Computer Vision

> **Whatever I do, I learn.**
> **Whatever I learn, I build.**
> **Whatever I build, I teach.**

---

<div align="center">

### ⭐ If you find this project interesting

Explore the code, learn from it, and experiment with your own AI agent.
If Agent7 helped you understand AI agents, APIs, memory, or automation, consider giving the repository a star.

</div>