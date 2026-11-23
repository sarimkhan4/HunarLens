# What: captures synthetic default app views at exact desktop and mobile widths.
# Why: verify responsive layout without introducing browser code into the app.
# Viva: the browser reads the same local Streamlit server as a normal user.
import base64
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request

from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
PORT = 9223


def find_chrome():
    """Find a locally installed browser without relying on a fixed machine path."""
    executable = shutil.which("google-chrome") or shutil.which("chrome")
    if executable:
        return executable
    for variable in ["PROGRAMFILES", "PROGRAMFILES(X86)"]:
        root = os.environ.get(variable)
        if root:
            candidate = Path(root) / "Google/Chrome/Application/chrome.exe"
            if candidate.exists():
                return str(candidate)
    raise RuntimeError("Chrome was not found; install it or add it to PATH for screenshots.")


def request(ws, identifier, method, params=None, session=None):
    """Send one DevTools command and ignore unrelated asynchronous events."""
    message = {"id": identifier, "method": method, "params": params or {}}
    if session:
        message["sessionId"] = session
    ws.send(json.dumps(message))
    while True:
        response = json.loads(ws.recv(timeout=30))
        if response.get("id") == identifier:
            if "error" in response:
                raise RuntimeError(response["error"])
            return response["result"]


def main():
    """Load the app with default synthetic values and save two viewport images."""
    profile = ROOT / "data/interim/chrome_capture"
    browser = subprocess.Popen([find_chrome(), "--headless=new", "--disable-gpu", "--no-first-run",
                                "--no-default-browser-check", "--remote-allow-origins=*",
                                f"--remote-debugging-port={PORT}", f"--user-data-dir={profile}", "about:blank"],
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
            raise RuntimeError("Could not start the headless browser.")
        with connect(endpoint, open_timeout=20, max_size=20_000_000) as ws:
            target = request(ws, 1, "Target.createTarget", {"url": "about:blank"})["targetId"]
            session = request(ws, 2, "Target.attachToTarget", {"targetId": target, "flatten": True})["sessionId"]
            request(ws, 3, "Page.enable", session=session)
            request(ws, 4, "Page.navigate", {"url": "http://localhost:8510"}, session)
            for index in range(60):
                result = request(ws, 100 + index, "Runtime.evaluate", {"expression": "document.body.innerText.includes('Your estimate')", "returnByValue": True}, session)
                if result["result"].get("value"):
                    break
                time.sleep(.5)
            else:
                raise RuntimeError("App did not become ready for screenshots.")
            time.sleep(3)
            for index, width in enumerate([1280, 390]):
                request(ws, 200 + index * 2, "Emulation.setDeviceMetricsOverride",
                        {"width": width, "height": 900, "deviceScaleFactor": 1, "mobile": False}, session)
                time.sleep(2)
                result = request(ws, 201 + index * 2, "Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False}, session)
                path = ROOT / f"docs/screenshots/estimate-{width}.png"
                path.write_bytes(base64.b64decode(result["data"]))
                print(f"Saved {path.name} at width {width}", flush=True)
                if width == 390:
                    request(ws, 400, "Runtime.evaluate", {"expression": "[...document.querySelectorAll('h1,h2,h3,h4')].find(x => x.textContent.includes('Your estimate'))?.scrollIntoView({block:'start'})"}, session)
                    time.sleep(2)
                    result = request(ws, 401, "Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False}, session)
                    (ROOT / "docs/screenshots/estimate-390-result.png").write_bytes(base64.b64decode(result["data"]))
                    print("Saved estimate-390-result.png", flush=True)
            request(ws, 300, "Browser.close")
    finally:
        if browser.poll() is None:
            browser.terminate()


if __name__ == "__main__":
    main()
