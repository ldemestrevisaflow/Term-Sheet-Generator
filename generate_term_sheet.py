#!/usr/bin/env python3
"""
Generate Term Sheet DOCX by filling in the master template with JSON questionnaire data
Usage: python generate_term_sheet.py <path_to_json_file>
"""

import json
import sys
import os
import glob
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.oxml import OxmlElement

def find_template():
    """Find the master Term Sheet template file"""
    import glob
    
    # Search for any DOCX file with "Term Sheet" in the name
    print("Searching for Term Sheet template...")
    
    # Try exact names first
    possible_names = [
        'Term Sheet - Share Sale - Binding_option1(ID 2740).docx',
        'Term Sheet - Share Sale - Binding_option[ID 2740].docx',
        'Term Sheet - Share Sale - Binding.docx',
        'Term_Sheet_Master.docx',
        'templates/Term Sheet - Share Sale - Binding_option1(ID 2740).docx',
    ]
    
    for template_name in possible_names:
        if os.path.exists(template_name):
            print(f"✓ Found template: {template_name}")
            return template_name
    
    # Fallback: search for any docx file with "Term Sheet" in name
    print("Exact match not found, searching for any 'Term Sheet' docx files...")
    for pattern in ['*Term Sheet*.docx', 'templates/*Term Sheet*.docx']:
        matches = glob.glob(pattern)
        if matches:
            template_file = matches[0]
            print(f"✓ Found template via glob: {template_file}")
            return template_file
    
    # List all files for debugging
    print("\n⚠️  Template not found! Available DOCX files:")
    for docx_file in glob.glob('**/*.docx', recursive=True):
        print(f"  - {docx_file}")
    
    raise FileNotFoundError(
        "Master Term Sheet template not found. "
        "Expected to find a file with 'Term Sheet' in the name ending in .docx"
    )

def replace_text_in_paragraph(paragraph, key, value):
    """Replace placeholder text in a paragraph"""
    if key in paragraph.text:
        # Clear the paragraph
        for run in paragraph.runs:
            run.text = run.text.replace(key, str(value))
        return True
    return False

def replace_text_in_table(table, replacements):
    """Replace placeholder text in table cells"""
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for key, value in replacements.items():
                    replace_text_in_paragraph(paragraph, key, str(value))

def replace_text_in_document(doc, replacements):
    """Replace all placeholder text in document with values from replacements dict"""
    
    # Replace in paragraphs
    for paragraph in doc.paragraphs:
        for key, value in replacements.items():
            if key in paragraph.text:
                # For each run in the paragraph, replace the text
                for run in paragraph.runs:
                    if key in run.text:
                        run.text = run.text.replace(key, str(value))
    
    # Replace in tables
    for table in doc.tables:
        replace_text_in_table(table, replacements)
    
    # Replace in headers/footers
    for section in doc.sections:
        # Header
        for paragraph in section.header.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    for run in paragraph.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, str(value))
        
        # Footer
        for paragraph in section.footer.paragraphs:
            for key, value in replacements.items():
                if key in paragraph.text:
                    for run in paragraph.runs:
                        if key in run.text:
                            run.text = run.text.replace(key, str(value))

def format_currency(value):
    """Format value as Australian currency"""
    try:
        if value:
            num = float(value)
            return f"A${num:,.2f}"
    except (ValueError, TypeError):
        pass
    return "—"

def format_date(value):
    """Format date value"""
    if value:
        return str(value)
    return "—"

