# What: checks report provenance, rendering, scope and presentation.
# Why: edits to prose must not introduce unsupported or overprecise statistics.
# Viva: re-read the saved evidence independently; no model is loaded or scored.
import importlib.util
import json
import re
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('report_writer', ROOT / 'scripts/write_project_report.py')
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)


@pytest.fixture(scope='module')
def report_output():
    return writer.render_reports()


def test_reports_and_numeric_ledger_match_generated_evidence(report_output):
    reports, ledger = report_output
    assert ledger == json.loads((ROOT / 'reports/tables/report_numbers.json').read_text(encoding='utf-8'))
    for name, expected in reports.items():
        assert (ROOT / 'docs' / name).read_text(encoding='utf-8') == expected


def test_report_cells_independently_match_saved_tables(report_output):
    """Check original table values, including rounding, outside the renderer."""
    _, ledger = report_output
    checked = 0
    for item in ledger.values():
        source = item['source']
        if not isinstance(source, dict) or 'table' not in source or 'column' not in source:
            continue
        table = pd.read_csv(ROOT / 'reports/tables' / (source['table'] + '.csv'), keep_default_na=False)
        if 'query' in source:
            selected = table.query(source['query']) if source['query'] else table
            assert len(selected) == 1
            value = selected.iloc[0][source['column']]
        elif 'row' in source:
            value = table.iloc[source['row']][source['column']]
        else:
            value = table.loc[table.iloc[:, 0].astype(float).eq(float(source['code']))].iloc[0][source['column']]
        value = float(value)
        if source.get('operation') == 'absolute':
            value = abs(value)
        if 'divide' in source:
            value /= source['divide']
        assert float(item['value']) == pytest.approx(value, abs=1e-12)
        checked += 1
    assert checked > 100


def test_report_structure_precision_and_links(report_output):
    reports, _ = report_output
    counts = writer.word_counts(reports)
    assert 6000 <= counts['main_prose'] <= 7500
    assert 150 <= counts['abstract'] <= 200
    assert reports['report_short.md'].count('\\newpage') == 3
    for text in reports.values():
        assert not re.search(r'\b(?:stage|phase|step|gate|sign-off|codex|draft)s?\b', text, re.I)
        assert '{{' not in text
        for line in text.splitlines():
            if line.startswith('|'):
                assert not re.search(r'\d+\.\d{4,}', line), line
                assert not re.search(r'\d+\.\d{2,}%', line), line
        for path in re.findall(r'!\[[^]]*\]\(([^)]+)\)', text):
            assert (ROOT / 'docs' / path).is_file()
    body = reports['project_report.md'].split('## References')[0]
    assert len(re.findall(r'^\*\*Table \d+\.', body, re.M)) == 8


def test_statistics_in_narrative_use_placeholders():
    """Disallow hand-entered decimal statistics outside bibliographic material."""
    for name in ['full.md', 'short.md']:
        text = (ROOT / 'scripts/report_templates' / name).read_text(encoding='utf-8')
        text = text.split('## References')[0]
        for line in text.splitlines():
            if line.startswith(('#', '![', '**Course', '**Members', 'Sarim Khan')):
                continue
            assert not re.search(r'(?<![\w/])\d+\.\d+%?', line), line
