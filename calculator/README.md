# Python Calculator

A calculator in three flavours that share one logic module:

| Version | Command | Where it runs |
|---|---|---|
| Command line | `python main.py` | Your terminal |
| Desktop (Tkinter) | `python main.py --gui` | Your computer |
| Web (Flask) | `python app.py` | Browser, and deployable on Render |

## Features
- Safe expression parser (no `eval`): `2 + 3 * (4 - 1)`, `sqrt(16) + 2^3`
- Operators `+ - * / // % ^`, functions `sqrt sin cos tan log ln abs`, constants `pi e`
- Memory (`M+ M- MR MC`) in the CLI and desktop versions
- History: saved to `history.json` (CLI/desktop) or in the browser (web)
- Unit tests with pytest

## Project structure
```
calculator/
├── main.py             # CLI + launcher for the GUI
├── logic.py            # calculator engine (no UI code)
├── gui.py              # Tkinter desktop app
├── app.py              # Flask web app (deployed on Render)
├── templates/index.html
├── static/             # style.css, script.js
├── tests/              # test_logic.py, test_app.py
├── history.json
├── requirements.txt    # runtime deps (used by Render)
├── requirements-dev.txt
├── render.yaml         # Render blueprint
└── README.md
```

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python main.py            # CLI
python main.py --gui      # desktop
python app.py             # web at http://127.0.0.1:5000
```

## Run tests
```bash
pytest
```

## Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: Python calculator"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Deploy on Render
1. Sign in at [render.com](https://render.com) and connect your GitHub account.
2. **New +** → **Web Service** → select this repository.
3. Use these settings (or choose **Blueprint** and Render reads `render.yaml`):
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
   - **Health check path:** `/health`
4. Click **Create Web Service**. Your calculator will be live at `https://<name>.onrender.com`.

Notes:
- The Tkinter GUI needs a desktop and can't run on Render. Render serves the web version.
- On Render's free plan the service sleeps after inactivity, so the first load can take about a minute.
