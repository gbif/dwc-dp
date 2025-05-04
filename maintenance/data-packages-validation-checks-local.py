#!/usr/bin/env python3
#
# Script to validate the data package locally to the extent possible - no calls to 
# non-local resources 

import json
import os
import sys
from pathlib import Path

# Paths to scan
directories_to_scan = ['.']

error_found = False

def check_valid_json(file_path):
    global error_found
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Error: Invalid JSON or missing file: {file_path}")
        error_found = True
        return False

def check_table_schemas(package_file_path, package_data):
    global error_found
    print(f"Checking: {package_file_path}")

    package_dir = os.path.dirname(package_file_path)
    table_schemas_dir = os.path.join(package_dir, 'table-schemas')

    if not os.path.exists(table_schemas_dir):
        print(f"Error: Table schemas directory missing: {table_schemas_dir}")
        error_found = True
        return

    declared_schemas = []
    schema_keys = {'identifier': set(), 'name': set(), 'title': set()}

    if "tableSchemas" in package_data:
        for schema in package_data['tableSchemas']:
            for key in ['identifier', 'name', 'title']:
                if key in schema:
                    if schema[key] in schema_keys[key]:
                        print(f"Error: Duplicate '{key}' in table schema: {schema}")
                        error_found = True
                    else:
                        schema_keys[key].add(schema[key])
                else:
                    print(f"Error: Missing '{key}' in table schema: {schema}")
                    error_found = True

            if 'url' in schema:
                schema_file = os.path.basename(schema['url'])
                declared_schemas.append(schema_file)
            else:
                print(f"Error: Missing 'url' in table schema: {schema}")
                error_found = True

    actual_schemas = [f for f in os.listdir(table_schemas_dir) if f.endswith('.json')]

    missing_files = [s for s in declared_schemas if s not in actual_schemas]
    extra_files = [s for s in actual_schemas if s not in declared_schemas]

    if missing_files:
        print(f"Error: Missing table schema files: {missing_files}")
        error_found = True
    if extra_files:
        print(f"Warning: Extra table schema files: {extra_files}")

    for schema_file in actual_schemas:
        schema_file_path = os.path.join(table_schemas_dir, schema_file)
        if not check_valid_json(schema_file_path):
            print(f"Error: Invalid table schema JSON: {schema_file_path}")


def check_foreign_keys(package_file, package_data):
    global error_found

    if "tableSchemas" not in package_data:
        return

    for schema in package_data['tableSchemas']:
        table_schema_file = package_file.replace("index.json", f"table-schemas/{schema['name']}.json")

        try:
            with open(table_schema_file, 'r') as f:
                table_schema_json = json.load(f)

            if "foreignKeys" in table_schema_json:
                for fk in table_schema_json['foreignKeys']:
                    fk_field = fk['fields']
                    fk_ref_resource = fk['reference']['resource']
                    fk_ref_field = fk['reference']['fields']

                    if not any(f['name'] == fk_field for f in table_schema_json['fields']):
                        print(f"Error: Field '{fk_field}' missing in {table_schema_file}")
                        error_found = True

                    ref_schema_file = package_file.replace(
                        "index.json", f"table-schemas/{fk_ref_resource}.json"
                    )

                    if Path(ref_schema_file).exists():
                        with open(ref_schema_file, 'r') as rf:
                            ref_schema_json = json.load(rf)
                        if not any(f['name'] == fk_ref_field for f in ref_schema_json['fields']):
                            print(f"Error: Foreign key {schema['name']}/{fk_field} references non-existing field {fk_ref_resource}/{fk_ref_field}")
                            error_found = True
                    else:
                        print(f"Error: Foreign key {schema['name']}/{fk_field} references non-existing table schema {fk_ref_resource}")
                        error_found = True

        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Error: Problem reading {table_schema_file}")
            error_found = True

def find_package_files(directories):
    package_files = []
    for base_dir in directories:
        for root, _, files in os.walk(base_dir):
            if 'index.json' in files:
                package_files.append(os.path.join(root, 'index.json'))
    return package_files

# Run validation
package_files = find_package_files(directories_to_scan)

for pkg_file in package_files:
    if not check_valid_json(pkg_file):
        continue
    with open(pkg_file, 'r') as f:
        pkg_data = json.load(f)

    check_table_schemas(pkg_file, pkg_data)
    check_foreign_keys(pkg_file, pkg_data)

if error_found:
    print("Validation failed.")
    sys.exit(1)

print("All validations passed.")
sys.exit(0)
