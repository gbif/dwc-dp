#!/usr/bin/env python3
#
# Data packages validation checks (executed in Jenkins).
# In the case of a PR is supposed to be run manually.
# Checks are:
# 1. Index and table schema files are valid JSON
# 2. All URLs are resolvable; if a URL returns 4xx, a local file at the
#    path-component of the URL is checked as a fallback (supports new
#    declarations not yet published)
# 3. Table schema declarations are complete and consistent:
#    - Required keys present and unique in index.json
#    - Declared files present on disk; extra files warned
#    - url, identifier, name, and title agree between index.json and each schema file
# 4. Each schema descriptor is valid per the Frictionless specification
# 5. Each field carries required metadata (description, type)
# 6. Foreign key referential integrity:
#    - Source fields exist in the declaring schema
#    - Target schemas exist (empty resource = self-reference)
#    - Target fields exist in the referenced schema
#    - Target fields are the primary key of the referenced schema

import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests
from frictionless import Schema

# ---------------------------------------------------------------------------
# Paths to scan
# ---------------------------------------------------------------------------

DIRECTORIES_TO_SCAN_SANDBOX = ['../../rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1']
DIRECTORIES_TO_SCAN_PROD    = ['data-packages']

# Field-level properties that must be present on every field in every schema
REQUIRED_FIELD_PROPERTIES = ['description', 'type']

# Properties that must match between an index.json tableSchemas entry and
# the corresponding table schema file
CROSS_CHECK_PROPERTIES = ['url', 'identifier', 'name', 'title']


# ---------------------------------------------------------------------------
# Validation result collector
# ---------------------------------------------------------------------------

class ValidationResult:
    """Accumulates errors and warnings across all validation passes."""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

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

def check_urls_are_resolvable(package_data: dict, result: ValidationResult) -> None:
    """
    Recursively find every 'url' value in the package data and verify it is
    reachable via HTTP HEAD.

    If a URL returns a 4xx response, the URL's path component is checked as a
    local file path. This supports new declarations that have been committed
    locally but not yet published to the remote server.

    Non-HTTP errors (network failures, timeouts) are always reported as errors.
    """

    def resolve_url(url: str) -> None:
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                # Fallback: check whether the URL's path exists as a local file.
                # This handles any domain, not just rs.gbif.org.
                local_path = urlparse(url).path.lstrip('/')
                if not os.path.exists(local_path):
                    result.error(f"Unreachable URL and no local file found: {url} "
                                 f"(checked local path: {local_path!r})")
        except requests.RequestException as exc:
            result.error(f"Network error resolving URL {url}: {exc}")

    def find_and_resolve_urls(data) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'url' and isinstance(value, str):
                    resolve_url(value)
                elif isinstance(value, (dict, list)):
                    find_and_resolve_urls(value)
        elif isinstance(data, list):
            for item in data:
                find_and_resolve_urls(item)

    find_and_resolve_urls(package_data)


