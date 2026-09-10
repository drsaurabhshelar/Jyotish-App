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
            if (typeof window.openCalendarModal === 'function') {
                window.openCalendarModal(2026, 0, dateObj.toDateString());
                const container = document.getElementById('calModalScrollContainer');
                if (!container) return 'calModalScrollContainer not found';
                const boxes = Array.from(container.querySelectorAll('.day-info-box'));
                return boxes.map(b => b.innerText);
            }
            return 'no function';
        }""")
        print("Modal boxes text:", res)
        await browser.close()

asyncio.run(run())
