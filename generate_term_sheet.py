#!/usr/bin/env python3
"""
Generate Term Sheet DOCX by filling in the master PwC template with JSON questionnaire data.
Uses the actual placeholder names from the template.

Usage: python generate_term_sheet.py <path_to_json_file>
"""

import json
import sys
import os
import glob
from datetime import datetime
from docx import Document

def find_template():
    """Find the master Term Sheet template file"""
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
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for key, value in replacements.items():
                        if key in paragraph.text:
                            for run in paragraph.runs:
                                if key in run.text:
                                    run.text = run.text.replace(key, str(value))
    
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
    return ""

def format_date(value):
    """Format date value"""
    if value:
        return str(value)
    return ""

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
    # Using the ACTUAL placeholders from the PwC template
    seller = data.get('seller', {})
    buyer = data.get('buyer', {})
    target = data.get('targetCompany', {})
    transaction = data.get('transaction', {})
    dates = data.get('dates', {})
    conditions = data.get('conditions', {})
    warranties = data.get('warranties', {})
    commercial = data.get('commercial', {})
    management = data.get('management', {})
    legal = data.get('legal', {})
    
    replacements = {
        # Party Details (Signature Pages)
        '[Insert Party 1 Name]': seller.get('name', ''),
        '[Insert ABN of Party 1]': seller.get('abn', ''),
        '[Insert Party 2 Name]': buyer.get('name', ''),
        '[Insert ABN of Party 2]': buyer.get('abn', ''),
        '[Insert Party 3 Name]': target.get('name', ''),
        '[Insert ABN of Party 3]': target.get('abn', ''),
        
        # Case-sensitive versions
        '[insert Party 1 Address]': seller.get('name', ''),
        '[insert Party 2 Address]': buyer.get('name', ''),
        '[insert Party 3 Address]': target.get('name', ''),
        '[insert Party  Name]': target.get('name', ''),
        '[insert ABN]': target.get('abn', ''),
        '[INSERT PARTY NAME]': buyer.get('name', ''),
        
        # Key Information - Company Details
        '[insert name and ABN of company]': f"{target.get('name', '')} (ABN {target.get('abn', '')})",
        
        # Dates
        '[Insert Date]': format_date(dates.get('termSheetDate', '')),
        '[insert date]': format_date(dates.get('completionDate', '')),
        
        # Transaction Amounts
        '[Insert Amount]': format_currency(transaction.get('purchasePrice')),
        '[insert amount]': format_currency(transaction.get('depositAmount')),
        
        # Conditions Precedent
        '[insert number]': str(conditions.get('infoRequestDays', '10')),
        '[30]': str(conditions.get('accessPeriodDays', '30')),
        '[insert address]': target.get('name', ''),
        
        # Commercial Terms - Non-Compete
        '[three]': str(commercial.get('nonCompetePeriod', '3')),
        '[12]': str(commercial.get('nonSolicitationPeriod', '12')),
        '[six months]': '6 months',
        '[five]': '5',
        
        # Management/Directors
        '[insert relevant name]': management.get('directorsResign', ''),
        
        # Legal/Jurisdiction
        '[New South Wales]': legal.get('jurisdiction', 'New South Wales'),
        
        # Schedules
        '[Insert list of Suppliers]': legal.get('suppliersSchedule', ''),
        '[Insert list of Customers]': legal.get('customersSchedule', ''),
        
        # Contact Details placeholders
        '[insert details]': '',
        '[insert details of representations]': '',
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
