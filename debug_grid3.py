import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(2000)

        # Click on cell with openCalendarModal
        modal_cells = await page.query_selector_all("[onclick*='openCalendarModal']")
        print("openCalendarModal cells count:", len(modal_cells))
        if modal_cells:
            await modal_cells[0].click()
            await page.wait_for_timeout(500)
            modal = await page.query_selector("#calendarModal")
            print("Modal visible:", await modal.is_visible() if modal else False)
            if modal:
                text = await modal.inner_text()
                print("Modal inner text:\n", text)
        await browser.close()

asyncio.run(run())
