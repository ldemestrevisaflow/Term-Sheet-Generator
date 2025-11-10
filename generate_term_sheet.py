#!/usr/bin/env python3
"""
Generate Term Sheet DOCX by filling in the master PwC template with JSON questionnaire data.
Handles split runs properly across all document elements.

Usage: python generate_term_sheet.py <path_to_json_file>
"""

import json
import sys
import os
import glob
import re
from datetime import datetime
from docx import Document
from docx.oxml import OxmlElement

def find_template():
    """Find the master Term Sheet template file"""
    print("Searching for Term Sheet template...")
    
    possible_names = [
        'Term Sheet - Share Sale - Binding_option1(ID 2740).docx',
        'Term Sheet - Share Sale - Binding_option[ID 2740].docx',
        'Term Sheet - Share Sale - Binding.docx',
    ]
    
    for template_name in possible_names:
        if os.path.exists(template_name):
            print(f"✓ Found template: {template_name}")
            return template_name
    
    for pattern in ['*Term Sheet*.docx', 'templates/*Term Sheet*.docx']:
        matches = glob.glob(pattern)
        if matches:
            print(f"✓ Found template via glob: {matches[0]}")
            return matches[0]
    
    raise FileNotFoundError("Term Sheet template not found")

def replace_text_in_paragraph(paragraph, replacements):
    """Replace all occurrences of placeholders in a paragraph, handling multi-run text"""
    
    if not paragraph.runs:
        return
    
    # Build full text from all runs
    full_text = ''.join([run.text for run in paragraph.runs])
    
    # Check if any replacement needed
    if not any(key in full_text for key in replacements.keys()):
        return
    
    # Do replacements
    for key, value in replacements.items():
        full_text = full_text.replace(key, str(value))
    
    # Clear all runs
    for run in list(paragraph.runs):
        r = run._element
        r.getparent().remove(r)
    
    # Add new run with replaced text
    if paragraph.runs:
        paragraph.runs[0].text = full_text
    else:
        paragraph.add_run(full_text)

def replace_in_all_document_text(doc, replacements):
    """Replace text everywhere in the document - paragraphs, tables, headers/footers"""
    
    print("Replacing all placeholders throughout document...")
    
    # Replace in all paragraphs
    for para in doc.paragraphs:
        replace_text_in_paragraph(para, replacements)
    
    # Replace in all table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    replace_text_in_paragraph(para, replacements)
    
    # Replace in headers/footers
    for section in doc.sections:
        for para in section.header.paragraphs:
            replace_text_in_paragraph(para, replacements)
        for para in section.footer.paragraphs:
            replace_text_in_paragraph(para, replacements)

def format_date_word(date_str):
    """Convert date from YYYY-MM-DD to 'DD Month YYYY' format"""
    if not date_str or date_str.strip() == '':
        return ''
    
    try:
        # Parse the date
        if 'T' in date_str:
            date_obj = datetime.fromisoformat(date_str.split('T')[0])
        else:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Format as "20 December 2025"
        formatted = date_obj.strftime('%d %B %Y')
        # Remove leading zero from day
        if formatted[0] == '0':
            formatted = formatted[1:]
        return formatted
    except Exception as e:
        print(f"Warning: Could not format date '{date_str}': {e}")
        return date_str

def format_currency(value):
    """Format value as Australian currency"""
    try:
        if value:
            num = float(value)
            return f"A${num:,.2f}"
    except (ValueError, TypeError):
        pass
    return ""

def generate_term_sheet(json_file):
    """Generate a Term Sheet DOCX by filling the master template with JSON data"""
    
    print(f"\nLoading JSON from: {json_file}")
    
    # Read JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Find and load template
    template_file = find_template()
    print(f"Loading template: {template_file}")
    doc = Document(template_file)
    
    # Extract data
    seller = data.get('seller', {})
    buyer = data.get('buyer', {})
    target = data.get('targetCompany', {})
    transaction = data.get('transaction', {})
    dates = data.get('dates', {})
    conditions = data.get('conditions', {})
    legal = data.get('legal', {})
    management = data.get('management', {})
    commercial = data.get('commercial', {})
    
    # Determine binding status
    is_binding = legal.get('termSheetType', 'binding') == 'binding'
    binding_text = '' if is_binding else 'non-'
    
    # Create all replacements
    replacements = {
        # Party details (first page, tables, signature blocks)
        '[Insert Party 1 Name]': seller.get('name', ''),
        '[Insert ABN of Party 1]': seller.get('abn', ''),
        '[Insert Party 2 Name]': buyer.get('name', ''),
        '[Insert ABN of Party 2]': buyer.get('abn', ''),
        '[Insert Party 3 Name]': target.get('name', ''),
        '[Insert ABN of Party 3]': target.get('abn', ''),
        '[insert Party  Name]': target.get('name', ''),  # Generic placeholder
        '[insert ABN]': target.get('abn', ''),  # Generic placeholder
        '[INSERT PARTY NAME]': buyer.get('name', ''),  # Signature block - buyer
        
        # Binding/Non-binding
        '[non-]': binding_text,
        'Non-]': 'Non-' if not is_binding else '',
        
        # Target company (Recital A)
        '[insert name and ABN of company]': f"{target.get('name', '')} (ABN {target.get('abn', '')})",
        
        # Dates - all formatted as words
        '[Insert Date]': format_date_word(dates.get('termSheetDate', '')),
        '[insert date]': format_date_word(dates.get('completionDate', '')),
        
        # Amounts
        '[Insert Amount]': format_currency(transaction.get('purchasePrice')),
        '[insert amount]': format_currency(transaction.get('depositAmount')),
        
        # Conditions
        '[insert number]': str(conditions.get('infoRequestDays', '10')),
        '[30]': str(conditions.get('accessPeriodDays', '30')),
        
        # Commercial terms
        '[three]': str(commercial.get('nonCompetePeriod', '3')),
        '[12]': str(commercial.get('nonSolicitationPeriod', '12')),
        '[six months]': '6 months',
        '[five]': '5',
        
        # Management
        '[insert relevant name]': management.get('directorsResign', ''),
        
        # Legal
        '[New South Wales]': legal.get('jurisdiction', 'New South Wales'),
        
        # Schedules
        '[Insert list of Suppliers]': legal.get('suppliersSchedule', ''),
        '[Insert list of Customers]': legal.get('customersSchedule', ''),
        
        # Generic details
        '[insert details]': '',
        '[insert details of representations]': '',
        '[insert Party 1 Address]': seller.get('name', ''),
        '[insert Party 2 Address]': buyer.get('name', ''),
        '[insert Party 3 Address]': target.get('name', ''),
        '[insert address]': target.get('name', ''),
    }
    
    print("Replacing placeholders...")
    replace_in_all_document_text(doc, replacements)
    
    # Save document
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'generated_TermSheet.docx')
    
    print(f"Saving to: {output_file}")
    doc.save(output_file)
    
    print(f"✅ Term Sheet generated successfully!")
    print(f"   File: {output_file}")
    print(f"   Size: {os.path.getsize(output_file)} bytes\n")
    
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
