# What: renders a readable, compact guide to the existing project as a PDF.
# Why: students and reviewers need an understandable alternative to raw code listings.
# Viva: the guide uses saved documentation and aggregate tables; it never scores data.
from __future__ import annotations

import ast
import csv
import hashlib
import json
import re
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'HunarLens_Complete_Project_Guide.pdf'
BLUE = '#172a53'
INK = '#27374b'
MUTED = '#64748b'
TEAL = '#177f89'


def read(path):
    return path.read_text(encoding='utf-8-sig', errors='replace')


def plain(text):
    text = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1', text)
    text = text.replace('**', '').replace('`', '').replace('\\newpage', '')
    return ''.join(' ' if ord(char) < 32 and char not in '\n\t' else char for char in text)


class Guide:
    """Lay out a series of labelled text blocks before writing the final PDF."""

    def __init__(self):
        self.pages = []
        self.current = []
        self.used = 0
        self.section_name = 'Project guide'
        self.contents = []

    def flush(self):
        if self.current:
            self.pages.append(('text', self.section_name, self.current))
            self.current, self.used = [], 0

    def add(self, text='', kind='body'):
        widths = {'body': 88, 'small': 99, 'h1': 58, 'h2': 72, 'row': 85}
        spacing = {'body': 1.0, 'small': .90, 'h1': 1.60, 'h2': 1.38, 'row': .95}
        indent = '   ' if kind == 'row' else ''
        lines = []
        for line in plain(text).splitlines() or ['']:
            lines.extend(textwrap.wrap(line.strip(), width=widths[kind],
                         break_long_words=True, break_on_hyphens=False) or [''])
        required = len(lines) * spacing[kind] + (.45 if kind in ('body', 'row') else .65)
        if self.used and self.used + required > 51:
            self.flush()
        # Long blocks can still be split across pages; the first-page label remains visible.
        for line in lines:
            if self.used + spacing[kind] > 51:
                self.flush()
            self.current.append((kind, indent + line, self.used))
            self.used += spacing[kind]
        self.used += .45 if kind in ('body', 'row') else .65

    def section(self, title):
        self.flush()
        self.section_name = title
        self.contents.append((title, len(self.pages) + 2))
        self.add(title, 'h1')

    def illustration(self, path, caption):
        file = ROOT / path
        if file.exists():
            self.flush()
            self.pages.append(('image', self.section_name, (file, caption)))


def report_body(guide):
    """Reflow the verified main report, preserving its numbers and explanations."""
    text = read(ROOT / 'docs/project_report.md')
    # The guide supplies its own cover and table of contents.
    text = text.split('## Abstract', 1)[1].split('## References', 1)[0]
    guide.add('Abstract', 'h2')
    lines = text.splitlines()
    index = 0
    paragraph = []

    def flush_paragraph():
        if paragraph:
            guide.add(' '.join(paragraph))
            paragraph.clear()

    while index < len(lines):
        line = lines[index].strip()
        if not line:
            flush_paragraph()
        elif line.startswith('!['):
            flush_paragraph()
            caption = line.split(']', 1)[0][2:]
            guide.add(caption + ' — see the original figure in reports/figures or docs/screenshots.', 'small')
        elif line.startswith('|'):
            flush_paragraph()
            table = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                table.append([cell.strip() for cell in lines[index].strip().strip('|').split('|')])
                index += 1
            headers = table[0]
            for row in table[2:]:
                if len(row) != len(headers):
                    continue
                first, rest = row[0], row[1:]
                pairs = [f'{head}: {value}' for head, value in zip(headers[1:], rest) if value]
                guide.add(first + '  —  ' + '; '.join(pairs), 'row')
            continue
        elif line.startswith('## '):
            flush_paragraph()
            title = plain(line.removeprefix('## '))
            guide.section(title)
        elif line.startswith('### '):
            flush_paragraph()
            guide.add(line.removeprefix('### '), 'h2')
        elif line.startswith('**Table '):
            flush_paragraph()
            guide.add(plain(line), 'h2')
        elif line.startswith('>'):
            flush_paragraph()
            guide.add(line.lstrip('> ').strip())
        elif line.startswith('\\newpage'):
            pass
        else:
            paragraph.append(line)
        index += 1
    flush_paragraph()


