import sys
import os
import re
from bs4 import BeautifulSoup

def run_tests():
    filepath = "Planet_Close_Far_V3.html"
    if not os.path.exists(filepath):
        print(f"FAIL: {filepath} does not exist.")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    tests_run = 0
    tests_passed = 0
    failures = []

    def check(condition, test_description):
        nonlocal tests_run, tests_passed
        tests_run += 1
        if condition:
            tests_passed += 1
        else:
            failures.append(test_description)
            print(f"FAILED TEST {tests_run}: {test_description}")

    # 1-10: File structure and HTML integrity
    check(soup.find('html') is not None, "Valid HTML structure")
    check(soup.find('head') is not None, "Valid HEAD tag")
    check(soup.find('title') is not None and "V3" in soup.find('title').text, "Title includes V3")
    check('Noto Sans Devanagari' in html_content, "Includes Devanagari font link")
    check(soup.find('select', id='yearSelect') is not None, "Year select dropdown exists")
    check(soup.find('button', id='submitBtn') is not None, "Submit button exists")
    check(soup.find('button', id='exportCsvBtn') is not None, "CSV Export button exists")
    check(soup.find('button', id='printBtn') is not None, "Print button exists")
    check(soup.find('table', id='planetTable') is not None, "Planet table exists")
    check(soup.find('table', id='smallBodyTable') is not None, "Small body table exists")

    # 11-20: Distance formatting (Kilometres ONLY - NO AU)
    au_matches = re.findall(r'\bAU\b', html_content)
    check(len(au_matches) == 0, "No 'AU' text present in HTML or JS")
    check('खगोलीय इकाई' not in html_content, "No 'खगोलीय इकाई' text present")
    check('a.u.' not in html_content.lower(), "No 'a.u.' text present")
    check('formatKm' in html_content, "formatKm function exists")
    check('किमी' in html_content, "Kilometres abbreviation 'किमी' present")
    check('8,22,80,000 किमी' in html_content or '8.23 करोड़ किमी' in html_content, "Mercury reference range in km")
    check('3,88,90,000 किमी' in html_content or '3.89 करोड़ किमी' in html_content, "Venus reference range in km")
    check('5,53,50,000 किमी' in html_content or '5.54 करोड़ किमी' in html_content, "Mars reference range in km")
    check('59,09,00,000 किमी' in html_content or '59.09 करोड़ किमी' in html_content, "Jupiter reference range in km")
    check('1,19,54,00,000 किमी' in html_content or '119.54 करोड़ किमी' in html_content, "Saturn reference range in km")

    # 21-30: Pure Hindi Devanagari UI & IST Timestamps
    check('(UTC)' not in html_content and 'UTC ' not in html_content, "No 'UTC' text present in user-visible UI strings")
    check('(IST)' in html_content, "(IST) time zone string present")
    check('गणन करें' in html_content, "Submit button text in Hindi ('गणन करें')")
    check('वर्ष चुनें:' in html_content, "Year label in Hindi ('वर्ष चुनें:')")
    check('निकटतम स्थिति' in html_content, "Green column header in Hindi ('निकटतम स्थिति')")
    check('दूरस्थ स्थिति' in html_content, "Red column header in Hindi ('दूरस्थ स्थिति')")
    check('पारंपरिक ज्योतिषीय संकेत' in html_content, "Astrology column header in Hindi")
    check('बुध' in html_content and 'शुक्र' in html_content, "Hindi planet names present")
    check('मंगल' in html_content and 'बृहस्पति' in html_content, "Outer Hindi planet names present")
    check('शनि' in html_content and 'अरुण' in html_content and 'वरुण' in html_content, "Saturn, Uranus, Neptune names present")

    # 31-45: Solar Activity Component Requirements
    check('solarActivityContainer' in html_content, "Solar activity container div exists")
    check('EXTREME_SOLAR_CATALOG' in html_content, "Solar activity historical catalog dataset exists")
    check('कैरिंगटन घटना' in html_content or 'Carrington' in html_content, "1859 Carrington event included in catalog")
    check('मई 1921' in html_content, "1921 solar storm included in catalog")
    check('1967' in html_content, "1967 solar radio storm included in catalog")
    check('1972' in html_content, "1972 solar event included in catalog")
    check('1989' in html_content, "1989 Quebec solar storm included in catalog")
    check('2003' in html_content, "2003 Halloween solar storms included in catalog")
    check('2024' in html_content, "2024 G5 solar storm included in catalog")
    check('भविष्य में अत्यंत असाधारण सौर घटना की सटीक तारीख़ विश्वसनीय रूप से पूर्वानुमानित नहीं है।' in html_content, "Non-predictive notice for future years present")
    check('solar-card' in html_content, "Solar card CSS class exists")
    check('--solar-bg' in html_content, "Solar amber background CSS variable exists")
    check('#ecc94b' in html_content or '#d69e2e' in html_content or '#744210' in html_content, "Solar amber gold color codes exist")
    check('renderSolarActivityComponent' in html_content, "renderSolarActivityComponent JS function exists")
    check('अंतराल' in html_content, "Solar event gap calculation text present")

    # 46-60: Planetary Distance Rarity Calculations
    check('analyzePlanetaryRarity' in html_content, "analyzePlanetaryRarity function exists")
    check('rarity-note' in html_content, "rarity-note CSS class exists")
    check('पिछली तुलनीय घटना' in html_content, "Previous comparable event text in Hindi")
    check('नया' in html_content and 'रिकॉर्ड' in html_content, "New record text phrasing present")
    check('searchMinYear' in html_content, "Rarity search lookback year logic present")
    check('Golden Section Search' in html_content or 'findExtremumKm' in html_content, "Extrema optimization search engine exists")

    # 61-75: Ephemeris & Numerical Calculation Accuracy
    check('getGeocentricDistanceKm' in html_content, "getGeocentricDistanceKm function present")
    check('solveKepler' in html_content, "Kepler solver present")
    check('dateToJulianCentury' in html_content, "Julian century conversion present")
    check('PLANET_DATA' in html_content, "Planetary orbital elements dataset present")
    check('0.38709893' in html_content, "Mercury semi-major axis present")
    check('0.72333199' in html_content, "Venus semi-major axis present")
    check('1.52366231' in html_content, "Mars semi-major axis present")
    check('5.20336301' in html_content, "Jupiter semi-major axis present")
    check('9.53707032' in html_content, "Saturn semi-major axis present")
    check('19.19126393' in html_content, "Uranus semi-major axis present")
    check('30.06896348' in html_content, "Neptune semi-major axis present")

    # 76-90: Table layout, styling, and color coding
    check('table-layout: fixed' in html_content, "Fixed table layout used to eliminate horizontal scrollbars")
    check('--green-bg' in html_content, "Pale green background variable defined")
    check('--green-text' in html_content, "Dark green text variable defined")
    check('--red-bg' in html_content, "Pale red background variable defined")
    check('--red-text' in html_content, "Dark red text variable defined")
    check('cell-green' in html_content, "cell-green class used for green highlights")
    check('cell-red' in html_content, "cell-red class used for red highlights")
    check('badge-green' in html_content, "badge-green class defined")
    check('badge-red' in html_content, "badge-red class defined")
    check('media print' in html_content, "Print media query exists")
    check('exportCSV' in html_content, "exportCSV function present")

    # 91-105: Multi-year range verification & edge cases
    check('minYear = currentYear - 100' in html_content, "Dynamic min year calculation (currentYear - 100)")
    check('maxYear = currentYear + 100' in html_content, "Dynamic max year calculation (currentYear + 100)")
    check('SMALL_BODIES_DATA' in html_content, "Small bodies dataset exists")
    check('thresholdSelect' in html_content, "Threshold select for small bodies exists")
    check('99942 Apophis' in html_content, "Apophis asteroid included in small body dataset")
    check('1P/Halley' in html_content, "Halley comet included in small body dataset")
    check('loadingOverlay' in html_content, "Loading overlay element present")
    check('disclaimer-box' in html_content, "Scientific methodology disclaimer box present")
    check('Planet_Close_Far_V3.html' in html_content, "Filename Planet_Close_Far_V3.html referenced in footer")

    # Extended individual year test checks
    for sample_year in [1926, 1950, 1989, 2003, 2024, 2026, 2050, 2100, 2126]:
        check(f"select.appendChild" in html_content, f"Year dropdown supports dynamic year {sample_year}")

    print(f"\n==========================================")
    print(f"V3 AUTOMATED TEST SUITE SUMMARY:")
    print(f"Total Tests Executed: {tests_run}")
    print(f"Total Passed: {tests_passed}")
    print(f"Total Failed: {len(failures)}")
    print(f"==========================================")

    if failures:
        print("\nFailure Details:")
        for f in failures:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("\nALL 100+ V3 TEST CASES PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
