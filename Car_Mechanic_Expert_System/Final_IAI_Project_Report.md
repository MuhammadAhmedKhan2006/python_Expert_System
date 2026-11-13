# Car Mechanic Expert System
## A Rule-Based Decision Support Tool — IAI Project Report

**Course:** Introduction to Artificial Intelligence (IAI)
**Submitted to:** Sir Wasiq Noor
**Submitted by:** M Ahmed Khan
**Roll Number:** CT-245
**Tagline:** Decide. Defend. Drive safe.

---

## 1. Title and Overview

**Car Mechanic Expert System: A Rule-Based Decision Support Tool**

This project is called the **IAI Expert System: Car Mechanic Assistant**. It is a web
application that helps a normal car owner understand how serious a car problem is. It is
built with Python and Streamlit and works in English and Urdu (right-to-left layout).

The system asks simple questions, checks the answers against a knowledge base of rules,
calculates a risk score, decides an urgency level, tells the user whether the car can be
driven, explains *why* it made that decision, suggests probable faults with evidence, and
produces a downloadable report that can be shown to a mechanic.

It is a **rule-based expert system**. It does not replace a qualified mechanic and it never
gives a final diagnosis — it only supports the owner in taking a safe and sensible decision.

## 2. Introduction and Problem Statement

Car problems are confusing for most people. When a warning light turns on or the car makes a
strange noise, the owner often does not know if the car is safe to drive, if it can wait until
next week, or if it needs a tow truck right now. Because of this, people either panic and
spend too much money, or they ignore a serious problem and put their life in danger.

A **decision support tool** helps in this situation. It asks simple questions, checks the
answers against a set of rules, and gives a clear suggestion with reasons.

The system demonstrates the four core IAI concepts required for this project:

| IAI requirement | Demonstrated by |
|---|---|
| **Decision making** | Risk scoring → 4 urgency levels → drive-or-stop decision |
| **Decision support system** | Explanations, action plans, inspection roadmap, downloadable reports, safety warnings |
| **Inferencing** | Forward-chaining rule chain, guided-mode triage voting, fault-pattern matcher with evidence |
| **Diagnosis** | Ranked probable faults with supporting/contradictory/missing evidence, honest insufficient-evidence handling |

## 3. How the System Works

### 3.1 Workflow

1. The user chooses one of **10 problem categories**: engine will not start, overheating,
   brakes, strange noise or vibration, battery/electrical, tyres, oil leak or smoke, AC,
   steering, and gear or clutch.
2. If the user does not know the problem, **Guided mode** asks 16 screening questions and
   finds the closest matching problem (triage voting).
3. A decision tree then asks Yes/No questions one by one; some steps ask for a report value
   (battery voltage, engine temperature, oil level, tyre pressure, km since service, etc.).
   Every screen has **Back/Next navigation** that preserves all previous answers.
4. Serious answers add risk points inline; each reason is stored as `"English|Urdu|points"`.
   Emergency signs use a safety minimum (`max(risk + points, 70)`) so one dangerous sign can
   never produce a low score.
5. The system calculates a **risk score 0–100** and maps it to an urgency level.
6. The final screen shows the decision, the reasons, an evidence-based diagnosis, an action
   plan, mechanic roadmap, repair verification, save-to-history, and downloadable reports
   (.txt and printable .html).

### 3.2 Urgency levels (decision making)

| Risk score | Level | Meaning |
|---|---|---|
| 0–19 | SELF-CARE | Simple problem; user can do basic checks |
| 20–39 | ROUTINE | Book a service this week |
| 40–69 | URGENT | See a mechanic today |
| 70–100 | EMERGENCY | Stop the car safely and call a tow truck |

Each level produces its own suggestion, "Can I drive?" answer, and 3-step action plan —
computed by `if/elif` rules on `s.risk` in `codebase.py` (`step == 'end'`).

### 3.3 Knowledge base and rule-based approach

The knowledge base is plain Python data inside `codebase.py`:

