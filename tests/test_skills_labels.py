# What: checks the readable labels used for survey groups and occupations.
# Why: numeric survey codes should not be presented without an explanation.
# Viva: labels change presentation only; filters still use the original codes.
import base64
from pathlib import Path
import shutil
import subprocess

import pytest
from streamlit.testing.v1 import AppTest
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_translates_survey_codes():
    if not shutil.which("node"):
        pytest.skip("Node is unavailable")
    source = (ROOT / "app/skills_dashboard.js").read_bytes()
    code = """const m=await import('data:text/javascript;base64,'+process.argv[1]);
    const labels=['Managers','Professionals','Technicians and associate professionals',
      'Clerical support workers','Service and sales workers',
      'Skilled agricultural, forestry and fishery workers','Craft and related trades workers',
      'Plant and machine operators and assemblers','Elementary occupations'];
    labels.forEach((label,i)=>{if(m.occupationLabel('occupation '+(i+1))!==label)throw Error(label)});
    for(const [code,label] of [['province=1.0','Khyber Pakhtunkhwa'],['province=2.0','Punjab'],
      ['province=3.0','Sindh'],['province=4.0','Balochistan'],
      ['sex=1.0, area=1.0','Male · Rural'],['sex=1.0, area=2.0','Male · Urban'],
      ['sex=2.0, area=1.0','Female · Rural'],['sex=2.0, area=2.0','Female · Urban']])
      if(m.surveyGroupLabel(code)!==label)throw Error(code);
    if(m.occupationLabel('occupation 99')!=='occupation 99')throw Error('unknown occupation');
    """
    subprocess.run(["node", "--input-type=module", "-e", code, base64.b64encode(source).decode()], check=True)


def test_classic_view_uses_labels_without_changing_filter_keys():
    app = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90)
    app.query_params["classic"] = "1"
    with threadpool_limits(limits=1):
        app.run()
        app.radio(key="navigation").set_value("Skills gap").run()
    assert not app.exception and not app.error
    choices = app.selectbox(key="skills_classic_attainment").options
    assert "Punjab" in choices and "Female · Urban" in choices
    with threadpool_limits(limits=1):
        app.selectbox(key="skills_classic_attainment").set_value("sex=2.0, area=2.0").run()
    assert app.selectbox(key="skills_classic_attainment").value == "sex=2.0, area=2.0"
    frames = [frame.value for frame in app.dataframe]
    assert any("Female · Urban" in frame.to_string() for frame in frames)
    assert any("Managers" in frame.to_string() and "Elementary occupations" in frame.to_string() for frame in frames)
