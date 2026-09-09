import json
import re

def build_html():
    with open('/tmp/extracted_full_days.json', 'r', encoding='utf-8') as f:
        days_data = json.load(f)

    with open('calendar.html', 'r', encoding='utf-8') as f:
        cal_html = f.read()

    style_match = re.search(r'<style>(.*?)</style>', cal_html, re.DOTALL)
    original_css = style_match.group(1) if style_match else ""

    pages_html = []

    for day in days_data:
        day_num = day['day_number']
        iso_date = day['iso_date']
        date_str = day['date_str']
        modal_html = day['modal_html']

        # Clean modal html: remove close button (button with × or onclick document.getElementById('calModalBg').remove())
        modal_html = re.sub(r'<button[^>]*onclick="document\.getElementById\(\'calModalBg\'\)\.remove\(\)"[^>]*>.*?</button>', '', modal_html, flags=re.DOTALL)
        modal_html = re.sub(r'<button[^>]*>✕</button>', '', modal_html)
        modal_html = re.sub(r'<button[^>]*>×</button>', '', modal_html)

        page_code = f"""
        <div class="a4-page">
            <div class="bg-watermark"></div>
            <div class="page-header">
                <div class="day-badge">DAY {day_num} / 365</div>
                <div class="header-title">शिवसिद्ध पंचांग एवं कैलेंडर 2026</div>
                <div class="date-badge">{date_str} ({iso_date})</div>
            </div>
            <div class="page-content">
                {modal_html}
            </div>
            <div class="page-footer">
                <span>Shivsiddha Calendar 2026</span>
                <span>Page {day_num} of 365</span>
            </div>
        </div>
        """
        pages_html.append(page_code)

    full_document = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <title>Shivsiddha Calendar 2026 - 365 Days Complete Edition</title>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        {original_css}

        @page {{
            size: A4 portrait;
            margin: 0;
        }}

        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }}

        body {{
            margin: 0;
            padding: 0;
            background: #e2e8f0;
            font-family: 'Noto Sans Devanagari', 'Cinzel', system-ui, sans-serif;
            color: #2d3748;
        }}

        .a4-page {{
            width: 210mm;
            height: 297mm;
            position: relative;
            margin: 0 auto 10mm auto;
            padding: 6mm 8mm 5mm 8mm;
            background: #ffffff;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            page-break-after: always;
            page-break-inside: avoid;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        @media print {{
            body {{
                background: none;
            }}
            .a4-page {{
                margin: 0;
                box-shadow: none;
                width: 210mm;
                height: 297mm;
            }}
        }}

        .bg-watermark {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(circle at 50% 50%, rgba(221, 107, 32, 0.02) 0%, rgba(255, 255, 255, 0) 70%),
                linear-gradient(to bottom, rgba(253, 250, 246, 0.4), rgba(255, 255, 255, 1));
            border: 5px solid #fbd38d18;
            pointer-events: none;
            z-index: 0;
        }}

        .page-header {{
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid var(--primary-color, #dd6b20);
            padding-bottom: 2px;
            margin-bottom: 3px;
        }}

        .day-badge {{
            background: var(--primary-color, #dd6b20);
            color: #ffffff;
            font-size: 8pt;
            font-weight: 700;
            padding: 1px 5px;
            border-radius: 3px;
        }}

        .header-title {{
            font-size: 10pt;
            font-weight: 800;
            color: var(--primary-color, #dd6b20);
            letter-spacing: 0.5px;
        }}

        .date-badge {{
            font-size: 8pt;
            font-weight: 600;
            color: #4a5568;
        }}

        .page-content {{
            position: relative;
            z-index: 1;
            flex-grow: 1;
            font-size: 6.8pt;
            line-height: 1.1;
            overflow: hidden;
        }}

        /* Reset modal container scroll limits for print */
        .page-content .card, .page-content .modal-scroll-container {{
            width: 100% !important;
            max-width: 100% !important;
            max-height: none !important;
            overflow-y: visible !important;
            box-shadow: none !important;
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }}

        /* Compact elements for A4 single-page fit */
        .page-content h2 {{
            font-size: 9pt !important;
            margin-top: 1px !important;
            margin-bottom: 1px !important;
            padding-bottom: 1px !important;
        }}

        .page-content h3 {{
            font-size: 8pt !important;
            margin-top: 1px !important;
            margin-bottom: 1px !important;
        }}

        .page-content h4 {{
            font-size: 7.2pt !important;
            margin-top: 1px !important;
            margin-bottom: 1px !important;
        }}

        .page-content p, .page-content div {{
            margin-bottom: 1px !important;
        }}

        .page-content [style*="grid"] {{
            gap: 2px !important;
            margin-bottom: 2px !important;
        }}

        .page-content [style*="padding: 10px"], .page-content [style*="padding: 15px"], .page-content [style*="padding: 12px"] {{
            padding: 2px 4px !important;
        }}

        .page-content [style*="padding: 22px"] {{
            padding: 6px 0 !important;
        }}

        .page-content svg {{
            max-height: 60px !important;
            width: auto !important;
        }}

        .page-footer {{
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            font-size: 6.5pt;
            color: #a0aec0;
            border-top: 1px solid #e2e8f0;
            padding-top: 1px;
            margin-top: 1px;
        }}
    </style>
</head>
<body>
    {''.join(pages_html)}
</body>
</html>
"""

    with open('/tmp/calendar_365_pages.html', 'w', encoding='utf-8') as f:
        f.write(full_document)

    print("Successfully built cleaned /tmp/calendar_365_pages.html")

if __name__ == '__main__':
    build_html()
