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

#
# Split-folder support
#
# Supported names:
# - Base folder:      שתי אותיות עבריות + 3 ספרות, לדוגמה: "ננ449"
# - Split parts:      אותו בסיס + אות עברית בסוף, לדוגמה: "ננ449א", "ננ449ב"
#
BASE_PATTERN = r'^[\u0590-\u05FF]{2}\d{3}$'
SPLIT_PATTERN = r'^([\u0590-\u05FF]{2}\d{3})([\u0590-\u05FF])$'


def parse_folder_name(name):
    """
    Parse a folder name into (base, suffix).
    - "ננ449"  -> ("ננ449", None)
    - "ננ449א" -> ("ננ449", "א")
    Returns (None, None) if not matching supported patterns.
    """
    m = re.match(SPLIT_PATTERN, name)
    if m:
        return m.group(1), m.group(2)
    if re.match(BASE_PATTERN, name):
        return name, None
    return None, None


HEBREW_ORDER = 'אבגדהוזחטיכלמנסעפצקרשת'


def hebrew_suffix_key(suffix):
    """
    Provide an order index for a Hebrew letter suffix.
    Non-existent or unknown suffixes are sorted last.
    """
    if not suffix:
        return len(HEBREW_ORDER) + 1
    try:
        return HEBREW_ORDER.index(suffix)
    except ValueError:
        return len(HEBREW_ORDER) + 1


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


def process_split_group(mother_folder, base_name, parts):
    """
    Process a split group of folders sharing the same base (e.g., ננ449א, ננ449ב).
    - Creates individual *_CLEANED.txt in each part folder
    - Merges all texts (ordered by Hebrew suffix) into base_cleaned_merged.txt in the mother folder
    """
    print(f"\n{'-'*60}")
    print(f"🔗 Split detected for base: {base_name}")
    print(f"{'-'*60}")

    texts = []
    any_success = False
    parts_sorted = sorted(parts, key=lambda p: hebrew_suffix_key(p.get('suffix')))

    for part in parts_sorted:
        part_path = part['path']
        part_name = part['name']
        pdf_path = find_matching_pdf(part_path, part_name)

        if not pdf_path:
            print(f"  ❌ PDF not found for {part_name}")
            continue

        try:
            print(f"  📖 Reading {part_name}...")
            cleaned = clean_and_structure_pdf(pdf_path)
            print(f"  🔄 Fixing Hebrew for {part_name}...")
            fixed = reverse_hebrew_in_text(cleaned)

            out_individual = os.path.join(part_path, f"{part_name}_CLEANED.txt")
            with open(out_individual, 'w', encoding='utf-8') as f:
                f.write(fixed)
            print(f"  ✅ Saved {os.path.basename(out_individual)}")

            texts.append(fixed)
            any_success = True
        except Exception as e:
            print(f"  ❌ Error processing {part_name}: {str(e)}")

    if len(texts) >= 2:
        merged = "\n\n".join(texts)
        merged_name = f"{base_name}_cleaned_merged.txt"
        merged_path = os.path.join(mother_folder, merged_name)
        with open(merged_path, 'w', encoding='utf-8') as f:
            f.write(merged)
        print(f"💾 Merged saved: {merged_path}")
        return True
    elif any_success:
        print("⚠ Only one part processed; merged file not created.")
        return True
    else:
        return False


def batch_process(mother_folder):
    """Process all folders in mother folder (supports split groups like ננ449א/ננ449ב)"""
    
    print("\n" + "="*60)
    print("🏥 PDF Medical Report Batch Processor")
    print("="*60)
    print(f"\n📂 Mother folder: {mother_folder}\n")
    
    if not os.path.exists(mother_folder):
        print(f"❌ Error: Folder not found: {mother_folder}")
        return
    
    # Discover folders and group by base name (supporting split suffix)
    all_items = os.listdir(mother_folder)
    groups = {}  # base -> list of parts dicts
    
    for item in all_items:
        item_path = os.path.join(mother_folder, item)
        if not os.path.isdir(item_path):
            continue
        base, suffix = parse_folder_name(item)
        if base:
            groups.setdefault(base, []).append({'path': item_path, 'name': item, 'suffix': suffix})
    
    if not groups:
        print("❌ No valid folders found!")
        print("   Looking for folders named: 2 Hebrew letters + 3 digits (and optional Hebrew suffix)")
        print("   Example: אה456, ננ449א, ננ449ב")
        return
    
    total_groups = len(groups)
    print(f"Found {sum(len(v) for v in groups.values())} folders in {total_groups} group(s):")
    for base, parts in sorted(groups.items()):
        if len(parts) >= 2:
            part_names = ", ".join(p['name'] for p in sorted(parts, key=lambda p: hebrew_suffix_key(p.get('suffix'))))
            print(f"  • {base} → [{part_names}] (split)")
        else:
            print(f"  • {parts[0]['name']}")
    
    print("\n" + "="*60)
    print("🚀 Starting batch processing...")
    print("="*60)
    
    success_count = 0
    failed_count = 0
    
    for i, (base, parts) in enumerate(sorted(groups.items()), 1):
        if len(parts) == 1 and parts[0]['suffix'] is None:
            folder_path = parts[0]['path']
            folder_name = parts[0]['name']
            print(f"\n[{i}/{total_groups}] Processing folder: {folder_name}")
            if process_folder(folder_path, folder_name):
                success_count += 1
            else:
                failed_count += 1
        else:
            print(f"\n[{i}/{total_groups}] Processing split group: {base}")
            if process_split_group(mother_folder, base, parts):
                success_count += 1
            else:
                failed_count += 1
    
    # Final summary
    print("\n" + "="*60)
    print("📊 BATCH PROCESSING COMPLETE")
    print("="*60)
    print(f"\n✅ Successful groups: {success_count}")
    print(f"❌ Failed groups: {failed_count}")
    print(f"📁 Total groups: {total_groups}")
    
    if success_count > 0:
        print(f"\n💾 Cleaned files saved in their respective folders")
        print(f"   Format: [folder_name]_CLEANED.txt")
        print(f"   Merged (when applicable): [base]_cleaned_merged.txt in the mother folder")
    
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


