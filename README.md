# Instagram Automation Server Bot

[![Project Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)](https://github.com/your-github-username/your-repo-name)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-blueviolet.svg)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3+-orange.svg)](https://docs.celeryq.dev/en/stable/)
[![CI/CD](https://github.com/ashishram7/deploy-test-insta-bot/actions/workflows/buildrun.yaml/badge.svg)](https://github.com/ashishram7/deploy-test-insta-bot/actions/workflows/buildrun.yaml)

## Overview

This project is a powerful and flexible Instagram automation server bot built using Python, FastAPI, and Celery. It's designed to intelligently handle Instagram Direct Messages (DMs) and comments by leveraging sentiment analysis and a Language Model (Google Gemini) for automated responses. The bot listens for real-time events from Instagram via webhooks, allowing for proactive engagement with your audience.

**Key Features:**

*   **Real-time Instagram Webhook Handling:**  Receives and processes Instagram webhook events for direct messages and comments.
*   **Webhook Signature Verification:**  Ensures the security of incoming webhooks by verifying signatures from Meta.
*   **Intelligent Response Automation:**
    *   **Sentiment Analysis:** Uses NLTK's VADER to analyze the sentiment of incoming messages and comments (Positive/Negative).
    *   **Language Model Integration (Google Gemini):** Generates contextually relevant responses to DMs based on sentiment and conversation history.
    *   **Default Responses:** Fallback responses are used for sentiment-based replies when the Language Model is unavailable or fails.
*   **Direct Message Automation:**
    *   Manages conversations and queues messages for each conversation.
    *   Schedules delayed responses using Celery to mimic human-like interaction.
    *   Responds to new messages within existing conversations, rescheduling response tasks dynamically.
*   **Comment Automation:**
    *   Automatically replies to Instagram comments based on sentiment (Positive/Negative) with default responses.
    *   Schedules delayed comment replies using Celery.
*   **Account Management:** Stores and retrieves Instagram access tokens securely using an SQLite database, allowing for multi-account support (expandable).
*   **Scalable Task Processing:** Utilizes Celery for asynchronous task management, ensuring efficient handling of responses and preventing blocking the main API server.
*   **Real-time Event Streaming (SSE):** Provides a Server-Sent Events endpoint (`/events`) to stream webhook events in real-time to connected clients for monitoring and debugging.
*   **Health Monitoring:** Includes `/ping` and `/health` endpoints for server health checks and uptime monitoring.
*   **Configuration via Environment Variables:**  Easily configure sensitive information (API keys, tokens) using a `.env` file.
*   **Detailed Logging:**  Comprehensive logging for debugging and monitoring bot activity.
*   **Easy Setup:**  Simple installation and configuration process.

## Tech Stack
*   **Backend Framework:** [FastAPI](https://fastapi.tiangolo.com/) (for building the API server)
*   **Asynchronous Task Queue:** [Celery](https://docs.celeryq.dev/en/stable/) (for managing background tasks like sending responses)
*   **Language Model (LLM):** [Google Gemini API](https://ai.google.dev/gemini-api) (for generating dynamic DM responses)
*   **Sentiment Analysis:** [NLTK (VADER)](https://www.nltk.org/howto/vader.html) (for sentiment analysis of text)
*   **Database:** [SQLite](https://www.sqlite.org/index.html) (for storing account access tokens - easily replaceable with other databases)
*   **Real-time Communication:** [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events) via `sse_starlette`
*   **HTTP Client:** [requests](https://requests.readthedocs.io/en/latest/) (for making API calls to Instagram and Google Gemini)
*   **Environment Management:** [python-dotenv](https://pypi.org/project/python-dotenv/) (for loading environment variables from `.env` file)
*   **Dependency Management:** [pip](https://pip.pypa.io/en/stable/)

## Setup and Installation

### Local Development Setup

1. **Prerequisites:**
    - Python 3.11+
    - Redis (for production-like setup):
      ```bash
      # Ubuntu/Debian
      sudo apt-get install redis-server
      # MacOS
      brew install redis
      ```

2. **Clone Repository:**
    ```bash
    git clone https://github.com/your-github-username/your-repo-name.git
    cd your-repo-name
    ```

3. **Environment Variables:**
    Create `.env` file:
    ```env
    APP_SECRET="your_meta_app_secret"
    VERIFY_TOKEN="your_verify_token"
    GEMINI_API_KEY="your_gemini_api_key"
    INSTAGRAM_ACCOUNT_ID="your_instagram_account_id"
    # For Redis production setup:
    # CELERY_BROKER_URL="redis_instance_internal_url"
    # CELERY_RESULT_BACKEND="redis_instance_internal_url"
    ```

4. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    python -c "import nltk; nltk.download('vader_lexicon')"
    ```

5. **Run Services:**
    ```bash
    # Terminal 1 - Celery Worker
    celery -A server.celery worker --loglevel=info
    
    # Terminal 2 - FastAPI Server
    uvicorn server:app --reload --host 0.0.0.0 --port 8000
    ```

### Production Deployment on Render

1. **Redis Instance:**
    - Create Redis instance on Render
    - Note connection URL: `redis://<username>:<password>@<host>:<port>`

2. **Web Service:**
    - **Build Command:**
      ```bash
      pip install -r requirements.txt && python -c "import nltk; nltk.download('vader_lexicon')"
      ```
    - **Start Command:**
      ```bash
      bash -c "celery -A server.celery worker -l info & uvicorn server:app --host 0.0.0.0 --port 8000"
      ```

3. **Environment Variables:**
    ```env
    APP_SECRET="your_meta_app_secret"
    VERIFY_TOKEN="your_verify_token"
    GEMINI_API_KEY="your_gemini_api_key"
    INSTAGRAM_ACCOUNT_ID="your_instagram_account_id"
    CELERY_BROKER_URL="redis://your-redis-url:6379/0"
    CELERY_RESULT_BACKEND="redis://your-redis-url:6379/0"
    ACCOUNTS='{"INSTAGRAM_ACCOUNT_ID": "INSTAGRAM_ACCESS_TOKEN"}'
    ```

4. **Webhook Configuration:**
    - Use Render domain: `https://your-service.onrender.com/webhook`

## CI/CD Pipeline

Automated testing with GitHub Actions:
- Runs on every push to `main` branch
- Executes unit tests with pytest
- Verifies server health endpoints
- Workflow file: `.github/workflows/buildrun.yaml`

## Usage

1. **Webhook Setup:**
    - In Meta Developer Portal:
      - Callback URL: `https://your-domain/webhook`
      - Verify Token: Your `VERIFY_TOKEN`
      - Subscribe to: messages, comments, mentions

2. **Account Management:**
    ```bash
    curl -X POST "http://localhost:8000/accounts" \
      -H "Content-Type: application/json" \
      -d '{"account_id": "YOUR_ACCOUNT_ID", "access_token": "YOUR_ACCESS_TOKEN"}'
    ```

3. **Endpoints:**
    - `GET /ping`: Server status check
    - `GET /health`: Detailed system metrics
    - `GET /events`: Real-time event stream
    - `GET /webhook_events`: Stored webhook events

## Customization

1. **Response Messages:**
    - Modify `default_dm_response_positive/negative` in `server.py`
    
2. **LLM Prompts:**
    - Edit `collection_system_prompt/system_prompt.txt`

3. **Sentiment Threshold:**
    - Adjust `analyze_sentiment` thresholds in `server.py`

4. **Task Delays:**
    - Modify `random.randint()` values in webhook handlers

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/awesome-feature`
3. Commit changes: `git commit -m "Add awesome feature"`
4. Push to branch: `git push origin feature/awesome-feature`
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contact

For issues and feature requests:
- [Open GitHub Issue](https://github.com/your-github-username/your-repo-name/issues)
- Email: your.email@example.com

**Disclaimer:** Use this bot in compliance with Instagram's terms of service. Avoid spammy behavior that might violate platform policies.