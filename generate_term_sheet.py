#!/usr/bin/env python3
"""
Generate Term Sheet DOCX from JSON questionnaire data
Usage: python generate_term_sheet.py <path_to_json_file>
"""

import json
import sys
import os
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_heading(doc, text, level=1):
    """Add a heading to the document"""
    heading = doc.add_heading(text, level=level)
    heading.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return heading

def add_paragraph_with_bold(doc, text, bold_parts=None):
    """Add paragraph with optional bold parts"""
    p = doc.add_paragraph()
    if bold_parts:
        for part in bold_parts:
            if part['bold']:
                run = p.add_run(part['text'])
                run.bold = True
            else:
                p.add_run(part['text'])
    else:
        p.add_run(text)
    return p

def format_currency(value):
    """Format value as Australian currency"""
    try:
        if value:
            num = float(value)
            return f"A${num:,.2f}"
    except (ValueError, TypeError):
        pass
    return "—"

def add_table(doc, data_dict, headers=['Field', 'Value']):
    """Add a formatted table to document"""
    if not data_dict:
        return None
    
    table = doc.add_table(rows=1, cols=2)
    table.style = 'Light Grid Accent 1'
    
    # Header row
    header_cells = table.rows[0].cells
    header_cells[0].text = headers[0]
    header_cells[1].text = headers[1]
    for cell in header_cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(11)
    
    # Data rows
    for key, value in data_dict.items():
        row_cells = table.add_row().cells
        row_cells[0].text = str(key) if key else ''
        row_cells[1].text = str(value) if value else '—'
    
    return table

