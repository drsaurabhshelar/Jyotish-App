import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(2000)

        modal_cells = await page.query_selector_all("[onclick*='openCalendarModal']")
        print("openCalendarModal cells count:", len(modal_cells))
        if modal_cells:
            # Click first cell
            oc = await modal_cells[0].get_attribute("onclick")
            print("Executing click on cell with onclick:", oc)
            await modal_cells[0].click()
            await page.wait_for_timeout(500)

            # Check modal
            modals = await page.query_selector_all(".modal")
            print("Found modals count:", len(modals))
            for m in modals:
                is_vis = await m.is_visible()
                m_id = await m.get_attribute("id")
                print(f"Modal ID {m_id} visible: {is_vis}")
                if is_vis:
                    print("Modal content:", await m.inner_text())

        await browser.close()

asyncio.run(run())
