import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = await browser.new_page()

        html_file = "/tmp/calendar_365_pages.html"
        print(f"Loading HTML into Playwright: {html_file}...")
        await page.goto(f"file://{os.path.abspath(html_file)}", wait_until="networkidle")

        pdf_path = "calendar_2026_365_days.pdf"
        print(f"Generating PDF: {pdf_path}...")

        await page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            margin={"top": "0mm", "right": "0mm", "bottom": "0mm", "left": "0mm"},
            prefer_css_page_size=True
        )
        await browser.close()
        print(f"PDF successfully generated at {pdf_path}!")

if __name__ == "__main__":
    asyncio.run(main())
