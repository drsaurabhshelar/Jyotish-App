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
            const modals = document.querySelectorAll('div');
            const found = [];
            for (let d of modals) {
                if (d.innerText && d.innerText.includes('नक्षत्र')) {
                    found.push({id: d.id, className: d.className, text: d.innerText.slice(0, 200)});
                }
            }
            return found;
        }""")
        print("Found divs count:", len(res))
        for item in res[:5]:
            print(item)
        await browser.close()

asyncio.run(run())
