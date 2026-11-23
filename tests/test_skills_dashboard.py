# What: checks the cached survey dashboard and its classic fallback.
# Why: the interface must use approved aggregate tables and preserve warnings.
# Viva: a displayed number is copied from a saved survey table, not typed by hand.
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

import pandas as pd
from streamlit.testing.v1 import AppTest
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "app"))
from dashboard_component import aggregate_number, static_data


def test_five_item_navigation_and_mobile_layout():
    html = (ROOT / "app/dashboard.html").read_text(encoding="utf-8")
    for nav in [html.split('<nav class="nav">', 1)[1].split('</nav>', 1)[0],
                html.split('class="bottom-nav">', 1)[1].split('</nav>', 1)[0]]:
        assert re.findall(r'data-page="([^"]+)"', nav) == ["overview", "skills", "explorer", "performance", "methodology"]
    css = (ROOT / "app/dashboard.css").read_text(encoding="utf-8")
    assert "repeat(5,minmax(0,1fr))" in css and "prefers-reduced-motion" in css


def test_all_skills_payload_values_match_aggregate_tables():
    data = static_data()
    tables = {name: frame for name, frame in data.items() if name.startswith("skills_")}
    assert len(tables) >= 13
    numeric = {"n", "positive_n", "employed_n", "unemployed_n", "estimate", "difference", "ci_low", "ci_high"}
    for name, actual in tables.items():
        expected = pd.read_csv(ROOT / "reports/tables" / f"{name}.csv", keep_default_na=False)
        for column in numeric.intersection(expected.columns):
            expected[column] = expected[column].map(aggregate_number)
        pd.testing.assert_frame_equal(actual, expected)


def test_skills_code_has_no_typed_statistics_or_causal_words():
    html = (ROOT / "app/dashboard.html").read_text(encoding="utf-8").split('id="page-skills">', 1)[1].split('id="page-explorer">', 1)[0]
    js = (ROOT / "app/skills_dashboard.js").read_text(encoding="utf-8")
    classic = (ROOT / "app/streamlit_app.py").read_text(encoding="utf-8").split("def skills_gap():", 1)[1].split("def main():", 1)[0]
    text = (html + js + classic).lower()
    assert not any(word in text for word in ["causes", "because of", "leads to", "reduces unemployment", "wasted"])
    assert not re.search(r"\b\d+\.\d+\s*%", text)
    assert "skills.mismatch_occupation_variants" in js
    assert "mode unstable; bootstrap range" in js


def test_classic_skills_view_renders_tables_and_filters():
    app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90)
    app.query_params["classic"] = "1"
    with threadpool_limits(limits=1):
        app.run()
        app.radio(key="navigation").set_value("Skills gap").run()
    assert not app.exception and not app.error
    assert len(app.dataframe) >= 9
    assert any(metric.label == "Approximate NEET / PBS NEET" for metric in app.metric)
    assert app.selectbox(key="skills_classic_group").value == "All youth"
    assert app.selectbox(key="skills_classic_definition").value == "Strict: all employed"


def test_unstable_rows_show_full_bootstrap_range():
    if not shutil.which("node"):
        import pytest
        pytest.skip("Node is unavailable")
    tables = static_data()
    rows = pd.concat([tables["skills_mismatch_by_occupation"], tables["skills_mismatch_occupation_variants"]])
    rows = rows.loc[rows.reliability.eq("mode unstable")]
    assert len(rows) > 0
    source = (ROOT / "app/skills_dashboard.js").read_text(encoding="utf-8")
    code = ("const m=await import('data:text/javascript;base64,'+Buffer.from(process.argv[1]).toString('base64'));"
            "for(const r of JSON.parse(process.argv[2])){const s=m.formatSkillsEstimate(r);"
            "const bounds=m.skillsPercent(r.ci_low)+'–'+m.skillsPercent(r.ci_high);"
            "if(!s.includes('mode unstable; bootstrap range '+bounds)||s.includes(' · interval '))process.exit(1)}")
    subprocess.run(["node", "--input-type=module", "-e", code, source, rows.to_json(orient="records")], check=True)
