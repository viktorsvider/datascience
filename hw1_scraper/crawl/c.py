import asyncio
import random
from playwright.async_api import async_playwright

async def anti_detection_browser():
    proxy = {
        'server': 'http://195.178.135.125:50100',
        'username': 'viktor64y',  # Uncomment if required
        'password': 'HWZ2hHE9je'   # Uncomment if required
    }

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.16 Safari/537.36'

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            # executable_path='/path/to/chromium/133.0.6943.16/chrome-win/chrome.exe',  # Update this path
            headless=False,
            args=[
                '--start-maximized',
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-infobars',
                f'--user-agent="{user_agent}"',
                '--lang=uk-UA',
                '--timezone=Europe/Kyiv',
                '--geolocation=51.0252,31.5312',
                '--allow-location-access',
                '--disable-build-check',
                '--chrome-version=133.0.6943.16',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding'
            ],
            proxy=proxy,
            ignore_default_args=['--enable-automation'],
            chromium_sandbox=False
        )

        context = await browser.new_context(
            user_agent=user_agent,
            permissions=['geolocation'],
            locale='uk-UA',
            timezone_id='Europe/Kyiv',
            viewport=None,
            geolocation={'longitude': 31.5312, 'latitude': 51.0252},
            color_scheme='light',
            screen={'width': 1920, 'height': 1080},
            device_scale_factor=random.uniform(0.95, 1.05)  # Randomize pixel ratio
        )

        # Core anti-detection overrides
        await context.add_init_script('''
            // WebDriver removal
            delete Object.getPrototypeOf(navigator).webdriver;
            
            // Plugin and MIME type emulation
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {0: {type: 'application/pdf', description: 'Portable Document Format', suffixes: 'pdf'}},
                    {0: {type: 'application/x-google-chrome-pdf', description: 'Portable Document Format', suffixes: 'pdf'}}
                ],
            });

            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => ({
                    'application/pdf': {type: 'application/pdf', suffixes: 'pdf'},
                    'application/x-google-chrome-pdf': {type: 'application/x-google-chrome-pdf', suffixes: 'pdf'}
                }),
            });

            // Hardware profile spoofing
            Object.defineProperty(navigator, 'hardwareConcurrency', {value: 4});
            Object.defineProperty(navigator, 'deviceMemory', {value: 8});
            
            // Battery API
            navigator.getBattery = async () => ({
                charging: true,
                chargingTime: Infinity,
                dischargingTime: Infinity,
                level: 1
            });

            // WebGL spoofing
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Open Source Technology Center';
                if (parameter === 37446) return 'Mesa DRI Intel(R) HD Graphics 520 (Skylake GT2)';
                return getParameter.call(this, parameter);
            };

            // Timezone protection
            Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                value: function() {
                    const result = Reflect.apply(Intl.DateTimeFormat.prototype.resolvedOptions, this, []);
                    result.timeZone = 'Europe/Kyiv';
                    return result;
                }
            });

            // AudioContext fingerprinting
            const originalCreateOscillator = AudioContext.prototype.createOscillator;
            AudioContext.prototype.createOscillator = function() {
                const oscillator = originalCreateOscillator.call(this);
                oscillator.frequency.value = 440 + Math.random() * 10;
                return oscillator;
            };
        ''')

        page = await context.new_page()

        # Additional fingerprint protection
        await page.add_init_script('''
            // Canvas fingerprint randomization
            HTMLCanvasElement.prototype.toDataURL = function(type) {
                const original = this.__proto__.toDataURL.apply(this, arguments);
                return original.replace(/[a-z0-9]{20,}/, () => Math.random().toString(36).slice(2));
            };

            // WebRTC leak prevention
            window.RTCPeerConnection = class extends RTCPeerConnection {
                constructor(config) {
                    const filteredServers = config.iceServers.filter(server => 
                        !server.urls.includes('stun:') && !server.urls.includes('turn:')
                    );
                    super({...config, iceServers: filteredServers});
                }
            };

            // Font fingerprinting
            const originalFillText = CanvasRenderingContext2D.prototype.fillText;
            CanvasRenderingContext2D.prototype.fillText = function(...args) {
                args[0] = args[0].replace(/[a-zA-Z]/g, c => 
                    Math.random() > 0.5 ? c.toUpperCase() : c.toLowerCase()
                );
                originalFillText.apply(this, args);
            };
        ''')

        # Detection test sequence
        test_sites = [
            ('https://bot.sannysoft.com', 'sannysoft'),
            ('https://pixelscan.net', 'pixelscan'),
            ('https://www.browserscan.net/bot-detection', 'browserscan'),
            ('https://browserleaks.com/webrtc', 'browserleaks_webrtc'),
            ('https://browserleaks.com/canvas', 'browserleaks_canvas'),
            ('https://abrahamjuliot.github.io/creepjs/', 'creepjs'),
            ('https://browserleaks.com/ip', 'browserleaks_ip'),
            ('https://browserleaks.com/javascript', 'browserleaks_js')
        ]

        for url, name in test_sites:
            try:
                await page.goto(url, wait_until='networkidle', timeout=120000)
                await page.wait_for_timeout(random.randint(3000, 7000))  # Random delay
                await page.screenshot(path=f'results/{name}_test.png', full_page=True)
                print(f'✅ Completed test: {name}')
                
                # Extra validation for critical sites
                if 'creepjs' in url:
                    await page.evaluate('''() => {
                        const trustScore = document.querySelector('.trust-score').innerText;
                        console.log('CreepJS Trust Score:', trustScore);
                    }''')
            except Exception as e:
                print(f'❌ Failed {name}: {str(e)}')

        # Version validation
        await page.goto('chrome://version/', timeout=60000)
        await page.screenshot(path='results/chrome_version.png')

        # Manual inspection period
        print("Browser ready for manual inspection...")
        await asyncio.sleep(3600)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(anti_detection_browser())