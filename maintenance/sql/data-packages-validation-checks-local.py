#!/usr/bin/env python3
#
# Script to validate the table schemas locally to the extent possible - no calls to
# non-local resources
#
# find all local data package index.json files under ../dwc-dp
# verify package JSON validity
# verify tableSchemas metadata completeness and uniqueness
# compare declared schema files with actual files in table-schemas
# verify each schema file is valid JSON
# verify each schema descriptor is acceptable to Frictionless
# verify each field has required metadata (description, type)
# verify foreign-key source fields, target tables, and target fields all exist
# verify foreign-key target fields are the primary key of the referenced table
# return a failing process exit code if any structural or referential errors were found

import json
import os
import sys
from pathlib import Path
from frictionless import Schema

# Paths to scan
DIRECTORIES_TO_SCAN = ['../dwc-dp']

# Field-level properties that must be present on every field in every schema
REQUIRED_FIELD_PROPERTIES = ['description', 'type']


# ---------------------------------------------------------------------------
# Validation result collector
# ---------------------------------------------------------------------------

class ValidationResult:
    """Accumulates errors and warnings across all validation passes."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg: str) -> None:
        print(f"Error: {msg}")
        self.errors.append(msg)

    def warning(self, msg: str) -> None:
        print(f"Warning: {msg}")
        self.warnings.append(msg)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_json(file_path: Path, result: ValidationResult) -> dict | None:
    """
    Load and return parsed JSON from *file_path*.
    Records an error and returns None on parse failure or missing file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        result.error(f"File not found: {file_path}")
    except json.JSONDecodeError as exc:
        result.error(f"Invalid JSON in {file_path}: {exc}")
    return None


def schemas_dir(package_file: Path) -> Path:
    """Return the table-schemas directory for a given index.json path."""
    return package_file.parent / 'table-schemas'


def schema_path(package_file: Path, schema_name: str) -> Path:
    """Return the expected path for a named table schema file."""
    return schemas_dir(package_file) / f'{schema_name}.json'


def find_package_files(directories: list[str]) -> list[Path]:
    """Recursively find all index.json package files under each directory."""
    package_files = []
    for base_dir in directories:
        for root, _, files in os.walk(base_dir):
            if 'index.json' in files:
                package_files.append(Path(root) / 'index.json')
    return package_files


# ---------------------------------------------------------------------------
# Validation passes
# ---------------------------------------------------------------------------

def check_index_json(package_file: Path, package_data: dict, result: ValidationResult) -> list[str]:
    """
    Verify tableSchemas entries in index.json for:
      - Presence of required keys (identifier, name, title, url)
      - Uniqueness of identifier, name, and title across all entries
      - Consistency between declared urls and files present on disk

    Returns the list of declared schema basenames for use by later passes.
    """
    print(f"Checking index: {package_file}")

    table_schemas_path = schemas_dir(package_file)
    if not table_schemas_path.exists():
        result.error(f"Table schemas directory missing: {table_schemas_path}")
        return []

    declared_basenames: list[str] = []
    seen: dict[str, set] = {'identifier': set(), 'name': set(), 'title': set()}

    for entry in package_data.get('tableSchemas', []):
        for key in ('identifier', 'name', 'title'):
            value = entry.get(key)
            if value is None:
                result.error(f"Missing '{key}' in tableSchemas entry: {entry}")
            elif value in seen[key]:
                result.error(f"Duplicate '{key}' value '{value}' in tableSchemas")
            else:
                seen[key].add(value)

        url = entry.get('url')
        if url is None:
            result.error(f"Missing 'url' in tableSchemas entry: {entry}")
        else:
            declared_basenames.append(Path(url).name)

    actual_basenames = {f.name for f in table_schemas_path.glob('*.json')}
    declared_set = set(declared_basenames)

    for missing in sorted(declared_set - actual_basenames):
        result.error(f"Declared schema file not found on disk: {missing}")
    for extra in sorted(actual_basenames - declared_set):
        result.warning(f"Schema file on disk not declared in index.json: {extra}")

    return declared_basenames


def check_schema_json(package_file: Path, schema_basenames: list[str], result: ValidationResult) -> dict[str, dict]:
    """
    For each declared schema file:
      - Verify it is valid JSON
      - Verify each field carries the required metadata properties (description, type)

    Returns a dict mapping schema name → parsed schema dict for valid files,
    so later passes can reuse the already-loaded data.
    """
    loaded: dict[str, dict] = {}

    for basename in schema_basenames:
        file_path = schemas_dir(package_file) / basename
        data = load_json(file_path, result)
        if data is None:
            # load_json already recorded the error; skip further checks on this file
            continue

        schema_name = file_path.stem
        loaded[schema_name] = data

        # Field-level metadata
        for field in data.get('fields', []):
            field_name = field.get('name', '<unnamed>')
            for prop in REQUIRED_FIELD_PROPERTIES:
                if prop not in field:
                    result.error(
                        f"Field '{field_name}' in {basename} is missing required property '{prop}'"
                    )

    return loaded


