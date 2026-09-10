#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate and validate Darwin Core Data Package artifacts.

Stage 1) Read the CSV files in ../vocabulary and generate:
  ../dwc-dp/dwc-dp-profile.json
  ../dwc-dp/table-schemas/*.json

Stage 2) Validate the generated table schemas locally:
  - JSON validity and required field metadata
  - Frictionless Table Schema validity
  - DwC-DP profile constraints
  - foreign-key source/target integrity and primary-key alignment

Stage 3) Render:
  ../qrg/index.html (DwC-DP Quick Reference Guide)

Stage 4) Generate:
  ../sql/dwc-dp.sql (PostgreSQL DDL)

Validation is performed before QRG and SQL generation.  Validation errors cause a
non-zero exit and prevent the QRG from being rendered.

Usage:
  python process_dwcdp.py <version>

Example:
  python process_dwcdp.py http://rs.tdwg.org/dwc-dp/1.0_DEV
"""

import os
import argparse
from typing import Any
from dataclasses import dataclass, field
from urllib.request import Request, urlopen
from urllib.error import URLError
import sys
import re
import io
import hashlib
import copy
import json
import csv
from pathlib import Path
from collections import defaultdict
from frictionless import Schema
from jsonschema import Draft4Validator, FormatChecker
from referencing import Registry
from referencing.jsonschema import DRAFT4


try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Expected headers for each source CSV.  Order is NOT enforced; presence is.
EXPECTED_HEADERS = {
    "dwc-dp-tables.csv": {
        "name", "title", "description", "notes", "example", "namespace",
        "dcterms:isVersionOf", "dcterms:references", "rdfs:comment", "status",
    },
    "dwc-dp-fields.csv": {
        "table", "name", "key", "predicate", "related_table", "related_field",
        "title", "description", "notes", "example", "type", "format",
        "unique", "required", "minimum", "maximum", "namespace",
        "dcterms:isVersionOf", "dcterms:references", "rdfs:comment", "status",
    },
}

# Columns that carry genuine boolean semantics; "no" / "yes" are coerced only here.
BOOLEAN_COLUMNS = {"required", "unique"}


# Field-level properties explicitly checked on every generated field.
# Additional DwC-DP field requirements are enforced by profile validation.
REQUIRED_FIELD_PROPERTIES = ("description", "type")

# The DwC-DP profile references this remote Frictionless Data Package schema.
# To keep processing fully local, that external reference is resolved to an
# empty schema during the DwC-DP-specific profile pass.  Base Frictionless
# Table Schema validity is checked independently with frictionless.Schema.
FRICTIONLESS_DATA_PACKAGE_SCHEMA_URI = (
    "https://specs.frictionlessdata.io/schemas/data-package.json"
)

# ---------------------------------------------------------------------------
# Profile generation constants
# ---------------------------------------------------------------------------

# Name of the profile template, which lives alongside this script.
PROFILE_TEMPLATE_FILENAME = "dwc-dp-profile_template.json"

# Name of the generated profile, written in ../dwc-dp/.
PROFILE_OUTPUT_FILENAME = "dwc-dp-profile.json"

# Location, within the profile template, of the enum listing the resource names
# that belong to a version.  Every key except the last must resolve to an object.
PROFILE_ENUM_PATH = ("$defs", "dwc-dp-resource-names", "enum")

# The template must carry exactly this one-item enum at PROFILE_ENUM_PATH.  The
# placeholder is replaced with the recommended table names for the version.
PROFILE_ENUM_PLACEHOLDER = "{{DWC_DP_RESOURCE_NAMES}}"

# Location, within the profile template, of the version string.  Every key
# except the last must resolve to an object.
PROFILE_VERSION_PATH = ("version",)

# The template must carry exactly this string at PROFILE_VERSION_PATH.  The
# placeholder is replaced with the version given on the command line.
PROFILE_VERSION_PLACEHOLDER = "{{DWC_DP_VERSION}}"

# Ordered display groups for the QRG.  Every recommended table name must appear
# exactly once; validate_ordered_groups() enforces this at runtime.
ORDERED_GROUPS = [
    ['event', 'chronometric-age', 'geological-context', 'occurrence', 'organism',
     'organism-interaction'],
    ['survey', 'survey-survey-target', 'survey-target', 'survey-target-descriptor'],
    ['identification', 'identification-taxon'],
    ['material', 'geological-material', 'material-geological-context'],
    ['nucleotide-analysis', 'molecular-protocol', 'nucleotide-sequence'],
    ['agent', 'agent-agent-role', 'chronometric-age-agent-role', 'event-agent-role',
     'identification-agent-role', 'material-agent-role', 'media-agent-role',
     'molecular-protocol-agent-role', 'occurrence-agent-role',
     'organism-interaction-agent-role', 'survey-agent-role'],
    ['media', 'agent-media', 'chronometric-age-media', 'event-media',
     'geological-context-media', 'material-media', 'occurrence-media',
     'organism-interaction-media'],
    ['protocol', 'chronometric-age-protocol', 'event-protocol', 'material-protocol',
     'occurrence-protocol', 'survey-protocol'],
    ['bibliographic-resource', 'chronometric-age-reference', 'event-reference',
     'identification-reference', 'material-reference', 'molecular-protocol-reference',
     'occurrence-reference', 'organism-reference', 'organism-interaction-reference',
     'protocol-reference', 'survey-reference'],
    ['chronometric-age-assertion', 'event-assertion', 'material-assertion',
     'media-assertion', 'molecular-protocol-assertion', 'nucleotide-analysis-assertion',
     'occurrence-assertion', 'organism-assertion', 'organism-interaction-assertion',
     'survey-assertion'],
    ['agent-identifier', 'event-identifier', 'material-identifier', 'media-identifier',
     'occurrence-identifier', 'organism-identifier', 'survey-identifier'],
    ['provenance', 'event-provenance', 'material-provenance', 'media-provenance'],
    ['usage-policy', 'event-usage-policy', 'material-usage-policy', 'media-usage-policy'],
    ['organism-relationship', 'resource-relationship'],
]

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def repo_root_from_script() -> Path:
    """Return the repository root, assuming this script lives one level below it."""
    return Path(__file__).resolve().parent.parent


def _derive_paths(version: str):
    """Return all paths used by DwC-DP generation, validation, QRG, and SQL output."""
    root = repo_root_from_script()
    script_dir = Path(__file__).resolve().parent

    table_schemas_dir = root / "dwc-dp" / "table-schemas"
    output_html_path = root / "qrg" / "index.html"
    profile_json_path = root / "dwc-dp" / PROFILE_OUTPUT_FILENAME

    # Templates and SQL configuration live alongside this script.
    template_path = script_dir / "qrg_template.html"
    profile_template_path = script_dir / PROFILE_TEMPLATE_FILENAME
    sql_config_path = script_dir / SQL_CONFIG_FILENAME

    # SQL output is always written under ../sql relative to this script.
    sql_output_path = root / "sql" / SQL_OUTPUT_FILENAME

    return (
        table_schemas_dir,
        output_html_path,
        template_path,
        profile_json_path,
        profile_template_path,
        sql_config_path,
        sql_output_path,
    )

# ---------------------------------------------------------------------------
# CSV scalar parsing
# ---------------------------------------------------------------------------

def _parse_scalar(s, *, column_name: str = ""):
    """Coerce a CSV cell to a proper JSON scalar.

    Boolean coercion (true/yes -> True, false/no -> False) is applied ONLY to
    columns listed in BOOLEAN_COLUMNS.  All other columns receive numeric
    coercion or are returned as plain strings.
    """
    if s is None:
        return None
    t = str(s).strip()
    if t == "":
        return None

    low = t.lower()

    # Boolean coercion: only for explicitly boolean-typed columns.
    if column_name in BOOLEAN_COLUMNS:
        if low in ("true", "yes", "1"):
            return True
        if low in ("false", "no", "0"):
            return False

    # Numeric coercion: match integers and valid scientific-notation floats.
    try:
        # Require digits around any 'e' to avoid false matches on plain words.
        if "." in t or (
            "e" in low
            and any(c.isdigit() for c in t)
            and low.replace("e", "", 1).replace(".", "", 1).replace("-", "", 1).replace("+", "", 1).isdigit()
        ):
            return float(t)
        return int(t)
    except ValueError:
        return t


# ---------------------------------------------------------------------------
# Stage 1: generation helpers
# ---------------------------------------------------------------------------

def validate_csv_headers(vocabulary_dir: Path) -> None:
    """Check that required CSVs exist and contain all expected column names.

    Column *order* is not enforced.  Extra (unexpected) columns trigger a
    warning; missing required columns raise ValueError.
    """
    for filename, expected in EXPECTED_HEADERS.items():
        path = vocabulary_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required input not found: {path}")
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            actual = set(reader.fieldnames or [])

        missing = expected - actual
        extra = actual - expected

        if missing:
            raise ValueError(
                f"Missing required columns in {path}:\n  {sorted(missing)}"
            )
        if extra:
            print(
                f"Warning: Unexpected columns in {path.name} "
                f"(will be ignored): {sorted(extra)}"
            )


def validate_ordered_groups(recommended_table_names: set) -> None:
    """Ensure every recommended table appears in ORDERED_GROUPS exactly once.

    Raises ValueError listing any tables that are absent from ORDERED_GROUPS,
    and logs warnings for any names in ORDERED_GROUPS that are not recommended.
    """
    grouped = [name for group in ORDERED_GROUPS for name in group]

    # Check for duplicates within ORDERED_GROUPS itself.
    seen = set()
    duplicates = []
    for name in grouped:
        if name in seen:
            duplicates.append(name)
        seen.add(name)
    if duplicates:
        raise ValueError(
            f"ORDERED_GROUPS contains duplicate table names: {duplicates}"
        )

    grouped_set = set(grouped)
    missing_from_groups = recommended_table_names - grouped_set
    if missing_from_groups:
        raise ValueError(
            "The following recommended tables are not listed in ORDERED_GROUPS "
            "and would be silently omitted from the QRG.  Add them to "
            f"ORDERED_GROUPS:\n  {sorted(missing_from_groups)}"
        )

    unknown_in_groups = grouped_set - recommended_table_names
    if unknown_in_groups:
        print(
            "Warning: ORDERED_GROUPS references table names that are not recommended "
            "in dwc-dp-tables.csv (they will be skipped): "
            f"{sorted(unknown_in_groups)}"
        )


def load_recommended_tables_map(vocabulary_dir: Path) -> dict:
    """Return {table_name: row_dict} for every recommended table."""
    tables_csv = vocabulary_dir / "dwc-dp-tables.csv"
    tables = {}
    with tables_csv.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if (row.get("status", "") or "").strip().lower() != "recommended":
                continue
            name = (row.get("name", "") or "").strip()
            if name:
                tables[name] = row
    return tables


def load_recommended_fields_map(vocabulary_dir: Path) -> dict:
    """Return {table_name: [ordered field rows]} for every recommended field."""
    fields_csv = vocabulary_dir / "dwc-dp-fields.csv"
    fields_by_table = defaultdict(list)
    with fields_csv.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if (row.get("status", "") or "").strip().lower() != "recommended":
                continue
            table = (row.get("table", "") or "").strip()
            name = (row.get("name", "") or "").strip()
            if table and name:
                fields_by_table[table].append(row)
    return dict(fields_by_table)


def validate_field_relationship_metadata(
    recommended_tables: dict, recommended_fields: dict
) -> None:
    """Validate relationship metadata embedded in dwc-dp-fields.csv."""
    field_names_by_table = {
        table_name: {(row.get("name", "") or "").strip() for row in rows}
        for table_name, rows in recommended_fields.items()
    }

    errors = []
    relationship_keys = {"fk", "wfk"}

    for table_name, rows in recommended_fields.items():
        if table_name not in recommended_tables:
            errors.append(
                f"Recommended field rows exist for table '{table_name}', "
                "but that table is not recommended in dwc-dp-tables.csv"
            )
        for row in rows:
            field_name = (row.get("name", "") or "").strip()
            key_val = (row.get("key", "") or "").strip().lower()
            predicate = (row.get("predicate", "") or "").strip()
            related_table = (row.get("related_table", "") or "").strip()
            related_field = (row.get("related_field", "") or "").strip()
            row_label = f"{table_name}.{field_name}"

            if key_val in relationship_keys:
                missing = [
                    col for col, value in (
                        ("predicate", predicate),
                        ("related_table", related_table),
                        ("related_field", related_field),
                    )
                    if not value
                ]
                if missing:
                    errors.append(
                        f"Relationship field {row_label} with key='{key_val}' "
                        f"is missing required columns: {', '.join(missing)}"
                    )
                    continue
                if related_table not in recommended_tables:
                    errors.append(
                        f"Relationship field {row_label} points to unknown or "
                        f"non-recommended related_table '{related_table}'"
                    )
                    continue
                target_fields = field_names_by_table.get(related_table, set())
                if related_field not in target_fields:
                    errors.append(
                        f"Relationship field {row_label} points to missing "
                        f"related_field '{related_field}' in "
                        f"related_table '{related_table}'"
                    )
            else:
                populated = [
                    col for col, value in (
                        ("predicate", predicate),
                        ("related_table", related_table),
                        ("related_field", related_field),
                    )
                    if value
                ]
                if populated:
                    errors.append(
                        f"Non-relationship field {row_label} has relationship "
                        f"metadata populated: {', '.join(populated)}"
                    )

    if errors:
        raise ValueError(
            "Relationship metadata validation failed in dwc-dp-fields.csv\n  - "
            + "\n  - ".join(errors)
        )


def build_table_schemas(vocabulary_dir: Path, version: str) -> list:
    """Build the tableSchemas list from recommended rows in dwc-dp-tables.csv."""
    tables_csv = vocabulary_dir / "dwc-dp-tables.csv"
    table_schemas = []
    with tables_csv.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if (row.get("status", "") or "").strip().lower() != "recommended":
                continue
            name = (row.get("name", "") or "").strip()
            title = (row.get("title", "") or "").strip()
            description = (row.get("description", "") or "").strip()
            notes = (row.get("notes", "") or "").strip()
            example = (row.get("example", "") or "").strip()
            namespace = (row.get("namespace", "") or "").strip()
            iri = (row.get("dcterms:isVersionOf", "") or "").strip()
            if not iri:
                iri = f"http://example.com/term-pending/{namespace}/{name}"
            iri_version = (row.get("dcterms:references", "") or "").strip()
            rdfs_comment = (row.get("rdfs:comment", "") or "").strip()

            ts = {
                "identifier": f"{version}/{name}",
                "dcterms:isPartOf": "http://www.tdwg.org/standards/450",
                "url": f"table-schemas/{name}.json",
                "name": name,
                "title": title,
                "description": description,
                "notes": notes,
                "examples": example,
                "namespace": namespace,
                "dcterms:isVersionOf": iri,
            }
            if iri_version:
                ts["dcterms:references"] = iri_version
            if rdfs_comment:
                ts["rdfs:comment"] = rdfs_comment
            table_schemas.append(ts)
    return table_schemas


def build_fields_for_table(
    fields_by_table: dict, table_name: str
) -> tuple:
    """Return (fields, pk_names, foreign_keys, weak_foreign_keys) for one table.

    Accepts the pre-loaded fields map to avoid repeated CSV reads.
    """
    rows = fields_by_table.get(table_name, [])
    fields = []
    pk_names = []
    weak_pk_names = []
    foreign_keys = []
    weak_foreign_keys = []

    for row in rows:
        name = (row.get("name", "") or "").strip()
        title = (row.get("title", "") or "").strip()
        description = (row.get("description", "") or "").strip()
        notes = (row.get("notes", "") or "").strip()
        example = (row.get("example", "") or "").strip()
        ftype = (row.get("type", "") or "").strip()
        fmt = (row.get("format", "") or "").strip()
        namespace = (row.get("namespace", "") or "").strip()
        iri = (row.get("dcterms:isVersionOf", "") or "").strip()
        if not iri:
            iri = f"http://example.com/term-pending/{namespace}/{name}"
        iri_version = (row.get("dcterms:references", "") or "").strip()
        rdfs_comment = (row.get("rdfs:comment", "") or "").strip()

        key_val = (row.get("key", "") or "").strip().lower()
        if key_val == "pk":
            pk_names.append(name)
        elif key_val == "wpk":
            weak_pk_names.append(name)
        elif key_val in {"fk", "wfk"}:
            predicate = (row.get("predicate", "") or "").strip()
            related_table = (row.get("related_table", "") or "").strip()
            related_field = (row.get("related_field", "") or "").strip()
            resource = "" if related_table == table_name else related_table
            rel_obj = {
                "fields": name,
                "predicate": predicate,
                "reference": {
                    "resource": resource,
                    "fields": related_field,
                },
            }
            if key_val == "fk":
                foreign_keys.append(rel_obj)
            else:
                weak_foreign_keys.append(rel_obj)

        constraints_candidates = {
            "required": _parse_scalar(row.get("required"), column_name="required"),
            "unique": _parse_scalar(row.get("unique"), column_name="unique"),
            "minimum": _parse_scalar(row.get("minimum"), column_name="minimum"),
            "maximum": _parse_scalar(row.get("maximum"), column_name="maximum"),
        }
        constraints = {k: v for k, v in constraints_candidates.items() if v is not None}

        field_obj = {
            "name": name,
            "title": title,
            "description": description,
            "notes": notes,
            "examples": example,
            "type": ftype,
            "format": fmt,
            "namespace": namespace,
            "dcterms:isVersionOf": iri,
        }
        if iri_version:
            field_obj["dcterms:references"] = iri_version
        if rdfs_comment:
            field_obj["rdfs:comment"] = rdfs_comment
        if constraints:
            field_obj["constraints"] = constraints

        fields.append(field_obj)

    return fields, pk_names, weak_pk_names, foreign_keys, weak_foreign_keys


def write_table_schema_files(
    out_dir: Path, table_schemas: list, fields_by_table: dict
) -> None:
    """Write one JSON schema file per table using the pre-loaded fields map."""
    ts_dir = out_dir / "table-schemas"
    ts_dir.mkdir(parents=True, exist_ok=True)

    for ts in table_schemas:
        name = ts.get("name", "")
        fields, pk_names, weak_pk_names, foreign_keys, weak_foreign_keys = build_fields_for_table(
            fields_by_table, name
        )

        payload = dict(ts)
        payload["fields"] = fields

        if pk_names:
            payload["primaryKey"] = pk_names[0] if len(pk_names) == 1 else pk_names
        if weak_pk_names:
            payload["weakPrimaryKey"] = weak_pk_names[0] if len(weak_pk_names) == 1 else weak_pk_names
        if foreign_keys:
            payload["foreignKeys"] = foreign_keys
        if weak_foreign_keys:
            payload["weakForeignKeys"] = weak_foreign_keys

        dest = ts_dir / f"{name}.json"
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")


# ---------------------------------------------------------------------------
# Profile generation
# ---------------------------------------------------------------------------

def load_profile_template(profile_template_path: Path) -> dict:
    """Load and parse the DwC-DP profile template from disk."""
    if not profile_template_path.is_file():
        raise FileNotFoundError(
            f"Profile template not found: {profile_template_path}\n"
            f"Expected {PROFILE_TEMPLATE_FILENAME} alongside this script in the "
            "same directory as this script."
        )
    with profile_template_path.open("r", encoding="utf-8") as fh:
        try:
            template = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Profile template is not valid JSON: {profile_template_path}\n  {exc}"
            ) from exc

    if not isinstance(template, dict):
        raise ValueError(
            f"Profile template must be a JSON object: {profile_template_path}"
        )
    return template


def _locate_profile_container(profile: dict, path: tuple) -> tuple:
    """Return (container_object, final_key) for path within profile.

    Raises ValueError if the path does not resolve, so a drifted template fails
    loudly rather than producing a profile with an unfilled placeholder.
    """
    container = profile
    for depth, key in enumerate(path[:-1]):
        nxt = container.get(key) if isinstance(container, dict) else None
        if not isinstance(nxt, dict):
            traversed = "/".join(path[: depth + 1])
            raise ValueError(
                "Profile template does not contain the expected object at "
                f"'{traversed}'.  Expected path: {'/'.join(path)}"
            )
        container = nxt
    return container, path[-1]


def build_profile_payload(template: dict, recommended_table_names, version: str) -> dict:
    """Return a copy of the template with both placeholders filled in.

    The enum at PROFILE_ENUM_PATH is populated with the sorted names of the
    recommended tables, which are exactly the tables that make up the version.
    The string at PROFILE_VERSION_PATH is replaced with the version given on the
    command line, used verbatim.  Nothing else in the template is altered.
    """
    if not recommended_table_names:
        raise ValueError(
            "Cannot build the profile: no recommended tables were found in "
            "dwc-dp-tables.csv"
        )
    if not str(version or "").strip():
        raise ValueError("Cannot build the profile: version is empty")

    payload = copy.deepcopy(template)

    # Resource-name enum.
    container, enum_key = _locate_profile_container(payload, PROFILE_ENUM_PATH)
    current = container.get(enum_key)
    if current != [PROFILE_ENUM_PLACEHOLDER]:
        raise ValueError(
            f"Profile template placeholder not found at "
            f"{'/'.join(PROFILE_ENUM_PATH)}.  Expected exactly "
            f'["{PROFILE_ENUM_PLACEHOLDER}"], found: '
            f"{json.dumps(current, ensure_ascii=False)}"
        )
    container[enum_key] = sorted(recommended_table_names)

    # Version string.
    container, version_key = _locate_profile_container(payload, PROFILE_VERSION_PATH)
    current = container.get(version_key)
    if current != PROFILE_VERSION_PLACEHOLDER:
        raise ValueError(
            f"Profile template placeholder not found at "
            f"{'/'.join(PROFILE_VERSION_PATH)}.  Expected exactly "
            f'"{PROFILE_VERSION_PLACEHOLDER}", found: '
            f"{json.dumps(current, ensure_ascii=False)}"
        )
    container[version_key] = version

    return payload


def write_profile_json(
    profile_json_path: Path,
    profile_template_path: Path,
    recommended_table_names,
    version: str,
) -> None:
    """Render the profile from its template and write it to disk."""
    template = load_profile_template(profile_template_path)
    payload = build_profile_payload(template, recommended_table_names, version)

    profile_json_path.parent.mkdir(parents=True, exist_ok=True)
    with profile_json_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")




# ---------------------------------------------------------------------------
# Stage 1 entry point
# ---------------------------------------------------------------------------

def make_schema_stage(
    table_schemas_dir: Path,
    version: str,
    profile_json_path: Path,
    profile_template_path: Path,
) -> None:
    """Validate CSVs, build table schemas, and write the DwC-DP profile."""
    out_dir = table_schemas_dir.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    table_schemas_dir.mkdir(parents=True, exist_ok=True)

    root = repo_root_from_script()
    vocabulary_dir = root / "vocabulary"

    validate_csv_headers(vocabulary_dir)
    recommended_tables = load_recommended_tables_map(vocabulary_dir)
    recommended_fields = load_recommended_fields_map(vocabulary_dir)
    validate_field_relationship_metadata(recommended_tables, recommended_fields)
    validate_ordered_groups(set(recommended_tables.keys()))

    table_schemas = build_table_schemas(vocabulary_dir, version)

    write_profile_json(
        profile_json_path,
        profile_template_path,
        set(recommended_tables.keys()),
        version,
    )

    write_table_schema_files(out_dir, table_schemas, recommended_fields)


# ---------------------------------------------------------------------------
# Stage 2: validation
# ---------------------------------------------------------------------------

class ValidationResult:
    """Accumulate validation errors and warnings."""

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


def load_json_for_validation(file_path: Path, result: ValidationResult) -> dict | None:
    """Load JSON for validation, recording parse or file errors."""
    try:
        with file_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        result.error(f"File not found: {file_path}")
    except json.JSONDecodeError as exc:
        result.error(f"Invalid JSON in {file_path}: {exc}")
    return None


def check_schema_json(
    table_schemas_dir: Path,
    result: ValidationResult,
) -> dict[str, dict]:
    """Load generated schemas and check required field metadata."""
    loaded: dict[str, dict] = {}

    schema_files = sorted(table_schemas_dir.glob("*.json"))
    if not schema_files:
        result.error(f"No JSON table schemas found in: {table_schemas_dir}")
        return loaded

    for file_path in schema_files:
        data = load_json_for_validation(file_path, result)
        if data is None:
            continue

        schema_name = file_path.stem
        loaded[schema_name] = data

        fields = data.get("fields", [])
        if not isinstance(fields, list):
            result.error(
                f"Schema '{schema_name}' has a non-list 'fields' property"
            )
            continue

        for field in fields:
            if not isinstance(field, dict):
                result.error(
                    f"Schema '{schema_name}' contains a non-object field descriptor"
                )
                continue
            field_name = field.get("name", "<unnamed>")
            for prop in REQUIRED_FIELD_PROPERTIES:
                if prop not in field:
                    result.error(
                        f"Field '{field_name}' in {file_path.name} is missing "
                        f"required property '{prop}'"
                    )

    return loaded


def check_frictionless(
    loaded_schemas: dict[str, dict],
    result: ValidationResult,
) -> None:
    """Validate every generated descriptor as a Frictionless Table Schema."""
    valid_count = 0
    for name, descriptor in loaded_schemas.items():
        try:
            Schema.from_descriptor(descriptor)
            valid_count += 1
        except Exception as exc:
            result.error(f"Frictionless validation failed for '{name}': {exc}")


def check_dwc_dp_profile(
    loaded_schemas: dict[str, dict],
    profile_json_path: Path,
    result: ValidationResult,
) -> None:
    """Validate generated schemas against DwC-DP-specific profile constraints.

    ``dwc-dp-profile.json`` is formally a Data Package profile, while the build
    produces standalone Table Schema descriptors.  To exercise the profile
    rules that apply to recognized DwC-DP resources, this function constructs
    an in-memory Data Package whose resources contain the generated schemas.

    The external Frictionless Data Package ``$ref`` is resolved locally to an
    empty schema.  Frictionless Table Schema validity is checked separately by
    ``check_frictionless``; this pass therefore enforces the additional
    DwC-DP-specific constraints expressed by the generated local profile.
    """
    profile = load_json_for_validation(profile_json_path, result)
    if profile is None:
        return

    synthetic_package = {
        "profile": profile.get("version", "urn:dwc-dp:profile"),
        "resources": [
            {
                "name": name,
                "profile": "tabular-data-resource",
                "schema": descriptor,
            }
            for name, descriptor in loaded_schemas.items()
        ],
    }

    registry = Registry().with_resource(
        FRICTIONLESS_DATA_PACKAGE_SCHEMA_URI,
        DRAFT4.create_resource({}),
    )

    try:
        Draft4Validator.check_schema(profile)
    except Exception as exc:
        result.error(
            f"Invalid DwC-DP profile schema '{profile_json_path}': {exc}"
        )
        return

    validator = Draft4Validator(
        profile,
        registry=registry,
        format_checker=FormatChecker(),
    )

    errors = sorted(
        validator.iter_errors(synthetic_package),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )

    if not errors:
        return

    leaf_errors = []

    def collect_leaves(error):
        if error.context:
            for child in error.context:
                collect_leaves(child)
        else:
            leaf_errors.append(error)

    for error in errors:
        collect_leaves(error)

    seen = set()
    for error in leaf_errors:
        if error.validator == "not":
            # For a recognized DwC-DP resource, the first branch of the
            # profile's oneOf is expected to fail this "not" condition.
            continue

        path = "/".join(str(part) for part in error.absolute_path) or "<package>"
        key = (path, error.message)
        if key in seen:
            continue
        seen.add(key)
        result.error(
            f"DwC-DP profile validation failed at '{path}': {error.message}"
        )

    if not seen:
        # Defensive fallback for future profile structures that yield only
        # top-level combinator errors.
        for error in errors:
            path = (
                "/".join(str(part) for part in error.absolute_path)
                or "<package>"
            )
            result.error(
                f"DwC-DP profile validation failed at '{path}': {error.message}"
            )


def check_foreign_keys(
    loaded_schemas: dict[str, dict],
    result: ValidationResult,
) -> None:
    """Validate foreign-key source/target existence and PK alignment."""

    def resolve_field(value) -> str | None:
        """Normalize a fields value that may be a string or a list."""
        if isinstance(value, list):
            return value[0] if value else None
        return value or None

    for schema_name, schema_data in loaded_schemas.items():
        source_fields = {
            field.get("name")
            for field in schema_data.get("fields", [])
            if isinstance(field, dict)
        }

        for fk in schema_data.get("foreignKeys", []):
            src_field = resolve_field(fk.get("fields"))

            if not src_field or src_field not in source_fields:
                result.error(
                    f"Foreign key in '{schema_name}' references non-existent "
                    f"source field '{src_field}'"
                )
                continue

            ref = fk.get("reference") or {}
            tgt_field = resolve_field(ref.get("fields"))
            tgt_resource = ref.get("resource", "").strip() or schema_name

            if tgt_resource not in loaded_schemas:
                result.error(
                    f"Foreign key {schema_name}/{src_field} references "
                    f"non-existent target schema '{tgt_resource}'"
                )
                continue

            ref_schema = loaded_schemas[tgt_resource]
            target_field_names = {
                field.get("name")
                for field in ref_schema.get("fields", [])
                if isinstance(field, dict)
            }

            if not tgt_field or tgt_field not in target_field_names:
                result.error(
                    f"Foreign key {schema_name}/{src_field} references "
                    f"non-existent target field '{tgt_resource}/{tgt_field}'"
                )
                continue

            tgt_primary_key = ref_schema.get("primaryKey")
            if tgt_primary_key is not None and tgt_field != tgt_primary_key:
                result.error(
                    f"Foreign key {schema_name}/{src_field} targets "
                    f"'{tgt_resource}/{tgt_field}' which is not the primary key "
                    f"(primaryKey='{tgt_primary_key}')"
                )


def validate_generated_artifacts(
    table_schemas_dir: Path,
    profile_json_path: Path,
) -> ValidationResult:
    """Run all validation passes on the artifacts generated in Stage 1."""
    result = ValidationResult()

    loaded_schemas = check_schema_json(table_schemas_dir, result)
    if loaded_schemas:
        check_frictionless(loaded_schemas, result)
        check_dwc_dp_profile(loaded_schemas, profile_json_path, result)
        check_foreign_keys(loaded_schemas, result)

    if result.has_errors:
        print(
            f"Validation failed: {len(result.errors)} error(s), "
            f"{len(result.warnings)} warning(s)."
        )
    else:
        warning_note = (
            f" ({len(result.warnings)} warning(s))"
            if result.warnings
            else ""
        )
        print(f"Validation passed{warning_note}.")

    return result


# ---------------------------------------------------------------------------
# Stage 3 helpers
# ---------------------------------------------------------------------------

def load_template(template_path: Path) -> str:
    """Load the HTML template from disk."""
    if not template_path.is_file():
        raise FileNotFoundError(
            f"HTML template not found: {template_path}\n"
            "Expected qrg_template.html alongside this script."
        )
    return template_path.read_text(encoding="utf-8")


def build_foreign_key_summary(table_schema: dict, current_table_name: str = None) -> str:
    """Build the relationship summary in the same order as key fields occur.

    The table schema's ``fields`` array preserves the row order from
    dwc-dp-fields.csv.  Relationship metadata is stored separately as primaryKey,
    weakPrimaryKey, foreignKeys, and weakForeignKeys, so iterating those structures
    directly groups rows by relationship type.  Instead, collect relationship rows
    by source field and then emit them while walking ``fields`` in schema order.
    """
    relationships_by_field = defaultdict(list)

    primary_key = table_schema.get("primaryKey")
    if primary_key:
        pk_fields = primary_key if isinstance(primary_key, list) else [primary_key]
        for pk in pk_fields:
            relationships_by_field[pk].append(
                (pk, "", "", "", "primary key", "Yes")
            )

    weak_primary_key = table_schema.get("weakPrimaryKey")
    if weak_primary_key:
        wpk_fields = weak_primary_key if isinstance(weak_primary_key, list) else [weak_primary_key]
        for wpk in wpk_fields:
            relationships_by_field[wpk].append(
                (wpk, "", "", "", "weak primary key", "No")
            )

    for rel_name, rel_type, enforced in [
        ("foreignKeys", "foreign key", "Yes"),
        ("weakForeignKeys", "weak foreign key", "No"),
    ]:
        for rel in (table_schema.get(rel_name) or []):
            predicate = rel.get("predicate", "")
            src_fields = rel.get("fields")
            ref = rel.get("reference", {}) or {}
            tgt_table = ref.get("resource", "")
            tgt_fields = ref.get("fields")

            src_fields = [src_fields] if isinstance(src_fields, str) else src_fields
            tgt_fields = [tgt_fields] if isinstance(tgt_fields, str) else tgt_fields

            # Empty resource means self-referential (same table).
            tgt_table_display = (
                tgt_table
                if (isinstance(tgt_table, str) and tgt_table.strip())
                else (current_table_name or tgt_table)
            )

            for src, tgt in zip(src_fields or [], tgt_fields or []):
                relationships_by_field[src].append(
                    (src, predicate, tgt_table_display, tgt, rel_type, enforced)
                )

    # Emit relationship rows in exactly the order their source fields occur in the
    # schema fields array, which preserves dwc-dp-fields.csv order for this table.
    relationships = []
    emitted_fields = set()
    for field in (table_schema.get("fields") or []):
        if not isinstance(field, dict):
            continue
        field_name = (field.get("name") or "").strip()
        if not field_name:
            continue
        relationships.extend(relationships_by_field.get(field_name, []))
        emitted_fields.add(field_name)

    # Defensive fallback: retain any relationship whose source field was not found
    # in the fields array rather than silently dropping it.
    for field_name, field_relationships in relationships_by_field.items():
        if field_name not in emitted_fields:
            relationships.extend(field_relationships)

    if not relationships:
        return ""

    # Build required-field lookup from constraints or top-level field["required"].
    field_required_map = {}
    for f in (table_schema.get("fields") or []):
        if not isinstance(f, dict):
            continue
        name = (f.get("name") or "").strip()
        if not name:
            continue
        cons = f.get("constraints") if isinstance(f.get("constraints"), dict) else {}
        val = cons.get("required", f.get("required", False))
        if isinstance(val, bool):
            req = val
        elif isinstance(val, (int, float)):
            req = bool(val)
        elif isinstance(val, str):
            req = val.strip().lower() in {"true", "1", "yes", "y"}
        else:
            req = False
        field_required_map[name] = req

    rows = [
        '<div class="foreign-key-summary">',
        '<h4>Relationships to Other Tables</h4>',
        '<table class="term-table">',
        '<tr><td class="label">Field</td><td><b>Predicate</b></td>'
        '<td><b>Target Table</b></td><td><b>Target Field</b></td>'
        '<td><b>Relationship Type</b></td><td><b>Enforced</b></td>'
        '<td><b>Required</b></td></tr>',
    ]
    for src, predicate, tgt_table, tgt_field, rel_type, enforced in relationships:
        required = "Yes" if field_required_map.get(src, False) else "No"
        rows.append(
            f'<tr><td class="label">{src}</td><td>{predicate}</td>'
            f'<td>{tgt_table}</td><td>{tgt_field}</td>'
            f'<td>{rel_type}</td><td>{enforced}</td><td>{required}</td></tr>'
        )
    rows.append("</table></div>")
    return "\n".join(rows)


def build_term_section(field: dict, class_name: str) -> str:
    if not isinstance(field, dict):
        return ""

    order = [
        "title", "namespace", "class", "description", "notes", "examples",
        "type", "default", "constraints", "format", "dcterms:isVersionOf",
        "dcterms:references",
    ]
    labels = {
        "title": "Title (Label)",
        "class": "Table:",
        "namespace": "Namespace",
        "dcterms:isVersionOf": "dcterms:isVersionOf",
        "description": "Description",
        "notes": "Notes",
        "examples": "Examples",
        "type": "Type",
        "default": "Default",
        "constraints": "Constraints",
        "format": "Format",
        "dcterms:references": "dcterms:references",
    }

    rows = []
    for key in order:
        value = field.get(key)

        # Suppress Format when it is the default value.
        if key == "format" and str(value or "").strip().lower() == "default":
            continue

        if value is None:
            if key == "class":
                value = class_name
            else:
                continue

        if key == "constraints" and isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        else:
            value = str(value).strip()

        if not value:
            continue

        if key in ("dcterms:isVersionOf", "dcterms:references"):
            if not (
                value.startswith("http://example.com/term-pending/")
                or value.startswith("https://example.com/term-pending/")
            ):
                value = f'<a href="{value}" target="_blank">{value}</a>'
        elif key == "class":
            value = f'<a href="#{value}" target="_blank">{value}</a>'
        elif key == "examples":
            parts = [ex.strip() for ex in str(value).split(";") if ex.strip()]
            value = ""
            for i, ex in enumerate(parts):
                if i > 0:
                    value += '<div class="examples-separator"></div>'
                value += f'<div class="examples-content">{ex}</div>'

        rows.append(f'<tr><td class="label">{labels[key]}</td><td>{value}</td></tr>')

    if not rows:
        return ""

    field_name = field.get("name", "").strip()
    full_id = f"{class_name}__{field_name}"
    display_name = field.get("name", "(no name)")
    return (
        f'<section class="term" id="{full_id}">\n'
        f'<div class="field-header-wrapper">'
        f'<h3 id="{full_id}">{display_name}</h3>'
        f'</div>\n'
        f'<table class="term-table">'
        + "".join(rows)
        + "</table>\n</section>"
    )


def generate_field_links(fields: list, class_name: str) -> str:
    return "".join(
        f'<a class="field-box" href="#{class_name}__{field.get("name", "").strip()}">'
        f'{field.get("name", "").strip()}</a>'
        for field in fields
        if isinstance(field, dict) and field.get("name")
    )


# ---------------------------------------------------------------------------
# Stage 2 entry point
# ---------------------------------------------------------------------------

def generate_qrg(
    table_schemas_dir: Path,
    output_html_path: Path,
    template_path: Path,
    version: str,
) -> None:
    """Read the standalone table schemas and render the QRG HTML."""
    content_parts = []
    class_links_parts = []

    for group in ORDERED_GROUPS:
        for table_name in group:
            schema_file = table_schemas_dir / f"{table_name}.json"
            if not schema_file.is_file():
                print(
                    f"Warning: Schema file for '{table_name}' not found at "
                    f"{schema_file} — skipping."
                )
                continue
            with schema_file.open("r", encoding="utf-8") as f:
                schema = json.load(f)

            table = schema
            fields = schema.get("fields", [])
            class_name = table.get("title", table_name)

            # --- Table header ---
            content_parts.append(
                f'<div class="class-header-wrapper">'
                f'<h2 id="{class_name}" class="class-header">{class_name}</h2>'
                f'</div>'
            )

            if table.get("identifier"):
                content_parts.append(
                    f'<p><strong>Identifier:</strong> {table["identifier"]}</p>'
                )

            content_parts.append(
                f'<p><strong>Description:</strong> '
                f'{table.get("description", "No description.")}</p>'
            )

            if table.get("notes"):
                content_parts.append(
                    f'<p><strong>Notes:</strong> {table["notes"]}</p>'
                )

            ex_val = table.get("examples") or table.get("example")
            if ex_val:
                content_parts.append("<p><strong>Examples:</strong></p>")
                parts = [ex.strip() for ex in str(ex_val).split(";") if ex.strip()]
                ex_html = ""
                for i, ex in enumerate(parts):
                    if i > 0:
                        ex_html += '<div class="examples-separator"></div>'
                    ex_html += f'<div class="examples-content">{ex}</div>'
                content_parts.append(ex_html)

            # dcterms:isVersionOf for the table.
            src = str(table.get("dcterms:isVersionOf") or "").strip()
            if src:
                if src.startswith(("http://", "https://")) and "example.com" not in src:
                    content_parts.append(
                        f'<p><strong>dcterms:isVersionOf:</strong> '
                        f'<a href="{src}" target="_blank">{src}</a></p>'
                    )
                else:
                    content_parts.append(
                        f'<p><strong>dcterms:isVersionOf:</strong> {src}</p>'
                    )

            # Relationship summary (schema already loaded above).
            content_parts.append(build_foreign_key_summary(schema, table_name))

            # Field index and term sections.
            field_links = generate_field_links(fields, class_name)
            if field_links:
                content_parts.append(
                    f'<nav class="field-index"><strong>Fields:</strong><br>'
                    f'{field_links}</nav>'
                )
            for field in fields:
                term_html = build_term_section(field, class_name)
                if term_html:
                    content_parts.append(term_html)

            class_links_parts.append(
                f'<a class="class-box" href="#{class_name}">{class_name}</a>'
            )

        class_links_parts.append('<div class="menu-separator"></div>')
    template = load_template(template_path)
    html = template.format(
        content="\n".join(content_parts),
        class_links="\n".join(class_links_parts),
        version=version,
    )

    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    with output_html_path.open("w", encoding="utf-8") as out:
        out.write(html)


# ---------------------------------------------------------------------------
# PostgreSQL DDL support
# ---------------------------------------------------------------------------

POSTGRES_RESERVED = {
    "all", "analyse", "analyze", "and", "any", "array", "as", "asc", "asymmetric",
    "authorization", "between", "bigint", "binary", "bit", "boolean", "both", "case",
    "cast", "char", "character", "check", "coalesce", "collate", "column", "constraint",
    "create", "cross", "current_catalog", "current_date", "current_role", "current_schema",
    "current_time", "current_timestamp", "current_user", "default", "deferrable", "desc",
    "distinct", "do", "else", "end", "except", "exists", "extract", "false", "fetch",
    "for", "foreign", "freeze", "from", "full", "grant", "group", "having", "ilike",
    "in", "initially", "inner", "intersect", "into", "is", "isnull", "join", "lateral",
    "leading", "left", "like", "limit", "localtime", "localtimestamp", "natural", "not",
    "notnull", "null", "offset", "on", "only", "or", "order", "outer", "overlaps",
    "placing", "primary", "references", "returning", "right", "select", "session_user",
    "similar", "smallint", "some", "symmetric", "table", "then", "to", "trailing", "true",
    "union", "unique", "user", "using", "variadic", "verbose", "when", "where", "window",
    "with", "class",
}


@dataclass
class Column:
    logical_name: str
    sql_name: str
    logical_type: str
    constraints: dict[str, Any] = field(default_factory=dict)
    description: str | None = None


@dataclass
class ForeignKey:
    source_fields: list[str]
    target_resource: str
    target_fields: list[str]
    weak: bool = False


@dataclass
class Table:
    logical_name: str
    sql_name: str
    columns: list[Column]
    primary_key: list[str] = field(default_factory=list)
    weak_primary_key: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    weak_foreign_keys: list[ForeignKey] = field(default_factory=list)
    title: str | None = None
    description: str | None = None


class GeneratorError(Exception):
    pass


def snake_case(name: str) -> str:
    name = name.replace("-", "_")
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"__+", "_", name)
    return name.lower()


def quote_ident(name: str) -> str:
    if re.fullmatch(r"[a-z_][a-z0-9_]*", name) and name not in POSTGRES_RESERVED:
        return name
    return '"' + name.replace('"', '""') + '"'


def make_constraint_name(table: str, base: str) -> str:
    raw = f"{table}_{base}"
    if len(raw) <= 63:
        return raw
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    head = raw[: 63 - 1 - len(digest)]
    return f"{head}_{digest}"


def normalize_listish(value: Any) -> list[str]:
    """Coerce None, a scalar, or a list into a flat list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def fetch_url_text(url: str) -> str:
    headers = {
        "Accept": "text/csv, text/plain;q=0.9, */*;q=0.8",
        "User-Agent": "generate_sql.py/1.0",
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:  # nosec B310
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace")
    except URLError as exc:  # pragma: no cover
        raise GeneratorError(f"Failed to fetch vocabulary URL {url}: {exc}") from exc


