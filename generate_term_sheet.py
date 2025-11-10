#!/usr/bin/env python3
"""
Term Sheet Document Generator - FIXED PARTY MAPPING
Converts questionnaire JSON to professional Word document with all placeholders properly replaced
"""

import json
import sys
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import re

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
    """Set text in a table cell"""
    cell.text = text

def replace_in_paragraph(para, old, new):
    """Replace text in a paragraph"""
    if old not in para.text:
        return False
    
    if old in para.text:
        para.text = para.text.replace(old, new)
        return True
    return False

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

def replace_in_cell(cell, old, new):
    """Replace text in a table cell"""
    for para in cell.paragraphs:
        replace_in_paragraph(para, old, new)

def fix_table_of_contents(doc, is_binding):
    """Fix [non-] in table of contents to Binding or Non-Binding"""
    print("Fixing Table of Contents binding/non-binding text...")
    
    for para_idx, para in enumerate(doc.paragraphs[:50]):  # Check first 50 paras for TOC
        text = para.text
        
        # Fix [non-]Binding variations
        if '[non-]' in text:
            if is_binding:
                para.text = text.replace('[non-]Binding', 'Binding')
                para.text = para.text.replace('[non-]', '')
            else:
                para.text = text.replace('[non-]Binding', 'Non-Binding')
                para.text = para.text.replace('[non-]', 'non-')
        
        if 'Non-]' in text:
            if is_binding:
                para.text = text.replace('Non-]Binding', 'Binding')
            else:
                para.text = text.replace('Non-]Binding', 'Non-Binding')
        
        if para.text != text:
            print(f"  ✓ Fixed: {para.text[:80]}")

def fix_parties_table(doc, seller, buyer):
    """Fix the parties table (Table 1) with correct Seller/Buyer mapping"""
    print("Fixing parties table with correct Seller/Buyer data...")
    
    if len(doc.tables) < 2:
        print("  ⚠️  Document doesn't have a parties table")
        return
    
    table = doc.tables[1]
    
    # Party 1: Seller (rows 3-8)
    print(f"\n  Party 1 - SELLER:")
    set_cell_text(table.rows[3].cells[1], seller.get('name', ''))
    print(f"    Name: {seller.get('name', '')}")
    
    set_cell_text(table.rows[4].cells[1], seller.get('abn', ''))
    print(f"    ABN: {seller.get('abn', '')}")
    
    set_cell_text(table.rows[5].cells[1], 'Seller')
    
    # Notice details for Seller
    seller_notice = seller.get('address', '')
    if seller.get('attention'):
        seller_notice += f"\nAttention: {seller.get('attention')}"
    set_cell_text(table.rows[6].cells[1], seller_notice)
    
    if seller.get('facsimile'):
        set_cell_text(table.rows[7].cells[1], f"Facsimile: {seller.get('facsimile')}")
    if seller.get('email'):
        set_cell_text(table.rows[8].cells[1], f"Email: {seller.get('email')}")
    
    # Party 2: Buyer (rows 10-15)
    print(f"\n  Party 2 - BUYER:")
    set_cell_text(table.rows[10].cells[1], buyer.get('name', ''))
    print(f"    Name: {buyer.get('name', '')}")
    
    set_cell_text(table.rows[11].cells[1], buyer.get('abn', ''))
    print(f"    ABN: {buyer.get('abn', '')}")
    
    set_cell_text(table.rows[12].cells[1], 'Buyer')
    
    # Notice details for Buyer
    buyer_notice = buyer.get('address', '')
    if buyer.get('attention'):
        buyer_notice += f"\nAttention: {buyer.get('attention')}"
    set_cell_text(table.rows[13].cells[1], buyer_notice)
    
    if buyer.get('facsimile'):
        set_cell_text(table.rows[14].cells[1], f"Facsimile: {buyer.get('facsimile')}")
    if buyer.get('email'):
        set_cell_text(table.rows[15].cells[1], f"Email: {buyer.get('email')}")
    
    # Party 3: Escrow Agent (rows 17-22) - LEAVE FOR NOW
    print(f"\n  Party 3 - ESCROW AGENT (left as is for now)")

