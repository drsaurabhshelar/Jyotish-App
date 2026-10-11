import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        file_url = f"file://{os.path.abspath('Planet_Close_Far_V2.html')}"
        await page.goto(file_url)
        await page.wait_for_timeout(1000)

        # Check horizontal scrollbar status on body/document
        scroll_width = await page.evaluate("document.documentElement.scrollWidth")
        client_width = await page.evaluate("document.documentElement.clientWidth")
        print(f"Viewport Client Width: {client_width}, Document Scroll Width: {scroll_width}")

        os.makedirs("/home/jules/verification", exist_ok=True)
        screenshot_path = "/home/jules/verification/verification_v2.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
