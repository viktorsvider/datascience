import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=r'C:\Users\Bohdan\AppData\Local\Google\Chrome\User Data',
            headless=False,
            args=[
                '--profile-directory=Profile 9',
                '--disable-infobars'
            ],
        )
        
        page = context.new_page()
        await page.goto('https://example.com')

asyncio.run(main())