- **Decision tree**: ~75 question steps across 10 complaint branches; each Yes/No answer
  stores a symptom key in `s.patient_data`, adds risk points, and appends a bilingual reason.
- **Report-value rules**: numeric thresholds (e.g. battery voltage < 11.0 V → +30 risk,
  engine temperature ≥ 120 °C → emergency).
- **Fault-pattern rules** (`probable_causes()`): ~40 structured fault entries, each a list
  of checks `(symptom key, expected answer)` or `(report key, operator, value)`. Example:
  "Worn brake pads" = `brake_grinding == Yes` AND `km_since_service > 15000`.

### 3.4 Inferencing mechanism

Two inference layers work together:

1. **Risk inference (forward chaining)**: symptom answers fire rules that add weighted risk
   points; the accumulated score is then classified into an urgency level.
2. **Fault inference (pattern matching)**: `probable_causes()` matches the collected
   answers/report values against each fault rule and computes a confidence percentage
   (`matched checks / total checks`).

To keep inference honest, two safeguards were added after testing:

- **System scoping** — `COMPLAINT_SYS` maps the chosen complaint to its vehicle system
  (no-start, cooling, brake, noise, electrical, tyre, oil, AC, steering, gearbox). Fault
  rules outside the reported system are skipped entirely.
- **Symptom anchor** — a rule containing Yes/No symptom checks must have at least one
  symptom answered **Yes**. 'No' answers and shared numeric values alone can never suggest
  a fault.

This fixed a real bug: shared report keys (e.g. `km_since_service` is asked in the brake,
AC and gearbox branches) previously let an AC consultation score 50% on a brake rule with
zero brake evidence.

Each suggested fault also reports:

- **support** — the answers that support it ("why suggested"),
- **against** — contradictory evidence that weakens it,
- **missing** — evidence never collected that a mechanic should check.

Confidence is labelled **Strong (≥75%)**, **Limited (50–74%)**, or **Insufficient (<50%)**.
If nothing reaches 50%, the app honestly shows: *"Insufficient information to identify a
probable fault. Please consult a qualified mechanic for physical inspection."* — it never
invents a fault to fill the screen. Multiple faults can be shown when evidence justifies
them.

### 3.5 Diagnosis vs. mechanic-confirmed findings

The AI output is always labelled a **preliminary, evidence-ranked hypothesis**, never a
final diagnosis. The app separates:

- **AI suggestions** (`probable_causes()`) — ranked hypotheses with evidence.
- **Mechanic-confirmed findings** — recorded separately through the repair-verification
  form (below) and stored in `data/inspections.json`.

A mandatory warning is shown on the result screen, inside both downloadable reports, and
in the verification section: the tool is decision support only; a qualified mechanic must
verify before any repair; the user must not attempt self-repair of serious faults.

## 4. Main Features

### 4.1 Guided mode

16 screening questions for users who do not know their problem. Every "Yes" adds weighted
votes to candidate problem codes (`s.triage`); the highest-voted category is selected, and
the user can accept it or start over.

### 4.2 Back/Next question navigation

- Every rendered step snapshots the full state (risk, reasons, all answers, report values,
  triage votes) into `s.snaps`; forward moves push the previous step onto `s.back_stack`.
- A generic **Back** button appears on every question screen (hidden on the first question
  and on the final result). Restoring the snapshot means re-answering never double-counts
  risk points or triage votes.
- Switching sidebar sections never resets an in-progress diagnosis.

### 4.3 Mechanic Inspection Roadmap (Feature 1)

`features.py` contains:

- `SYSTEM_INFO` — roadmaps for all 10 vehicle systems (component, inspection points,
  standard tests).
- `FAULT_INFO` — ~40 fault-specific entries: targeted test, findings that support the
  fault, findings that weaken it.

`roadmap_panel()` renders one expandable card per suspected fault showing: component/system,
inspection priority (derived from the urgency level), whether the car may be driven before
inspection, the specific test, inspection points, tests a mechanic may perform, supporting
and weakening findings, and missing evidence.

### 4.4 Repair Verification

