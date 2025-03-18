from playwright.sync_api import sync_playwright
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
    with open(path, "r") as file:
        session_data = json.load(file)

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
    browser = p.chromium.launch(
        headless=False,
        proxy=load_proxy(),
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-features=site-per-process"
    ])

    context = browser.new_context()

    page = context.new_page()
    load_session_data(page, context)
    # can add auto check if context correctly loaded

    url = "https://arh.antoinevastel.com/bots/areyouheadless"
    # url = "https://www.yelp.com/biz/the-porch-at-schenley-pittsburgh"
    page.goto(url)
    save_session(page, context)

    page.pause() 