def extract_controlled_values_from_csv(text: str, url: str) -> list[str]:
    """Extract controlled value strings from a TDWG rs.tdwg.org CSV vocabulary file.

    Expects a header row containing 'controlled_value_string' and 'type' columns.
    Rows where type is skos:Concept and the term is not deprecated are included.
    """
    skos_concept = "http://www.w3.org/2004/02/skos/core#Concept"
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or "controlled_value_string" not in reader.fieldnames:
        raise GeneratorError(
            f"CSV at {url} has no 'controlled_value_string' column — "
            "check that the vocabulary_url points to a TDWG rs.tdwg.org CSV file"
        )
    values: list[str] = []
    for row in reader:
        if row.get("term_deprecated", "").strip():
            continue
        if row.get("type", "").strip() != skos_concept:
            continue
        cv = row.get("controlled_value_string", "").strip()
        if cv:
            values.append(cv)
    return values


def parse_fk_items(items: list[dict[str, Any]], *, weak: bool) -> list[ForeignKey]:
    output: list[ForeignKey] = []
    for item in items or []:
        ref = item.get("reference", {})
        source_fields = normalize_listish(item.get("fields"))
        target_resource = ref.get("resource", "")
        target_fields = normalize_listish(ref.get("fields"))
        if not source_fields or not target_fields:
            raise GeneratorError(f"Malformed foreign key entry: {item}")
        output.append(
            ForeignKey(
                source_fields=source_fields,
                target_resource=str(target_resource),
                target_fields=target_fields,
                weak=weak,
            )
        )
    return output