`verification_panel()` lets the user record the **real mechanic outcome** after inspection:

- Outcome: Fault Confirmed / Fault Not Found / Different Fault Identified / Further Testing Required
- Confirmed fault name, findings, repair details, inspection date, notes.

Records are saved to `data/inspections.json` via `store.py`, are kept strictly separate
from AI predictions, can be linked to a diagnosis (`diagnosis_id`), and are viewable and
deletable in Saved Records.

### 4.5 Diagnosis History (SQLite)

`history.py` uses only Python's built-in `sqlite3` — a single local file `data/iai.db` with
one table:

```sql
diagnoses(id, saved_at, complaint, risk, risk_level,
          answers_json, report_json, causes_json, report_text)
```

A "Save this diagnosis to history" button on the result screen stores the complaint, risk,
level, every answer, report values, top faults, and the full report text. The Saved Records
page lists all records with date/time, complaint, risk + category, expandable full details
(answers, faults, report values, report text), a badge showing whether a mechanic
verification exists, and delete-with-confirmation. Simple `INSERT / SELECT / DELETE`
queries only — no ORM, no external database.

### 4.6 Bilingual UI, themes, reports

- **English/Urdu** one-button switch; Urdu renders right-to-left. All text goes through
  `T(en, ur)` / `t(en, ur)` helpers; reasons are stored bilingual.
- **Light/Dark theme** toggle with CSS custom properties; form inputs, placeholders,
  dropdowns, date pickers and text areas are styled for both themes.
- **Reports**: a `.txt` mechanic handover report and a styled printable `.html` report
  (urgency banner, red verification-warning box, causes table, reasons, action plan).

## 5. Code Explanation (key parts)

### 5.1 Session state and reset (`codebase.py`)

Streamlit re-runs the whole script on every interaction, so `st.session_state` remembers
step, risk score, reasons and answers. `reset_system()` returns to the start screen.

```python
def reset_system():
    s = st.session_state
    s.step = 'start'; s.patient_data = {}; s.report_data = {}
    s.risk = 0; s.reasons = []; s.balloons_done = False; s.area = "-|-"
    s.triage = {}; s.tri_match = ''; s.notice = ''
```

### 5.2 Language system

```python
def T(en, ur):
    return en if st.session_state.lang == 'en' else ur
```

### 5.3 Decision tree and one question

The app is one big `if / elif` chain on `s.step`. A "Yes" stores the symptom, adds risk
points and a bilingual reason, then moves to the next step:

```python
elif step == 'br2':
    # "Do you hear grinding or loud squealing when you brake?"
    if c1.button(YES, key="br2y", type="primary"):
        s.patient_data['brake_grinding'] = "Yes"
        s.risk = max(s.risk + 20, 40)
        s.reasons.append("Grinding / squealing when braking: +20 risk|...|20")
        s.step = 'br3'; st.rerun()
```

### 5.4 Emergency safety minimum

```python
# soft brake pedal → can never score below EMERGENCY
s.risk = max(s.risk + 50, 70)
s.step = 'end'
```

### 5.5 Report-value inputs

```python
val = st.number_input('Battery voltage (V)', min_value=0.0, max_value=20.0,
                      value=12.6, step=0.1, key="ns_bat_in")
if st.button(SUBMIT, key="ns_bat_b", type="primary"):
    s.report_data['battery_voltage'] = val
    if val < 11.0:   s.risk = s.risk + 30
    elif val < 12.2: s.risk = s.risk + 15
    elif val > 15.0: s.risk = s.risk + 20
```

### 5.6 Fault inference (`probable_causes()` in `codebase.py`)

```python
cur_sys = COMPLAINT_SYS.get(pd.get('complaint'), None)   # system scoping
for name_en, name_ur, checks in FAULT_RULES:
    if cur_sys and rule_system(name_en) != cur_sys: continue   # skip other systems
    matched = against = 0; support = []; against_ev = []; missing = []
    has_symptom_check = any(c[0] in SYMPTOMS for c in checks)
    sym_yes = any(pd.get(k) == 'Yes' for k in SYMPTOMS if k in pd)
    if has_symptom_check and not sym_yes: continue   # symptom anchor
    ...  # score each check, collect support/against/missing evidence
    conf = int(round(100 * matched / total))
```

