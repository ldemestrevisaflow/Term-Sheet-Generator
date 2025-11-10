#!/usr/bin/env python3
"""
Term Sheet Document Generator
Converts questionnaire JSON to professional Word document with all placeholders properly replaced
"""

import json
import sys
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re

def number_to_words(n):
    """Convert number to words (e.g., 1 -> one, 20 -> twenty)"""
    ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 
             'sixteen', 'seventeen', 'eighteen', 'nineteen']
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    
    if n < 10:
        return ones[n]
    elif n < 20:
        return teens[n - 10]
    elif n < 100:
        return tens[n // 10] + (' ' + ones[n % 10] if n % 10 else '')
    elif n < 1000:
        return ones[n // 100] + ' hundred' + (' ' + number_to_words(n % 100) if n % 100 else '')
    else:
        return str(n)

def parse_date_to_words(date_str):
    """Convert date string (2025-12-20) to words (20 December 2025)"""
    if not date_str:
        return ""
    try:
        if 'T' in date_str:
            date_str = date_str.split('T')[0]
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        day = dt.day
        month = dt.strftime('%B')
        year = dt.year
        return f"{day} {month} {year}"
    except:
        return date_str

def set_cell_text(cell, text):
    """Set text in a table cell, replacing all paragraphs"""
    cell.text = text

def get_all_text(doc):
    """Get all text from document including tables"""
    all_text = []
    for para in doc.paragraphs:
        all_text.append(para.text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    all_text.append(para.text)
    return '\n'.join(all_text)

def replace_in_paragraph(para, old, new):
    """Replace text in a paragraph, handling text split across runs"""
    if old not in para.text:
        return False
    
    full_text = para.text
    if old in full_text:
        # Rebuild with replacement
        new_text = full_text.replace(old, new)
        # Clear runs
        for run in para.runs:
            run.text = ""
        # Add new text
        para.text = new_text
        return True
    return False

def replace_in_cell(cell, old, new):
    """Replace text in a table cell"""
    for para in cell.paragraphs:
        replace_in_paragraph(para, old, new)

def replace_in_document(doc, replacements):
    """Replace placeholders throughout entire document"""
    # Replace in paragraphs
    for para in doc.paragraphs:
        for old, new in replacements.items():
            replace_in_paragraph(para, old, new)
    
    # Replace in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for old, new in replacements.items():
                    replace_in_cell(cell, old, new)
    
    # Replace in headers and footers
    for section in doc.sections:
        for para in section.header.paragraphs:
            for old, new in replacements.items():
                replace_in_paragraph(para, old, new)
        for para in section.footer.paragraphs:
            for old, new in replacements.items():
                replace_in_paragraph(para, old, new)

def fix_first_page_parties(doc, seller, buyer, target):
    """Fix first page party placeholders - handles both names and numbers"""
    print("Fixing first page parties and removing numbers...")
    
    # Define all variations we might encounter
    replacements = {
        # Party 1 (Seller)
        '[Insert Party 1 Name]': seller.get('name', ''),
        '[Insert Party 1 Address]': seller.get('address', ''),
        'Party 1': f"Party {buyer.get('name', '')}",  # If labeled as Party 1
        '1.': '',  # Remove trailing numbers
        
        # Party 2 (Buyer)
        '[Insert Party 2 Name]': buyer.get('name', ''),
        '[Insert Party 2 Address]': buyer.get('address', ''),
        'Party 2': f"Party {seller.get('name', '')}",  # If labeled as Party 2
        '2.': '',  # Remove trailing numbers
        
        # Party 3 (Target)
        '[Insert Party 3 Name]': target.get('name', ''),
        '[Insert Party 3 Address]': target.get('address', ''),
        'Party 3': f"Party {target.get('name', '')}",
        '3.': '',  # Remove trailing numbers
    }
    
    # Apply to all paragraphs and table cells
    for para in doc.paragraphs:
        text = para.text
        
        # Remove trailing "1" or "2" after party names in contents/heading
        # e.g., "Seller 1" -> "Seller", "Buyer 2" -> "Buyer"
        if seller.get('name', '') in text and ' 1' in text:
            para.text = text.replace(f"{seller.get('name', '')} 1", seller.get('name', ''))
        if buyer.get('name', '') in text and ' 2' in text:
            para.text = text.replace(f"{buyer.get('name', '')} 2", buyer.get('name', ''))
        if target.get('name', '') in text and ' 3' in text:
            para.text = text.replace(f"{target.get('name', '')} 3", target.get('name', ''))
        
        # Do regular replacements
        for old, new in replacements.items():
            if old in para.text:
                para.text = para.text.replace(old, new)
    
    # Apply to table cells
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    text = para.text
                    
                    # Remove trailing numbers
                    if seller.get('name', '') in text and ' 1' in text:
                        para.text = text.replace(f"{seller.get('name', '')} 1", seller.get('name', ''))
                    if buyer.get('name', '') in text and ' 2' in text:
                        para.text = text.replace(f"{buyer.get('name', '')} 2", buyer.get('name', ''))
                    
                    # Do replacements
                    for old, new in replacements.items():
                        if old in para.text:
                            para.text = para.text.replace(old, new)

def fix_binding_text(doc, is_binding):
    """Fix the [non-]Binding text in table of contents and headers"""
    print(f"Fixing binding/non-binding text (is_binding={is_binding})...")
    
    # Replacement text
    binding_text = "Binding" if is_binding else "Non-Binding"
    
    for para in doc.paragraphs:
        # Handle various formats
        if '[non-]' in para.text:
            para.text = para.text.replace('[non-]', '' if is_binding else 'non-')
        if 'Non-]' in para.text:
            para.text = para.text.replace('Non-]', '' if is_binding else 'Non-')
        if '[non-]Binding' in para.text:
            para.text = para.text.replace('[non-]Binding', binding_text)
    
    # Handle in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if '[non-]' in para.text:
                        para.text = para.text.replace('[non-]', '' if is_binding else 'non-')
                    if 'Non-]' in para.text:
                        para.text = para.text.replace('Non-]', '' if is_binding else 'Non-')
                    if '[non-]Binding' in para.text:
                        para.text = para.text.replace('[non-]Binding', binding_text)

def fix_recital_a(doc, target):
    """Fix Recital A with target company name and ABN"""
    print("Fixing Recital A with target company name...")
    
    replacement = f"{target.get('name', '')} (ABN {target.get('abn', '')})"
    
    for para in doc.paragraphs:
        if '[insert name and ABN of company]' in para.text:
            para.text = para.text.replace('[insert name and ABN of company]', replacement)
        if 'insert name and ABN' in para.text:
            para.text = para.text.replace('insert name and ABN of company', replacement)
    
    # Handle in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if '[insert name and ABN of company]' in para.text:
                        para.text = para.text.replace('[insert name and ABN of company]', replacement)
                    if 'insert name and ABN' in para.text:
                        para.text = para.text.replace('insert name and ABN of company', replacement)

def fix_signature_blocks(doc, buyer, seller):
    """Fix signature blocks with buyer and seller names"""
    print("Fixing signature blocks...")
    
    buyer_name = buyer.get('name', '')
    seller_name = seller.get('name', '')
    
    for para in doc.paragraphs:
        if '[INSERT PARTY NAME]' in para.text:
            # Determine which one based on context
            if 'Buyer' in para.text or 'BUYER' in para.text:
                para.text = para.text.replace('[INSERT PARTY NAME]', buyer_name)
            elif 'Seller' in para.text or 'SELLER' in para.text:
                para.text = para.text.replace('[INSERT PARTY NAME]', seller_name)
    
    # Handle in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if '[INSERT PARTY NAME]' in para.text:
                        if 'Buyer' in para.text or 'BUYER' in para.text:
                            para.text = para.text.replace('[INSERT PARTY NAME]', buyer_name)
                        elif 'Seller' in para.text or 'SELLER' in para.text:
                            para.text = para.text.replace('[INSERT PARTY NAME]', seller_name)

def convert_dates_to_words(doc):
    """Convert all ISO dates to word format"""
    print("Converting dates to word format...")
    
    # Pattern to find dates like 2025-12-20
    date_pattern = r'\b(\d{4})-(\d{2})-(\d{2})\b'
    
    for para in doc.paragraphs:
        def replace_date(match):
            date_str = match.group(0)
            return parse_date_to_words(date_str)
        
        para.text = re.sub(date_pattern, replace_date, para.text)
    
    # Handle in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.text = re.sub(date_pattern, lambda m: parse_date_to_words(m.group(0)), para.text)

def generate_term_sheet(questionnaire_file, template_file, output_file):
    """Main function to generate term sheet"""
    
    print(f"Loading questionnaire from: {questionnaire_file}")
    with open(questionnaire_file, 'r') as f:
        data = json.load(f)
    
    print(f"Loading template from: {template_file}")
    doc = Document(template_file)
    
    # Extract data
    parties = data.get('parties', {})
    seller = parties.get('seller', {})
    buyer = parties.get('buyer', {})
    target = parties.get('targetCompany', {})
    
    deal = data.get('deal', {})
    legal = data.get('legal', {})
    
    is_binding = legal.get('termSheetType', 'binding') == 'binding'
    
    print("\n" + "=" * 80)
    print("TERM SHEET GENERATION PROCESS")
    print("=" * 80)
    
    # Build replacement dictionary
    replacements = {
        # Parties
        '[Seller Name]': seller.get('name', ''),
        '[Buyer Name]': buyer.get('name', ''),
        '[Target Company Name]': target.get('name', ''),
        '[Seller ABN]': seller.get('abn', ''),
        '[Buyer ABN]': buyer.get('abn', ''),
        '[Target ABN]': target.get('abn', ''),
        
        # Deal dates
        '[Completion Date]': parse_date_to_words(deal.get('completionDate', '')),
        '[Announcement Date]': parse_date_to_words(deal.get('announcementDate', '')),
        '[Execution Date]': parse_date_to_words(deal.get('executionDate', '')),
        
        # Prices and amounts
        '[Purchase Price]': f"${deal.get('purchasePrice', 0):,.0f}",
        '[Deposit Amount]': f"${deal.get('depositAmount', 0):,.0f}",
    }
    
    print("\n1️⃣  Applying general placeholder replacements...")
    replace_in_document(doc, replacements)
    
    print("2️⃣  Fixing first page parties and removing numbers...")
    fix_first_page_parties(doc, seller, buyer, target)
    
    print("3️⃣  Fixing binding/non-binding text...")
    fix_binding_text(doc, is_binding)
    
    print("4️⃣  Fixing Recital A...")
    fix_recital_a(doc, target)
    
    print("5️⃣  Converting dates to word format...")
    convert_dates_to_words(doc)
    
    print("6️⃣  Fixing signature blocks...")
    fix_signature_blocks(doc, buyer, seller)
    
    print(f"\nSaving document to: {output_file}")
    doc.save(output_file)
    
    print("\n" + "=" * 80)
    print("✅ TERM SHEET GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"Output: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python3 generate_term_sheet_CLEAN.py <questionnaire.json> <template.docx> <output.docx>")
        sys.exit(1)
    
    questionnaire_file = sys.argv[1]
    template_file = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        generate_term_sheet(questionnaire_file, template_file, output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
