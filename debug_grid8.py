import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(1000)

        res = await page.evaluate("""() => {
            const dateObj = new Date(2026, 0, 1);
            window.openCalendarModal(2026, 0, dateObj.toDateString());

            // Check document.body.innerHTML for any modal or overlay
            const overlays = Array.from(document.querySelectorAll('div')).filter(d => d.style && d.style.position === 'fixed');
            return overlays.map(o => ({
                style: o.getAttribute('style'),
                innerText: o.innerText.slice(0, 300)
            }));
        }""")
        print("Fixed overlays count:", len(res))
        for item in res:
            print(item)
        await browser.close()

asyncio.run(run())