### 5.7 Guided-mode triage

Every screening "Yes" adds weighted votes (`s.triage[code] += weight`); `tri_end` picks the
highest-voted problem code.

### 5.8 Final decision and reports

`step == 'end'` classifies `s.risk` into the four levels, then renders: suggestion, possible
area, drive decision, risk meter + highlighted category grid, mandatory warning,
"Why this decision?", "Defending this suggestion", probable causes with evidence, roadmap,
verification panel, save-to-history button, and both report downloads.

## 6. Project Files

| File | Role |
|---|---|
| `car_ai.py` | Streamlit page: setup, CSS (light/dark), header, disclaimer, language + theme buttons, sidebar section navigation |
| `codebase.py` | Expert-system brain: `T()`, `reset_system()`, `probable_causes()`, `run()` with guided mode, decision tree, risk scoring, final result, reports, history save |
| `features.py` | Roadmap + verification knowledge base, `roadmap_panel()`, `verification_panel()`, `records_page()` (inspections + diagnosis history viewer) |
| `history.py` | SQLite diagnosis history (`data/iai.db`) — save/list/get/delete |
| `store.py` | Simple JSON-file helpers for inspection records (`data/inspections.json`) |

Only **Streamlit** (UI), **sqlite3** (history) and **datetime** (report timestamps) are used —
plain basic Python otherwise. Data files live in `data/` and are created at runtime.

## 7. Technologies Used

- **Python 3** — all logic
- **Streamlit** — the entire web UI (the only UI framework)
- **sqlite3** (built-in) — diagnosis history database
- **JSON files** — mechanic verification records
- **HTML/CSS inside Streamlit markdown** — question cards, risk meter, printable report

## 8. Testing and Results

- `python -m py_compile` on all project files — clean.
- **Brake-bias regression**: an AC consultation (30,000 km since service) previously surfaced
  brake faults → now returns only AC faults. All-No brake answers → empty result +
  insufficient-evidence warning. Overheating, tyre and no-start paths rank correctly.
- **Streamlit AppTest** end-to-end runs:
  - Full questionnaire paths (incl. emergency soft-brake-pedal shortcut) reach the result
    screen with 0 exceptions.
  - Back navigation: answer → back → re-answer keeps risk/reasons consistent (no
    double-counting).
  - Diagnosis save → SQLite row; records page lists it with full details; delete works.
  - Mechanic verification save → `inspections.json`, linked to the diagnosis.
  - Dark and light themes render; form widgets styled for both.
- Live app verified locally at `http://localhost:8501` (HTTP 200).

## 9. Limitations

- The app is **decision support, not a diagnosis** — a qualified mechanic must always verify.
- Fault rules cover the defined patterns for the 10 complaint areas; unusual faults fall back
  to system-level inspection guidance.
- Roadmap inspection points are general guidance, not manufacturer-specific procedures.
- Records persist in local files (`data/*.json`, `data/iai.db`); on ephemeral hosting
  (e.g. Streamlit Cloud) they reset on redeploy.
- A public WAN link requires deployment (e.g. Streamlit Cloud); the app runs locally with
  `streamlit run car_ai.py`.
- The interface is bilingual (English/Urdu); other languages are not included.

## 10. Conclusion

The Car Mechanic Expert System demonstrates all four required IAI concepts with real,
tested logic: rule-based **decision making** (risk → urgency → drive decision), a genuine
**decision support system** (explanations, roadmap, reports, warnings), transparent
**inferencing** (scoped fault matching with supporting/contradictory/missing evidence and
honest insufficient-evidence handling), and preliminary **diagnosis** that is clearly
separated from mechanic-confirmed findings. It stays simple — Python + Streamlit + sqlite3 —
while remaining genuinely useful to a non-expert car owner.
