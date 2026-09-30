# PocketSmart AI — Complete project

A FastAPI + Jinja2 budget recommendation assistant with Home, Party and Jewelry planners, optional Gemini text/image support, account registration/login, session/JWT authentication, SQLite history, INR estimates and retailer search links.

## Documentation alignment
The source document describes Flask in its initial overview but specifies FastAPI in Milestones 3–5 and the conclusion. This build consistently uses FastAPI. The document's “Gemini 1.5 Flash Pro” wording is retained as the intended model family, but the exact model identifier is configurable because availability depends on the Google AI account. Retailer links are search links, not live inventory integrations; no vendor API credentials were provided.

## Complete folder structure
```text
pocketsmart-ai/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── web.py
│   │   └── api.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── gemini_utils.py
│   │   └── recommendations.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── planner.html
│   │   └── history.html
│   └── static/
│       ├── styles.css
│       └── app.js
└── tests/
    └── test_app.py
```

## Beginner setup in VS Code (Windows)
1. Install Python 3.11+ from https://www.python.org/downloads/ and enable **Add Python to PATH** during setup.
2. Install VS Code from https://code.visualstudio.com/ and install Microsoft's **Python** extension.
3. Download and extract this ZIP. In VS Code choose **File → Open Folder** and open `pocketsmart-ai`.
4. Choose **Terminal → New Terminal**.
5. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
6. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and activate again. Look for `(.venv)` in the terminal prompt.
7. Press `Ctrl+Shift+P`, choose **Python: Select Interpreter**, and select the Python inside this folder's `.venv`.
8. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
9. Copy `.env.example` and rename the copy to `.env` (not `.env.txt`). For first launch keep `USE_MOCK_AI=true`, leave the API key blank, and change `SECRET_KEY` to a long random string.
10. Start the app from the project root:
    ```powershell
    uvicorn app.main:app --reload
    ```
11. Open http://127.0.0.1:8000. Keep the terminal open; press `Ctrl+C` there to stop the server.

## Enable Gemini AI
1. Create an API key in Google AI Studio.
2. Open `.env` in VS Code and set `GEMINI_API_KEY=your_key`.
3. Set `USE_MOCK_AI=false`.
4. Set `GEMINI_MODEL` to a model name currently enabled for your key (default is `gemini-1.5-flash`; change it if your account no longer offers it).
5. Restart Uvicorn. Never share the key or commit `.env` to GitHub.
The jewelry route accepts an optional JPG, PNG or WEBP image up to 5 MB. If Gemini is unavailable, a clearly labeled fallback demo plan is returned.

## How to use
1. Register using a username, email and password of at least 8 characters.
2. Dashboard opens after registration. Select one of the three planners.
3. Enter the budget and requested details. For Home, select at least one room.
4. Submit. The result area shows category allocations, item estimates, remaining budget and search links.
5. Open History to revisit saved recommendations. Log out from the top navigation.

## Testing
Run:
```powershell
pytest -q
```
Tests cover health, browser registration/login/session, protected endpoint behavior and demo home recommendations. You can also visit `/docs` for interactive API docs and `/health` for the health check.

## API routes
- `GET /health`
- Browser: `GET/POST /register`, `GET/POST /login`, `POST /logout`, `GET /dashboard`, `GET /history`, `GET /planner/home`, `/planner/party`, `/planner/jewelry`
- API: `POST /api/register`, `POST /api/login` (OAuth2 form; returns JWT), `POST /api/logout`, `GET /api/token`, `/api/session-info`, `/api/session-data`, `GET /api/history`
- Recommendations: `POST /api/generate-home` (JSON), `POST /api/generate-party` (JSON), `POST /api/generate-jewelry` (multipart form with optional image)

## Notes and limitations
The app uses SQLite locally and signed sessions for the browser. It is a development/learning project, not production-hardened: before deployment, use HTTPS, a strong secret, CSRF protections, stricter CORS, persistent production database migrations and secure deployment settings. Search links take users to platform search pages; prices are illustrative and are not verified live offers.
