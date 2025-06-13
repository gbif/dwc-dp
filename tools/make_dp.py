# Python script to generate datapackage.json for a folder full of DwC-DP table schema 
# CSV/TSV/TXT files.
#
# Usage: python make_dp.py -p path_to_table_files -t title -n name

import os
import csv
import json
import argparse
import re
import urllib.request

SCHEMA_BASE_URL = "https://raw.githubusercontent.com/gbif/rs.gbif.org/master/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas"

def fetch_model_schema(table_name):
    url = f"{SCHEMA_BASE_URL}/{table_name}.json"
    print(f"\nFetching schema for {table_name} from {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except Exception as e:
        print(f"Warning: Schema not found for '{table_name}' at URL: {url}")
        return None

def normalize_fieldname(field):
    return field.lower().replace("-", "").replace("_", "")

def normalize_package_name(name):
    return re.sub(r"[^a-z0-9._/]+", "-", name.lower())

def get_dialect(delimiter):
    return {
        "delimiter": delimiter,
        "quoteChar": '"',
        "lineTerminator": "\n",
        "header": True,
        "doubleQuote": True,
        "skipInitialSpace": False,
        "commentChar": "#",
        "caseSensitiveHeader": False
    }

def build_datapackage(path, title, name):
    resources = []
    name = normalize_package_name(name)

    present_tables = set(
        os.path.splitext(f)[0]
        for f in os.listdir(path)
        if os.path.isfile(os.path.join(path, f)) and f.lower().endswith(('.csv', '.tsv', '.txt'))
    )

    print(f"Detected tables: {sorted(present_tables)}\n")

    for filename in os.listdir(path):
        if filename.lower().endswith(('.csv', '.tsv', '.txt')):
            table_name = os.path.splitext(filename)[0]
            delimiter = "," if filename.endswith(".csv") else "\t"
            schema = fetch_model_schema(table_name)

            if not schema:
                print(f"Skipping {filename}, no schema found.")
                continue

            # Save original fields before filtering
            original_fields_lookup = {f['name']: f for f in schema.get('fields', [])}

            full_path = os.path.join(path, filename)
            with open(full_path, newline='\n', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                headers = reader.fieldnames

            # Filter fields based on actual file columns
            schema['fields'] = [
                field for field in schema.get('fields', [])
                if normalize_fieldname(field['name']) in [normalize_fieldname(h) for h in headers]
            ]

            # Remove nullable foreign keys to missing tables, with debug output
            if 'foreignKeys' in schema:
                filtered_fks = []
                for fk in schema['foreignKeys']:
                    ref_table = fk['reference']['resource']
                    field_name = fk['fields'] if isinstance(fk['fields'], str) else fk['fields'][0]
                    field_def = original_fields_lookup.get(field_name)
                    is_required = field_def.get('required', False) if field_def else False
                    if ref_table in present_tables or is_required:
                        print(f"Table: {table_name} Keeping foreign key to '{ref_table}' via field '{field_name}'")
                        filtered_fks.append(fk)
                    else:
                        print(f"Table: {table_name} Removing foreign key to '{ref_table}' via field '{field_name}' (missing table and nullable field)")

                schema['foreignKeys'] = filtered_fks

            resource = {
                "profile": "tabular-data-resource",
                "name": table_name,
                "path": filename,
                "format": "csv" if delimiter == "," else "tsv",
                "mediatype": "text/csv" if delimiter == "," else "text/tab-separated-values",
                "schema": schema,
                "dialect": get_dialect(delimiter)
            }

            resources.append(resource)

    datapackage = {
        "profile": "tabular-data-package",
        "name": name,
        "title": title,
        "resources": resources
    }

    output_path = os.path.join(path, "datapackage.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(datapackage, f, indent=2)
    print(f"Data package written to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a Frictionless Data Package from DwC-DP tables")
    parser.add_argument("-p", "--path", required=True, help="Path to folder containing CSV/TSV files")
    parser.add_argument("-t", "--title", required=True, help="Title for the data package")
    parser.add_argument("-n", "--name", required=True, help="Name for the data package (URL-safe id)")

    args = parser.parse_args()
    build_datapackage(args.path, args.title, args.name)