def fix_recital_a(doc, target):
    """Fix Recital A with target company name and ABN"""
    print("\nFixing Recital A with target company name...")
    
    target_text = f"{target.get('name', '')} (ABN {target.get('abn', '')})"
    
    # Find Recital A in paragraphs
    for para_idx, para in enumerate(doc.paragraphs):
        if 'Recital A' in para.text or 'RECITAL A' in para.text:
            # Next few paragraphs should contain the company reference
            for offset in range(1, 5):
                if para_idx + offset < len(doc.paragraphs):
                    next_para = doc.paragraphs[para_idx + offset]
                    
                    # Replace placeholder variations
                    if '[insert name and ABN of company]' in next_para.text:
                        next_para.text = next_para.text.replace('[insert name and ABN of company]', target_text)
                        print(f"  ✓ Updated Recital A: {target_text}")
                        return
                    elif 'insert name and ABN' in next_para.text:
                        next_para.text = next_para.text.replace('insert name and ABN of company', target_text)
                        print(f"  ✓ Updated Recital A: {target_text}")
                        return

def fix_signature_blocks(doc, buyer, seller):
    """Fix signature blocks with buyer and seller names"""
    print("\nFixing signature blocks...")
    
    buyer_name = buyer.get('name', '')
    seller_name = seller.get('name', '')
    
    for table_idx, table in enumerate(doc.tables):
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    if '[INSERT PARTY NAME]' in para.text:
                        # Context-based replacement
                        if 'Buyer' in para.text or 'BUYER' in para.text:
                            para.text = para.text.replace('[INSERT PARTY NAME]', buyer_name)
                            print(f"  ✓ Buyer signature block: {buyer_name}")
                        elif 'Seller' in para.text or 'SELLER' in para.text:
                            para.text = para.text.replace('[INSERT PARTY NAME]', seller_name)
                            print(f"  ✓ Seller signature block: {seller_name}")

def convert_dates_to_words(doc):
    """Convert all ISO dates to word format"""
    print("\nConverting dates to word format...")
    
    date_pattern = r'\b(\d{4})-(\d{2})-(\d{2})\b'
    
    for para in doc.paragraphs:
        if date_pattern in para.text or any(c in para.text for c in ['2024', '2025', '2026']):
            def replace_date(match):
                return parse_date_to_words(match.group(0))
            para.text = re.sub(date_pattern, replace_date, para.text)
    
    # Handle in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.text = re.sub(date_pattern, lambda m: parse_date_to_words(m.group(0)), para.text)

def remove_conditional_placeholders(doc):
    """Remove remaining conditional placeholders like [Balance of], [Consider...], etc."""
    print("\nRemoving conditional placeholders...")
    
    conditional_placeholders = [
        '[Balance of]',
        '[Use the following for a binding term sheet]',
        '[Consider whether security/parent guarantee is required to be given by the Buyer]',
        '[and accounting]',
        '[insert Party 3 Name]',
    ]
    
    for para in doc.paragraphs:
        for placeholder in conditional_placeholders:
            if placeholder in para.text:
                para.text = para.text.replace(placeholder, '')
    
    # Handle in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for placeholder in conditional_placeholders:
                        if placeholder in para.text:
                            para.text = para.text.replace(placeholder, '')

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
    print("TERM SHEET GENERATION - FIXED PARTY MAPPING")
    print("=" * 80)
    
    # Build replacement dictionary for general placeholders
    replacements = {
        # Dates
        '[Completion Date]': parse_date_to_words(deal.get('completionDate', '')),
        '[Announcement Date]': parse_date_to_words(deal.get('announcementDate', '')),
        '[Execution Date]': parse_date_to_words(deal.get('executionDate', '')),
        
        # Prices and amounts
        '[Purchase Price]': f"${deal.get('purchasePrice', 0):,.0f}",
        '[Deposit Amount]': f"${deal.get('depositAmount', 0):,.0f}",
    }
    
    print("\n1️⃣  Fixing Table of Contents...")
    fix_table_of_contents(doc, is_binding)
    
    print("\n2️⃣  Fixing Parties Table (Seller/Buyer/Escrow Agent)...")
    fix_parties_table(doc, seller, buyer)
    
    print("\n3️⃣  Fixing Recital A with target company...")
    fix_recital_a(doc, target)
    
    print("\n4️⃣  Applying general placeholder replacements...")
    replace_in_document(doc, replacements)
    
    print("\n5️⃣  Converting dates to word format...")
    convert_dates_to_words(doc)
    
    print("\n6️⃣  Fixing signature blocks...")
    fix_signature_blocks(doc, buyer, seller)
    
    print("\n7️⃣  Removing conditional placeholders...")
    remove_conditional_placeholders(doc)
    
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
