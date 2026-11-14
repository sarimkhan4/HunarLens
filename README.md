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

Five tests marked `full_data` read the complete processed dataset, including test rows. They are excluded by default while the test split is sealed. After Stage 8, run them with `python -m pytest -q -m full_data`, or run the entire suite with `python -m pytest -q -m ""`.
