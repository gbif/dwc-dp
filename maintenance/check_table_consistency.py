#!/usr/bin/env python3
#
# Script to check that the descriptions, comments, and examples in the local 
# ../dwc-dp/0.1/table-schema files follow some consistent patterns.

import os
import json
import re
import csv
import requests
from collections import defaultdict

# --- CONFIG ---

# Local directory of table schemas
table_schemas_dir = '../dwc-dp/0.1/table-schemas'

# Darwin Core canonical CSV (correct source)
dwc_csv_url = 'https://raw.githubusercontent.com/tdwg/dwc/master/vocabulary/term_versions.csv'

# Accepted namespace prefixes (skip checks if term is already used with one of these)
ACCEPTED_PREFIXES = ['dwc:', 'dcterms:', 'dc:', 'dwciri:', 'foaf:', 'chrono:', 'eco:']

# --- FETCH CANONICAL DARWIN CORE TERMS ---

print("Fetching Darwin Core term_versions...")
response = requests.get(dwc_csv_url)
response.raise_for_status()

dwc_term_definitions = {}  # field_name -> dict with definition/comments/examples
dwc_terms = set()

reader = csv.DictReader(response.text.splitlines())
for row in reader:
    local_name = row.get('term_localName', '').strip()
    status = row.get('status', '').strip().lower()
    if local_name and status == 'recommended':
        dwc_term_definitions[local_name] = {
            'definition': row.get('definition', '').strip(),
            'comments': row.get('comments', '').strip(),
            'examples': row.get('examples', '').strip()
        }
        dwc_terms.add(local_name)

print(f"Loaded {len(dwc_term_definitions)} recommended Darwin Core term definitions.\n")

# --- PREP ---

canonical_definitions = {}  # field_name -> canonical definition from local table schemas
fields_to_compare = defaultdict(list)  # field_name -> list of (table_name, field details)

# Regex patterns
dwc_pattern = re.compile(r'\bdwc:([A-Za-z0-9_]+)\b')
bare_term_pattern = re.compile(r'\b([A-Z][a-zA-Z0-9_]+)\b')

def check_examples_format(examples):
    issues = []
    if not examples:
        return issues

    # Pattern: backtick-wrapped content, optional explanatory parentheses after
    pattern = re.compile(r'`[^`]+`\s*(\([^)]+\))?')

    # Find all valid examples
    matches = list(pattern.finditer(examples))

    # If no valid examples at all, it's a problem
    if not matches:
        issues.append(f"Example format issue: no valid backtick-wrapped content found.")
        return issues

    # Now check if the entire string is made up of valid examples plus separators (e.g., semicolons)
    rebuilt = ''
    last_end = 0
    for match in matches:
        # Add everything from the last match end to this match start (e.g., separators)
        rebuilt += examples[last_end:match.end()]
        last_end = match.end()
    rebuilt += examples[last_end:].strip()

    # Normalize spacing for comparison
    original_normalized = re.sub(r'\s+', ' ', examples.strip())
    rebuilt_normalized = re.sub(r'\s+', ' ', rebuilt.strip())

    if original_normalized != rebuilt_normalized:
        issues.append(f"Example format issue: extra/malformed content outside valid examples.")

    return issues

# --- MAIN PASS: Process files ---

for filename in os.listdir(table_schemas_dir):
    if not filename.endswith('.json'):
        continue

    path = os.path.join(table_schemas_dir, filename)
    with open(path, 'r') as f:
        schema = json.load(f)

    table_name = schema.get('name', filename)
    table_description = schema.get('description', '').strip()

    print(f"\nChecking table: {table_name}")

    # Get primary key(s)
    primary_keys = schema.get('primaryKey')
    if isinstance(primary_keys, str):
        primary_keys = [primary_keys]
    elif not primary_keys:
        primary_keys = []

    # === 1️⃣ TABLE-LEVEL CHECKS ===

    if not re.match(r'^(A|An)\b', table_description):
        print(f"  [TablePattern-DescriptionMissingA/An] Table description doesn't start with 'A/An'")
        print(f"      {table_description}")

    bare_terms_in_table = bare_term_pattern.findall(table_description)
    for term in bare_terms_in_table:
        already_prefixed = any(f'{prefix}{term}' in table_description for prefix in ACCEPTED_PREFIXES)
        if term in dwc_terms and not already_prefixed:
            print(f"  [DarwinCore-TableDescription] Possibly missing dwc: prefix: '{term}'")
            print(f"      {table_description}")

    # === 2️⃣ FIELD-LEVEL CHECKS ===

    for field in schema.get('fields', []):
        field_name = field.get('name')
        description = field.get('description', '').strip()
        comments = field.get('comments', '').strip()
        examples = field.get('examples', '').strip()

        # --- Pattern checks: description ---
