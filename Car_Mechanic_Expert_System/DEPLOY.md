# Deploying to Streamlit Cloud (auto-update on push)

Streamlit Community Cloud redeploys automatically every time you push to the
connected GitHub branch — no manual steps needed after the first setup.

## One-time setup

1. Push this repo to GitHub (already done — `origin` is configured).
2. Go to https://share.streamlit.io → **Create app** → **Deploy from GitHub**.
3. Select repository `MuhammadAhmedKhan2006/python_Expert_System`, branch `master`.
4. Set:
   - **Main file path:** `Car_Mechanic_Expert_System/car_ai.py`
   - **Requirements file:** `Car_Mechanic_Expert_System/requirements.txt`
5. Click **Deploy**. Wait ~2 minutes, copy the `*.streamlit.app` URL.

## After every code change

```bash
git add .
git commit -m "UI fixes and enhancements"
git push
```

Streamlit Cloud detects the push and redeploys automatically — the live link updates
by itself within a few minutes.

## Notes

- `data/` (SQLite history + JSON records) is git-ignored and ephemeral on Streamlit
  Cloud — records reset if the app is redeployed from scratch.
- The app needs no secrets or API keys.
