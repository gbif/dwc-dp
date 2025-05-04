#!/usr/bin/env python3
#
# Script to make a CSV file with one entry for each field from the 
# ../dwc-dp/0.1/table-schemas.

import os
import json
import csv
import re
import requests

# --- CONFIG ---

table_schemas_dir = '../dwc-dp/0.1/table-schemas'
output_csv = 'all_fields_summary.csv'

# Canonical sources
term_sources = [
    {
        'namespace': 'dwc:',
        'url': 'https://raw.githubusercontent.com/tdwg/dwc/master/vocabulary/term_versions.csv'
    },
    {
        'namespace': 'eco:',
        'url': 'https://raw.githubusercontent.com/tdwg/hc/main/vocabulary/term_versions.csv'
    },
    {
        'namespace': 'chrono:',
        'url': 'https://raw.githubusercontent.com/tdwg/chrono/master/vocabulary/term_versions.csv'
    }
]

# --- FETCH CANONICAL TERMS ---

canonical_terms = {}  # field_name -> namespace

for source in term_sources:
    print(f"Fetching {source['namespace']} term_versions...")
    response = requests.get(source['url'])
    response.raise_for_status()
    reader = csv.DictReader(response.text.splitlines())
    for row in reader:
        local_name = row.get('term_localName', '').strip()
        status = row.get('status', '').strip().lower()
        if local_name and status == 'recommended':
            canonical_terms[local_name] = source['namespace']
    print(f"Loaded terms from {source['namespace']}\n")

# --- FUNCTION: Convert lowerCamelCase to Label ---

def camel_to_words(name):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', name).replace('_', ' ').title()

# --- FUNCTION: Extract Category from Label ---

def extract_category(label):
    parts = label.strip().split()
    return parts[-1] if parts else ''

# --- WRITE CSV ---

with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        'table_schema',
        'name',
        'namespace',
        'namespace_dp',
        'iri',
        'description',
        'comments',
        'examples',
        'label',
        'category'
    ])
    writer.writeheader()

    # Process each schema file and write every field
    for filename in os.listdir(table_schemas_dir):
        if not filename.endswith('.json'):
            continue

        path = os.path.join(table_schemas_dir, filename)
        with open(path, 'r') as f:
            schema = json.load(f)

        table_name = schema.get('name', filename)

        for field in schema.get('fields', []):
            field_name = field.get('name')
            description = field.get('description', '').strip()
            comments = field.get('comments', '').strip()
            examples = field.get('examples', '').strip()
            namespace_dp = field.get('namespace', '').strip()
            iri = field.get('iri', '').strip()

            namespace = canonical_terms.get(field_name, '')
            label = camel_to_words(field_name)
            category = extract_category(label)

            writer.writerow({
                'table_schema': table_name,
                'name': field_name,
                'namespace': namespace,
                'namespace_dp': namespace_dp,
                'iri': iri,
                'description': description,
                'comments': comments,
                'examples': examples,
                'label': label,
                'category': category
            })

print(f"\n✅ All fields summary written to {output_csv}.")