def generate_term_sheet(json_file):
    """Generate a Term Sheet DOCX document from JSON data"""
    
    print(f"Loading JSON from: {json_file}")
    
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print("Creating DOCX document...")
    
    # Create document
    doc = Document()
    
    # Set default font
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    
    # ========== TITLE PAGE ==========
    title = doc.add_paragraph()
    title_run = title.add_run('TERM SHEET')
    title_run.font.size = Pt(28)
    title_run.bold = True
    title_run.font.color.rgb = RGBColor(45, 45, 45)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    subtitle = doc.add_paragraph()
    subtitle_run = subtitle.add_run('SHARE SALE AND PURCHASE AGREEMENT')
    subtitle_run.font.size = Pt(14)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph()  # Spacing
    
    # ========== 1. PARTIES ==========
    add_heading(doc, '1. PARTIES', level=1)
    parties_table = add_table(doc, {
        'Seller': data.get('seller', {}).get('name', ''),
        'Seller ABN': data.get('seller', {}).get('abn', ''),
        'Buyer': data.get('buyer', {}).get('name', ''),
        'Buyer ABN': data.get('buyer', {}).get('abn', ''),
        'Target Company': data.get('targetCompany', {}).get('name', ''),
        'Target ABN': data.get('targetCompany', {}).get('abn', '')
    })
    doc.add_paragraph()
    
    # ========== 2. TRANSACTION DETAILS ==========
    add_heading(doc, '2. TRANSACTION DETAILS', level=1)
    transaction = data.get('transaction', {})
    transaction_table = add_table(doc, {
        'Total Purchase Price': format_currency(transaction.get('purchasePrice')),
        'Deposit Amount': format_currency(transaction.get('depositAmount')),
        'Base Net Assets': format_currency(transaction.get('baseNetAssets'))
    })
    doc.add_paragraph()
    
    # ========== 3. KEY DATES ==========
    add_heading(doc, '3. KEY DATES', level=1)
    dates = data.get('dates', {})
    dates_table = add_table(doc, {
        'Term Sheet Date': dates.get('termSheetDate', ''),
        'Due Diligence Completion Date': dates.get('dueDiligenceDate', ''),
        'Long Form Agreement Date': dates.get('longFormDate', ''),
        'Condition Satisfaction Date': dates.get('conditionSatisfactionDate', ''),
        'Completion Date': dates.get('completionDate', '')
    })
    doc.add_paragraph()
    
    # ========== 4. CONDITIONS PRECEDENT ==========
    add_heading(doc, '4. CONDITIONS PRECEDENT', level=1)
    conditions = data.get('conditions', {})
    conditions_table = add_table(doc, {
        'Due Diligence Type': conditions.get('dueDiligenceType', 'Unstructured'),
        'Information Request Timeline': f"{conditions.get('infoRequestDays', 10)} days",
        'Access Period': f"{conditions.get('accessPeriodDays', 30)} days"
    })
    
    if conditions.get('additionalConditions'):
        doc.add_paragraph()
        add_heading(doc, 'Additional Conditions', level=2)
        doc.add_paragraph(conditions['additionalConditions'])
    
    doc.add_paragraph()
    
    # ========== 5. WARRANTIES & INDEMNITIES ==========
    add_heading(doc, '5. WARRANTIES & INDEMNITIES', level=1)
    warranties = data.get('warranties', {})
    warranties_table = add_table(doc, {
        'Warranty Structure': warranties.get('structure', 'Joint & Several'),
        'Tax Indemnity': 'Included' if warranties.get('taxIndemnity') else 'Not Included'
    })
    
    if warranties.get('limitations'):
        doc.add_paragraph()
        add_heading(doc, 'Warranty Limitations', level=2)
        doc.add_paragraph(warranties['limitations'])
    
    doc.add_paragraph()
    
    # ========== 6. COMMERCIAL TERMS ==========
    add_heading(doc, '6. COMMERCIAL TERMS', level=1)
    commercial = data.get('commercial', {})
    commercial_table = add_table(doc, {
        'Non-Compete Period': f"{commercial.get('nonCompetePeriod', 3)} years",
        'Non-Solicitation Period': f"{commercial.get('nonSolicitationPeriod', 12)} months",
        'Exclusivity Required': 'Yes' if commercial.get('exclusivityRequired') == 'yes' else 'No'
    })
    doc.add_paragraph()
    
    # ========== 7. MANAGEMENT & KEY PERSONNEL ==========
    add_heading(doc, '7. MANAGEMENT & KEY PERSONNEL', level=1)
    management = data.get('management', {})
    
    if management.get('directorsResign'):
        add_heading(doc, 'Directors to Resign', level=2)
        doc.add_paragraph(management['directorsResign'])
    
    if management.get('directorsNewAgreements'):
        add_heading(doc, 'Directors Entering New Agreements', level=2)
        doc.add_paragraph(management['directorsNewAgreements'])
    
    if management.get('retentionPersonnel'):
        add_heading(doc, 'Key Personnel Arrangements', level=2)
        doc.add_paragraph(management['retentionPersonnel'])
    
    doc.add_paragraph()
    
    # ========== 8. LEGAL & JURISDICTION ==========
    add_heading(doc, '8. LEGAL & JURISDICTION', level=1)
    legal = data.get('legal', {})
    legal_table = add_table(doc, {
        'Jurisdiction': legal.get('jurisdiction', 'New South Wales'),
        'Jurisdiction Type': 'Exclusive' if legal.get('jurisdictionType') == 'exclusive' else 'Non-Exclusive',
        'Term Sheet Type': 'Binding' if legal.get('termSheetType') == 'binding' else 'Non-Binding'
    })
    
    if legal.get('suppliersSchedule'):
        doc.add_paragraph()
        add_heading(doc, 'Key Suppliers (Schedule 1)', level=2)
        doc.add_paragraph(legal['suppliersSchedule'])
    
    if legal.get('customersSchedule'):
        doc.add_paragraph()
        add_heading(doc, 'Key Customers (Schedule 2)', level=2)
        doc.add_paragraph(legal['customersSchedule'])
    
    # ========== SIGNATURE PAGE ==========
    doc.add_page_break()
    add_heading(doc, 'SIGNATURE PAGE', level=1)
    
    doc.add_paragraph('This Term Sheet is executed as of the date first written above.')
    doc.add_paragraph()
    
    doc.add_paragraph('FOR AND ON BEHALF OF THE BUYER:', style='Heading 2')
    doc.add_paragraph()
    doc.add_paragraph('_____________________________')
    doc.add_paragraph('Signature')
    doc.add_paragraph()
    doc.add_paragraph('_____________________________')
    doc.add_paragraph('Name and Title')
    doc.add_paragraph()
    doc.add_paragraph('_____________________________')
    doc.add_paragraph('Date')
    doc.add_paragraph()
    doc.add_paragraph()
    
    doc.add_paragraph('FOR AND ON BEHALF OF THE SELLER:', style='Heading 2')
    doc.add_paragraph()
    doc.add_paragraph('_____________________________')
    doc.add_paragraph('Signature')
    doc.add_paragraph()
    doc.add_paragraph('_____________________________')
    doc.add_paragraph('Name and Title')
    doc.add_paragraph()
    doc.add_paragraph('_____________________________')
    doc.add_paragraph('Date')
    
    # Save document
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'generated_TermSheet.docx')
    
    print(f"Saving to: {output_file}")
    doc.save(output_file)
    
    print(f"✅ Term Sheet generated successfully!")
    print(f"   File: {output_file}")
    print(f"   Size: {os.path.getsize(output_file)} bytes")
    
    return output_file

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_term_sheet.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    if not os.path.exists(json_file):
        print(f"Error: File not found: {json_file}")
        sys.exit(1)
    
    try:
        generate_term_sheet(json_file)
        print("Success!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