def read_schema_file(path: Path) -> Table:
    with path.open("r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise GeneratorError(f"Invalid JSON in schema file {path}: {exc}") from exc

    try:
        logical_name = data["name"]
        sql_name = snake_case(logical_name)
        columns: list[Column] = []
        for field_obj in data.get("fields", []):
            logical_field = field_obj["name"]
            sql_field = snake_case(logical_field)
            columns.append(
                Column(
                    logical_name=logical_field,
                    sql_name=sql_field,
                    logical_type=field_obj.get("type", "string"),
                    constraints=field_obj.get("constraints", {}) or {},
                    description=field_obj.get("description"),
                )
            )
    except KeyError as exc:
        raise GeneratorError(f"Schema file {path} is missing required key {exc}") from exc

    return Table(
        logical_name=logical_name,
        sql_name=sql_name,
        columns=columns,
        primary_key=normalize_listish(data.get("primaryKey")),
        weak_primary_key=normalize_listish(data.get("weakPrimaryKey")),
        foreign_keys=parse_fk_items(data.get("foreignKeys", []), weak=False),
        weak_foreign_keys=parse_fk_items(data.get("weakForeignKeys", []), weak=True),
        title=data.get("title"),
        description=data.get("description"),
    )


def collect_schema_files(input_path: Path) -> list[Path]:
    """Return JSON table schema files from the generated schema directory."""
    if not input_path.is_dir():
        raise GeneratorError(f"Table schema directory not found: {input_path}")

    files = [
        p for p in input_path.glob("*.json")
        if p.is_file() and not p.name.startswith("._")
    ]
    if not files:
        raise GeneratorError(f"No JSON schema files found in {input_path}")
    return sorted(files)


def load_tables(input_path: Path) -> dict[str, Table]:
    """Load all generated table schemas from the fixed schema directory."""
    tables: dict[str, Table] = {}
    for path in collect_schema_files(input_path):
        table = read_schema_file(path)
        if table.logical_name in tables:
            raise GeneratorError(f"Duplicate table name found: {table.logical_name}")
        tables[table.logical_name] = table
    return tables

def load_sidecar(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise GeneratorError("YAML sidecar root must be a mapping/object")
    return data


class SqlGenerator:
    def __init__(self, tables: dict[str, Table], config: dict[str, Any]) -> None:
        self.tables = tables
        self.config = config
        self.column_name_map = {
            table.logical_name: {column.logical_name: column.sql_name for column in table.columns}
            for table in tables.values()
        }
        self.validate_references()

    def validate_references(self) -> None:
        for table in self.tables.values():
            column_names = {column.logical_name for column in table.columns}
            for logical_pk in table.primary_key:
                if logical_pk not in column_names:
                    raise GeneratorError(
                        f"Table {table.logical_name}: primaryKey references missing field {logical_pk}"
                    )
            for fk in [*table.foreign_keys, *table.weak_foreign_keys]:
                for source in fk.source_fields:
                    if source not in column_names:
                        raise GeneratorError(
                            f"Table {table.logical_name}: FK source field {source} does not exist"
                        )
                target_table_name = table.logical_name if fk.target_resource == "" else fk.target_resource
                if target_table_name not in self.tables:
                    raise GeneratorError(
                        f"Table {table.logical_name}: FK target resource {target_table_name} does not exist"
                    )
                target_table = self.tables[target_table_name]
                target_columns = {column.logical_name for column in target_table.columns}
                for target in fk.target_fields:
                    if target not in target_columns:
                        raise GeneratorError(
                            f"Table {table.logical_name}: FK target field {target_table_name}.{target} does not exist"
                        )
                # Check that target fields form a key (primary key or unique) on the target table.
                target_fields_set = set(fk.target_fields)
                is_pk = target_fields_set == set(target_table.primary_key)
                is_weak_pk = target_fields_set == set(target_table.weak_primary_key)
                
                unique_cols = {
                    col.logical_name
                    for col in target_table.columns
                    if (col.constraints or {}).get("unique")
                }
                is_unique = len(fk.target_fields) == 1 and fk.target_fields[0] in unique_cols
                if not (is_pk or is_weak_pk or is_unique):
                    msg = (
                        f"Table {table.logical_name}: FK target fields {fk.target_fields} "
                        f"on {target_table_name} are not a primary key or unique column"
                    )
                    if fk.weak:
                        print(f"Warning: {msg}", file=sys.stderr)
                    else:
                        raise GeneratorError(msg)

    def type_override(self, table: str, column: str) -> str | None:
        return (
            self.config.get("types", {})
            .get("columns", {})
            .get(table, {})
            .get(column, {})
            .get("sql_type")
        )

    def enum_binding(self, table: str, column: str) -> str | None:
        return (
            self.config.get("enum_bindings", {})
            .get(table, {})
            .get(column, {})
            .get("enum")
        )

    def default_value(self, table: str, column: str) -> Any:
        return (
            self.config.get("defaults", {})
            .get("columns", {})
            .get(table, {})
            .get(column, {})
            .get("value")
        )

    def pg_type_for_column(self, table: str, column: Column) -> str:
        enum_name = self.enum_binding(table, column.logical_name)
        if enum_name:
            if enum_name not in self.config.get("enums", {}):
                raise GeneratorError(
                    f"Column {table}.{column.logical_name} binds to undefined enum {enum_name}"
                )
            return quote_ident(snake_case(enum_name))

        override = self.type_override(table, column.logical_name)
        if override:
            return override

        type_map = {
            "string": "TEXT",
            "integer": "INTEGER",
            "number": "NUMERIC",
            "boolean": "BOOLEAN",
        }
        try:
            return type_map[column.logical_type]
        except KeyError as exc:
            raise GeneratorError(
                f"Unsupported logical type {column.logical_type!r} for {table}.{column.logical_name}"
            ) from exc

    def column_checks_from_schema(self, column: Column) -> list[str]:
        checks: list[str] = []
        constraints = column.constraints or {}
        minimum = constraints.get("minimum")
        maximum = constraints.get("maximum")
        if minimum is not None:
            checks.append(f"value >= {minimum}")
        if maximum is not None:
            checks.append(f"value <= {maximum}")
        return checks

    def render_header_comment(self) -> str:
        metadata = self.config.get("metadata", {})
        lines = ["/*"]
        preferred_order = ["title", "version", "source_table_schemas", "generated_by"]
        seen: set[str] = set()
        for key in preferred_order:
            if key in metadata:
                label = key.replace("_", " ").capitalize()
                lines.append(f"{label}: {metadata[key]}")
                seen.add(key)
        for key, value in metadata.items():
            if key in ("notes", "example_run") or key in seen:
                continue
            label = key.replace("_", " ").capitalize()
            lines.append(f"{label}: {value}")
        notes = metadata.get("notes", [])
        if notes:
            lines.append("")
            lines.append("Notes:")
            for note in notes:
                lines.append(f"- {note}")
        example_run = metadata.get("example_run", "").strip()
        if example_run:
            lines.append("")
            lines.append("Example run:")
            for run_line in example_run.splitlines():
                lines.append(f"  {run_line}")
        lines.append("*/")
        return "\n".join(lines)

    def resolve_enum_values(self, enum_name: str, spec: dict[str, Any]) -> list[str]:
        values = [str(v) for v in spec.get("values", []) or []]
        if values:
            return values

        vocabulary_url = spec.get("vocabulary_url")
        if vocabulary_url:
            text = fetch_url_text(str(vocabulary_url))
            values = extract_controlled_values_from_csv(text, str(vocabulary_url))
            if values:
                print(
                    f"Enum '{enum_name}': fetched {len(values)} value(s) from {vocabulary_url}",
                    file=sys.stderr,
                )
                return values
            raise GeneratorError(
                f"Enum {enum_name} could not extract controlled values from {vocabulary_url}"
            )

        raise GeneratorError(
            f"Enum {enum_name} must define either 'values' or 'vocabulary_url'"
        )

    def render_enums(self) -> str:
        enums = self.config.get("enums", {})
        if not enums:
            return ""
        statements: list[str] = []
        for enum_name, spec in enums.items():
            values = self.resolve_enum_values(enum_name, spec)
            if not values:
                raise GeneratorError(f"Enum {enum_name} has no values")
            qname = quote_ident(snake_case(enum_name))
            literal_list = ",\n  ".join("'" + str(v).replace("'", "''") + "'" for v in values)
            statements.append(f"CREATE TYPE {qname} AS ENUM (\n  {literal_list}\n);")
        return "\n\n".join(statements)

    def render_create_table(self, table: Table) -> str:
        lines: list[str] = []
        if table.title or table.description:
            if table.title:
                lines.append(f"-- {table.title}")
            if table.description:
                for desc_line in str(table.description).splitlines():
                    lines.append(f"-- {desc_line}")
        column_defs: list[str] = []
        pk_sql_names = [self.column_name_map[table.logical_name][name] for name in table.primary_key]
        single_pk = pk_sql_names[0] if len(pk_sql_names) == 1 else None

        for column in table.columns:
            parts = [quote_ident(column.sql_name), self.pg_type_for_column(table.logical_name, column)]
            constraints = column.constraints or {}
            if constraints.get("required"):
                parts.append("NOT NULL")
            if constraints.get("unique") and column.sql_name != single_pk:
                parts.append("UNIQUE")
            default_value = self.default_value(table.logical_name, column.logical_name)
            if default_value is not None:
                parts.append(f"DEFAULT {default_value}")
            checks = self.column_checks_from_schema(column)
            for expr in checks:
                parts.append(f"CHECK ({expr})")
            if column.sql_name == single_pk:
                parts.append("PRIMARY KEY")
            column_defs.append("  " + " ".join(parts))

        if len(pk_sql_names) > 1:
            pk_expr = ", ".join(quote_ident(name) for name in pk_sql_names)
            column_defs.append(f"  PRIMARY KEY ({pk_expr})")

        lines.append(f"CREATE TABLE {quote_ident(table.sql_name)} (")
        lines.append(",\n".join(column_defs))
        lines.append(");")
        return "\n".join(lines)

    def per_table_foreign_key_statements(self, table: Table) -> list[str]:
        statements: list[str] = []
        for fk in table.foreign_keys:
            src_cols = [self.column_name_map[table.logical_name][name] for name in fk.source_fields]
            target_table_logical = table.logical_name if fk.target_resource == "" else fk.target_resource
            target_table = self.tables[target_table_logical]
            tgt_cols = [self.column_name_map[target_table_logical][name] for name in fk.target_fields]
            base = "_".join(src_cols + ["fkey"])
            cname = make_constraint_name(table.sql_name, base)
            statements.append(
                "ALTER TABLE {table_name} ADD CONSTRAINT {cname} FOREIGN KEY ({src}) "
                "REFERENCES {target} ({tgt}) ON DELETE CASCADE DEFERRABLE;".format(
                    table_name=quote_ident(table.sql_name),
                    cname=quote_ident(cname),
                    src=", ".join(quote_ident(c) for c in src_cols),
                    target=quote_ident(target_table.sql_name),
                    tgt=", ".join(quote_ident(c) for c in tgt_cols),
                )
            )
        return statements

    def per_table_extra_check_statements(self, table: Table) -> list[str]:
        checks_cfg = self.config.get("checks", {})
        statements: list[str] = []

        for item in checks_cfg.get("tables", {}).get(table.logical_name, []):
            name = item["name"]
            sql_expr = item["sql"]
            statements.append(
                f"ALTER TABLE {quote_ident(table.sql_name)} "
                f"ADD CONSTRAINT {quote_ident(make_constraint_name(table.sql_name, name))} "
                f"CHECK ({sql_expr});"
            )

        for logical_col, items in checks_cfg.get("columns", {}).get(table.logical_name, {}).items():
            if logical_col not in self.column_name_map[table.logical_name]:
                raise GeneratorError(f"Unknown column in checks.columns: {table.logical_name}.{logical_col}")
            for item in items:
                name = item["name"]
                sql_expr = item["sql"]
                statements.append(
                    f"ALTER TABLE {quote_ident(table.sql_name)} "
                    f"ADD CONSTRAINT {quote_ident(make_constraint_name(table.sql_name, name))} "
                    f"CHECK ({sql_expr});"
                )
        return statements

    def per_table_index_statements(self, table: Table) -> list[str]:
        statements: list[str] = []
        seen: set[tuple[str, ...]] = set()
        for fk in [*table.foreign_keys, *table.weak_foreign_keys]:
            src_cols = tuple(self.column_name_map[table.logical_name][name] for name in fk.source_fields)
            if src_cols in seen:
                continue
            seen.add(src_cols)
            idx_name = make_constraint_name(table.sql_name, "_".join([*src_cols, "idx"]))
            statements.append(
                f"CREATE INDEX {quote_ident(idx_name)} ON {quote_ident(table.sql_name)} "
                f"({', '.join(quote_ident(c) for c in src_cols)});"
            )
        return statements

    def render_table_section(self, table: Table) -> str:
        parts = [self.render_create_table(table)]
        fk_statements = self.per_table_foreign_key_statements(table)
        if fk_statements:
            parts.append("\n".join(fk_statements))
        check_statements = self.per_table_extra_check_statements(table)
        if check_statements:
            parts.append("\n".join(check_statements))
        index_statements = self.per_table_index_statements(table)
        if index_statements:
            parts.append("\n".join(index_statements))
        return "\n\n".join(parts)

    def generate(self) -> str:
        sections = [self.render_header_comment()]
        enums = self.render_enums()
        if enums:
            sections.extend(["", "-- ENUMs", enums])
        sections.append("")
        sections.append("-- Tables, constraints, and indexes")
        sections.append(
            "\n\n".join(
                self.render_table_section(table)
                for table in sorted(self.tables.values(), key=lambda t: t.sql_name)
            )
        )
        return "\n".join(sections)


# ---------------------------------------------------------------------------
# Stage 4: PostgreSQL DDL generation
# ---------------------------------------------------------------------------

SQL_CONFIG_FILENAME = "generate_sql.yaml"
SQL_OUTPUT_FILENAME = "dwc-dp.sql"


def generate_postgresql_ddl(
    table_schemas_dir: Path,
    config_path: Path,
    output_path: Path,
    version: str,
) -> None:
    """Generate PostgreSQL DDL from the validated DwC-DP table schemas."""
    if not config_path.is_file():
        raise GeneratorError(f"SQL configuration file not found: {config_path}")

    tables = load_tables(table_schemas_dir)
    config = load_sidecar(config_path)

    # The SQL metadata version is derived from the same version argument used
    # to generate the DwC-DP profile and table schemas.  It is intentionally
    # not maintained independently in generate_sql.yaml.
    metadata = config.setdefault("metadata", {})
    metadata["version"] = version

    generator = SqlGenerator(tables, config)
    sql = generator.generate() + "\n"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(sql, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI and main
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate, validate, and render DwC-DP artifacts and PostgreSQL DDL"
    )
    parser.add_argument(
        "version",
        help="DwC-DP version (e.g., http://rs.tdwg.org/dwc-dp/1.0_DEV)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    (
        table_schemas_dir,
        output_html_path,
        template_path,
        profile_json_path,
        profile_template_path,
        sql_config_path,
        sql_output_path,
    ) = _derive_paths(args.version)

    # Stage 1: generate profile and standalone table schemas.
    print(f"Generating DwC-DP profile and table schemas in {table_schemas_dir.parent}...")
    make_schema_stage(
        table_schemas_dir,
        args.version,
        profile_json_path,
        profile_template_path,
    )
    print(
        f"Generation complete: profile -> {profile_json_path}; "
        f"table schemas -> {table_schemas_dir}"
    )

    # Stage 2: validate exactly the artifacts just generated.
    print(f"Validating generated DwC-DP artifacts in {table_schemas_dir}...")
    validation = validate_generated_artifacts(
        table_schemas_dir,
        profile_json_path,
    )
    if validation.has_errors:
        print("Processing stopped because validation failed.")
        return 1

    # Stage 3: render the QRG only from validated table schemas.
    print(f"Rendering DwC-DP Quick Reference Guide to {output_html_path}...")
    generate_qrg(
        table_schemas_dir,
        output_html_path,
        template_path,
        args.version,
    )
    print(f"QRG rendering complete: {output_html_path}")

    # Stage 4: generate PostgreSQL DDL from the validated table schemas.
    print(f"Generating PostgreSQL DDL to {sql_output_path}...")
    try:
        generate_postgresql_ddl(
            table_schemas_dir,
            sql_config_path,
            sql_output_path,
            args.version,
        )
    except GeneratorError as exc:
        print(f"Error: {exc}")
        print("Processing stopped because PostgreSQL DDL generation failed.")
        return 1

    print(f"PostgreSQL DDL generation complete: {sql_output_path}")
    print("DwC-DP processing completed successfully.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
