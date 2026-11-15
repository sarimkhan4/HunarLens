# HunarLens

HunarLens is a semester project studying youth unemployment vulnerability in Pakistan. The current app is a placeholder; no model or dataset has been built yet.

## Setup

Use Python 3.12. From the repository root, create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest -q
streamlit run app/streamlit_app.py
```

On macOS or Linux, use `python3.12 -m venv .venv` and `source .venv/bin/activate` instead. The public Streamlit URL will be added after the team configures deployment.

The planned data sources are described in [data/README.md](data/README.md). Stage instructions and decisions are in `docs/`; reusable code is in `src/hunarlens/`.

Five tests marked `full_data` read the complete processed dataset, including test rows. Stage 8 has opened the test split, so they are enabled in the default `python -m pytest -q` run. To run only those checks, use `python -m pytest -q -m full_data`.
