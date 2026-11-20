# What: captures synthetic dashboard screenshots in a local headless browser.
# Why: check the layouts without placing real survey records in screenshots.
# Viva: the screenshots use the default synthetic profile, never real user input.
import base64
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import time
import urllib.request

import pandas as pd
from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("capture", ROOT / "scripts/capture_screenshots.py")
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)
OUTPUT = ROOT / "docs/screenshots/final"
PORT = 9250
PAGES = ["overview", "explorer", "performance", "methodology"]


def main(url: str = "http://localhost:8513", desktop_only: bool = False, output: Path = OUTPUT):
    """Capture synthetic pages and compare displayed figures with saved reports."""
    output.mkdir(parents=True, exist_ok=True)
    profile = ROOT / "data/interim/stage9e_browser"
    browser = subprocess.Popen([capture.find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run",
                                "--remote-allow-origins=*", f"--remote-debugging-port={PORT}",
                                f"--user-data-dir={profile}", "about:blank"],
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        for _ in range(60):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2) as response:
                    endpoint = json.load(response)["webSocketDebuggerUrl"]
                break
            except OSError:
                time.sleep(.5)
        else:
            raise RuntimeError("Browser could not start.")
        with connect(endpoint, open_timeout=20, max_size=20_000_000) as ws:
            target = capture.request(ws, 1, "Target.createTarget", {"url": "about:blank"})["targetId"]
            session = capture.request(ws, 2, "Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
            capture.request(ws, 3, "Page.enable", session=session)
            capture.request(ws, 4, "Page.navigate", {"url": url}, session)
            counter = 10
            shadow = "(()=>{for(const e of document.querySelectorAll('*'))if(e.shadowRoot&&e.shadowRoot.querySelector('.shell'))return e.shadowRoot;return null})()"
            def evaluate(expression):
                nonlocal counter
                counter += 1
                return capture.request(ws, counter, "Runtime.evaluate",
                                       {"expression": expression, "returnByValue": True}, session)["result"].get("value")
            indicators = pd.read_csv(ROOT / "reports/tables/overview_indicators.csv").query('status == "verified"').set_index("indicator")
            metric_table = pd.read_csv(ROOT / "reports/tables/test_metrics.csv").set_index("model_threshold")
            metrics = metric_table.loc["HGB F1"]
            dummy = metric_table.loc["Stratified Dummy"]
            confidence = pd.read_csv(ROOT / "reports/tables/test_bootstrap_ci.csv")
            interval = confidence[(confidence.model_threshold == "HGB F1") & (confidence.metric == "f1")].iloc[0]
            subgroup = pd.read_csv(ROOT / "reports/tables/test_subgroups.csv")
            education = subgroup[subgroup.subgroup.str.contains("education", case=False) & subgroup.threshold.eq("f1")]
            importance = pd.read_csv(ROOT / "reports/tables/grouped_permutation_importance.csv")
            importance = importance[~importance.group.isin(["Region", "Sex and area"])].sort_values("importance_mean", ascending=False).head(5)
            expected_overview = [f"{indicators.loc[key, 'pbs_value']:.1%}" for key in ["youth_all", "all_ages", "youth_male", "youth_female"]]
            expected_performance = [f"{int(metrics['n']):,}", f"{metrics['prevalence']:.1%}",
                                    f"{(metrics['tp'] + metrics['fp']) / metrics['n']:.1%}", f"{metrics['roc_auc']:.3f}"]
            for _ in range(120):
                if evaluate(f"!!{shadow} && getComputedStyle({shadow}.querySelector('.shell')).visibility === 'visible'"):
                    break
                time.sleep(.5)
            else:
                raise RuntimeError("Dashboard did not load.")
            sizes = [(1440, 900), (1280, 900)] if desktop_only else [(1440, 900), (1024, 768), (390, 844)]
            for width, height in sizes:
                counter += 1
                capture.request(ws, counter, "Emulation.setDeviceMetricsOverride",
                                {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False}, session)
                for page in (PAGES if width != 390 else ["explorer"]):
                    selector = f"[data-page={page}]"
                    evaluate(f"{shadow}.querySelector('{selector}').click()")
                    for _ in range(60):
                        if evaluate(f"!!{shadow}.querySelector('#page-{page}.active')"):
                            break
                        time.sleep(.5)
                    else:
                        raise RuntimeError(f"Navigation failed: {page}")
                    # Streamlit dims the previous page while a component update is running.
                    # Wait for the render to settle before recording the image.
                    time.sleep(10)
                    if not evaluate(f"!!{shadow}.querySelector('#page-{page}.active')"):
                        raise RuntimeError(f"Page changed while rendering: {page}")
                    if page in {"overview", "performance"}:
                        selector = f"#page-{page} .kpi-value"
                        rendered = evaluate(f"Array.from({shadow}.querySelectorAll('{selector}'), x => x.textContent)")
                        expected = expected_overview if page == "overview" else expected_performance
                        if rendered != expected:
                            raise RuntimeError(f"{page} indicators do not match the generated tables")
                        page_text = evaluate(f"{shadow}.querySelector('#page-{page}').innerText")
                        if page == "overview":
                            keys = [key for key in indicators.index if key.startswith(("participation_", "unemployment_"))]
                            # Table 15's total participation and total/male/female unemployment rates are visible.
                            keys = [key for key in keys if key.startswith("unemployment_") or key.endswith("_total")]
                            expected_values = [f"{indicators.loc[key, 'pbs_value']:.1%}" for key in keys]
                        else:
                            expected_values = [f"{metrics['precision']:.1%}", f"{metrics['recall']:.1%}",
                                               f"{1 - metrics['recall']:.1%}", f"{metrics['prevalence']:.3f}",
                                               f"{metrics['f1']:.3f}", f"{metrics['pr_auc']:.3f}",
                                               f"{metrics['roc_auc']:.3f}", f"{dummy['f1']:.3f}",
                                               f"{interval.lower_95:.3f}", f"{interval.upper_95:.3f}",
                                               f"{int(metrics['positives']):,}"]
                            expected_values += [str(int(value)) for value in education["n"]]
                            expected_values += [str(int(value)) for value in education.positives]
                            expected_values += [f"{value:.1%}" for value in education.recall]
                            expected_values += [f"{value:.3f}" for value in importance.importance_mean]
                        if any(value not in page_text for value in expected_values):
                            raise RuntimeError(f"{page} contains a missing or inconsistent generated value")
                    evaluate("window.scrollTo(0,0)")
                    counter += 1
                    screenshot = capture.request(ws, counter, "Page.captureScreenshot", {"format": "png"}, session)
                    path = output / f"{page}-{width}x{height}.png"
                    path.write_bytes(base64.b64decode(screenshot["data"]))
                    print(f"Saved {path}", flush=True)
    finally:
        browser.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify saved dashboard numbers and capture synthetic UI screenshots.")
    parser.add_argument("--url", default="http://localhost:8513")
    parser.add_argument("--desktop-only", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    main(arguments.url, arguments.desktop_only, arguments.output)