#         if description and not re.match(r'^(A|An)\b', description):
#             print(f"  [FieldPattern-DescriptionMissingA/An] {field_name}: Description doesn't start with 'A/An'")
#             print(f"      {description}")

        the_ns_matches_desc = re.findall(r'\bthe (dwc:[A-Za-z0-9_]+)\b', description, flags=re.IGNORECASE)
        for match in the_ns_matches_desc:
            print(f"  [FieldPattern-HasThe-Description] {field_name}: Uses 'the' before {match}")
            print(f"      {description}")

        if description and not description.rstrip().endswith('.'):
            print(f"  [FieldPattern-NoEndingPeriod-Description] {field_name}: Description does not end with a period")
            print(f"      {description}")

        # --- Darwin Core checks: description ---
        bare_terms_desc = bare_term_pattern.findall(description)
        for term in bare_terms_desc:
            already_prefixed = any(f'{prefix}{term}' in description for prefix in ACCEPTED_PREFIXES)
            if term in dwc_terms and not already_prefixed:
                print(f"  [DarwinCore-Description] {field_name}: Possibly missing dwc: prefix: '{term}'")
                print(f"      {description}")

        # --- Pattern checks: comments ---
        the_ns_matches_comments = re.findall(r'\bthe (dwc:[A-Za-z0-9_]+)\b', comments, flags=re.IGNORECASE)
        for match in the_ns_matches_comments:
            print(f"  [FieldPattern-HasThe-Comments] {field_name}: Uses 'the' before {match}")
            print(f"      {comments}")

        if comments and not comments.rstrip().endswith('.'):
            print(f"  [FieldPattern-NoEndingPeriod-Comments] {field_name}: Comments do not end with a period")
            print(f"      {comments}")

        # --- Darwin Core checks: comments ---
        bare_terms_comments = bare_term_pattern.findall(comments)
        for term in bare_terms_comments:
            already_prefixed = any(f'{prefix}{term}' in comments for prefix in ACCEPTED_PREFIXES)
            if term in dwc_terms and not already_prefixed:
                print(f"  [DarwinCore-Comments] {field_name}: Possibly missing dwc: prefix: '{term}'")
                print(f"      {comments}")

        # --- Example formatting ---
        issues = check_examples_format(examples)
        for issue in issues:
            print(f"  [Examples] {field_name}: {issue}")
            print(f"      {examples}")

        # Prepare field details for canonical check
        field_details = {
            'table': table_name,
            'description': description,
            'comments': comments,
            'examples': examples
        }

        if field_name in primary_keys:
            canonical_definitions[field_name] = field_details
        else:
            fields_to_compare[field_name].append(field_details)

# === 3️⃣ CROSS-SCHEMA SHARED FIELD COMPARISON ===

print("\nChecking cross-schema consistency with local primary-key definitions...\n")
for field_name, occurrences in fields_to_compare.items():
    canonical = canonical_definitions.get(field_name)
    if not canonical:
        continue  # no canonical found, skip

    for occ in occurrences:
        for key in ['description', 'comments', 'examples']:
            if canonical[key] != occ[key]:
                print(f"  [PrimaryKeyMismatch] {occ['table']}.{field_name}: {key} differs from canonical ({canonical['table']})")
                print(f"    - Canonical: {canonical[key]!r}")
                print(f"    - Found: {occ[key]!r}\n")

print("\nThorough check complete.")
