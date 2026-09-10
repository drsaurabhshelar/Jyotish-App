import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(1000)

        found_swati = None

        for year in range(2025, 2030):
            for m in range(0, 12):
                for d in range(1, 32):
                    res = await page.evaluate(f"""() => {{
                        try {{
                            const dateObj = new Date({year}, {m}, {d});
                            if (dateObj.getMonth() !== {m}) return null;

                            window.openCalendarModal({year}, {m}, dateObj.toDateString());

                            const overlays = Array.from(document.querySelectorAll('div')).filter(el => el.style && el.style.position === 'fixed');
                            if (overlays.length === 0) return null;

                            const modal = overlays[overlays.length - 1];
                            const text = modal.innerText;

                            const closeBtn = modal.querySelector('button');
                            if (closeBtn) closeBtn.click();
                            else modal.remove();

                            return text;
                        }} catch(e) {{
                            return null;
                        }}
                    }}""")

                    if not res:
                        continue

                    lines = [l.strip() for l in res.split("\n") if l.strip()]
                    for idx, line in enumerate(lines):
                        if "नक्षत्र (Nakshatra)" in line and idx + 1 < len(lines):
                            val = lines[idx + 1]
                            nak_name = val.split("/")[0].strip()
                            if "स्वाती" in nak_name or "स्वाति" in nak_name or "Swati" in val:
                                print(f"Found Swati on {year}-{m+1:02d}-{d:02d}: {val}")
                                found_swati = (year, m+1, d, val, res)
                                break
                    if found_swati:
                        break
                if found_swati:
                    break
            if found_swati:
                break

        await browser.close()
        return found_swati

asyncio.run(run())