def generate_term_sheet(json_file):
    """Generate a Term Sheet DOCX by filling the master template with JSON data"""
    
    print(f"Loading JSON from: {json_file}")
    
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Find and load template
    template_file = find_template()
    print(f"Loading template: {template_file}")
    doc = Document(template_file)
    
    # Prepare replacements dictionary
    # These are placeholder tags that should exist in the template
    replacements = {
        # Parties
        '[SELLER_NAME]': data.get('seller', {}).get('name', ''),
        '[SELLER_ABN]': data.get('seller', {}).get('abn', ''),
        '[BUYER_NAME]': data.get('buyer', {}).get('name', ''),
        '[BUYER_ABN]': data.get('buyer', {}).get('abn', ''),
        '[TARGET_COMPANY]': data.get('targetCompany', {}).get('name', ''),
        '[TARGET_ABN]': data.get('targetCompany', {}).get('abn', ''),
        '[TARGET_ACN]': data.get('targetCompany', {}).get('acn', ''),
        
        # Transaction Details
        '[PURCHASE_PRICE]': format_currency(data.get('transaction', {}).get('purchasePrice')),
        '[DEPOSIT_AMOUNT]': format_currency(data.get('transaction', {}).get('depositAmount')),
        '[BASE_NET_ASSETS]': format_currency(data.get('transaction', {}).get('baseNetAssets')),
        
        # Key Dates
        '[TERM_SHEET_DATE]': format_date(data.get('dates', {}).get('termSheetDate')),
        '[DUE_DILIGENCE_DATE]': format_date(data.get('dates', {}).get('dueDiligenceDate')),
        '[LONG_FORM_DATE]': format_date(data.get('dates', {}).get('longFormDate')),
        '[CONDITION_SATISFACTION_DATE]': format_date(data.get('dates', {}).get('conditionSatisfactionDate')),
        '[COMPLETION_DATE]': format_date(data.get('dates', {}).get('completionDate')),
        
        # Conditions Precedent
        '[DUE_DILIGENCE_TYPE]': data.get('conditions', {}).get('dueDiligenceType', 'Unstructured'),
        '[INFO_REQUEST_DAYS]': str(data.get('conditions', {}).get('infoRequestDays', 10)),
        '[ACCESS_PERIOD_DAYS]': str(data.get('conditions', {}).get('accessPeriodDays', 30)),
        '[ADDITIONAL_CONDITIONS]': data.get('conditions', {}).get('additionalConditions', ''),
        
        # Warranties
        '[WARRANTY_STRUCTURE]': data.get('warranties', {}).get('structure', 'Joint & Several'),
        '[TAX_INDEMNITY]': 'Included' if data.get('warranties', {}).get('taxIndemnity') else 'Not Included',
        '[WARRANTY_LIMITATIONS]': data.get('warranties', {}).get('limitations', ''),
        
        # Commercial Terms
        '[NON_COMPETE_PERIOD]': str(data.get('commercial', {}).get('nonCompetePeriod', 3)),
        '[NON_SOLICITATION_PERIOD]': str(data.get('commercial', {}).get('nonSolicitationPeriod', 12)),
        '[EXCLUSIVITY_REQUIRED]': 'Yes' if data.get('commercial', {}).get('exclusivityRequired') == 'yes' else 'No',
        '[EXCLUSIVITY_END_DATE]': format_date(data.get('commercial', {}).get('exclusivityEndDate')),
        '[LIQUIDATED_DAMAGES]': format_currency(data.get('commercial', {}).get('liquidatedDamages')),
        
        # Management
        '[DIRECTORS_RESIGN]': data.get('management', {}).get('directorsResign', ''),
        '[DIRECTORS_NEW_AGREEMENTS]': data.get('management', {}).get('directorsNewAgreements', ''),
        '[RETENTION_PERSONNEL]': data.get('management', {}).get('retentionPersonnel', ''),
        
        # Legal & Jurisdiction
        '[JURISDICTION]': data.get('legal', {}).get('jurisdiction', 'New South Wales'),
        '[JURISDICTION_TYPE]': 'Exclusive' if data.get('legal', {}).get('jurisdictionType') == 'exclusive' else 'Non-Exclusive',
        '[TERM_SHEET_TYPE]': 'Binding' if data.get('legal', {}).get('termSheetType') == 'binding' else 'Non-Binding',
        '[GOVERNING_LAW]': data.get('legal', {}).get('governingLaw', 'New South Wales'),
        '[BUYER_SIGNATORIES]': data.get('legal', {}).get('buyerSignatories', ''),
        '[SELLER_SIGNATORIES]': data.get('legal', {}).get('sellerSignatories', ''),
        '[KEY_SUPPLIERS]': data.get('legal', {}).get('suppliersSchedule', ''),
        '[KEY_CUSTOMERS]': data.get('legal', {}).get('customersSchedule', ''),
    }
    
    print("Replacing placeholders in document...")
    replace_text_in_document(doc, replacements)
    
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