def notebook_summary(guide):
    for path in sorted((ROOT / 'notebooks').glob('*.ipynb')):
        data = json.loads(read(path))
        cells = data.get('cells', [])
        guide.add(path.name.replace('_', ' ').removesuffix('.ipynb').title(), 'h2')
        guide.add('File: notebooks/' + path.name, 'small')
        sections = []
        for cell in cells:
            if cell.get('cell_type') == 'markdown':
                for line in ''.join(cell.get('source', [])).splitlines():
                    if line.strip().startswith('#'):
                        sections.append(line.strip().lstrip('#').strip())
        guide.add('Topics: ' + ('; '.join(sections[:12]) if sections else 'See the notebook narrative and code cells.'))
        guide.add(f'Contains {sum(c.get("cell_type") == "markdown" for c in cells)} narrative cells and '
                  f'{sum(c.get("cell_type") == "code" for c in cells)} code cells. '
                  'Stored outputs and personal records are not reproduced in this guide.', 'small')
    guide.add('The final evaluation notebook documents the existing frozen evaluation. '
              'Do not rerun test scoring during review.', 'body')


def files(folder, patterns):
    paths = []
    for pattern in patterns:
        paths += sorted((ROOT / folder).glob(pattern))
    return [p for p in paths if p.name != Path(__file__).name]


def file_description(path):
    text = read(path)
    description = []
    for line in text.splitlines()[:6]:
        if line.startswith('# What:'):
            description.append(line.split(':', 1)[1].strip())
        if line.startswith('# Why:'):
            description.append(line.split(':', 1)[1].strip())
    symbols = []
    if path.suffix == '.py':
        try:
            tree = ast.parse(text)
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    symbols.append(node.name)
            if not description:
                doc = ast.get_docstring(tree)
                if doc:
                    description.append(' '.join(doc.split()))
        except SyntaxError:
            pass
    elif path.suffix == '.js':
        symbols = [a or b for a, b in re.findall(
            r'\b(?:async\s+)?function\s+([\w$]+)\s*\(|\b(?:const|let)\s+([\w$]+)\s*=\s*(?:\([^\n]*?\)|[\w$]+)\s*=>', text)]
    if not description:
        description = {
            '.html': ['Provides the dashboard structure and accessible elements.'],
            '.css': ['Defines the dashboard visual styling and responsive presentation.'],
            '.js': ['Implements client-side dashboard presentation and interaction.'],
            '.py': ['Project helper; inspect its named functions and source for details.'],
        }.get(path.suffix, ['Project asset.'])
    return ' '.join(description), symbols


def file_reference(guide):
    groups = [
        ('Core package: data, model and explanations', 'src/hunarlens', ('*.py',)),
        ('Workflow and supporting scripts', 'scripts', ('*.py',)),
        ('Dashboard and interface assets', 'app', ('*.py', '*.js', '*.html', '*.css')),
        ('Automated tests', 'tests', ('*.py',)),
    ]
    for title, folder, patterns in groups:
        guide.add(title, 'h2')
        for path in files(folder, patterns):
            description, symbols = file_description(path)
            guide.add(str(path.relative_to(ROOT)).replace('\\', '/'), 'small')
            guide.add(description, 'body')
            if symbols:
                listed = ', '.join(symbols[:9])
                if len(symbols) > 9:
                    listed += f' and {len(symbols) - 9} more'
                guide.add('Key definitions: ' + listed + '.', 'small')


