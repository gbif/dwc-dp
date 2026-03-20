#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run DwC-DP build in two stages:
Stage 1) read the csv files in ../vocabulary and generate:
  ../dwc-dp/index.json
  ../dwc-dp/version.json
  ../dwc-dp/table-schemas/*.json

Stage 2) renders the
  ../qrg/index.html (DwC-DP Quick Reference Guide)

Usage:
  python generate_qrg.py <version>

Examples:
  python generate_qrg.py 0.1
"""

import sys
import os
import argparse
import json
import csv
import logging
from pathlib import Path
from collections import defaultdict
from datetime import date

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Expected headers for each source CSV.  Order is NOT enforced; presence is.
EXPECTED_HEADERS = {
    "dwc-dp-tables.csv": {
        "name", "title", "description", "comments", "example", "namespace",
        "dcterms:isVersionOf", "dcterms:references", "rdfs:comment", "status",
        "new", "ignore",
    },
    "dwc-dp-fields.csv": {
        "table", "name", "key", "predicate", "related_table", "related_field",
        "title", "description", "comments", "example", "type", "format",
        "unique", "required", "minimum", "maximum", "namespace",
        "dcterms:isVersionOf", "dcterms:references", "rdfs:comment", "status",
        "new", "ignore",
    },
}

# Columns that carry genuine boolean semantics; "no" / "yes" are coerced only here.
BOOLEAN_COLUMNS = {"required", "unique"}

# Ordered display groups for the QRG.  Every recommended table name must appear
# exactly once; validate_ordered_groups() enforces this at runtime.
ORDERED_GROUPS = [
    ['event', 'chronometric-age', 'geological-context', 'occurrence', 'organism',
     'organism-interaction'],
    ['survey', 'survey-survey-target', 'survey-target', 'survey-target-descriptor'],
    ['identification', 'identification-taxon'],
    ['material', 'material-geological-context'],
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
    ['usage-policy', 'material-usage-policy', 'media-usage-policy'],
    ['organism-relationship', 'resource-relationship'],
]

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def repo_root_from_script() -> Path:
    """Return the repository root, assuming this script lives in <root>/maintenance/."""
    return Path(__file__).resolve().parent.parent.parent


def _derive_paths(version: str):
    """Return (index_json_path, table_schemas_dir, output_html_path, template_path)
    all anchored to the repository root so they are independent of cwd."""
    root = repo_root_from_script()
    index_json_path = root / "dwc-dp" / "index.json"
    table_schemas_dir = root / "dwc-dp" / "table-schemas"
    output_html_path = root / "qrg" / "index.html"
    # Template lives alongside this script in maintenance/
    template_path = Path(__file__).resolve().parent / "qrg_template.html"
    return index_json_path, table_schemas_dir, output_html_path, template_path


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
# Stage 1 helpers
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
            logger.warning(
                "Unexpected columns in %s (will be ignored): %s", path.name, sorted(extra)
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
        logger.warning(
            "ORDERED_GROUPS references table names that are not recommended in "
            "dwc-dp-tables.csv (they will be skipped): %s",
            sorted(unknown_in_groups),
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
            comments = (row.get("comments", "") or "").strip()
            example = (row.get("example", "") or "").strip()
            namespace = (row.get("namespace", "") or "").strip()
            iri = (row.get("dcterms:isVersionOf", "") or "").strip()
            if not iri:
                iri = f"http://example.com/term-pending/{namespace}/{name}"
            iri_version = (row.get("dcterms:references", "") or "").strip()
            rdfs_comment = (row.get("rdfs:comment", "") or "").strip()

            ts = {
                "identifier": f"http://rs.tdwg.org/dwc/dwc-dp/{name}",
                "url": f"table-schemas/{name}.json",
                "name": name,
                "title": title,
                "description": description,
                "comments": comments,
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
    foreign_keys = []
    weak_foreign_keys = []

    for row in rows:
        name = (row.get("name", "") or "").strip()
        title = (row.get("title", "") or "").strip()
        description = (row.get("description", "") or "").strip()
        comments = (row.get("comments", "") or "").strip()
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
            "comments": comments,
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

    return fields, pk_names, foreign_keys, weak_foreign_keys


def build_index_payload(version: str, vocabulary_dir: Path) -> dict:
    return {
        "identifier": "http://rs.tdwg.org/dwc/dwc-dp",
        "url": "",
        "name": "dwc-dp",
        "version": version,
        "title": "Darwin Core Data Package",
        "shortTitle": "dwc-dp",
        "description": "A data package for sharing biodiversity data using Darwin Core.",
        "issued": date.today().strftime("%Y-%m-%d"),
        "isLatest": True,
        "tableSchemas": build_table_schemas(vocabulary_dir, version),
    }


def write_table_schema_files(
    out_dir: Path, table_schemas: list, fields_by_table: dict
) -> None:
    """Write one JSON schema file per table using the pre-loaded fields map."""
    ts_dir = out_dir / "table-schemas"
    ts_dir.mkdir(parents=True, exist_ok=True)

    for ts in table_schemas:
        name = ts.get("name", "")
        fields, pk_names, foreign_keys, weak_foreign_keys = build_fields_for_table(
            fields_by_table, name
        )

        payload = dict(ts)
        payload["fields"] = fields

        if pk_names:
            payload["primaryKey"] = pk_names[0] if len(pk_names) == 1 else pk_names
        if foreign_keys:
            payload["foreignKeys"] = foreign_keys
        if weak_foreign_keys:
            payload["weakForeignKeys"] = weak_foreign_keys

        dest = ts_dir / f"{name}.json"
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        logger.info("Wrote %s", dest)


def write_version_json(out_dir: Path, version: str) -> None:
    payload = {
        "version": version,
        "latestCompatibleVersion": version,
    }
    dest = out_dir / "version.json"
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    logger.info("Wrote %s", dest)


# ---------------------------------------------------------------------------
# Stage 1 entry point
# ---------------------------------------------------------------------------

def make_index_stage(index_json_path: Path, table_schemas_dir: Path, version: str) -> None:
    """Validate CSVs, build JSON schemas, write index.json and version.json."""
    out_dir = index_json_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    table_schemas_dir.mkdir(parents=True, exist_ok=True)

    root = repo_root_from_script()
    vocabulary_dir = root / "vocabulary"

    # Validate CSV structure.
    validate_csv_headers(vocabulary_dir)

    # Load CSVs once; pass results to all consumers.
    recommended_tables = load_recommended_tables_map(vocabulary_dir)
    recommended_fields = load_recommended_fields_map(vocabulary_dir)

    # Cross-validate relationship metadata.
    validate_field_relationship_metadata(recommended_tables, recommended_fields)

    # Validate ORDERED_GROUPS covers all recommended tables.
    validate_ordered_groups(set(recommended_tables.keys()))

    # Build and write index.json.
    payload = build_index_payload(version, vocabulary_dir)
    with index_json_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    logger.info("Wrote %s", index_json_path)

    # Write version.json.
    write_version_json(out_dir, version)

    # Write per-table schema files using the already-loaded fields map.
    write_table_schema_files(out_dir, payload["tableSchemas"], recommended_fields)

    logger.info("Index + schemas ready under %s", out_dir)


# ---------------------------------------------------------------------------
# Stage 2 helpers
# ---------------------------------------------------------------------------

def load_template(template_path: Path) -> str:
    """Load the HTML template from disk."""
    if not template_path.is_file():
        raise FileNotFoundError(
            f"HTML template not found: {template_path}\n"
            "Expected qrg_template.html alongside this script in the maintenance/ directory."
        )
    return template_path.read_text(encoding="utf-8")


def build_foreign_key_summary(table_schema: dict, current_table_name: str = None) -> str:
    relationships = []

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
                relationships.append(
                    (src, predicate, tgt_table_display, tgt, rel_type, enforced)
                )

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
        "title", "namespace", "class", "description", "comments", "examples",
        "type", "default", "constraints", "format", "dcterms:isVersionOf",
        "dcterms:references",
    ]
    labels = {
        "title": "Title (Label)",
        "class": "Table:",
        "namespace": "Namespace",
        "dcterms:isVersionOf": "dcterms:isVersionOf",
        "description": "Description",
        "comments": "Comments",
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
    index_json_path: Path,
    table_schemas_dir: Path,
    output_html_path: Path,
    template_path: Path,
    version: str,
) -> None:
    """Read the index JSON and per-table schemas, then render the QRG HTML."""
    logger.info("Loading index from %s", index_json_path)
    with index_json_path.open("r", encoding="utf-8") as f:
        index_data = json.load(f)

    tables = index_data.get("tableSchemas", [])
    table_map = {table["name"]: table for table in tables}

    content_parts = []
    class_links_parts = []

    for group in ORDERED_GROUPS:
        for table_name in group:
            table = table_map.get(table_name)
            if not table:
                logger.warning("Table '%s' not found in index.json — skipping.", table_name)
                continue

            schema_file = table_schemas_dir / f"{table_name}.json"
            if not schema_file.is_file():
                logger.warning(
                    "Schema file for '%s' not found at %s — skipping.", table_name, schema_file
                )
                continue

            logger.info("Loading schema for %s", table_name)
            with schema_file.open("r", encoding="utf-8") as f:
                schema = json.load(f)

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

            if table.get("comments"):
                content_parts.append(
                    f'<p><strong>Comments:</strong> {table["comments"]}</p>'
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

    logger.info("Assembling final HTML output...")
    template = load_template(template_path)
    html = template.format(
        content="\n".join(content_parts),
        class_links="\n".join(class_links_parts),
        version=version,
    )

    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    with output_html_path.open("w", encoding="utf-8") as out:
        out.write(html)
    logger.info("Quick Reference Guide written to %s", output_html_path)


# ---------------------------------------------------------------------------
# CLI and main
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Build DwC-DP index and QRG")
    parser.add_argument("version", help="DwC-DP version (e.g., 0.1)")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    index_json_path, table_schemas_dir, output_html_path, template_path = (
        _derive_paths(args.version)
    )

    logger.info("index.json    -> %s", index_json_path)
    logger.info("table-schemas -> %s", table_schemas_dir)
    logger.info("QRG output    -> %s", output_html_path)
    logger.info("HTML template <- %s", template_path)

    # Stage 1: build JSON artefacts.
    make_index_stage(index_json_path, table_schemas_dir, args.version)

    # Stage 2: render the QRG.
    generate_qrg(
        index_json_path,
        table_schemas_dir,
        output_html_path,
        template_path,
        args.version,
    )


if __name__ == "__main__":
    main()
