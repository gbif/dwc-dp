#!/usr/bin/env python3
#
# Script to check for potential orthographic errors in descriptions, comments, and 
# examples in the local ../dwc-dp/0.1/table-schemas.

import os
import json
import re

# === Configuration ===
# Set your root folder path here:
root_folder = '../dwc-dp/0.1/table-schemas'

# Fields to check within each JSON file
fields_to_check = ['description', 'title', 'comments', 'examples']

# Function to detect likely spelling errors (you can add more patterns as needed)
def find_potential_issues(text):
    issues = []
    # Extract words longer than 3 characters
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
    for word in words:
        lw = word.lower()
        # Look for known typo patterns and suspect structures
        if 'interation' in lw:
            issues.append((word, 'Did you mean "interaction"?'))
        if re.search(r'(.)\1\1', lw):  # 3+ repeated letters
            issues.append((word, 'Suspicious: repeated letters'))
        if lw.endswith('tionn') or lw.endswith('inng'):
            issues.append((word, 'Suspicious suffix'))
    return issues

# Scan files recursively
report = []

for subdir, dirs, files in os.walk(root_folder):
    for file in files:
        if file.endswith('.json'):
            filepath = os.path.join(subdir, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Skipping {filepath} (could not read JSON): {e}")
                continue

            file_issues = []
            # Check top-level fields
            for field in fields_to_check:
                if field in data and isinstance(data[field], str):
                    issues = find_potential_issues(data[field])
                    if issues:
                        file_issues.append({
                            'field': field,
                            'issues': issues,
                            'text': data[field]
                        })

            # Check each field in the 'fields' array
            for field_obj in data.get('fields', []):
                field_name = field_obj.get('name', '[unknown]')
                for subfield in fields_to_check:
                    if subfield in field_obj and isinstance(field_obj[subfield], str):
                        issues = find_potential_issues(field_obj[subfield])
                        if issues:
                            file_issues.append({
                                'field': f"{field_name}.{subfield}",
                                'issues': issues,
                                'text': field_obj[subfield]
                            })

            if file_issues:
                report.append({
                    'file': filepath,
                    'issues': file_issues
                })

# Output report
if report:
    print("\n=== Potential Orthographic Issues Found ===\n")
    for entry in report:
        print(f"\nFile: {entry['file']}")
        for issue in entry['issues']:
            print(f"  Field: {issue['field']}")
            print(f"  Text: {issue['text']}")
            for word, comment in issue['issues']:
                print(f"    -> {word}: {comment}")
else:
    print("No potential orthographic issues found.")
