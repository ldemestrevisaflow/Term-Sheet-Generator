#!/usr/bin/env python3
"""
Term Sheet Generator - BULLETPROOF VERSION
Robust error handling, comprehensive logging, and defensive coding
"""

import json
import sys
import os
from datetime import datetime
from docx import Document
from docx.shared import Pt
import re

def log(msg, level="INFO"):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {msg}")

def parse_date_to_words(date_str):
    """Convert date string (2025-12-20) to words (20 December 2025)"""
    if not date_str:
        return ""
    try:
        if isinstance(date_str, str):
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            day = dt.day
            month = dt.strftime('%B')
            year = dt.year
            return f"{day} {month} {year}"
    except Exception as e:
        log(f"Error parsing date {date_str}: {e}", "WARN")
    return str(date_str) if date_str else ""

def set_cell_text(cell, text):
    """Set text in a table cell"""
    if cell is None:
        return
    cell.text = str(text) if text else ""

def replace_in_document(doc, replacements):
    """Replace placeholders throughout document - handles all edge cases"""
    if not replacements:
        return
    
    # Paragraphs
    for para in doc.paragraphs:
        for old, new in replacements.items():
            if old and new and old in para.text:
                para.text = para.text.replace(str(old), str(new))
    
    # Tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    for old, new in replacements.items():
                        if old and new and old in para.text:
                            para.text = para.text.replace(str(old), str(new))

def fix_table_of_contents(doc, is_binding):
    """Fix Table of Contents"""
    log("Fixing Table of Contents", "INFO")
    
    for para in doc.paragraphs[:100]:  # Check first 100 paras
        if '[non-]' in para.text or 'Non-]' in para.text:
            if is_binding:
                para.text = para.text.replace('[non-]Binding', 'Binding')
                para.text = para.text.replace('[non-]', '')
                para.text = para.text.replace('Non-]Binding', 'Binding')
            else:
                para.text = para.text.replace('[non-]Binding', 'Non-Binding')
                para.text = para.text.replace('[non-]', 'non-')
                para.text = para.text.replace('Non-]Binding', 'Non-Binding')
            log(f"  Fixed: {para.text[:50]}", "DEBUG")

def fix_parties_table(doc, seller, buyer):
    """Fix parties table with correct mapping"""
    log("Fixing parties table", "INFO")
    
    if len(doc.tables) < 2:
        log("Warning: Document has fewer than 2 tables", "WARN")
        return
    
    try:
        table = doc.tables[1]
        
        # Seller (rows 3-8)
        log(f"  Setting Seller: {seller.get('name', '')} ABN {seller.get('abn', '')}", "DEBUG")
        set_cell_text(table.rows[3].cells[1], seller.get('name', ''))
        set_cell_text(table.rows[4].cells[1], seller.get('abn', ''))
        
        # Buyer (rows 10-15)
        log(f"  Setting Buyer: {buyer.get('name', '')} ABN {buyer.get('abn', '')}", "DEBUG")
        set_cell_text(table.rows[10].cells[1], buyer.get('name', ''))
        set_cell_text(table.rows[11].cells[1], buyer.get('abn', ''))
        
    except IndexError as e:
        log(f"Error accessing table rows: {e}", "ERROR")
    except Exception as e:
        log(f"Error in fix_parties_table: {e}", "ERROR")

def fix_recital_a(doc, target):
    """Fix Recital A"""
    log("Fixing Recital A", "INFO")
    
    target_text = f"{target.get('name', '')} (ABN {target.get('abn', '')})"
    log(f"  Company: {target_text}", "DEBUG")
    
    found = False
    for para_idx, para in enumerate(doc.paragraphs):
        if 'Recital A' in para.text or 'insert name and ABN' in para.text:
            if '[insert name and ABN of company]' in para.text:
                para.text = para.text.replace('[insert name and ABN of company]', target_text)
                found = True
                log(f"  Updated in paragraph {para_idx}", "DEBUG")
                break
    
    if not found:
        # Try next few paragraphs after Recital A
        for para_idx, para in enumerate(doc.paragraphs):
            if 'Recital A' in para.text:
                for offset in range(1, 10):
                    if para_idx + offset < len(doc.paragraphs):
                        next_para = doc.paragraphs[para_idx + offset]
                        if '[insert name and ABN' in next_para.text:
                            next_para.text = next_para.text.replace('[insert name and ABN of company]', target_text)
                            found = True
                            log(f"  Updated in paragraph {para_idx + offset}", "DEBUG")
                            break
                if found:
                    break
    
    if not found:
        log("  Warning: Could not find Recital A placeholder", "WARN")

