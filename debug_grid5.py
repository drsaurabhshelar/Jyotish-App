import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(2000)

        # Execute openCalendarModal directly in page context
        res = await page.evaluate("""() => {
            if (typeof window.openCalendarModal === 'function') {
                window.openCalendarModal(2026, 8, 'Tue Sep 01 2026');
                const modals = document.querySelectorAll('.modal, [id*="modal"], [class*="modal"]');
                return Array.from(modals).map(m => ({id: m.id, className: m.className, innerHTML: m.innerHTML.slice(0, 100)}));
            }
            return 'openCalendarModal not a function';
        }""")
        print("Evaluate result:", res)
        await browser.close()

asyncio.run(run())
