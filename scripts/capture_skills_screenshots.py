# What: captures the local skills page at the requested screen sizes.
# Why: desktop and mobile layout need a reproducible visual check.
# Viva: the browser displays saved aggregate survey data, not personal records.
import base64
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import time
import urllib.request

from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("capture_helpers", ROOT / "scripts/capture_screenshots.py")
capture = module_from_spec(spec)
spec.loader.exec_module(capture)


def main():
    """Connect to a running local app and capture three synthetic views."""
    profile = ROOT / "data/interim/skills_browser_profile"
    output = ROOT / "docs/screenshots"
    output.mkdir(parents=True, exist_ok=True)
    browser = subprocess.Popen([capture.find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run",
                                "--remote-allow-origins=*", "--remote-debugging-port=9279",
                                f"--user-data-dir={profile}", "about:blank"],
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        for _ in range(60):
            try:
                endpoint = json.load(urllib.request.urlopen("http://127.0.0.1:9279/json/version", timeout=2))["webSocketDebuggerUrl"]
                break
            except OSError:
                time.sleep(.5)
        else:
            raise RuntimeError("Headless browser unavailable")
        with connect(endpoint, open_timeout=20, max_size=20_000_000) as ws:
            target = capture.request(ws, 1, "Target.createTarget", {"url": "about:blank"})["targetId"]
            session = capture.request(ws, 2, "Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
            capture.request(ws, 3, "Page.enable", session=session)
            capture.request(ws, 4, "Page.navigate", {"url": "http://localhost:8519"}, session)
            root = "(()=>{for(const e of document.querySelectorAll('*'))if(e.shadowRoot&&e.shadowRoot.querySelector('.shell'))return e.shadowRoot;return null})()"
            counter = 10

            def evaluate(expression):
                nonlocal counter
                counter += 1
                return capture.request(ws, counter, "Runtime.evaluate", {"expression": expression, "returnByValue": True}, session)["result"].get("value")

            for _ in range(120):
                if evaluate(f"!!{root} && !!{root}.querySelector('#skills-kpis .kpi-value')"):
                    break
                if evaluate(f"!!{root} && !!{root}.querySelector('[role=alert]')"):
                    raise RuntimeError("Skills rendering reported: " + str(evaluate(f"{root}.querySelector('[role=alert]').textContent")))
                time.sleep(.5)
            else:
                raise RuntimeError("Skills page did not render")
            for width, height in [(1440, 900), (1024, 768), (390, 844)]:
                counter += 1
                capture.request(ws, counter, "Emulation.setDeviceMetricsOverride", {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False}, session)
                button = ".bottom-nav [data-page=skills]" if width == 390 else ".nav [data-page=skills]"
                evaluate(f"{root}.querySelector('{button}').click()")
                time.sleep(2)
                if not evaluate(f"!!{root}.querySelector('#page-skills.active') && {root}.querySelector('#skills-kpis').children.length > 0"):
                    raise RuntimeError("Skills navigation failed")
                if evaluate(f"!!{root}.querySelector('[role=alert]')"):
                    raise RuntimeError("The dashboard reported an error: " + str(evaluate(f"{root}.querySelector('[role=alert]').textContent")))
                if width == 390 and not evaluate(f"{root}.querySelectorAll('.bottom-nav button').length === 5 && [...{root}.querySelectorAll('.bottom-nav button')].every(b=>b.getBoundingClientRect().height >= 44)"):
                    raise RuntimeError("Mobile navigation does not have five accessible targets")
                counter += 1
                image = capture.request(ws, counter, "Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False}, session)
                (output / f"skills-{width}x{height}.png").write_bytes(base64.b64decode(image["data"]))
                print(f"Captured skills-{width}x{height}.png")
            evaluate(f"(()=>{{const x={root}.querySelector('#skills-definition');x.value='youth';x.dispatchEvent(new Event('change',{{bubbles:true}}));}})()")
            if not evaluate(f"{root}.querySelector('#skills-mismatch').textContent.includes('mode unstable') && {root}.querySelector('#skills-mismatch').textContent.includes('bootstrap range')"):
                raise RuntimeError("Mode-unstable range was not displayed")
    finally:
        browser.terminate()


if __name__ == "__main__":
    main()
