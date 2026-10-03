#!/usr/bin/env python3
"""
test_birthday_generator.py

Generates synthetic XML Kundali files along with non-XML files (.grp, .pdf, .txt),
and tests generate_birthday_pdf.py to ensure strictly XML files are processed
and DOB records extracted across varied encodings and structures.
"""

import os
import shutil
import unittest
from datetime import datetime
import generate_birthday_pdf as gbp
import pypdf

TEST_KUNDALIS_DIR = "Kundalis"
TEST_PDF_PATH = "birthdays.pdf"

SAMPLE_DATA = [
    # (Filename, XML Content, Expected Name, Expected Month, Expected Day, Expected Year)
    (
        "kundali_01.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Aarav Sharma</name>
            <dob>15/01/1992</dob>
            <tob>10:30:00</tob>
            <pob>Delhi</pob>
        </kundali>""",
        "Aarav Sharma", 1, 15, 1992
    ),
    (
        "kundali_02.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali native_name="Bhavna Patel" birthdate="1988-02-28">
            <details>
                <place>Mumbai</place>
            </details>
        </kundali>""",
        "Bhavna Patel", 2, 28, 1988
    ),
    (
        "kundali_03.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <jataka>
            <person_name>Chirag Gupta</person_name>
            <date_of_birth>10-03-1995</date_of_birth>
        </jataka>""",
        "Chirag Gupta", 3, 10, 1995
    ),
    (
        "kundali_04.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <horoscope>
            <full_name>Divya Joshi</full_name>
            <birth_day>05</birth_day>
            <birth_month>04</birth_month>
            <birth_year>1999</birth_year>
        </horoscope>""",
        "Divya Joshi", 4, 5, 1999
    ),
    (
        "kundali_05.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <chart>
            <title>Esha Kumar</title>
            <date>1991/05/20</date>
        </chart>""",
        "Esha Kumar", 5, 20, 1991
    ),
    (
        "kundali_06.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Farhan Akhtar</name>
            <dob>18 June 1985</dob>
        </kundali>""",
        "Farhan Akhtar", 6, 18, 1985
    ),
    (
        "kundali_07.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Gita Roy</name>
            <dob>04/07/2001</dob>
        </kundali>""",
        "Gita Roy", 7, 4, 2001
    ),
    (
        "kundali_08.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Harish Verma</name>
            <dob>25-08-1993</dob>
        </kundali>""",
        "Harish Verma", 8, 25, 1993
    ),
    (
        "kundali_09.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Isha Nair</name>
            <dob>09/09/1997</dob>
        </kundali>""",
        "Isha Nair", 9, 9, 1997
    ),
    (
        "kundali_10.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Jai Singh</name>
            <dob>12/10/1980</dob>
        </kundali>""",
        "Jai Singh", 10, 12, 1980
    ),
    (
        "kundali_11.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Kavita Reddy</name>
            <dob>11/11/1994</dob>
        </kundali>""",
        "Kavita Reddy", 11, 11, 1994
    ),
    (
        "kundali_12.xml",
        """<?xml version="1.0" encoding="UTF-8"?>
        <kundali>
            <name>Lakshmi Narayanan</name>
            <dob>31/12/1986</dob>
        </kundali>""",
        "Lakshmi Narayanan", 12, 31, 1986
    ),
    # Additional test XML with regex fallback date and non-standard structure
    (
        "kundali_13_unstructured.xml",
        """<!-- Custom Kundali format -->
        <custom_kundali>
            <client_name>Mohan Das</client_name>
            <description>Born on 14/08/1975 at 05:00 AM in Chennai</description>
        </custom_kundali>""",
        "Mohan Das", 8, 14, 1975
    )
]

NON_XML_FILES = [
    ("data.grp", "BINARY_OR_GRP_DATA_01010101"),
    ("sample.pdf", "%PDF-1.4 ... Fake PDF binary content ..."),
    ("notes.txt", "Some text file notes about birthdates"),
    ("chart.png", "PNG Fake Image Bytes")
]

def setup_test_files():
    """Creates the Kundalis directory and populates test XML and non-XML files."""
    if os.path.exists(TEST_KUNDALIS_DIR):
        shutil.rmtree(TEST_KUNDALIS_DIR)
    os.makedirs(TEST_KUNDALIS_DIR, exist_ok=True)

    # Write XML files
    for filename, content, _, _, _, _ in SAMPLE_DATA:
        filepath = os.path.join(TEST_KUNDALIS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip())

    # Write Non-XML files to ensure scanner ignores them
    for filename, content in NON_XML_FILES:
        filepath = os.path.join(TEST_KUNDALIS_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

class TestBirthdayGenerator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        setup_test_files()

    def test_xml_only_filtering(self):
        xml_files = gbp.find_xml_files(TEST_KUNDALIS_DIR)
        # Verify non-xml files are excluded
        self.assertEqual(len(xml_files), len(SAMPLE_DATA))
        for xml_f in xml_files:
            self.assertTrue(xml_f.lower().endswith(".xml"))

    def test_xml_parsing_and_sorting(self):
        xml_files = gbp.find_xml_files(TEST_KUNDALIS_DIR)
        records = []
        for xml_file in xml_files:
            rec = gbp.parse_xml_for_dob_and_name(xml_file)
            self.assertIsNotNone(rec, f"Failed to parse {xml_file}")
            records.append(rec)

        self.assertEqual(len(records), len(SAMPLE_DATA))

        grouped = gbp.group_and_sort_birthdays(records)

        # Check all 12 months are present
        for month_num in range(1, 13):
            self.assertIn(month_num, grouped)
            self.assertGreaterEqual(len(grouped[month_num]), 1)

        # Generate PDF
        gbp.create_pdf(grouped, TEST_PDF_PATH)
        self.assertTrue(os.path.exists(TEST_PDF_PATH))
        self.assertGreater(os.path.getsize(TEST_PDF_PATH), 0)

        # Verify PDF page content using pypdf
        reader = pypdf.PdfReader(TEST_PDF_PATH)
        self.assertGreater(len(reader.pages), 0)
        extracted_text = "".join([page.extract_text() for page in reader.pages])

        # Check that expected names are in PDF
        for _, _, name, _, _, _ in SAMPLE_DATA:
            self.assertIn(name, extracted_text)

if __name__ == "__main__":
    unittest.main()