def evidence_index(guide):
    guide.add('These are aggregate outputs. The full tables and confidence bounds are in reports/tables; '
              'this guide does not load person-level test predictions.', 'body')
    groups = {
        'Data and reproduction': ['row_waterfall.csv', 'label_reproduction.csv', 'future_starters_diagnostic.csv',
                                  'skills_reproduction.csv', 'feature_missingness.csv'],
        'Splits and model comparison': ['split_summary.csv', 'experiments.csv', 'cv_fold_scores.csv',
                                        'generalization_gap.csv', 'feature_group_ablation.csv',
                                        'validation_thresholds.csv', 'calibration_validation.csv'],
        'Final test and model explanation': ['test_metrics.csv', 'test_bootstrap_ci.csv', 'test_subgroups.csv',
                                             'test_error_distributions.csv', 'grouped_permutation_importance.csv'],
        'Skills-gap analysis': ['skills_unemployment_by_education.csv', 'skills_graduate_absorption.csv',
                                'skills_mismatch.csv', 'skills_mismatch_sensitivity.csv',
                                'skills_mismatch_variants.csv', 'skills_mode_stability.csv',
                                'skills_neet.csv', 'skills_model_shift.csv'],
    }
    for title, names in groups.items():
        guide.add(title, 'h2')
        for name in names:
            path = ROOT / 'reports/tables' / name
            if not path.exists():
                continue
            with path.open(encoding='utf-8-sig', newline='') as stream:
                reader = csv.reader(stream)
                columns = next(reader, [])
                count = sum(1 for _ in reader)
            guide.add(f'{name} — {count:,} rows. Columns: ' + ', '.join(columns), 'small')


def extra_guidance(guide):
    guide.add('Running the application and tests', 'h2')
    guide.add('Create a Python 3.12 virtual environment and install requirements.txt and '
              'requirements-dev.txt. From the project root run python -m pytest -q to execute '
              'the test suite, or streamlit run app/streamlit_app.py to start the dashboard. '
              'Append ?classic=1 to the local app URL for the native fallback. See README.md '
              'for operating-system-specific commands and data prerequisites.')
    guide.add('Protecting the frozen evaluation', 'h2')
    guide.add('Do not refit the model, change thresholds or re-score the test set during review. '
              'The previously saved individual test-prediction file was removed during an earlier '
              'cleanup; the aggregate test tables remain. The guide uses those saved tables and '
              'does not recreate individual predictions.')
    guide.add('How to prepare for a viva', 'h2')
    for question, answer in [
        ('What is the predicted outcome?', 'Unemployment among youth already classified as in the labour force, not all youth without paid work.'),
        ('Why group households?', 'To reduce leakage between related household members across train, validation and test.'),
        ('Why AP and a dummy?', 'Average precision evaluates ranking in an imbalanced problem; the dummy and prevalence provide context.'),
        ('Why HGB if Random Forest led?', 'The CV difference was within the agreed tie margin; the team considered the smaller generalisation gap and deployment properties.'),
        ('What does the probability mean?', 'A model association for the specified profile, not a verdict or a direct measure of an individual’s prospects.'),
        ('What is a confidence interval?', 'A range from the stated bootstrap procedure, not a guarantee and not a causal effect.'),
        ('What is the skills gap here?', 'A descriptive comparison using education and training as proxies, including education relative to occupation modes.'),
        ('Why is the NEET indicator approximate?', 'The data do not identify recent training sufficiently to reproduce the full indicator.'),
    ]:
        guide.add(question, 'small')
        guide.add(answer)
    guide.add('Before submission', 'h2')
    guide.add('Complete the team’s AI-assistance statement, individual contributions, instructor and '
              'date. Verify the flagged publication details and the current live app URL. Review '
              'the latest UI screenshots and check pagination after export. The report and the '
              'decision log remain the detailed supporting sources for this guide.')


