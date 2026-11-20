# What: captures synthetic dashboard views for the submission.
# Why: document the desktop and phone layouts without real user input.
# Viva: a headless browser visits the same local app as a normal user.
import base64
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess
import time
import urllib.request
import json

from websockets.sync.client import connect

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('capture_helpers', ROOT / 'scripts/capture_screenshots.py')
capture = module_from_spec(spec)
spec.loader.exec_module(capture)


def main():
    """Capture five desktop and three phone views of the running local app."""
    profile = ROOT / 'data/interim/submission_browser'
    browser = subprocess.Popen([capture.find_chrome(), '--headless=new', '--disable-gpu', '--no-first-run',
                                '--remote-allow-origins=*', '--remote-debugging-port=9281',
                                f'--user-data-dir={profile}', 'about:blank'],
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    try:
        for _ in range(60):
            try:
                with urllib.request.urlopen('http://127.0.0.1:9281/json/version', timeout=2) as response:
                    endpoint = json.load(response)['webSocketDebuggerUrl']
                break
            except OSError:
                time.sleep(.5)
        else:
            raise RuntimeError('Headless browser unavailable')
        with connect(endpoint, open_timeout=20, max_size=20_000_000) as ws:
            target = capture.request(ws, 1, 'Target.createTarget', {'url': 'about:blank'})['targetId']
            session = capture.request(ws, 2, 'Target.attachToTarget', {'targetId': target, 'flatten': True})['sessionId']
            capture.request(ws, 3, 'Page.enable', session=session)
            capture.request(ws, 4, 'Page.navigate', {'url': 'http://localhost:8513'}, session)
            shadow = "(()=>{for(const e of document.querySelectorAll('*'))if(e.shadowRoot&&e.shadowRoot.querySelector('.shell'))return e.shadowRoot;return null})()"
            counter = 10
            def evaluate(expression):
                nonlocal counter
                counter += 1
                return capture.request(ws, counter, 'Runtime.evaluate', {'expression': expression, 'returnByValue': True}, session)['result'].get('value')
            for _ in range(120):
                if evaluate(f'!!{shadow} && !!{shadow}.querySelector("#skills-kpis")'):
                    break
                time.sleep(.5)
            else:
                raise RuntimeError('Dashboard did not load')
            for width, height, pages in [(1440, 900, ['overview', 'skills', 'explorer', 'performance', 'methodology']),
                                         (390, 844, ['overview', 'skills', 'explorer'])]:
                counter += 1
                capture.request(ws, counter, 'Emulation.setDeviceMetricsOverride', {'width': width, 'height': height, 'deviceScaleFactor': 1, 'mobile': False}, session)
                for page in pages:
                    selector = f'.bottom-nav [data-page={page}]' if width == 390 else f'.nav [data-page={page}]'
                    if not evaluate(f"(()=>{{const node={shadow}.querySelector('{selector}');if(!node)return false;node.click();return true}})()"):
                        raise RuntimeError(f'Navigation missing for {page}')
                    time.sleep(5)
                    if not evaluate(f"!!{shadow}.querySelector('#page-{page}.active')"):
                        raise RuntimeError(f'Navigation failed for {page}')
                    counter += 1
                    image = capture.request(ws, counter, 'Page.captureScreenshot', {'format': 'png', 'captureBeyondViewport': False}, session)
                    path = ROOT / 'docs/screenshots' / f'{page}-{width}x{height}.png'
                    path.write_bytes(base64.b64decode(image['data']))
                    print(f'Captured {path}', flush=True)
    finally:
        browser.terminate()


if __name__ == '__main__':
    main()
