#!/usr/bin/env python3
#
# Script to validate the data package locally to the extent possible - no calls to 
# non-local resources 

import json
import os
import sys
from pathlib import Path
from frictionless import Schema

# Paths to scan
directories_to_scan = ['../dwc-dp']

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
    """
    Validate that all foreignKeys declared in each table schema:
      - Reference an existing source field in the current table schema
      - Point to an existing target table schema (including self-reference when `resource` is empty/missing)
      - Reference an existing target field in the referenced schema
    The function is tolerant of:
      - `fields` being a string or a one-element list
      - missing/empty `reference.resource` (interpreted as self-reference)
    """
    global error_found

    # Optional: skip known sandbox aggregate indexes if desired
    if package_file in ('sandbox/data-packages/index.json', 'data-packages/index.json'):
        return

    table_schemas = package_data.get('tableSchemas') or []
    if not table_schemas:
        return

    for schema in table_schemas:
        table_schema_name = schema.get('name')
        table_schema_file = package_file.replace('index.json', f'table-schemas/{table_schema_name}.json')

        try:
            with open(table_schema_file, 'r', encoding='utf-8') as f:
                table_schema_json = json.load(f)
        except Exception as e:
            print(f"Error: Problem reading {table_schema_file}: {e}")
            error_found = True
            continue

        # Build a quick set of source field names for existence checks
        source_fields = { (fld.get('name')) for fld in (table_schema_json.get('fields') or []) }

        for fk in (table_schema_json.get('foreignKeys') or []):
            # Source field (string or [string])
            src_field = fk.get('fields')
            if isinstance(src_field, list):
                src_field = src_field[0] if src_field else None

            if not src_field or src_field not in source_fields:
                print(f"Error: Field '{src_field}' missing in {table_schema_name} (schema file {os.path.basename(table_schema_file)})")
                error_found = True
                # Can't validate further without a valid source field
                continue

            ref = fk.get('reference') or {}
            # Target field (string or [string])
            tgt_field = ref.get('fields')
            if isinstance(tgt_field, list):
                tgt_field = tgt_field[0] if tgt_field else None

            # Target resource (self if empty/missing)
            tgt_resource = ref.get('resource')
            if not tgt_resource or (isinstance(tgt_resource, str) and not tgt_resource.strip()):
                tgt_resource = table_schema_name  # interpret as self-reference

            # Open referenced schema
            ref_schema_file = package_file.replace('index.json', f'table-schemas/{tgt_resource}.json')
            if not os.path.exists(ref_schema_file):
                print(f"Error: Foreign key {table_schema_name}/{src_field} references non-existing table schema {tgt_resource}")
                error_found = True
                continue

            try:
                with open(ref_schema_file, 'r', encoding='utf-8') as rf:
                    ref_schema_json = json.load(rf)
            except Exception as e:
                print(f"Error: Problem reading referenced schema {ref_schema_file}: {e}")
                error_found = True
                continue

            target_fields = { (fld.get('name')) for fld in (ref_schema_json.get('fields') or []) }
            if not tgt_field or tgt_field not in target_fields:
                print(f"Error: Foreign key {table_schema_name}/{src_field} references non-existing field {tgt_resource}/{tgt_field}")
                error_found = True

def check_valid_frictionless(index_file_str):
    table_schema_files = find_package_table_schemas(index_file_str)

    for file in table_schema_files:
        try:
            Schema.from_descriptor(file)
            # print(f"{file}: Valid frictionless")
        except Exception as e:
            print(f"{file}: Error - {str(e)}")


def find_package_table_schemas(index_file_str):
    index_path_parent = Path(index_file_str).parent
    table_schemas_dir = index_path_parent / 'table-schemas'
    table_schemas = [tsf for tsf in table_schemas_dir.rglob('*.json') if tsf.is_file()]

    return table_schemas

def find_package_files(directories):
    package_files = []
    for base_dir in directories:
        for root, _, files in os.walk(base_dir):
            if 'index.json' in files:
                package_files.append(os.path.join(root, 'index.json'))
    return package_files

# Run validation
package_files = find_package_files(directories_to_scan)

for package_file in package_files:
    if not check_valid_json(package_file):
        continue
    with open(package_file, 'r') as f:
        package_data = json.load(f)

    check_table_schemas(package_file, package_data)
    check_valid_frictionless(package_file)
    check_foreign_keys(package_file, package_data)

if error_found:
    print("Validation failed.")
    sys.exit(1)

print("All validations passed.")
sys.exit(0)
