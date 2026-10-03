#!/usr/bin/env python3
"""
generate_birthday_pdf.py

Searches a specified directory (default "Kundalis") strictly for XML files (ignoring .grp, .pdf, etc.),
extracts names and Dates of Birth (DOB) using structured parsing, Julian Day Number (JDN) conversion,
and regex fallback across various encodings, sorts them in ascending order from January to December (and by day/year),
and generates a PDF birthday report grouped by month with clickable month navigation links on the first page.
"""

import os
import sys
import re
import math
import glob
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
from dateutil import parser as date_parser

# ReportLab imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

DATE_REGEX_PATTERNS = [
    r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-\.](0?[1-9]|1[012])[\/\-\.](19|20)\d\d\b', # DD/MM/YYYY
    r'\b(19|20)\d\d[\/\-\.](0?[1-9]|1[012])[\/\-\.](0?[1-9]|[12][0-9]|3[01])\b', # YYYY/MM/DD
    r'\b(0?[1-9]|[12][0-9]|3[01])\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(19|20)\d\d\b', # DD Mon YYYY
    r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(0?[1-9]|[12][0-9]|3[01])[\s,]+(19|20)\d\d\b' # Mon DD, YYYY
]

def julian_day_to_gregorian(jd_value):
    """
    Converts a Julian Day Number (JDN / JD) float/int into a datetime object.
    Used by Parashara's Light / Kundali software XML export formats (<BirthDate>2446255.8715278</BirthDate>).
    """
    try:
        jd = float(jd_value)
        if jd < 2000000 or jd > 3000000:
            return None

        jd += 0.5
        z = math.floor(jd)
        f = jd - z
        if z < 2299161:
            a = z
        else:
            alpha = math.floor((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - math.floor(alpha / 4)
        b = a + 1524
        c = math.floor((b - 122.1) / 365.25)
        d = math.floor(365.25 * c)
        e = math.floor((b - d) / 30.6001)
        day = b - d - math.floor(30.6001 * e) + f
        month = e - 1 if e < 14 else e - 13
        year = c - 4716 if month > 2 else c - 4715

        day_int = int(math.floor(day))
        if day_int < 1 or day_int > 31 or month < 1 or month > 12:
            return None
        return datetime(int(year), int(month), day_int)
    except Exception:
        return None

def find_xml_files(folder_path):
    """
    Finds all XML files in the given directory recursively.
    Strictly filters for files ending in .xml (case-insensitive).
    Excludes files ending with .grp, .pdf, .txt, etc.
    """
    if not os.path.exists(folder_path):
        return []
    xml_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext == ".xml":
                xml_files.append(os.path.join(root, file))
    return sorted(xml_files)

def read_file_content(filepath):
    """
    Attempts to read file content using multiple encodings.
    Returns string content or None.
    """
    encodings = ['utf-8', 'utf-8-sig', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception:
            break
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            return content.decode('utf-8', errors='ignore')
    except Exception:
        return None

def parse_xml_for_dob_and_name(filepath):
    """
    Parses an XML file to extract name and date of birth.
    Returns a dict with 'name', 'dob_str', 'dob_date', 'file' or None if not found/invalid.
    """
    content = read_file_content(filepath)
    if not content or not content.strip():
        print(f"Warning: File '{filepath}' is empty or unreadable.", file=sys.stderr)
        return None

    root = None
    try:
        clean_content = content.strip()
        root = ET.fromstring(clean_content)
    except Exception:
        try:
            if '<' in content:
                content_xml = content[content.find('<'):]
                root = ET.fromstring(content_xml)
        except Exception:
            pass

    name = None
    first_name = None
    last_name = None
    dob_raw = None
    dob_date = None

    name_tags = ["name", "native_name", "person_name", "full_name", "jataka_name", "first_name", "title", "native", "client_name"]
    dob_tags = ["dob", "date_of_birth", "birthdate", "birth_date", "dateofbirth", "date", "birth_date_time", "bdate"]

    if root is not None:
        birth_info = root.find(".//BirthInfo")
        if birth_info is not None:
            fn_elem = birth_info.find("FirstName")
            ln_elem = birth_info.find("LastName")
            bd_elem = birth_info.find("BirthDate")

            if fn_elem is not None and fn_elem.text:
                first_name = fn_elem.text.strip()
            if ln_elem is not None and ln_elem.text:
                last_name = ln_elem.text.strip()

            if first_name and last_name:
                name = f"{first_name} {last_name}"
            elif first_name:
                name = first_name
            elif last_name:
                name = last_name

            if bd_elem is not None and bd_elem.text:
                raw_bd = bd_elem.text.strip()
                jdn_dt = julian_day_to_gregorian(raw_bd)
                if jdn_dt:
                    dob_date = jdn_dt
                    dob_raw = raw_bd

        if not name or not dob_date:
            for elem in root.iter():
                elem_tag = elem.tag.split("}")[-1].lower() if "}" in elem.tag else elem.tag.lower()

                for attr, val in elem.attrib.items():
                    attr_lower = attr.lower()
                    if not name and any(nt in attr_lower for nt in name_tags):
                        name = val.strip()
                    if not dob_raw and any(dt in attr_lower for dt in dob_tags):
                        dob_raw = val.strip()

                if elem.text and elem.text.strip():
                    text_val = elem.text.strip()
                    if elem_tag == "firstname" and not first_name:
                        first_name = text_val
                    elif elem_tag == "lastname" and not last_name:
                        last_name = text_val
                    elif not name and elem_tag in name_tags:
                        name = text_val
                    elif not dob_raw and elem_tag in dob_tags:
                        dob_raw = text_val

            if not name and (first_name or last_name):
                name = f"{first_name or ''} {last_name or ''}".strip()

            if not dob_raw and not dob_date:
                day_elem = (root.find(".//day") if root.find(".//day") is not None else
                            root.find(".//Day") if root.find(".//Day") is not None else
                            root.find(".//birth_day") if root.find(".//birth_day") is not None else
                            root.find(".//bday"))

                month_elem = (root.find(".//month") if root.find(".//month") is not None else
                              root.find(".//Month") if root.find(".//Month") is not None else
                              root.find(".//birth_month") if root.find(".//birth_month") is not None else
                              root.find(".//bmonth"))

                year_elem = (root.find(".//year") if root.find(".//year") is not None else
                             root.find(".//Year") if root.find(".//Year") is not None else
                             root.find(".//birth_year") if root.find(".//birth_year") is not None else
                             root.find(".//byear"))

                if day_elem is not None and month_elem is not None and year_elem is not None:
                    if day_elem.text and month_elem.text and year_elem.text:
                        dob_raw = f"{day_elem.text.strip()}/{month_elem.text.strip()}/{year_elem.text.strip()}"

    if not dob_raw and not dob_date:
        for pattern in DATE_REGEX_PATTERNS:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                dob_raw = match.group(0).strip()
                break

    if not name:
        name_match = re.search(r'<(?:name|native_name|full_name|person_name|title|native)[^>]*>([^<]+)</', content, re.IGNORECASE)
        if name_match:
            name = name_match.group(1).strip()

    if not name:
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        cleaned_name = base_name.replace("_", " ").replace("-", " ")
        if cleaned_name.lower().startswith("kundali"):
            cleaned_name = cleaned_name[7:].strip()
        name = cleaned_name if cleaned_name else base_name

    if not dob_date and dob_raw:
        jdn_dt = julian_day_to_gregorian(dob_raw)
        if jdn_dt:
            dob_date = jdn_dt
        else:
            dob_date = parse_date_string(dob_raw)

    if not dob_date:
        print(f"Warning: Could not parse DOB in '{filepath}'", file=sys.stderr)
        return None

    return {
        "name": name,
        "dob_str": dob_raw or dob_date.strftime("%d/%m/%Y"),
        "dob_date": dob_date,
        "file": os.path.basename(filepath)
    }

def parse_date_string(date_str):
    """Parses various date formats safely."""
    cleaned_str = date_str.strip()
    if " " in cleaned_str and (":" in cleaned_str or "T" in cleaned_str):
        parts = cleaned_str.split()
        cleaned_str = parts[0]

    try:
        return date_parser.parse(cleaned_str, dayfirst=True)
    except Exception:
        try:
            return date_parser.parse(cleaned_str, dayfirst=False)
        except Exception:
            return None

def group_and_sort_birthdays(records):
    """
    Groups records by month (1 to 12) and sorts each month's records by day and year.
    Returns a dict { month_num: [record, ...] }
    """
    grouped = defaultdict(list)
    for rec in records:
        month = rec["dob_date"].month
        grouped[month].append(rec)

    for month in grouped:
        grouped[month].sort(key=lambda r: (r["dob_date"].day, r["dob_date"].year, r["name"].lower()))

    return grouped

def create_pdf(grouped_records, output_pdf_path="birthdays.pdf"):
    """Generates a beautifully formatted PDF grouped by month with navigation links on page 1."""
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1A365D'),
        alignment=1, # Center
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4A5568'),
        alignment=1,
        spaceAfter=15
    )

    nav_heading_style = ParagraphStyle(
        'NavHeading',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#2C6CB0'),
        alignment=1,
        spaceAfter=8
    )

    nav_link_active = ParagraphStyle(
        'NavLinkActive',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1A365D'),
        alignment=1
    )

    nav_link_disabled = ParagraphStyle(
        'NavLinkDisabled',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#A0AEC0'),
        alignment=1
    )

    month_heading_style = ParagraphStyle(
        'MonthHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=12,
        spaceAfter=6
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#2D3748')
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("Birthday Calendar & Directory", title_style))
    total_count = sum(len(records) for records in grouped_records.values())
    generated_on = datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph(f"Total Records: {total_count} &nbsp;|&nbsp; Generated on: {generated_on}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2B6CB0'), spaceAfter=15))

    # --- PAGE 1: MONTH QUICK NAVIGATION GRID ---
    elements.append(Paragraph("<b>Quick Jump to Month</b>", nav_heading_style))

    # Build 4 columns x 3 rows grid for 12 months
    nav_table_data = []
    row = []
    for month_num in range(1, 13):
        m_name = MONTH_NAMES[month_num - 1]
        m_records = grouped_records.get(month_num, [])
        count = len(m_records)

        if count > 0:
            link_text = f'<a href="#Month_{m_name}" color="#2B6CB0"><u><b>{m_name}</b> ({count})</u></a>'
            cell_p = Paragraph(link_text, nav_link_active)
        else:
            cell_p = Paragraph(f"{m_name} (0)", nav_link_disabled)

        row.append(cell_p)
        if len(row) == 4:
            nav_table_data.append(row)
            row = []

    nav_table = Table(nav_table_data, colWidths=[1.85 * inch] * 4)
    nav_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F7FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elements.append(nav_table)
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E0'), spaceAfter=15))

    # --- MONTH BIRTHDAY SECTIONS ---
    has_entries = False
    for month_num in range(1, 13):
        month_name = MONTH_NAMES[month_num - 1]
        records = grouped_records.get(month_num, [])

        if not records:
            continue

        has_entries = True
        month_elements = []

        # Add destination anchor for internal PDF link
        anchor_p = Paragraph(f'<a name="Month_{month_name}"/>{month_name}', month_heading_style)
        month_elements.append(anchor_p)

        # Build table data
        table_data = [
            [
                Paragraph("<b>#</b>", table_header_style),
                Paragraph("<b>Name</b>", table_header_style),
                Paragraph("<b>Date of Birth</b>", table_header_style),
                Paragraph("<b>Day of Week</b>", table_header_style),
                Paragraph("<b>Source File</b>", table_header_style)
            ]
        ]

        for idx, rec in enumerate(records, 1):
            dob_dt = rec["dob_date"]
            formatted_dob = dob_dt.strftime("%d %b %Y")
            day_of_week = dob_dt.strftime("%A")

            table_data.append([
                Paragraph(str(idx), table_cell_style),
                Paragraph(rec["name"], table_cell_style),
                Paragraph(formatted_dob, table_cell_style),
                Paragraph(day_of_week, table_cell_style),
                Paragraph(rec["file"], table_cell_style)
            ])

        col_widths = [0.4 * inch, 2.5 * inch, 1.5 * inch, 1.3 * inch, 1.8 * inch]
        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2B6CB0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F7FAFC'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ]))

        month_elements.append(t)
        month_elements.append(Spacer(1, 15))

        elements.append(KeepTogether(month_elements))

    if not has_entries:
        elements.append(Paragraph("No valid DOB records found in the Kundalis folder.", subtitle_style))

    doc.build(elements)
    print(f"Successfully generated PDF: {output_pdf_path}")

def main():
    parser = argparse.ArgumentParser(description="Extract DOBs from XML Kundalis and generate birthday PDF.")
    parser.add_argument("--input-dir", default="Kundalis", help="Path to directory containing Kundali XML files.")
    parser.add_argument("--output-pdf", default="birthdays.pdf", help="Output PDF file path.")
    args = parser.parse_args()

    xml_files = find_xml_files(args.input_dir)
    print(f"Found {len(xml_files)} XML file(s) in '{args.input_dir}'.")

    records = []
    for xml_file in xml_files:
        rec = parse_xml_for_dob_and_name(xml_file)
        if rec:
            records.append(rec)

    print(f"Extracted {len(records)} valid DOB record(s).")
    grouped = group_and_sort_birthdays(records)
    create_pdf(grouped, args.output_pdf)

if __name__ == "__main__":
    main()