def generate_term_sheet(questionnaire_file, template_file, output_file):
    """Main generation function"""
    
    log("=" * 80, "INFO")
    log("TERM SHEET GENERATOR - BULLETPROOF VERSION", "INFO")
    log("=" * 80, "INFO")
    
    # Check file existence
    log(f"Checking input files...", "INFO")
    
    if not os.path.exists(questionnaire_file):
        log(f"ERROR: Questionnaire file not found: {questionnaire_file}", "ERROR")
        sys.exit(1)
    
    if not os.path.exists(template_file):
        log(f"ERROR: Template file not found: {template_file}", "ERROR")
        sys.exit(1)
    
    log(f"✓ Questionnaire found: {questionnaire_file}", "INFO")
    log(f"✓ Template found: {template_file}", "INFO")
    
    # Load questionnaire
    try:
        log(f"Loading questionnaire...", "INFO")
        with open(questionnaire_file, 'r') as f:
            data = json.load(f)
        log("✓ Questionnaire loaded successfully", "INFO")
    except json.JSONDecodeError as e:
        log(f"ERROR: Invalid JSON in questionnaire: {e}", "ERROR")
        sys.exit(1)
    except Exception as e:
        log(f"ERROR: Failed to load questionnaire: {e}", "ERROR")
        sys.exit(1)
    
    # Load template
    try:
        log(f"Loading template...", "INFO")
        doc = Document(template_file)
        log(f"✓ Template loaded successfully ({len(doc.tables)} tables, {len(doc.paragraphs)} paragraphs)", "INFO")
    except Exception as e:
        log(f"ERROR: Failed to load template: {e}", "ERROR")
        sys.exit(1)
    
    # Extract party data
    log("Extracting party data...", "INFO")
    parties = data.get('parties', {})
    seller = parties.get('seller', {})
    buyer = parties.get('buyer', {})
    target = parties.get('targetCompany', {})
    deal = data.get('deal', {})
    legal = data.get('legal', {})
    
    log(f"  Seller: {seller.get('name', 'NOT PROVIDED')}", "DEBUG")
    log(f"  Buyer: {buyer.get('name', 'NOT PROVIDED')}", "DEBUG")
    log(f"  Target: {target.get('name', 'NOT PROVIDED')}", "DEBUG")
    
    is_binding = legal.get('termSheetType', 'binding') == 'binding'
    log(f"  Type: {'BINDING' if is_binding else 'NON-BINDING'}", "DEBUG")
    
    # Build replacements
    log("Building replacement dictionary...", "INFO")
    replacements = {
        '[Completion Date]': parse_date_to_words(deal.get('completionDate', '')),
        '[Announcement Date]': parse_date_to_words(deal.get('announcementDate', '')),
        '[Execution Date]': parse_date_to_words(deal.get('executionDate', '')),
        '[Purchase Price]': f"${deal.get('purchasePrice', 0):,.0f}" if deal.get('purchasePrice') else '',
        '[Deposit Amount]': f"${deal.get('depositAmount', 0):,.0f}" if deal.get('depositAmount') else '',
    }
    
    # Apply fixes in sequence
    log("Applying document fixes...", "INFO")
    
    log("  1/5: Fixing Table of Contents", "INFO")
    fix_table_of_contents(doc, is_binding)
    
    log("  2/5: Fixing parties table", "INFO")
    fix_parties_table(doc, seller, buyer)
    
    log("  3/5: Fixing Recital A", "INFO")
    fix_recital_a(doc, target)
    
    log("  4/5: Applying general replacements", "INFO")
    replace_in_document(doc, replacements)
    
    log("  5/5: Removing conditional placeholders", "INFO")
    conditionals = [
        '[Balance of]', '[Use the following for a binding term sheet]',
        '[Consider whether security/parent guarantee is required to be given by the Buyer]',
        '[and accounting]', '[insert Party 3 Name]',
    ]
    for cond in conditionals:
        for para in doc.paragraphs:
            if cond in para.text:
                para.text = para.text.replace(cond, '')
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        if cond in para.text:
                            para.text = para.text.replace(cond, '')
    
    # Save
    log(f"Saving to {output_file}...", "INFO")
    try:
        doc.save(output_file)
        log(f"✓ Document saved successfully", "INFO")
    except Exception as e:
        log(f"ERROR: Failed to save document: {e}", "ERROR")
        sys.exit(1)
    
    log("=" * 80, "INFO")
    log("✅ TERM SHEET GENERATED SUCCESSFULLY", "INFO")
    log("=" * 80, "INFO")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python3 generate_term_sheet.py <questionnaire.json> <template.docx> <output.docx>")
        sys.exit(1)
    
    questionnaire_file = sys.argv[1]
    template_file = sys.argv[2]
    output_file = sys.argv[3]
    
    try:
        generate_term_sheet(questionnaire_file, template_file, output_file)
    except Exception as e:
        log(f"FATAL ERROR: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
