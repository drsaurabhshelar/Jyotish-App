import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(1000)

        cells = await page.query_selector_all(".calendar-day")
        print("Cell count:", len(cells))
        for i, c in enumerate(cells[:5]):
            text = await c.inner_text()
            print(f"Cell {i}:", repr(text))
        await browser.close()

asyncio.run(run())
