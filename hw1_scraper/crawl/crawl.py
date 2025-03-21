from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json
import os

# can also add CAPTCHA bypassing

def load_proxy(path: str = "proxy.txt") -> dict:
    """
    Function that reads proxy from txt file and returns config dict in Playwright proxy format 
    Args:
        path: str
        Path to file that contains proxy in format
            https://www.example.com:5050
            username:password
    Returns:
        proxy: dict
        Dictionary that contains: 
            "server" : str, "username" : str, "password" : str
    """
    proxy = {}
    with open(path, "r") as file:
        proxy["server"] = file.readline()
        proxy["username"], proxy["password"] = file.readline().split(":")
    
    return proxy
    
def load_session_data(page, context, path="session.json"):
    if os.path.exists(path):
        with open(path, "r") as file:
            session_data = json.load(file)
    else:
        print("Can not load session: does not exist")
        return

    context.add_cookies(session_data["cookies"])

    script = f'''
        const localStorageData = {json.dumps(session_data["localStorage"])};
        const sessionStorageData = {json.dumps(session_data["sessionStorage"])};

        Object.keys(localStorageData).forEach(key => {{
            localStorage.setItem(key, localStorageData[key]);
        }});

        Object.keys(sessionStorageData).forEach(key => {{
            sessionStorage.setItem(key, sessionStorageData[key]);
        }});
    '''
    page.add_init_script(script)
    print("✅ Session load script added successfully!")

def save_session(page, context, path="session.json"):
    if os.path.exists(path):
        print("✅ Session already exists!")
        return

    cookies = context.cookies()

    local_storage = page.evaluate("Object.fromEntries(Object.entries(localStorage));")
    session_storage = page.evaluate("Object.fromEntries(Object.entries(sessionStorage));")

    session_data = {
        "cookies": cookies,
        "localStorage": local_storage,
        "sessionStorage": session_storage
    }

    with open(path, "w") as file:
        json.dump(session_data, file, indent=4)

    print("✅ Session saved successfully!")


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
    ])

    # can add auto check if context correctly loaded
    url = "https://bot.sannysoft.com/"
    # url = "https://pixelscan.net/"
    # url = "https://www.browserscan.net/bot-detection"

    # === site to scrape ===
    # url = "https://www.yelp.com/biz/the-porch-at-schenley-pittsburgh"
    
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        java_script_enabled=True,
        permissions=['geolocation'],
        bypass_csp=True,
    )
    context.add_init_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined});""")
    context.add_init_script("""
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.'; // Spoof Vendor
            if (parameter === 37446) return 'Intel Iris OpenGL Engine'; // Spoof Renderer
            return getParameter.apply(this, [parameter]);
        };
    """)
    context.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        Object.defineProperty(navigator, 'mimeTypes', {
            get: () => ['application/pdf', 'application/x-shockwave-flash']
        });
    """)
    
    page = context.new_page()
    stealth_sync(page)

    # Prevent WebRTC leaks
    page.add_init_script("Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });")

    # Spoof screen size and timezone
    page.add_init_script("""
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

    if "yelp" in url:
        load_session_data(page, context)
    
    page.goto(url)
    save_session(page, context)

    page.pause() 