def check_frictionless(loaded_schemas: dict[str, dict], result: ValidationResult) -> None:
    """
    Validate each schema descriptor against the Frictionless specification.
    Reports a summary count on success.
    """
    valid_count = 0
    for name, descriptor in loaded_schemas.items():
        try:
            Schema.from_descriptor(descriptor)
            valid_count += 1
        except Exception as exc:
            result.error(f"Frictionless validation failed for '{name}': {exc}")

    print(f"  Frictionless: {valid_count}/{len(loaded_schemas)} schemas valid")


def check_foreign_keys(
    package_file: Path,
    loaded_schemas: dict[str, dict],
    result: ValidationResult,
) -> None:
    """
    For every foreignKey in every table schema, verify:
      - The source field exists in the declaring schema
      - The target schema exists (empty/missing resource = self-reference)
      - The target field exists in the referenced schema
      - The target field is the primary key of the referenced schema

    Tolerates `fields` being either a bare string or a one-element list.
    """

    def resolve_field(value) -> str | None:
        """Normalise a fields value that may be a string or a list."""
        if isinstance(value, list):
            return value[0] if value else None
        return value or None

    for schema_name, schema_data in loaded_schemas.items():
        source_fields = {f.get('name') for f in schema_data.get('fields', [])}

        for fk in schema_data.get('foreignKeys', []):
            src_field = resolve_field(fk.get('fields'))

            if not src_field or src_field not in source_fields:
                result.error(
                    f"Foreign key in '{schema_name}' references non-existent "
                    f"source field '{src_field}'"
                )
                continue

            ref = fk.get('reference') or {}
            tgt_field = resolve_field(ref.get('fields'))
            tgt_resource = ref.get('resource', '').strip() or schema_name  # empty = self

            if tgt_resource not in loaded_schemas:
                result.error(
                    f"Foreign key {schema_name}/{src_field} references "
                    f"non-existent target schema '{tgt_resource}'"
                )
                continue

            ref_schema = loaded_schemas[tgt_resource]
            target_field_names = {f.get('name') for f in ref_schema.get('fields', [])}

            if not tgt_field or tgt_field not in target_field_names:
                result.error(
                    f"Foreign key {schema_name}/{src_field} references "
                    f"non-existent target field '{tgt_resource}/{tgt_field}'"
                )
                continue

            # Verify the target field is the primary key of the referenced schema
            tgt_primary_key = ref_schema.get('primaryKey')
            if tgt_primary_key is not None and tgt_field != tgt_primary_key:
                result.error(
                    f"Foreign key {schema_name}/{src_field} targets "
                    f"'{tgt_resource}/{tgt_field}' which is not the primary key "
                    f"(primaryKey='{tgt_primary_key}')"
                )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def validate_package(package_file: Path, result: ValidationResult) -> None:
    """Run all validation passes for a single index.json package file."""
    package_data = load_json(package_file, result)
    if package_data is None:
        return

    # Pass 1: index.json structure and file/declaration consistency
    declared_basenames = check_index_json(package_file, package_data, result)
    if not declared_basenames:
        return

    # Pass 2: individual schema JSON validity and required field metadata
    # Only declared schemas are validated; extra files on disk are already warned about.
    loaded_schemas = check_schema_json(package_file, declared_basenames, result)

    # Pass 3: Frictionless descriptor validation (uses already-loaded dicts)
    check_frictionless(loaded_schemas, result)

    # Pass 4: foreign key referential integrity + PK alignment
    check_foreign_keys(package_file, loaded_schemas, result)


def main() -> None:
    result = ValidationResult()

    package_files = find_package_files(DIRECTORIES_TO_SCAN)
    if not package_files:
        print(f"No index.json files found under: {DIRECTORIES_TO_SCAN}")
        sys.exit(1)

    for package_file in sorted(package_files):
        validate_package(package_file, result)

    print()
    if result.has_errors:
        print(f"Validation failed: {len(result.errors)} error(s), {len(result.warnings)} warning(s).")
        sys.exit(1)

    warning_note = f" ({len(result.warnings)} warning(s))" if result.warnings else ""
    print(f"All validations passed{warning_note}.")
    sys.exit(0)


if __name__ == '__main__':
    main()
