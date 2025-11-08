#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch PDF Processor for Medical Reports
Processes multiple folders automatically

Usage:
    python3 pdf_batch_processor.py
    (Will prompt for folder path)
"""

import os
import sys
import re
import pdfplumber
from pathlib import Path

try:
    from bidi.algorithm import get_display
    BIDI_AVAILABLE = True
except ImportError:
    BIDI_AVAILABLE = False


def is_valid_folder_name(name):
    """
    Check if folder name matches pattern: 2 Hebrew letters + 3 digits
    Example: אה456, בל123, גר789
    """
    pattern = r'^[\u0590-\u05FF]{2}\d{3}$'
    return bool(re.match(pattern, name))


def find_matching_pdf(folder_path, folder_name):
    """
    Find PDF file with the same name as folder
    Example: In folder "אל723" find "אל723.pdf"
    """
    pdf_name = f"{folder_name}.pdf"
    pdf_path = os.path.join(folder_path, pdf_name)
    
    if os.path.exists(pdf_path):
        return pdf_path
    
    # Try case-insensitive search
    for file in os.listdir(folder_path):
        if file.lower() == pdf_name.lower():
            return os.path.join(folder_path, file)
    
    return None


def clean_and_structure_pdf(input_pdf_path):
    """Clean and structure PDF text"""
    
    # Read PDF
    full_text = ""
    with pdfplumber.open(input_pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                full_text += page_text + "\n"
    
    if not full_text.strip():
        raise Exception("No text found in PDF")
    
    # Clean
    text = full_text
    text = re.sub(r'<[^>]+>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'--- PAGE \d+ ---', '', text, flags=re.IGNORECASE)
    
    # Remove repetitive headers
    repetitive_headers = [
        r'-+\s*סודי רפואי\s*-+',
        r'תדפיס מפגש רופא',
        r'פרטי מטופל/נבדק',
        r'The following table:',
        r'פרטי המפגש נשלחו למרפאת האם של החייל',
    ]
    
    for pattern in repetitive_headers:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Structure - Meeting separators
    text = re.sub(
        r'(\d{3}/\d+)\s+מפגש',
        r'\n\n=== מפגש \1 - START ===\n',
        text,
        flags=re.MULTILINE
    )
    
    # Internal headers
    internal_headers = {
        r'אנמנזה\s*:?': '**אנמנזה:**',
        r'ממצאים\s*:?': '**ממצאים:**',
        r'אבחנות\s*:?': '**אבחנות:**',
        r'דיון ותוכנית\s*:?': '**דיון ותוכנית:**',
        r'הפניות\s*:?': '**הפניות:**',
        r'תרופות במפגש\s*:?': '**תרופות במפגש:**',
    }
    
    for pattern, replacement in internal_headers.items():
        text = re.sub(
            pattern,
            f'\n{replacement}\n',
            text,
            flags=re.MULTILINE | re.IGNORECASE
        )
    
    # Cleanup whitespace
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    text = re.sub(r' {2,}', ' ', text)
    text = text.strip()
    
    return text


def reverse_hebrew_in_text(text):
    """Fix reversed Hebrew text"""
    
    def fix_hebrew_line(line):
        tokens = []
        current_token = ""
        
        for char in line:
            if char in ' \t':
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            else:
                current_token += char
        
        if current_token:
            tokens.append(current_token)
        
        tokens.reverse()
        
        result_tokens = []
        for token in tokens:
            if token in ' \t':
                result_tokens.append(token)
            elif any('\u0590' <= c <= '\u05FF' for c in token):
                result_tokens.append(token[::-1])
            else:
                result_tokens.append(token)
        
        return ''.join(result_tokens)
    
    lines = text.split('\n')
    fixed_lines = []
    
    for line in lines:
        if any('\u0590' <= c <= '\u05FF' for c in line):
            try:
                fixed_line = fix_hebrew_line(line)
                fixed_lines.append(fixed_line)
            except:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def process_folder(folder_path, folder_name):
    """Process a single folder"""
    
    print(f"\n{'='*60}")
    print(f"📁 Processing: {folder_name}")
    print(f"{'='*60}")
    
    # Find PDF
    pdf_path = find_matching_pdf(folder_path, folder_name)
    
    if not pdf_path:
        print(f"❌ PDF not found: {folder_name}.pdf")
        return False
    
    print(f"✓ Found PDF: {os.path.basename(pdf_path)}")
    
    try:
        # Process PDF
        print("📖 Reading PDF...")
        cleaned_text = clean_and_structure_pdf(pdf_path)
        print(f"✓ Read {len(cleaned_text):,} characters")
        
        print("🔄 Fixing Hebrew...")
        fixed_text = reverse_hebrew_in_text(cleaned_text)
        print("✓ Hebrew fixed")
        
        # Save in same folder
        output_filename = f"{folder_name}_CLEANED.txt"
        output_path = os.path.join(folder_path, output_filename)
        
        print(f"💾 Saving: {output_filename}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(fixed_text)
        
        print(f"✅ Success! Saved: {output_path}")
        print(f"📊 Stats: {len(fixed_text):,} chars, {len(fixed_text.splitlines()):,} lines")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def batch_process(mother_folder):
    """Process all folders in mother folder"""
    
    print("\n" + "="*60)
    print("🏥 PDF Medical Report Batch Processor")
    print("="*60)
    print(f"\n📂 Mother folder: {mother_folder}\n")
    
    if not os.path.exists(mother_folder):
        print(f"❌ Error: Folder not found: {mother_folder}")
        return
    
    # Find all valid folders
    all_items = os.listdir(mother_folder)
    valid_folders = []
    
    for item in all_items:
        item_path = os.path.join(mother_folder, item)
        if os.path.isdir(item_path) and is_valid_folder_name(item):
            valid_folders.append((item_path, item))
    
    if not valid_folders:
        print("❌ No valid folders found!")
        print("   Looking for folders named: 2 Hebrew letters + 3 digits")
        print("   Example: אה456, בל123, גר789")
        return
    
    print(f"Found {len(valid_folders)} folders to process:")
    for _, name in valid_folders:
        print(f"  • {name}")
    
    print("\n" + "="*60)
    print("🚀 Starting batch processing...")
    print("="*60)
    
    # Process each folder
    success_count = 0
    failed_count = 0
    
    for i, (folder_path, folder_name) in enumerate(valid_folders, 1):
        print(f"\n[{i}/{len(valid_folders)}] Processing folder: {folder_name}")
        
        if process_folder(folder_path, folder_name):
            success_count += 1
        else:
            failed_count += 1
    
    # Final summary
    print("\n" + "="*60)
    print("📊 BATCH PROCESSING COMPLETE")
    print("="*60)
    print(f"\n✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📁 Total folders: {len(valid_folders)}")
    
    if success_count > 0:
        print(f"\n💾 Cleaned files saved in their respective folders")
        print(f"   Format: [folder_name]_CLEANED.txt")
    
    print("\n🎉 Done!\n")


def main():
    print("\n" + "="*60)
    print("🏥 PDF Medical Report Batch Processor")
    print("="*60)
    print("\nThis tool processes folders containing medical PDF reports.")
    print("\nThe mother folder should contain subfolders named:")
    print("  • 2 Hebrew letters + 3 digits")
    print("  • Examples: אה456, בל123, גר789")
    print("\nEach subfolder should contain a PDF with the same name.")
    print("="*60)
    
    # Ask for folder path
    print("\n📂 Please enter the path to the mother folder:")
    mother_folder = input("➤ ").strip()
    
    # Remove quotes if user added them
    if mother_folder.startswith('"') and mother_folder.endswith('"'):
        mother_folder = mother_folder[1:-1]
    elif mother_folder.startswith("'") and mother_folder.endswith("'"):
        mother_folder = mother_folder[1:-1]
    
    if not mother_folder:
        print("\n❌ Error: No folder path provided")
        sys.exit(1)
    
    batch_process(mother_folder)


if __name__ == "__main__":
    main()


