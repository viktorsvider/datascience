import asyncio
import random
import os
from playwright.async_api import async_playwright

class AntiDetectionBrowser:
    def __init__(self):
        self.proxy_config = {
            'server': 'http://195.178.135.125:50100',
            'username': 'viktor64y',
            'password': 'HWZ2hHE9je',
        }
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.16 Safari/537.36'
        self.test_sites = [
            ('https://bot.sannysoft.com', 'sannysoft'),
            ('https://pixelscan.net', 'pixelscan'),
            ('https://www.browserscan.net/bot-detection', 'browserscan'),
            ('https://abrahamjuliot.github.io/creepjs/', 'creepjs'),
            ('https://browserleaks.com/ip', 'browserleaks_ip')
        ]
        os.makedirs('results', exist_ok=True)

    async def human_movement(self, page, element):
        box = await element.bounding_box()
        target_x = box['x'] + box['width'] * random.uniform(0.4, 0.6)
        target_y = box['y'] + box['height'] * random.uniform(0.4, 0.6)

        for _ in range(random.randint(3, 5)):
            await page.mouse.move(
                target_x * random.uniform(0.97, 1.03),
                target_y * random.uniform(0.97, 1.03),
                steps=random.randint(25, 35)
            )
            await asyncio.sleep(random.uniform(0.08, 0.15))

    async def configure_browser(self, playwright):
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--lang=uk-UA',
                '--timezone=Europe/Kyiv',
                '--geolocation=51.0252,31.5312',
                '--allow-location-access',
                '--disable-background-timer-throttling',
                '--enable-features=WebRtcHideLocalIpsWithMdns',
                '--force-color-profile=srgb',
                '--force-device-scale-factor=1'
            ],
            proxy=self.proxy_config,
            ignore_default_args=['--enable-automation'],
            chromium_sandbox=False
        )

        context = await browser.new_context(
            user_agent=self.user_agent,
            permissions=['geolocation'],
            locale='uk-UA',
            timezone_id='Europe/Kyiv',
            viewport={'width': 1920, 'height': 1080},
            geolocation={'longitude': 31.5312, 'latitude': 51.0252},
            color_scheme='light',
            device_scale_factor=random.uniform(0.98, 1.02),
            ignore_https_errors=True
        )

        await self.apply_anti_detection_overrides(context)
        return browser, context

    async def apply_anti_detection_overrides(self, context):
        await context.add_init_script('''
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: 'denied' }) :
                originalQuery(parameters)
        );

        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 34076) return 'Intel HD Graphics 620';
            return getParameter.call(this, parameter);
        };

        Object.defineProperty(navigator, 'plugins', {
            get: () => [{
                description: 'Portable Document Format',
                filename: 'internal-pdf-viewer',
                name: 'Chrome PDF Viewer'
            }]
        });

        delete window.chrome;
        delete window.outerWidth;
        delete window.outerHeight;
        ''')
    
    async def run_tests(self, page):
        for url, name in self.test_sites:
            try:
                await page.goto(url)#, wait_until='networkidle', timeout=1200)
                await page.wait_for_timeout(random.randint(2000, 5000))

                if 'creepjs' in url:
                    button = await page.query_selector('.test-button')
                    if button:
                        await self.human_movement(page, button)
                        await button.click(delay=random.randint(80, 250))

                await page.screenshot(path=f'results/{name}_test.png', full_page=True)
                print(f'Successfully passed: {name}')
            except Exception as e:
                print(f'Failed {name}: {str(e)}')

    async def execute(self):
        async with async_playwright() as playwright:
            browser, context = await self.configure_browser(playwright)
            page = await context.new_page()

            try:
                # await self.run_tests(page)
                url_yelp = "https://www.yelp.com/biz/red-o-cantina-santa-monica"
                await page.goto(url_yelp, timeout=1000000)
                await page.goto('chrome://version/', timeout=60000)
                await page.screenshot(path='results/chrome_version.png')
                print("\nManual inspection phase (1 hour)...")
                await asyncio.sleep(3600)
            finally:
                await browser.close()



if __name__ == '__main__':
    detector = AntiDetectionBrowser()
    asyncio.run(detector.execute())