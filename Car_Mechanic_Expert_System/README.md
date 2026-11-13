# IAI Expert System: Car Mechanic Assistant

A rule-based expert system that helps car owners understand how serious a car problem is.
It asks simple Yes/No questions, calculates a risk score, picks an urgency level
(SELF-CARE / ROUTINE / URGENT / EMERGENCY), explains its reasoning, suggests probable
faults with evidence, gives a mechanic inspection roadmap, and produces downloadable
reports — in **English and Urdu**.

> This is a **decision support tool, NOT a diagnosis**. Always consult a qualified mechanic.

## Features

- **70+ questions** across 10 car-problem categories + 16-question guided mode
- **Decision making**: risk score (0–100) → urgency level → drive-or-stop decision
- **Inferencing**: ~40 fault rules with system scoping, symptom anchoring, and
  supporting / contradictory / missing evidence
- **Diagnosis**: ranked probable causes (Strong / Limited / Insufficient), honest
  insufficient-evidence handling, never invents faults
- **Mechanic inspection roadmap** per suspected fault
- **Repair verification** form — mechanic outcomes stored separately from AI predictions
- **Diagnosis history** — SQLite (`data/iai.db`) save / view / delete
- **Back/Next navigation** on every question — answers are never lost
- **Bilingual UI** (English/Urdu, RTL) + **light/dark themes**
- **Reports**: downloadable `.txt` and printable `.html` mechanic reports

## Run locally

```bash
pip install -r requirements.txt
streamlit run car_ai.py
```

Open http://localhost:8501

## Project structure

| File | Role |
|---|---|
| `car_ai.py` | Streamlit page: setup, CSS themes, header, language/theme buttons, section navigation |
| `codebase.py` | Expert-system brain: decision tree, risk scoring, `probable_causes()` inference, reports, history save |
| `features.py` | Inspection roadmap + repair verification knowledge base, saved-records page |
| `history.py` | SQLite diagnosis history (built-in `sqlite3`, `data/iai.db`) |
| `store.py` | JSON-file storage helpers for verification records (`data/inspections.json`) |
| `requirements.txt` | `streamlit` |
| `Final_IAI_Project_Report.md` | Full project report |

## Deployment (Streamlit Cloud)

See `DEPLOY.md`. The app auto-redeploys on every `git push` once the repo is connected.

## Limitations

- Decision support only — not a final diagnosis; professional verification is mandatory.
- Fault rules cover the defined patterns for the 10 complaint areas.
- `data/` records are local files (ephemeral on cloud hosting).
