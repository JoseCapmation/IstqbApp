# IstqbApp

CLI trainer for **ISTQB Certified Tester Foundation Level (CTFL)**-style study: curated theory chapters, chapter practice quizzes, and a 40-question mock exam. Content ships as JSON; PDFs are optional for end users.

## Quick start

1. **Python 3.11+** recommended.
2. Install dependencies (from the repo root):

   ```bash
   cd istqb_trainer
   py -m pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   py main.py
   ```

   Always run `main.py` from inside the **`istqb_trainer`** folder so paths to `data/` resolve correctly.

## What you need

- **`istqb_trainer/data/theory.json`** and **`istqb_trainer/data/questions.json`** are required. They are included in this repo.
- **PDFs are not required** to use the trainer day to day.
- Optional: copy **`istqb_trainer/.env.example`** to **`istqb_trainer/.env`** if you use `PDF_DIR` or optional AI question generation (see comments in `.env.example`).

## Using the app

- Progress is saved in **`istqb_trainer/data/progress.json`** (ignored by git so your machine keeps its own state).
- **Continue** runs theory in short chunks (**Enter** next part, **Q** back to menu, **S** restart chapter), then a short chapter quiz (70% to pass the chapter).
- From the menu you can use **P** for practice only (skip reading) or **M** for a full mock exam (40 questions, 65% pass, no per-question feedback until the end).
- **R** resets all progress (with confirmation). **Q** quits and saves.

## Rebuilding question/theory data (maintainers)

With syllabus and sample PDFs under **`istqb_trainer/samplePdfs/`** (or set **`PDF_DIR`** in `.env`**):

```bash
cd istqb_trainer
py scripts/build_data.py
```

- By default, **`theory.json`** is preserved; use **`py scripts/build_data.py --theory-from-pdf`** to regenerate theory from the syllabus PDF.
- **`py main.py --rebuild`** refreshes JSON from PDFs when PDFs are present (same theory-preserving behavior as the build script).

## Disclaimer

Study text and questions are aligned with public CTFL-style material and sample papers; the **official ISTQB syllabus and accredited materials** remain the authority for certification. This project is for **personal practice** only.

## Web UI (React + FastAPI)

A polished web interface is included alongside the CLI. It exposes the same data and progress, so both modes share `data/progress.json`.

### Development (two terminals)

**Terminal 1 — API backend** (run from `istqb_trainer/`):

```bash
cd istqb_trainer
py -m pip install -r requirements.txt
py -m uvicorn backend.app:app --reload --port 8000
```

**Terminal 2 — React frontend** (run from `frontend/`):

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

### Production (single command)

Build the frontend once, then serve everything from the FastAPI process:

```bash
cd frontend
npm run build
cd ../istqb_trainer
py -m uvicorn backend.app:app --port 8000
```

Open **http://localhost:8000**.

### Features

- Dashboard with progress ring, chapter list, stat cards, and quick actions
- Paged theory reader with auto-saved reading position per chapter
- Per-chapter practice quiz (3–5 questions, 70% to pass)
- 40-question mock exam (65% to pass, results revealed at the end)
- Expandable per-question review with correct answer and explanation
- Reset all progress with typed confirmation
- Mobile-friendly sidebar layout

## Repository layout

| Path | Purpose |
|------|---------|
| `istqb_trainer/main.py` | CLI entrypoint |
| `istqb_trainer/data/` | Bundled theory + questions JSON; local `progress.json` |
| `istqb_trainer/modules/` | Learning, quiz, exam, progress |
| `istqb_trainer/backend/` | FastAPI app, routes, and pure-logic services |
| `istqb_trainer/scripts/build_data.py` | Maintainer build from PDFs |
| `frontend/` | Vite + React + Tailwind web UI |

## License / copyright

Respect ISTQB and original PDF publishers’ terms when copying or redistributing syllabus or exam PDFs. This repo’s curated JSON is intended for private learning use.
