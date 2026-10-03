import os
import glob
import math
import xml.etree.ElementTree as ET

YOGINIS = [
    {'name': 'Mangala', 'years': 1},
    {'name': 'Pingala', 'years': 2},
    {'name': 'Dhanya', 'years': 3},
    {'name': 'Bhramari', 'years': 4},
    {'name': 'Bhadrika', 'years': 5},
    {'name': 'Ulka', 'years': 6},
    {'name': 'Siddha', 'years': 7},
    {'name': 'Sankata', 'years': 8},
]

TOTAL_YOGINI_YEARS = 36.0
DAYS_PER_YEAR = 365.2425

def calculate_moon_lon(jd):
    T = (jd - 2451545.0) / 36525.0
    L0 = 218.3164477 + 481267.88123421 * T - 0.0015786 * T**2 + T**3 / 538841.0 - T**4 / 65194000.0
    D = 297.8501921 + 445267.1114034 * T - 0.0018819 * T**2 + T**3 / 545868.0 - T**4 / 113065000.0
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T**2 + T**3 / 24490000.0
    M1 = 134.9633964 + 477198.8675055 * T + 0.0087414 * T**2 + T**3 / 69699.0 - T**4 / 14712000.0
    F = 93.2720950 + 483202.0175233 * T - 0.0036539 * T**2 - T**3 / 3526000.0 + T**4 / 863310000.0

    def rad(deg): return math.radians(deg)

    dL = (62886 * math.sin(rad(M1)) +
          12740 * math.sin(rad(2*D - M1)) +
          6583 * math.sin(rad(2*D)) +
          2136 * math.sin(rad(2*M1)) -
          1851 * math.sin(rad(M)) -
          1143 * math.sin(rad(2*F)) +
          587 * math.sin(rad(2*D - 2*M1)) +
          570 * math.sin(rad(2*D - M - M1)) +
          533 * math.sin(rad(2*D + M1)) +
          457 * math.sin(rad(2*D - M)) -
          410 * math.sin(rad(M - M1)) -
          347 * math.sin(rad(D)) -
          306 * math.sin(rad(M + M1))) / 10000.0

    tropical_lon = (L0 + dL) % 360.0
    year = 2000.0 + (jd - 2451545.0) / 365.25
    ayanamsa = 23.85709167 + (year - 2000.0) * 0.0139694
    sidereal_lon = (tropical_lon - ayanamsa) % 360.0
    return sidereal_lon

def jd_to_date_string(jd):
    # Standard Astronomical Julian Day Number to Gregorian calendar date YYYY-MM-DD
    Z = int(math.floor(jd + 0.5))
    if Z < 2299161:
        A = Z
    else:
        alpha = int(math.floor((Z - 1867216.25) / 36524.25))
        A = Z + 1 + alpha - int(math.floor(alpha / 4.0))

    B = A + 1524
    C = int(math.floor((B - 122.1) / 365.25))
    D = int(math.floor(365.25 * C))
    E = int(math.floor((B - D) / 30.6001))

    day = int(math.floor(B - D - int(math.floor(30.6001 * E))))
    month = int(E - 1 if E < 14 else E - 13)
    year = int(C - 4715 if month > 2 else C - 4604)

    return f"{year:04d}-{month:02d}-{day:02d}"

def get_yogini_periods(birth_jd, max_years=100):
    moon_lon = calculate_moon_lon(birth_jd)
    nak_span = 360.0 / 27.0
    nak_index = int(math.floor(moon_lon / nak_span)) # 0 to 26
    nak_num = nak_index + 1
    rem_deg = moon_lon % nak_span

    elapsed_fraction = rem_deg / nak_span

    # Starting Yogini
    start_y_idx = (nak_num + 3 - 1) % 8

    # MD 0 total duration
    first_md_years = YOGINIS[start_y_idx]['years']
    elapsed_md_days = elapsed_fraction * first_md_years * DAYS_PER_YEAR

    # Start JD of MD 0
    md_start_jd = birth_jd - elapsed_md_days

    periods = []
    current_md_start_jd = md_start_jd
    curr_y_idx = start_y_idx

    end_jd_limit = birth_jd + (max_years * DAYS_PER_YEAR)

    while current_md_start_jd < end_jd_limit:
        md_info = YOGINIS[curr_y_idx]
        md_name = md_info['name']
        md_years = md_info['years']
        md_duration_days = md_years * DAYS_PER_YEAR

        # Calculate ADs within this MD
        curr_ad_start_jd = current_md_start_jd
        for ad_offset in range(8):
            ad_y_idx = (curr_y_idx + ad_offset) % 8
            ad_info = YOGINIS[ad_y_idx]
            ad_name = ad_info['name']
            ad_years = ad_info['years']

            ad_duration_days = (md_years * ad_years / TOTAL_YOGINI_YEARS) * DAYS_PER_YEAR
            curr_ad_end_jd = curr_ad_start_jd + ad_duration_days

            periods.append({
                'mahadasha': md_name,
                'antardasha': ad_name,
                'start_jd': curr_ad_start_jd,
                'end_jd': curr_ad_end_jd,
                'start_date': jd_to_date_string(curr_ad_start_jd),
                'end_date': jd_to_date_string(curr_ad_end_jd),
            })

            curr_ad_start_jd = curr_ad_end_jd

        current_md_start_jd += md_duration_days
        curr_y_idx = (curr_y_idx + 1) % 8

    return periods

def main():
    files = sorted(glob.glob('Kundalis/*.xml'))
    print(f"Found {len(files)} XML files.")
    for f in files:
        tree = ET.parse(f)
        root = tree.getroot()
        binfo = root.find('BirthInfo')
        fname = binfo.find('FirstName').text or ''
        lname = binfo.find('LastName').text or ''
        birth_jd = float(binfo.find('BirthDate').text)

        periods = get_yogini_periods(birth_jd)
        print(f"\n--- {fname} {lname} (Birth JD: {birth_jd}) ---")
        print(f"First 5 periods:")
        for p in periods[:5]:
            print(f"  MD: {p['mahadasha']:<10} AD: {p['antardasha']:<10} | {p['start_date']} to {p['end_date']}")

if __name__ == '__main__':
    main()
