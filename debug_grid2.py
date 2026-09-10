import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(2000)

        body_text = await page.evaluate("() => document.body.innerText")
        print("Body text snippet:", repr(body_text[:300]))

        clickable = await page.query_selector_all("[onclick]")
        print("Clickable elements count:", len(clickable))
        for c in clickable[:5]:
            oc = await c.get_attribute("onclick")
            print("onclick:", oc)

        await browser.close()

asyncio.run(run())