def check_index_json(
    package_file: Path,
    package_data: dict,
    result: ValidationResult,
) -> list[str]:
    """
    Verify tableSchemas entries in index.json for:
      - Presence of required keys (identifier, name, title, url)
      - Warning on missing description
      - Uniqueness of identifier, name, title, and url
      - Consistency between declared urls and files present on disk

    Returns the list of declared schema basenames for use by later passes.
    """
    print(f"Checking index: {package_file}")

    table_schemas_path = schemas_dir(package_file)
    if not table_schemas_path.exists():
        result.error(f"Table schemas directory missing: {table_schemas_path}")
        return []

    declared_basenames: list[str] = []
    seen: dict[str, set] = {
        'identifier': set(),
        'name': set(),
        'title': set(),
        'url': set(),
    }

    for entry in package_data.get('tableSchemas', []):
        # Required unique keys
        for key in ('identifier', 'name', 'title'):
            value = entry.get(key)
            if value is None:
                result.error(f"Missing '{key}' in tableSchemas entry: {entry}")
            elif value in seen[key]:
                result.error(f"Duplicate '{key}' value '{value}' in tableSchemas")
            else:
                seen[key].add(value)

        # description: optional, warn if absent (not checked for uniqueness)
        if 'description' not in entry:
            result.warning(f"Missing 'description' in tableSchemas entry for "
                           f"'{entry.get('name', '<unknown>')}'")

        # url: required and unique
        url = entry.get('url')
        if url is None:
            result.error(f"Missing 'url' in tableSchemas entry: {entry}")
        elif url in seen['url']:
            result.error(f"Duplicate 'url' value '{url}' in tableSchemas")
        else:
            seen['url'].add(url)
            declared_basenames.append(Path(url).name)

    actual_basenames = {f.name for f in table_schemas_path.glob('*.json')}
    declared_set = set(declared_basenames)

    for missing in sorted(declared_set - actual_basenames):
        result.error(f"Declared schema file not found on disk: {missing}")
    for extra in sorted(actual_basenames - declared_set):
        result.warning(f"Schema file on disk not declared in index.json: {extra}")

    return declared_basenames


