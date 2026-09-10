import asyncio
from playwright.async_api import async_playwright

EXPECTED_VRUKSHA = {
    "अश्विनी": "करस्तर",
    "भरणी": "आमलक (आँवला)",
    "कृत्तिका": "उदुम्बर (गूलर)",
    "रोहिणी": "जामुन",
    "मृगशिरा": "खैर",
    "आर्द्रा": "कृष्ण",
    "पुनर्वसु": "पिप्पली",
    "पुष्य": "बाँस",
    "आश्लेषा": "नाग",
    "मघा": "रोहिण",
    "पूर्वाफाल्गुनी": "पलाश",
    "उत्तराफाल्गुनी": "पर्कटी",
    "हस्त": "आम्र",
    "चित्रा": "बिल्व",
    "स्वाती": "अर्जुन",
    "विशाखा": "विकंकत",
    "अनुराधा": "वकुल",
    "ज्येष्ठा": "सरल (देवदार)",
    "मूल": "सर्ज",
    "पूर्वाषाढ़ा": "बकुल",
    "उत्तराषाढ़ा": "पनस (कटहल)",
    "श्रवण": "अर्कक (मदार)",
    "धनिष्ठा": "शमी",
    "शतभिषा": "कदम्ब",
    "पूर्वाभाद्रपद": "आम",
    "उत्तराभाद्रपद": "निम्ब",
    "रेवती": "मधूक"
}

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("http://localhost:8000/panchang-v128.html")
        await page.wait_for_timeout(1000)

        found = set()

        for year in [2026, 2027]:
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
                            found.add(nak_name)

        print("Total unique found:", len(found))
        missing = set(EXPECTED_VRUKSHA.keys()) - found
        print("Missing nakshatras:", missing)
        await browser.close()

asyncio.run(run())
