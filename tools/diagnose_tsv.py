#!/usr/bin/env python3
# Diagnostic script to check a TSV file for issues that might break Frictionless validation.

import sys
import os
import re

def check_bom(file_path):
    with open(file_path, 'rb') as f:
        first_bytes = f.read(3)
        if first_bytes == b'\xef\xbb\xbf':
            print("❗ UTF-8 BOM detected at start of file (should be removed).")
        else:
            print("✅ No UTF-8 BOM found.")

def check_line_lengths(file_path):
    col_counts = {}
    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        for lineno, line in enumerate(f, 1):
            cols = line.rstrip('\n').split('\t')
            count = len(cols)
            col_counts.setdefault(count, []).append(lineno)
    if len(col_counts) == 1:
        count = next(iter(col_counts))
        print(f"✅ All rows have {count} columns.")
    else:
        print("❗ Inconsistent column counts detected:")
        for count, lines in sorted(col_counts.items()):
            sample = ", ".join(map(str, lines[:3])) + ("..." if len(lines) > 3 else "")
            print(f"  {count} columns: {len(lines)} lines (e.g., lines {sample})")

def check_invisible_chars(file_path):
    ctrl_chars = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]')
    carriage_lines = []
    control_lines = []

    with open(file_path, 'r', encoding='utf-8', newline='') as f:
        for lineno, line in enumerate(f, 1):
            if '\r' in line:
                carriage_lines.append(lineno)
            if ctrl_chars.search(line):
                control_lines.append(lineno)

    if carriage_lines:
        print(f"❗ Lines with carriage returns (\\r): {carriage_lines[:5]}{'...' if len(carriage_lines) > 5 else ''}")
    else:
        print("✅ No carriage return characters found.")

    if control_lines:
        print(f"❗ Lines with control characters: {control_lines[:5]}{'...' if len(control_lines) > 5 else ''}")
    else:
        print("✅ No control characters found.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python diagnose_tsv.py path/to/file.tsv")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    print(f"🔍 Running diagnostics on: {file_path}\n")
    check_bom(file_path)
    check_line_lengths(file_path)
    check_invisible_chars(file_path)

if __name__ == "__main__":
    main()
