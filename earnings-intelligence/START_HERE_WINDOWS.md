# Windows Setup Guide — Earnings Intelligence

## Prerequisites (install these first)

1. **Python 3.11** — https://www.python.org/downloads/  
   During install: check "Add Python to PATH"

2. **Node.js 20 LTS** — https://nodejs.org/  
   Includes npm automatically

3. **Git for Windows** — https://git-scm.com/download/win

---

## Step 1 — Clone the project

Open **PowerShell** and run:

```powershell
cd C:\Users\cmelillo\Documents
git clone <your-repo-url> earnings-intelligence
cd earnings-intelligence
```

Or if you downloaded a zip, extract it to `C:\Users\cmelillo\Documents\earnings-intelligence\`.

---

## Step 2 — Backend setup (run once)

```powershell
cd C:\Users\cmelillo\Documents\earnings-intelligence\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

In `.env`, set your API key:
```
ANTHROPIC_API_KEY=sk-ant-...your key here...
NEWS_API_KEY=                  # optional, from newsapi.org
SECRET_KEY=any-random-string
```

> **If PowerShell blocks script execution**, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

---

## Step 3 — Frontend setup (run once)

Open a **second PowerShell window**:

```powershell
cd C:\Users\cmelillo\Documents\earnings-intelligence\frontend
npm install
```

---

## Step 4 — Run the app

**PowerShell window 1 (backend):**
```powershell
cd C:\Users\cmelillo\Documents\earnings-intelligence\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**PowerShell window 2 (frontend):**
```powershell
cd C:\Users\cmelillo\Documents\earnings-intelligence\frontend
npm run dev
```

Then open **http://localhost:3000** in your browser.

---

## Quick test (no browser needed)

With the backend running, open a third PowerShell window:

```powershell
# Health check
Invoke-RestMethod http://127.0.0.1:8000/api/health

# Full NVDA report
Invoke-RestMethod "http://127.0.0.1:8000/api/report/NVDA?period=Q4+2024"

# Download PDF
Invoke-WebRequest "http://127.0.0.1:8000/api/report/NVDA/pdf?period=Q4+2024" -OutFile nvda_report.pdf
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not found | Reinstall Python with "Add to PATH" checked |
| `npm` not found | Reinstall Node.js, restart PowerShell |
| Port 8000 in use | Change to `--port 8001` in backend start command |
| Port 3000 in use | Vite will auto-pick 3001 — check terminal output |
| WeasyPrint install fails | Run: `pip install weasyprint==60.2 pydyf==0.9.0` |
| CORS error in browser | Make sure backend is running on port 8000 |