def render(guide, subtitle='A practical guide to the project',
           strapline='Data  ·  Model  ·  Skills gap  ·  Dashboard  ·  Code'):
    """Use a proportional font, larger type, whitespace and numbered page footers."""
    pages = guide.pages
    total = len(pages) + 1
    with PdfPages(OUTPUT, metadata={'Title': 'HunarLens: Project Guide', 'Author': 'AlphaDevs',
                                    'Subject': 'Project methods, evidence and code reference'}) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
        fig.text(.085, .91, 'HUNARLENS', fontsize=29, fontweight='bold', color=BLUE)
        fig.text(.085, .862, subtitle, fontsize=19, color=INK)
        fig.text(.085, .817, strapline, fontsize=10.5, color=MUTED)
        fig.add_artist(Line2D([.085, .915], [.785, .785], transform=fig.transFigure, color=TEAL, linewidth=2))
        fig.text(.085, .745, 'Contents', fontsize=15, fontweight='bold', color=BLUE)
        for i, (name, page) in enumerate(guide.contents):
            fig.text(.10, .715 - i * .027, name, fontsize=10, color=INK)
            fig.text(.91, .715 - i * .027, str(page), fontsize=10, color=MUTED, ha='right')
        fig.text(.085, .085, 'For the project team, reviewers and viva preparation.', fontsize=10, color=INK)
        fig.text(.085, .06, 'Research tool only; not a decision tool for individuals.', fontsize=9, color=MUTED)
        pdf.savefig(fig); plt.close(fig)
        for page_number, (kind, section, data) in enumerate(pages, 2):
            fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')
            fig.text(.075, .965, 'HUNARLENS  /  ' + section[:72], fontsize=8, color=MUTED, va='top')
            fig.add_artist(Line2D([.075, .925], [.944, .944], transform=fig.transFigure, color='#dce4ef', linewidth=.7))
            if kind == 'image':
                path, caption = data
                fig.text(.075, .915, caption, fontsize=13, color=BLUE, fontweight='bold', va='top')
                ax = fig.add_axes([.07, .18, .86, .65]); ax.imshow(mpimg.imread(path)); ax.axis('off')
                fig.text(.075, .12, str(path.relative_to(ROOT)).replace('\\', '/'), fontsize=9, color=MUTED)
            else:
                for style, line, position in data:
                    opts = {'h1': (17, BLUE, 'bold'), 'h2': (12, BLUE, 'bold'),
                            'body': (10, INK, 'normal'), 'row': (9.2, INK, 'normal'),
                            'small': (9, MUTED, 'normal')}
                    size, color, weight = opts[style]
                    fig.text(.078, .915 - position * .0151, line, fontsize=size, color=color,
                             fontweight=weight, va='top', fontfamily='DejaVu Sans')
            fig.add_artist(Line2D([.075, .925], [.06, .06], transform=fig.transFigure, color='#dce4ef', linewidth=.7))
            fig.text(.075, .038, 'Project guide  ·  Based on saved project evidence', fontsize=8, color=MUTED)
            fig.text(.925, .038, f'{page_number} / {total}', fontsize=8, color=MUTED, ha='right')
            pdf.savefig(fig); plt.close(fig)
    print(f'Created {OUTPUT.name}: {total} pages, {OUTPUT.stat().st_size:,} bytes.')
    print('Model SHA-256:', hashlib.sha256((ROOT / 'models/final_pipeline.joblib').read_bytes()).hexdigest())


def main():
    guide = Guide()
    guide.section('How to use this guide')
    guide.add('This guide explains the project from source data through the dashboard, '
              'including the reasons for the main decisions and alternatives. It retains '
              'a concise description of each code file and notebook while leaving the '
              'full source in the repository, where it is easier to search and maintain.')
    guide.add('The model describes associations for labour-force youth aged 15–24. '
              'The separate weighted survey analysis uses education and training as proxies. '
              'Neither tool should be used to decide an individual’s employment or services.')
    guide.add('The explanatory sections below are drawn from the evidence-linked project report. '
              'Metrics are from saved aggregate results. The historical decision log may '
              'contain superseded choices; the latest decisions and current implementation '
              'are the relevant ones.')
    report_body(guide)
    guide.section('Visual overview')
    guide.illustration('reports/figures/report_architecture.png', 'Architecture: model and survey-analysis paths')
    guide.illustration('reports/figures/test_pr_curve_wide.png', 'Frozen-model test precision–recall curve')
    guide.illustration('reports/figures/grouped_permutation_importance.png', 'Validation grouped permutation importance')
    guide.section('Notebook guide')
    notebook_summary(guide)
    guide.section('Code and test file guide')
    guide.add('Each entry states a file’s documented purpose and representative definitions. '
              'The repository contains the complete source, including the implementation details '
              'and line numbers, without making this PDF hundreds of pages long.')
    file_reference(guide)
    guide.section('Where to find the results')
    evidence_index(guide)
    guide.section('Practical use and viva questions')
    extra_guidance(guide)
    guide.flush()
    render(guide)


if __name__ == '__main__':
    main()
