from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json
import os

def load_proxy(path: str = "proxy.txt") -> dict:
    proxy = {}
    with open(path, "r") as file:
        proxy["server"] = file.readline().strip()
        proxy["username"], proxy["password"] = file.readline().strip().split(":")
    return proxy

def load_session_data(page, context, path="session.json"):
    if os.path.exists(path):
        with open(path, "r") as file:
            session_data = json.load(file)
        context.add_cookies(session_data.get("cookies", []))
        script = f'''
            const localStorageData = {json.dumps(session_data.get("localStorage", {}))};
            const sessionStorageData = {json.dumps(session_data.get("sessionStorage", {}))};
            Object.keys(localStorageData).forEach(key => localStorage.setItem(key, localStorageData[key]));
            Object.keys(sessionStorageData).forEach(key => sessionStorage.setItem(key, sessionStorageData[key]));
        '''
        page.add_init_script(script)
        print("✅ Session data loaded.")
    else:
        print("⚠️ Session file not found.")

def save_session(page, context, path="session.json"):
    cookies = context.cookies()
    local_storage = page.evaluate("Object.fromEntries(Object.entries(localStorage));")
    session_storage = page.evaluate("Object.fromEntries(Object.entries(sessionStorage));")
    session_data = {"cookies": cookies, "localStorage": local_storage, "sessionStorage": session_storage}
    with open(path, "w") as file:
        json.dump(session_data, file, indent=4)
    print("✅ Session saved.")

with sync_playwright() as p:
    proxy = load_proxy()
    browser = p.chromium.launch(
        headless=False,
        proxy=proxy,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-features=site-per-process",
            "--enable-features=NetworkService,NetworkServiceInProcess"
        ]
    )
    context = browser.new_context(
        # user_agent=browser.user_agent(),
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        permissions=['geolocation'],
        bypass_csp=True,
    )

    # Apply stealth and further fingerprint spoofing
    page = context.new_page()
    stealth_sync(page)

    context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    window.navigator.chrome = { runtime: {} };

    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
        if (parameter === 37445) return 'Intel Inc.';
        if (parameter === 37446) return 'Intel Iris OpenGL Engine';
        return getParameter.apply(this, [parameter]);
    };

    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'mimeTypes', { get: () => ['application/pdf', 'application/x-shockwave-flash'] });

    Object.defineProperty(HTMLCanvasElement.prototype, 'toDataURL', {
        value: function() { return "data:image/png;base64,fakeimage"; }
    });

    Object.defineProperty(navigator, 'mediaDevices', { get: () => ({ enumerateDevices: () => Promise.resolve([]) }) });
    Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });

    Object.defineProperty(window, 'screen', {
        get: () => ({
            width: 1920,
            height: 1080,
            availWidth: 1920,
            availHeight: 1080,
            colorDepth: 24,
            pixelDepth: 24
        })
    });
    Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
        value: () => ({ timeZone: 'America/New_York' })
    });
    """)
    # can add auto check if context correctly loaded
    url = "https://bot.sannysoft.com/"
    url2 = "https://pixelscan.net/"
    url3 = "https://www.browserscan.net/bot-detection"

    # === site to scrape ===
    # url = "https://www.yelp.com/biz/the-porch-at-schenley-pittsburgh"
    url = "https://bot.sannysoft.com/"
    page.goto(url)
    page2 = context.new_page()
    page2.goto(url2)
    page3 = context.new_page()
    page3.goto(url3)
    # save_session(page, context)
    page.pause()
