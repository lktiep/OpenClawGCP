---
name: camoufox
description: Anti-detect stealth browser for scraping, automation and bypassing bot detection. Use when normal browser fails or gets blocked.
metadata:
  {
    "openclaw":
      {
        "emoji": "🦊",
        "os": ["linux"],
        "requires": { "bins": ["python3"] }
      }
  }
---

# Camoufox — Anti-Detect Stealth Browser

Camoufox is a Firefox-based anti-detect browser that spoofs fingerprints (OS, User-Agent, canvas, WebGL, fonts) to bypass bot detection systems like Cloudflare, DataDome, and reCAPTCHA. It uses Playwright under the hood.

## When to use

- When the built-in Chromium browser gets **blocked or detected** by anti-bot systems
- When you need to **scrape protected websites** (Cloudflare-protected, login-required sites)
- When human-like browsing behavior is needed (mouse movements, realistic timing)
- When you need a **spoofed fingerprint** (e.g., appear as macOS Firefox user)

## Quick Usage (Python)

### Basic page fetch

```python
python3 -c "
from camoufox.sync_api import Camoufox
with Camoufox(headless='virtual', humanize=True) as browser:
    page = browser.new_page()
    page.goto('https://example.com', timeout=30000)
    page.wait_for_load_state('networkidle')
    print(page.content())
"
```

### Get page text content

```python
python3 -c "
from camoufox.sync_api import Camoufox
with Camoufox(headless='virtual', humanize=True) as browser:
    page = browser.new_page()
    page.goto('https://example.com', timeout=30000)
    page.wait_for_load_state('networkidle')
    print(page.inner_text('body'))
"
```

### Screenshot a page

```python
python3 -c "
from camoufox.sync_api import Camoufox
with Camoufox(headless='virtual', humanize=True) as browser:
    page = browser.new_page()
    page.goto('https://example.com', timeout=30000)
    page.wait_for_load_state('networkidle')
    page.screenshot(path='/tmp/screenshot.png', full_page=True)
    print('Screenshot saved to /tmp/screenshot.png')
"
```

### Fill form and click

```python
python3 -c "
from camoufox.sync_api import Camoufox
with Camoufox(headless='virtual', humanize=True) as browser:
    page = browser.new_page()
    page.goto('https://example.com/login', timeout=30000)
    page.fill('input[name=username]', 'myuser')
    page.fill('input[name=password]', 'mypass')
    page.click('button[type=submit]')
    page.wait_for_load_state('networkidle')
    print(page.inner_text('body'))
"
```

### Extract JSON from API endpoint

```python
python3 -c "
import json
from camoufox.sync_api import Camoufox
with Camoufox(headless='virtual', humanize=True) as browser:
    page = browser.new_page()
    page.goto('https://api.example.com/data', timeout=30000)
    data = json.loads(page.inner_text('body'))
    print(json.dumps(data, indent=2, ensure_ascii=False))
"
```

## Key Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `headless` | `True`, `"virtual"` | `True`=basic headless, `"virtual"`=Xvfb (more stealth, recommended) |
| `humanize` | `True`, `False` | Human-like mouse/keyboard behavior |
| `geoip` | `True` | Auto-detect and spoof geolocation based on IP |
| `locale` | `"vi-VN"` | Set browser locale |
| `os` | `"windows"`, `"macos"`, `"linux"` | Spoof operating system fingerprint (random if not set) |

## Advanced: Custom config

```python
from camoufox.sync_api import Camoufox
with Camoufox(
    headless="virtual",
    humanize=True,
    geoip=True,
    os="windows",
    locale="vi-VN"
) as browser:
    page = browser.new_page()
    # ... your code
```

## Important Notes

- Always use `headless="virtual"` for best anti-detect results on this server
- Always use `humanize=True` for realistic behavior
- Camoufox is **slower** than built-in Chromium — only use when stealth is needed
- Each session creates a fresh fingerprint (no persistent sessions)
- Max timeout recommended: 30000ms for page loads
