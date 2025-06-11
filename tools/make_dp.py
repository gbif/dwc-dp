# Python script to generate datapackage.json for a folder full of DwC-DP table schema CSV 
# files.
# Usage: python generate_qrg.py

import os
import csv
import json
import urllib.request
import sys

SCHEMA_BASE_URL = "https://raw.githubusercontent.com/gbif/rs.gbif.org/master/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas"

def fetch_model_schema(table_name):
    url = f"{SCHEMA_BASE_URL}/{table_name}.json"
    print(f"Fetching schema for {table_name} from {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except Exception as e:
        print(f"Warning: Schema not found for '{table_name}' at URL: {url}")
        return None

def normalize_fieldname(field):
    return field.lower().replace("-", "").replace("_", "")

def map_csv_fields_to_schema_fields(csv_fields, schema_fields):
    schema_lookup = {normalize_fieldname(f['name']): f['name'] for f in schema_fields}
    mapped_fields = []
    for field in csv_fields:
        normalized = normalize_fieldname(field)
        if normalized in schema_lookup:
            mapped_fields.append(schema_lookup[normalized])
    return mapped_fields

def get_populated_fields(file_path, delimiter):
    print(f"Inspecting populated fields in {file_path}...")
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        if not reader.fieldnames:
            print("  No headers found.")
            return []
        print(f"  Headers found: {reader.fieldnames}")
        fields = {field: False for field in reader.fieldnames}
        for row in reader:
            for field in fields:
                if row.get(field) and row.get(field).strip():
                    fields[field] = True
            if all(fields.values()):
                break
        populated = [field for field, used in fields.items() if used]
        print(f"  Populated fields: {populated}")
        return populated

def generate_resource_descriptor(table_name, data_filename, model_schema, populated_fields):
    schema_fields = model_schema['fields']
    mapped_fieldnames = map_csv_fields_to_schema_fields(populated_fields, schema_fields)
    filtered_fields = [f for f in schema_fields if f['name'] in mapped_fieldnames]
    print(f"  Generating resource for {table_name}, using {len(filtered_fields)} populated fields.")
    resource = {
        "name": table_name,
        "path": data_filename,
        "schema": {
            "fields": filtered_fields
        }
    }
    if 'primaryKey' in model_schema:
        resource['primaryKey'] = model_schema['primaryKey']
    if 'foreignKeys' in model_schema:
        filtered_fks = []
        for fk in model_schema['foreignKeys']:
            fk_fields = fk['fields']
            if isinstance(fk_fields, list):
                if all(f in mapped_fieldnames for f in fk_fields):
                    filtered_fks.append(fk)
            elif fk_fields in mapped_fieldnames:
                filtered_fks.append(fk)
        if filtered_fks:
            resource['foreignKeys'] = filtered_fks
    return resource

def create_datapackage(folder_path, package_name):
    resources = []
    for filename in os.listdir(folder_path):
        if not (filename.endswith(".csv") or filename.endswith(".tsv")):
            continue

        delimiter = '\t' if filename.endswith(".tsv") else ','
        table_name = os.path.splitext(filename)[0]
        file_path = os.path.join(folder_path, filename)

        print(f"Processing {filename}...")
        populated_fields = get_populated_fields(file_path, delimiter)
        if not populated_fields:
            print(f"  Skipping {filename} (no populated fields).")
            continue
        model_schema = fetch_model_schema(table_name)
        if not model_schema:
            print(f"  Skipping {filename} (no schema found).")
            continue
        resource = generate_resource_descriptor(table_name, filename, model_schema, populated_fields)
        resources.append(resource)

    datapackage = {
        "profile": "tabular-data-package",
        "name": package_name,
        "resources": resources
    }

    with open(os.path.join(folder_path, "datapackage.json"), "w", encoding="utf-8") as f:
        json.dump(datapackage, f, indent=2, ensure_ascii=False)

    print(f"Darwin Core Data Package created at: {os.path.join(folder_path, 'datapackage.json')}")
    print(f"Included {len(resources)} resources.")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py /path/to/folder package_name")
        sys.exit(1)
    folder_path = sys.argv[1]
    package_name = sys.argv[2]
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a directory.")
        sys.exit(1)
    create_datapackage(folder_path, package_name)

if __name__ == "__main__":
    main()
