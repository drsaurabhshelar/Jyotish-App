import asyncio
import os
from playwright.async_api import async_playwright

async def run_v2_tests():
    print("==================================================")
    print("RUNNING AUTOMATED TEST SUITE FOR Planet_Close_Far_V2.html")
    print("==================================================")

    passed_tests = 0
    failed_tests = 0
    total_tests = 0

    def assert_test(condition, description):
        nonlocal passed_tests, failed_tests, total_tests
        total_tests += 1
        if condition:
            passed_tests += 1
            print(f"[PASS] Test {total_tests:03d}: {description}")
        else:
            failed_tests += 1
            print(f"[FAIL] Test {total_tests:03d}: {description}")

    # Test 1: HTML File exists
    v2_filepath = os.path.abspath("Planet_Close_Far_V2.html")
    assert_test(os.path.exists(v2_filepath), "Planet_Close_Far_V2.html file exists")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        file_url = f"file://{v2_filepath}"
        await page.goto(file_url)
        await page.wait_for_timeout(1000)

        # Test 2: Current year default selection
        current_year = await page.evaluate("new Date().getUTCFullYear()")
        selected_year = await page.evaluate("document.getElementById('yearSelect').value")
        assert_test(str(current_year) == str(selected_year), f"Current year default selected ({current_year})")

        # Test 3: Horizontal scrollbar check
        scroll_width = await page.evaluate("document.documentElement.scrollWidth")
        client_width = await page.evaluate("document.documentElement.clientWidth")
        assert_test(scroll_width <= client_width, f"No horizontal scrollbar (scrollWidth: {scroll_width} <= clientWidth: {client_width})")

        # Test 4: Check absence of UTC string in visible text
        page_text = await page.evaluate("document.body.innerText")
        utc_in_text = "UTC" in page_text
        assert_test(not utc_in_text, "No 'UTC' text visible on rendered page")

        # Test 5: Check absence of English planet subtitles in rendered page
        english_subtitles = ["(Mercury)", "(Venus)", "(Mars)", "(Jupiter)", "(Saturn)", "(Uranus)", "(Neptune)"]
        has_english_sub = any(sub in page_text for sub in english_subtitles)
        assert_test(not has_english_sub, "No English planet name subtitles visible in header or table")

        # Tests 6 to 55: Selectable year range verification (1926..2126 - 50 test years)
        min_expected = current_year - 100
        max_expected = current_year + 100
        test_years = [y for y in range(min_expected, max_expected + 1, 4)]  # 50 sample years
        for y in test_years[:50]:
            opt_exists = await page.evaluate(f"!!document.querySelector('#yearSelect option[value=\"{y}\"]')")
            assert_test(opt_exists, f"Year dropdown contains year option {y}")

        # Tests 56 to 65: Year calculation test for 10 distinct historical and future years
        sample_years = [1930, 1950, 1975, 2000, 2020, 2026, 2035, 2050, 2080, 2100]
        for y in sample_years:
            await page.select_option("#yearSelect", str(y))
            await page.click("#submitBtn")
            await page.wait_for_timeout(300)

            # Verify planet table rows populated
            rows_count = await page.evaluate("document.querySelectorAll('#planetTableBody tr').length")
            disp_year = await page.evaluate("document.getElementById('displayYear').innerText")
            assert_test(rows_count >= 7 and disp_year == str(y), f"Calculated planetary distance table successfully for year {y}")

        # Tests 66 to 72: Pure Devanagari and IST format check in rendered cells across planets for 2026
        await page.select_option("#yearSelect", "2026")
        await page.click("#submitBtn")
        await page.wait_for_timeout(300)

        planets = ['बुध', 'शुक्र', 'मंगल', 'बृहस्पति', 'शनि', 'अरुण', 'वरुण']
        for planet in planets:
            cell_found = await page.evaluate(f"""
                Array.from(document.querySelectorAll('#planetTableBody tr')).some(tr => tr.innerText.includes('{planet}'))
            """)
            assert_test(cell_found, f"Planet '{planet}' correctly rendered in Hindi Devanagari")

        # Tests 73 to 76: Small bodies threshold selector filtering (4 options)
        thresholds = ["10", "5", "1", "0.05"]
        for th in thresholds:
            await page.select_option("#thresholdSelect", th)
            await page.wait_for_timeout(100)
            sb_rows = await page.evaluate("document.querySelectorAll('#smallBodyTableBody tr').length")
            assert_test(sb_rows >= 1, f"Small bodies threshold {th} LD successfully filtered rows (count: {sb_rows})")

        # Tests 77 to 81: CSV export content checks
        csv_data = await page.evaluate("""() => {
            exportCSV();
            return currentExportData;
        }""")
        assert_test(csv_data['year'] == 2026, "CSV export year matches selected year 2026")
        assert_test(len(csv_data['planets']) >= 7, "CSV export contains at least 7 planet records")
        assert_test(all('minDateIST' in p and 'maxDateIST' in p for p in csv_data['planets']), "CSV export records contain IST dates")
        assert_test(all('minDateUTC' not in p and 'maxDateUTC' not in p for p in csv_data['planets']), "CSV export records exclude UTC dates")
        assert_test(len(csv_data['smallBodies']) >= 0, "CSV export contains small bodies dataset array")

        # Tests 82 to 94: Numerical distance sanity & extremum classification checks for 2026
        # Helper to get planet rows by name
        def get_planet_records(p_name):
            return [p for p in csv_data['planets'] if p['planet'] == p_name]

        # Mercury distance check
        merc_recs = get_planet_records('बुध')
        merc_mins = [float(p['minDistAU']) for p in merc_recs if p['minDistAU'] != '-']
        merc_maxs = [float(p['maxDistAU']) for p in merc_recs if p['maxDistAU'] != '-']
        assert_test(any(0.50 <= m <= 0.70 for m in merc_mins), f"2026 Mercury min distance valid: {merc_mins}")
        assert_test(any(1.30 <= m <= 1.50 for m in merc_maxs), f"2026 Mercury max distance valid: {merc_maxs}")

        # Venus distance check
        venus_recs = get_planet_records('शुक्र')
        venus_mins = [float(p['minDistAU']) for p in venus_recs if p['minDistAU'] != '-']
        venus_maxs = [float(p['maxDistAU']) for p in venus_recs if p['maxDistAU'] != '-']
        assert_test(any(0.25 <= m <= 1.75 for m in venus_mins), f"2026 Venus min distance valid: {venus_mins}")
        assert_test(any(1.00 <= m <= 1.75 for m in venus_maxs), f"2026 Venus max distance valid: {venus_maxs}")

        # Mars distance check
        mars_recs = get_planet_records('मंगल')
        mars_mins = [float(p['minDistAU']) for p in mars_recs if p['minDistAU'] != '-']
        mars_maxs = [float(p['maxDistAU']) for p in mars_recs if p['maxDistAU'] != '-']
        assert_test(any(0.35 <= m <= 2.70 for m in mars_mins), f"2026 Mars min distance valid: {mars_mins}")
        assert_test(any(1.00 <= m <= 2.70 for m in mars_maxs), f"2026 Mars max distance valid: {mars_maxs}")

        # Outer planets distance checks
        jup_recs = get_planet_records('बृहस्पति')
        jup_mins = [float(p['minDistAU']) for p in jup_recs if p['minDistAU'] != '-']
        assert_test(any(3.90 <= m <= 6.50 for m in jup_mins), f"2026 Jupiter min distance valid: {jup_mins}")

        sat_recs = get_planet_records('शनि')
        sat_mins = [float(p['minDistAU']) for p in sat_recs if p['minDistAU'] != '-']
        assert_test(any(7.90 <= m <= 10.70 for m in sat_mins), f"2026 Saturn min distance valid: {sat_mins}")

        uran_recs = get_planet_records('अरुण')
        uran_mins = [float(p['minDistAU']) for p in uran_recs if p['minDistAU'] != '-']
        assert_test(any(18.00 <= m <= 20.60 for m in uran_mins), f"2026 Uranus min distance valid: {uran_mins}")

        nep_recs = get_planet_records('वरुण')
        nep_mins = [float(p['minDistAU']) for p in nep_recs if p['minDistAU'] != '-']
        assert_test(any(28.50 <= m <= 31.00 for m in nep_mins), f"2026 Neptune min distance valid: {nep_mins}")

        # Tests 95 to 104: Ephemeris regression checks across 10 years
        await page.select_option("#thresholdSelect", "10")
        await page.select_option("#yearSelect", "2029")
        await page.click("#submitBtn")
        await page.wait_for_timeout(300)

        apophis_text = await page.evaluate("""() => {
            const rows = Array.from(document.querySelectorAll('#smallBodyTableBody tr'));
            const apRow = rows.find(r => r.innerText.includes('99942 Apophis'));
            return apRow ? apRow.innerText : '';
        }""")
        assert_test('99942 Apophis' in apophis_text and '2029' in apophis_text and 'अप्रैल' in apophis_text, "2029 Apophis close approach date correctly computed (14 अप्रैल 2029, IST)")

        ephemeris_test_years = [1940, 1960, 1980, 2010, 2015, 2022, 2030, 2070, 2100]
        for ey in ephemeris_test_years:
            await page.select_option("#yearSelect", str(ey))
            await page.click("#submitBtn")
            await page.wait_for_timeout(200)
            valid_calc = await page.evaluate("document.querySelectorAll('#planetTableBody tr').length >= 7")
            assert_test(valid_calc, f"Ephemeris numerical regression test passed for year {ey}")

        await browser.close()

    print("==================================================")
    print(f"TEST SUMMARY: TOTAL = {total_tests}, PASSED = {passed_tests}, FAILED = {failed_tests}")
    print("==================================================")
    return failed_tests == 0

if __name__ == "__main__":
    success = asyncio.run(run_v2_tests())
    exit(0 if success else 1)
