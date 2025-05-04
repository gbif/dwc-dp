#!/usr/bin/env python3
#
# Script to check that the descriptions, comments, and examples in the local 
# ../dwc-dp/0.1/table-schemas are the same as their corresponding terms in the canonical
# term_versions files in the TDWG GitHub repositories.

import os
import json
import csv
import requests

# --- CONFIG ---

# Local directory of table schemas
table_schemas_dir = '../dwc-dp/0.1/table-schemas'

# List of canonical term_versions sources to check
term_sources = [
    {
        'name': 'Darwin Core',
        'namespace': 'dwc:',
        'url': 'https://raw.githubusercontent.com/tdwg/dwc/master/vocabulary/term_versions.csv'
    },
    {
        'name': 'Humboldt Extension',
        'namespace': 'eco:',
        'url': 'https://raw.githubusercontent.com/tdwg/hc/main/vocabulary/term_versions.csv'
    },
    {
        'name': 'ChronometricAge Extension',
        'namespace': 'chrono:',
        'url': 'https://raw.githubusercontent.com/tdwg/chrono/master/vocabulary/term_versions.csv'
    }
]

# --- FETCH TERMS FROM ALL SOURCES ---

all_term_definitions = {}  # (namespace, local_name) -> dict with definition/comments/examples

for source in term_sources:
    print(f"Fetching {source['name']} term_versions...")
    response = requests.get(source['url'])
    response.raise_for_status()

    reader = csv.DictReader(response.text.splitlines())
    loaded_count = 0
    for row in reader:
        local_name = row.get('term_localName', '').strip()
        status = row.get('status', '').strip().lower()
        if local_name and status == 'recommended':
            key = (source['namespace'], local_name)
            all_term_definitions[key] = {
                'definition': row.get('definition', '').strip(),
                'comments': row.get('comments', '').strip(),
                'examples': row.get('examples', '').strip()
            }
            loaded_count += 1

    print(f"Loaded {loaded_count} recommended terms from {source['name']}.\n")

# --- PROCESS LOCAL TABLE SCHEMAS ---

for filename in os.listdir(table_schemas_dir):
    if not filename.endswith('.json'):
        continue

    path = os.path.join(table_schemas_dir, filename)
    with open(path, 'r') as f:
        schema = json.load(f)

    table_name = schema.get('name', filename)

    print(f"Checking table: {table_name}")

    # Check each field
    for field in schema.get('fields', []):
        field_name = field.get('name')
        description = field.get('description', '').strip()
        comments = field.get('comments', '').strip()
        examples = field.get('examples', '').strip()

        # Find matching namespace(s) for this field
        matched = False
        for namespace, local_name in all_term_definitions.keys():
            if field_name == local_name:
                term_def = all_term_definitions[(namespace, local_name)]
                matched = True

                comparisons = [
                    ('description', 'definition'),
                    ('comments', 'comments'),
                    ('examples', 'examples')
                ]

                for local_key, canonical_key in comparisons:
                    local_value = locals()[local_key]
                    canonical_value = term_def[canonical_key]
                    if canonical_value != local_value:
                        print(f"[{namespace}Mismatch] {table_name}.{field_name}: {local_key} differs from {namespace} canonical")
                        print(f"    - Canonical: {canonical_value!r}")
                        print(f"    - Found: {local_value!r}\n")
                break  # Found the match, no need to check other namespaces

        if not matched:
            # Not a canonical term we are tracking, skip
            continue

print("\nConsistency check against all canonical sources complete.")
