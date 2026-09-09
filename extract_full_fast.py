import asyncio
import json
import os
import time
from playwright.async_api import async_playwright

async def extract_all_days_fast():
    start_time = time.time()
    print("Starting ultra-fast extraction of all 365 days of 2026...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_path = os.path.abspath('calendar.html')
        await page.goto(f'file://{file_path}', wait_until='networkidle')

        result = await page.evaluate('''() => {
            let records = [];
            let days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
            let months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

            for (let i = 0; i < 365; i++) {
                let d = new Date(2026, 0, 1 + i);
                let year = d.getFullYear();
                let monthIdx = d.getMonth();
                let dateNum = d.getDate();
                let dayName = days[d.getDay()];
                let monthName = months[monthIdx];
                let dateStr = `${dayName} ${monthName} ${dateNum < 10 ? '0' + dateNum : dateNum} ${year}`;

                // Call modal function directly
                openCalendarModal(year, monthIdx, dateStr);

                let modalContent = document.querySelector("#calModalScrollContainer");
                let modalHtml = modalContent ? modalContent.innerHTML : '';
                let modalText = modalContent ? modalContent.innerText : '';

                // Clean up modal
                let bg = document.querySelector("#calModalBg");
                if (bg) bg.remove();

                records.push({
                    day_number: i + 1,
                    iso_date: d.toISOString().split('T')[0],
                    date_str: dateStr,
                    modal_html: modalHtml,
                    modal_text: modalText
                });
            }
            return records;
        }''')

        await browser.close()

    print(f"Extracted {len(result)} records in {time.time() - start_time:.2f} seconds.")

    with open('/tmp/extracted_full_days.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("Saved to /tmp/extracted_full_days.json successfully!")

if __name__ == '__main__':
    asyncio.run(extract_all_days_fast())
