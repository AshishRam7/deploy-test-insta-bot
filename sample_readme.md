# Instagram Automation Server Bot

![Instagram Automation Bot](path/to/your/image.png)

[![Project Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/your-github-username/your-repo-name)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-blueviolet.svg)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3+-orange.svg)](https://docs.celeryq.dev/en/stable/)

## Overview

This project is a robust and scalable **Instagram Automation Server Bot** built using **FastAPI** and **Celery**. It enables **intelligent automation of Instagram Direct Messages (DMs) and comments** through **sentiment analysis** and **Google Gemini (LLM) integration**. The bot listens for **real-time events** via **Instagram Webhooks**, ensuring dynamic and proactive engagement with followers.

### **Key Features**

- **Webhook Handling:** Real-time processing of Instagram messages and comments.
- **Security:** Webhook signature verification for authenticity.
- **Intelligent Responses:**
  - **Sentiment Analysis (VADER - NLTK)** for Positive/Negative categorization.
  - **Google Gemini API** for context-aware message replies.
  - **Fallback Responses** when the LLM is unavailable.
- **Direct Message Automation:**
  - Queueing and scheduling responses for human-like interaction.
  - Handling ongoing conversations dynamically.
- **Comment Automation:**
  - Auto-reply to comments based on sentiment.
  - Scheduled responses to avoid bot-like behavior.
- **Account Management:** Secure storage of **Instagram Access Tokens** in **SQLite**.
- **Scalable Architecture:** Background task execution using **Celery**.
- **Real-time Monitoring:** **Server-Sent Events (SSE)** endpoint to stream webhook events.
- **Health Monitoring:** `/ping` and `/health` endpoints for uptime checks.
- **Configuration Management:** Environment variables stored securely in `.env`.
- **Detailed Logging:** Comprehensive logs for debugging and performance analysis.
- **Ease of Deployment:** Ready for **local development** and **cloud deployment** (e.g., **Render**).

---

## **Architecture**

![System Architecture](path/to/architecture-diagram.png)

The system consists of three primary components:

1. **FastAPI Web Server**: Handles incoming webhook events, processes them, and triggers automation logic.
2. **Celery Task Queue**: Manages background tasks asynchronously to avoid blocking the API server.
3. **Redis** (Broker & Result Backend): Used by Celery for task scheduling and execution.

**Workflow:**
1. Instagram sends a webhook event (message/comment) → Received by FastAPI.
2. FastAPI verifies the webhook signature and extracts the event data.
3. Sentiment analysis and response generation are handled asynchronously via Celery.
4. Responses are either **default sentiment-based** or generated dynamically using **Google Gemini API**.
5. Replies are sent back to Instagram using the Graph API.

---

## **Installation & Setup**

### **Local Development Setup**

#### **Prerequisites**
- Python 3.11+
- Redis (for Celery broker)

```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Install Redis (MacOS)
brew install redis
```

#### **Clone Repository & Setup Environment**

```bash
git clone https://github.com/your-github-username/your-repo-name.git
cd your-repo-name
```

#### **Configure Environment Variables**
Create a `.env` file and add:

```ini
APP_SECRET="your_meta_app_secret"
VERIFY_TOKEN="your_verify_token"
GEMINI_API_KEY="your_gemini_api_key"
INSTAGRAM_ACCOUNT_ID="your_instagram_account_id"
ACCOUNTS={"IG_ACCOUNT_ID_1":"IG_ACCESS_TOKEN_1", "": "", ...}
CELERY_BROKER_URL="redis://localhost:6379/0"
CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

#### **Install Dependencies**

```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon')"
```

#### **Run Services**

```bash
# Terminal 1 - Start Celery Worker
celery -A server.celery worker --loglevel=info

# Terminal 2 - Start FastAPI Server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

---

## **Meta App Setup for Webhooks**

1. **Create a Meta App** on the [Meta Developer Dashboard](https://developers.facebook.com/).
2. **Navigate to Subscriptions** → Subscribe to **Instagram**.
3. Click **Setup with Instagram Login**.
4. Set the Webhook URL as `https://<public_url>/webhook` and use the verification token from `.env`.
5. Click **Verify Webhook Server**.
6. **Add Instagram Tester Accounts**:
   - Click **Add Account**.
   - If access token is not displayed, navigate to **App Roles** → **Roles Subsection**.
   - Click **Add People**, select **Instagram Tester Account**, and provide username & login.
   - Go to **API Setup with Instagram Login** → **Generate Token**.
   - If a blank white screen appears, inspect the page and search for `IGAA`.
   - Copy the token and store it securely.

<descriptive_img>

---

## **Deployment on Render**

### **1. Provision Redis Instance**
- Create a **Redis instance** on Render.
- Obtain connection URL: `redis://<username>:<password>@<host>:<port>`.

### **2. Deploy Web Service**
- Create a new **Web Service** on Render.
- Connect the GitHub repository.
- Set up **Build Command:**

```bash
pip install -r requirements.txt && python -c "import nltk; nltk.download('vader_lexicon')"
```

- Set up **Start Command:**

```bash
bash -c "celery -A server.celery worker -l info & uvicorn server:app --host 0.0.0.0 --port 8000"
```

- Set `/health` as the health check endpoint.

---

## **API Documentation**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/ping` | Server status check |
| `GET` | `/health` | System metrics and health check |
| `GET` | `/events` | Stream webhook events in real-time |
| `POST` | `/webhook` | Handles Instagram webhook events |

---

## **License**

[MIT License](LICENSE)

---

## **Contact**

- [GitHub Issues](https://github.com/your-github-username/your-repo-name/issues)
- Email: `your.email@example.com`