def check_schema_json(
    package_file: Path,
    package_data: dict,
    declared_basenames: list[str],
    result: ValidationResult,
) -> dict[str, dict]:
    """
    For each declared schema file:
      - Verify it is valid JSON
      - Cross-check url, identifier, name, and title against the index.json entry
      - Verify each field carries the required metadata properties

    Returns a dict mapping schema name → parsed schema dict for valid files,
    so later passes can reuse the already-loaded data without re-reading files.
    """
    # Build a lookup from basename → index.json entry for cross-checking
    index_entries: dict[str, dict] = {
        Path(entry['url']).stem: entry
        for entry in package_data.get('tableSchemas', [])
        if 'url' in entry
    }

    loaded: dict[str, dict] = {}

    for basename in declared_basenames:
        file_path = schemas_dir(package_file) / basename
        data = load_json(file_path, result)
        if data is None:
            # load_json already recorded the error; skip further checks
            continue

        schema_name = file_path.stem
        loaded[schema_name] = data

        # Cross-check properties between index.json entry and schema file
        index_entry = index_entries.get(schema_name)
        if index_entry is None:
            # Already reported as a missing declaration; nothing more to do
            continue

        for prop in CROSS_CHECK_PROPERTIES:
            declared_val = index_entry.get(prop)
            actual_val = data.get(prop)
            if declared_val != actual_val:
                result.error(
                    f"'{prop}' mismatch for schema '{schema_name}': "
                    f"index.json has {declared_val!r}, "
                    f"schema file has {actual_val!r}"
                )

        # Field-level metadata
        for field in data.get('fields', []):
            field_name = field.get('name', '<unnamed>')
            for prop in REQUIRED_FIELD_PROPERTIES:
                if prop not in field:
                    result.error(
                        f"Field '{field_name}' in '{basename}' "
                        f"is missing required property '{prop}'"
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
    loaded_schemas: dict[str, dict],
    result: ValidationResult,
) -> None:
    """
    For every foreignKey in every table schema, verify:
      - All source fields exist in the declaring schema
      - The target schema exists (empty/missing resource = self-reference)
      - All target fields exist in the referenced schema
      - The target field is the primary key of the referenced schema

    Supports composite keys (fields as a list) and self-referential FKs.
    Self-referential FKs additionally require the declaring schema to have
    a primaryKey defined.
    """

    def as_list(value) -> list:
        if isinstance(value, list):
            return value
        return [value] if value is not None else []

    for schema_name, schema_data in loaded_schemas.items():
        source_field_names = {
            fld.get('name')
            for fld in schema_data.get('fields', [])
            if isinstance(fld, dict) and 'name' in fld
        }

        for fk in schema_data.get('foreignKeys', []):
            fk_fields = as_list(fk.get('fields'))
            ref = fk.get('reference') or {}
            tgt_resource = (ref.get('resource') or '').strip() or None
            tgt_fields = as_list(ref.get('fields'))

            # Check all source fields exist
            missing_src = [f for f in fk_fields if f not in source_field_names]
            if missing_src:
                result.error(
                    f"Foreign key in '{schema_name}' references non-existent "
                    f"source field(s): {missing_src}"
                )
                continue

            # Self-referential FK (resource is empty/missing)
            if tgt_resource is None:
                pk = as_list(schema_data.get('primaryKey'))
                if not pk:
                    result.error(
                        f"Self-referential FK in '{schema_name}' "
                        f"requires a primaryKey in the same schema"
                    )
                elif set(tgt_fields) != set(pk):
                    result.error(
                        f"Self-referential FK in '{schema_name}' must reference "
                        f"the primaryKey {pk}, but references {tgt_fields}"
                    )
                continue

            # FK referencing another schema
            if tgt_resource not in loaded_schemas:
                result.error(
                    f"Foreign key {schema_name}/{fk_fields} references "
                    f"non-existent target schema '{tgt_resource}'"
                )
                continue

            ref_schema = loaded_schemas[tgt_resource]
            ref_field_names = {
                fld.get('name')
                for fld in ref_schema.get('fields', [])
                if isinstance(fld, dict) and 'name' in fld
            }

            missing_tgt = [f for f in tgt_fields if f not in ref_field_names]
            if missing_tgt:
                result.error(
                    f"Foreign key {schema_name}/{fk_fields} references "
                    f"non-existent field(s) in '{tgt_resource}': {missing_tgt}"
                )
                continue

            # Verify target fields are the primary key of the referenced schema
            tgt_pk = as_list(ref_schema.get('primaryKey'))
            if tgt_pk and set(tgt_fields) != set(tgt_pk):
                result.error(
                    f"Foreign key {schema_name}/{fk_fields} targets "
                    f"'{tgt_resource}/{tgt_fields}' which is not the primary key "
                    f"(primaryKey={tgt_pk})"
                )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def validate_package(package_file: Path, result: ValidationResult) -> None:
    """Run all validation passes for a single index.json package file."""
    package_data = load_json(package_file, result)
    if package_data is None:
        return

    # Pass 1: URL reachability
    check_urls_are_resolvable(package_data, result)

    # Pass 2: index.json structure and file/declaration consistency
    declared_basenames = check_index_json(package_file, package_data, result)
    if not declared_basenames:
        return

    # Pass 3: individual schema JSON validity, cross-checks, and field metadata
    loaded_schemas = check_schema_json(
        package_file, package_data, declared_basenames, result
    )

    # Pass 4: Frictionless descriptor validation (uses already-loaded dicts)
    check_frictionless(loaded_schemas, result)

    # Pass 5: foreign key referential integrity
    check_foreign_keys(loaded_schemas, result)


def main() -> None:
    result = ValidationResult()

    all_package_files = (
        find_package_files(DIRECTORIES_TO_SCAN_SANDBOX)
        + find_package_files(DIRECTORIES_TO_SCAN_PROD)
    )

    if not all_package_files:
        print(f"No index.json files found under: "
              f"{DIRECTORIES_TO_SCAN_SANDBOX + DIRECTORIES_TO_SCAN_PROD}")
        sys.exit(1)

    for package_file in sorted(all_package_files):
        validate_package(package_file, result)

    print()
    if result.has_errors:
        print(f"Validation failed: {len(result.errors)} error(s), "
              f"{len(result.warnings)} warning(s).")
        sys.exit(1)

    warning_note = f" ({len(result.warnings)} warning(s))" if result.warnings else ""
    print(f"All validations passed{warning_note}.")
    sys.exit(0)


if __name__ == '__main__':
    main()
