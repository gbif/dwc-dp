#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run DwC-DP build in two stages:
Stage 1) read the csv files in ../vocabulary and generate:
  ../dwc-dp/<version>/index.json
  ../dwc-dp/<version>/version.json
  ../dwc-dp/<version>/table-schemas/*.json

Stage 2) renders the 
  ../qrg/index.html (DwC-DP Quick Reference Guide)
  ../explorer/index.html (DwC-DP Relationship Explorer)

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
from pathlib import Path
from collections import defaultdict

# Original source files for rendering the data package files, the DwC-DP Quick Reference
# Guide, and the DwC-DP Relationsip Explorer

EXPECTED_HEADERS = {
    "dwc-dp-tables.csv": [
        "name","title","description","comments","example","namespace",
        "dcterms:isVersionOf","dcterms:references","rdfs:comment","status","new","ignore"
    ],
    "dwc-dp-fields.csv": [
        "table","name","key","title","description","comments","example","type","format",
        "unique","required","minimum","maximum","namespace","dcterms:isVersionOf",
        "dcterms:references","rdfs:comment","status","new","ignore"
    ],
    "dwc-dp-predicates.csv": [
       "subject_table","subject_field","predicate","related_table","related_field",
       "status"
    ],
}

ORDERED_GROUPS = [
    ['event', 'chronometric-age', 'geological-context', 'occurrence', 'organism', 
     'organism-interaction', 'survey', 'survey-target'],
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
    ['organism-relationship', 'resource-relationship']
]

# ---- CLI ----
parser = argparse.ArgumentParser(description="Build DwC-DP index and QRG")
parser.add_argument("version", help="DwC-DP version (e.g., 0.1)")
args, _unknown = parser.parse_known_args()

# Derived paths shared by both stages
INDEX_JSON_PATH = '../dwc-dp/' + args.version + '/index.json'
TABLE_SCHEMAS_DIR = '../dwc-dp/' + args.version + '/table-schemas'

print(f"Using INDEX_JSON_PATH: {INDEX_JSON_PATH}")
print(f"Using TABLE_SCHEMAS_DIR: {TABLE_SCHEMAS_DIR}")

# Ensure output dir exists
os.makedirs(os.path.dirname(INDEX_JSON_PATH), exist_ok=True)
os.makedirs(TABLE_SCHEMAS_DIR, exist_ok=True)

# ==================== Stage 1: make_index_json ====================
def make_index_stage(output_dir: str, version: str):
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    root = repo_root_from_script()
    vocabulary_dir = root / "vocabulary"

    # Validate required CSVs and headers
    validate_csv_headers(vocabulary_dir)

    # Build payload including tableSchemas
    payload = build_index_payload(version, vocabulary_dir)

    # Write index.json
    out_path = out_dir / "index.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"Wrote {out_path}")

    # Write version.json
    write_version_json(out_dir, version)

    # Write per-table schema files
    write_table_schema_files(out_dir, payload["tableSchemas"], vocabulary_dir)

    print(f"Index + schemas ready under {out_dir}")
    return out_path

def repo_root_from_script() -> Path:
    # Script is expected in <repo_root>/maintenance/
    return Path(__file__).resolve().parent.parent

def validate_csv_headers(vocabulary_dir: Path) -> None:
    """Ensure the three required CSVs exist and have the exact headers (order matters)."""
    for filename, expected in EXPECTED_HEADERS.items():
        path = vocabulary_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required input not found: {path}")
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            actual = reader.fieldnames or []
            if actual != expected:
                raise ValueError(
                    "Header mismatch in {file}:\n  Expected: {exp}\n  Actual:   {act}".format(
                        file=path, exp=expected, act=actual
                    )
                )

def build_table_schemas(vocabulary_dir: Path, version: str):
    """Build tableSchemas list from dwc-dp-tables.csv where status == 'recommended'."""
    tables_csv = vocabulary_dir / "dwc-dp-tables.csv"
    table_schemas = []
    with tables_csv.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            status = (row.get("status", "") or "").strip().lower()
            if status != "recommended":
                continue
            name = (row.get("name", "") or "").strip()
            title = (row.get("title", "") or "").strip()
            description = (row.get("description", "") or "").strip()
            comments = (row.get("comments", "") or "").strip()
            example = (row.get("example", "") or "").strip()
            namespace = (row.get("namespace", "") or "").strip()
            iri = (row.get("dcterms:isVersionOf", "") or "").strip()
            iri_version = (row.get("dcterms:references", "") or "").strip()
            rdfs_comment = (row.get("rdfs:comment", "") or "").strip()

            ts = {
                "identifier": f"http://rs.tdwg.org/dwc/dwc-dp/{name}",
                "url": f"https://github.com/gbif/dwc-dp/blob/master/dwc-dp/{version}/table-schemas/{name}.json",
                "name": name,
                "title": title,
                "description": description,
                "comments": comments,
                "example": example,
                "namespace": namespace,
                "iri": iri,
                "iri_version": iri_version,
                "rdfs:comment": rdfs_comment,
            }
            table_schemas.append(ts)
    return table_schemas

def build_fields_for_table(vocabulary_dir: Path, table_name: str):
    """Return (ordered fields list, pk_names list, fk_field_names list) for a table."""
    fields_csv = vocabulary_dir / "dwc-dp-fields.csv"
    fields = []
    pk_names = []
    fk_field_names = []
    with fields_csv.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            status = (row.get("status", "") or "").strip().lower()
            table = (row.get("table", "") or "").strip()
            if table != table_name or status != "recommended":
                continue

            name = (row.get("name", "") or "").strip()
            title = (row.get("title", "") or "").strip()
            description = (row.get("description", "") or "").strip()
            comments = (row.get("comments", "") or "").strip()
            example = (row.get("example", "") or "").strip()
            ftype = (row.get("type", "") or "").strip()
            fmt = (row.get("format", "") or "").strip()
            namespace = (row.get("namespace", "") or "").strip()
            iri = (row.get("dcterms:isVersionOf", "") or "").strip()
            iri_version = (row.get("dcterms:references", "") or "").strip()
            rdfs_comment = (row.get("rdfs:comment", "") or "").strip()

            # Track pk / fk
            key_val = (row.get("key", "") or "").strip().lower()
            if key_val == "pk":
                pk_names.append(name)
            elif key_val == "fk":
                fk_field_names.append(name)

            # Constraints
            constraints_candidates = {
                "required": (row.get("required", "") or "").strip(),
                "unique": (row.get("unique", "") or "").strip(),
                "minimum": (row.get("minimum", "") or "").strip(),
                "maximum": (row.get("maximum", "") or "").strip(),
            }
            constraints = {k: v for k, v in constraints_candidates.items() if v != ""}

            field_obj = {
                "name": name,
                "title": title,
                "description": description,
                "comments": comments,
                "example": example,
                "type": ftype,
                "format": fmt,
                "namespace": namespace,
                "iri": iri,
                "iri_version": iri_version,
                "rdfs:comment": rdfs_comment,
            }
            if constraints:
                field_obj["constraints"] = constraints

            fields.append(field_obj)
    return fields, pk_names, fk_field_names

def load_predicates_map(vocabulary_dir: Path):
    """Return a mapping: (subject_table, subject_field) -> ordered rows (recommended first)."""
    preds_csv = vocabulary_dir / "dwc-dp-predicates.csv"
    mapping_all = defaultdict(list)
    with preds_csv.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            subj_tbl = (row.get("subject_table", "") or "").strip()
            subj_fld = (row.get("subject_field", "") or "").strip()
            mapping_all[(subj_tbl, subj_fld)].append(row)
    # Order with recommended first
    mapping = {}
    for key, rows in mapping_all.items():
        recommended = [r for r in rows if (r.get("status", "") or "").strip().lower() == "recommended"]
        ordered = recommended + [r for r in rows if r not in recommended]
        mapping[key] = ordered
    return mapping

def build_foreign_keys_for_table(pred_map, table_name: str, fk_field_names: list):
    """Create foreign key dicts for the given table/fields using predicate rows."""
    fks = []
    for fld in fk_field_names:
        rows = pred_map.get((table_name, fld), [])
        if not rows:
            print(f"Warning: No predicate mapping found for {table_name}.{fld}; skipping FK entry")
            continue
        row = rows[0]  # prefer 'recommended' if present
        predicate = (row.get("predicate", "") or "").strip()
        related_table = (row.get("related_table", "") or "").strip()
        related_field = (row.get("related_field", "") or "").strip()
        resource = "" if related_table == table_name else related_table

        fk = {
            "fields": fld,
            "predicate": predicate,
            "reference": {
                "resource": resource,
                "fields": related_field,
            },
        }
        fks.append(fk)
    return fks

def build_index_payload(version: str, vocabulary_dir: Path) -> dict:
    return {
        "identifier": "http://rs.tdwg.org/dwc/dwc-dp",
        "url": f"https://github.com/gbif/dwc-dp/blob/master/dwc-dp/{version}",
        "name": "dwc-dp",
        "version": version,
        "title": "Darwin Core Data Package",
        "shortTitle": "dwc-dp",
        "description": "A data package for sharing biodiversity data using Darwin Core.",
        "issued": version,
        "isLatest": True,
        "tableSchemas": build_table_schemas(vocabulary_dir, version),
    }

def write_table_schema_files(out_dir: Path, table_schemas: list, vocabulary_dir: Path):
    ts_dir = out_dir / "table-schemas"
    ts_dir.mkdir(parents=True, exist_ok=True)

    pred_map = load_predicates_map(vocabulary_dir)

    for ts in table_schemas:
        name = ts.get("name", "")

        # Build fields, pk, and fk field names
        fields, pk_names, fk_field_names = build_fields_for_table(vocabulary_dir, name)

        # Build FK objects using predicates csv
        foreign_keys = build_foreign_keys_for_table(pred_map, name, fk_field_names)

        # Construct the table schema JSON: top-level = same structure as in index.json + fields
        payload = dict(ts)  # shallow copy preserves order
        payload["fields"] = fields

        # Add primaryKey if present (single string if one; list if multiple)
        if pk_names:
            payload["primaryKey"] = pk_names[0] if len(pk_names) == 1 else pk_names

        # Add foreignKeys if any
        if foreign_keys:
            payload["foreignKeys"] = foreign_keys

        dest = ts_dir / f"{name}.json"
        with dest.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        print(f"Wrote {dest}")

def write_version_json(out_dir: Path, version: str):
    """Write version.json next to index.json."""
    payload = {
        "version": version,
        "latestCompatibleVersion": version,
    }
    dest = out_dir / "version.json"
    with dest.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"Wrote {dest}")

# ==================== Stage 2: Generate QRG and Explorer ====================
# INDEX_JSON_PATH will be set from CLI 'version'
# TABLE_SCHEMAS_DIR will be set from CLI 'version'
OUTPUT_PATH = '../qrg/index.html'
JS_INDEX_JSON_PATH = '../explorer/indexJson.js'
JS_PREDICATES_PATH = '../explorer/predicates.js'

# Full HTML template (no placeholders, uses .format)
TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Darwin Core Data Package - Quick Reference Guide</title>
    <style>
        html, body {{ margin: 0; padding: 0; box-sizing: border-box; overflow-x: hidden; height: 100%; }}
        body {{ font-family: Arial, sans-serif; line-height: 1.4; display: flex; align-items: flex-start; }}
        main {{ flex: 1; padding: 20px; max-width: calc(100% - 260px); box-sizing: border-box; }}
        aside.nav-menu {{
            width: 240px;
            border-left: 1px solid #ccc;
            padding: 15px;
            height: 100vh;
            overflow-y: auto;
            position: sticky;
            top: 0;
            box-sizing: border-box;
            background: #fafafa;
        }}
        h1 {{ border-bottom: 1px solid #ccc; padding-bottom: 4px; margin: 12px 0 8px; }}
        h2 {{ padding-bottom: 4px; margin: 12px 0 8px; }}
        .intro {{ margin: 12px 0; font-size: 1.02em; color: #333; }}
        .intro img {{ display: block; width: 100%; height: auto; border: 1px solid #ccc; box-sizing: border-box; }}
        .figure-caption {{ font-size: 1.02em; color: #555; text-align: left; margin-top: 4px; }}
        nav.class-index a.class-box {{
            display: inline-block;
            margin: 2px;
            padding: 2px 6px;
            border: 1px solid #8da7b5;
            border-radius: 4px;
            background: #f1f6f9;
            color: #003c71;
            text-decoration: none;
            font-size: 0.8em;
        }}
        nav.class-index a.class-box:hover {{ background: #e1ecf4; }}
        nav.field-index {{ margin: 12px 0; }}
        nav.field-index a.field-box {{ display: inline-block; margin: 3px; padding: 3px 6px; border: 1px solid #8da7b5; border-radius: 4px; background: #f1f6f9; color: #003c71; text-decoration: none; font-size: 0.85em; }}
        nav.field-index a.field-box:hover {{ background: #e1ecf4; }}
        .menu-separator {{ border-top: 1px solid #ccc; margin: 5px 0; }}
        section.term {{ border-top: 1px solid #ddd; padding: 6px 0; margin-bottom: 8px; }}
        .class-header-wrapper {{
            width: 100vw;
            position: relative;
            left: -20px;
            background: #dfe5d8;
            padding: 8px 20px;
            box-sizing: border-box;
            margin-bottom: 8px;
            border-bottom: 1px solid #ccc; 
            border-top: 1px solid #ccc; 
        }}
        .class-header-wrapper h2 {{
            margin: 0;
            font-size: 1.1em;
            color: #003c71;
        }}
        .foreign-key-summary h4 {{
            margin-top: 20px;
            font-size: 1.1em;
            color: #003c71;
        }}
        .foreign-key-summary table td.label {{
            font-weight: bold;
            color: #003c71;
        }}
        .field-header-wrapper {{
            width: 100vw;
            position: relative;
            left: -20px;
            background: #cdd8de;
            padding: 4px 20px;
            box-sizing: border-box;
        }}
        .field-header-wrapper h3 {{
            margin: 0;
            font-size: 1em;
            color: #003c71;
        }}
        table.term-table {{ width: 100%; border-collapse: collapse; margin-top: 2px; }}
        table.term-table td {{ vertical-align: top; padding: 2px 3px; border-top: 1px solid #ccc; font-size: 0.9em; }}
        table.term-table td:first-child {{ border-left: none; }}
        table.term-table td.label {{ width: 20%; font-weight: bold; color: #003c71; }}
        .examples-content {{ color: #d63384; padding: 1px 0; }}
        .examples-separator {{ border-top: 1px solid #ccc; margin: 2px 0; }}
        footer {{ margin-top: 25px; font-size: 0.85em; color: #555; border-top: 1px solid #ccc; padding-top: 6px; }}
        .top-link {{ display: block; margin-bottom: 6px; font-weight: bold; text-decoration: none; color: #007BFF; }}
    </style>
</head>
<body>
    <main>
        <h1 id="top">Darwin Core Data Package - Quick Reference Guide</h1>
        <h2 id="top">Introduction</h2>
        <div class="intro">
            <p>This guide is provided to assist users to understand the structure and content of Darwin Core Data Packages. The Darwin Core Data Package (DwC-DP) is an implementation of the Darwin Core Conceptual Model following the specifications in the <a href="https://gbif.github.io/dwc-dp/dp/" target="_blank">Darwin Core Data Package Guide</a>.</p>

<p>This quick reference guide is in support of the DwC-DP and is distinct from the <a href="https://dwc.tdwg.org/terms/" target="_blank">Darwin Core Quick Reference Guide</a>. It provides a navigable reference to the vast array of options for tables and fields that can be used for sharing biodiversity data using DwC-DP.</p>

<p>DwC-DP is implemented using tables, most of which correspond directly to classes in Darwin Core. The sidebar at the right provides quick access to table definitions, and the definitions of available fields for each table. For an overview of the tables and their relationships, see the <a href="#model">Visual Summary</a>. Supplementary to this document is the <a href="https://gbif.github.io/dwc-dp/explorer/" target="_blank">Darwin Core Data Package Relationship Explorer</a>, which provides an interactive visual guide to the relationships between tables in DwC-DP.</p>
        </div>
        {content}
        <h1 id="model">Visual Summary</h1>
        <p>The diagram below shows an overview of the DwC-DP tables (boxes) and the relationships between them (arrows). To avoid clutter, the diagram simplifies the representation of the model in a variety of ways. First, myriad join tables (tables that connect two classes in many-to-many relationships, e.g., EventMedia, MaterialMedia, OccurrenceMedia, etc.) are represented with stacks of boxes by category (e.g., under the box labeled ...Media) rather than with separate boxes for each join table. The relationships to the tables connected through the join tables are represented by single arrows (e.g., to the Media table) and the label "join to" rather than the myriad arrows that would otherwise be required. 
        Second, the directionality of the relationships are shown with arrows, but the fields that connect the tables (keys), the cardinality of those connections (uniqueness and whether they are required), and the nature of the relationships (predicates) are not shown. The keys, cardinality and predicates are all shown in the sections for each table titled "Relationships to Other Tables".</p>
        <div class="intro">
            <img src="../images/dwc-dp-schema-overview.png" alt="How tables relate to each other.">
            <div class="figure-caption">Figure 1. Overview of the Darwin Core Data Package (DwC-DP), showing tables (classes) and their relationships to each other. To further explore the relationships between tables, see the <a href="https://gbif.github.io/dwc-dp/explorer/" target="_blank">Darwin Core Data Package Relationship Explorer</a>.</div>
        </div>
        <footer>
            <p>Version: {version}</p>
        </footer>
    </main>
    <aside class="nav-menu">
        <a class="top-link" href="#top">&uarr; Top</a>
        <a class="top-link" href="#model">&darr; Visual Summary</a>
        <a class="top-link" href="https://gbif.github.io/dwc-dp/explorer/" target="_blank">Relationship Explorer</a>
        <h3>Tables</h3>
        <nav class="class-index">
            {class_links}
        </nav>
    </aside>
</body>
</html>'''

def build_term_section(field, class_name):
    rows = []
    if not isinstance(field, dict):
        return ''
    order = ["title", "namespace", "class", "iri", "description", "comments", "example", "type", "default", "constraints", "format", "iri_version"]
    labels = {"title": "Title (Label)", "class": "Table:", "namespace": "Namespace", "iri": "IRI", "description": "Description",
              "comments": "Comments", "example": "Examples", "type": "Type", "default": "Default", "constraints": "Constraints", "format": "Format", "iri_version": "Source"}

    for key in order:
        value = field.get(key)
        # Hide Format if default
        if key == 'format' and str(value or '').strip().lower() == 'default':
            continue
        # Use field IRI for the Source row
        if key == 'iri_version':
            value = field.get('iri')
        if value is None:
            if key == 'class':
                value = class_name
            else:
                continue
        value = str(value).strip()
        if not value:
            continue
        if key == 'iri' or key == 'iri_version':
            value = f'<a href="{value}" target="_blank">{value}</a>'
        if key == 'class':
            value = f'<a href="#{value}" target="_blank">{value}</a>'
        elif key == 'example':
            examples = [ex.strip() for ex in str(value).split(';') if ex.strip()]
            value = ''
            for i, ex in enumerate(examples):
                if i > 0:
                    value += '<div class="examples-separator"></div>'
                value += f'<div class="examples-content">{ex}</div>'
        rows.append(f'<tr><td class="label">{labels[key]}</td><td>{value}</td></tr>')
    if not rows:
        return ''
    field_name = field.get("name", "").strip()
    full_id = f"{class_name}__{field_name}"
    return f'<section class="term" id="{full_id}">\n<div class="field-header-wrapper"><h3 id="{full_id}">{field.get("name", "(no name)")}</h3></div>\n<table class="term-table">' + ''.join(rows) + '</table>\n</section>'

def generate_field_links(fields, class_name):
    return ''.join([
        f'<a class="field-box" href="#{class_name}__{field.get("name", "").strip()}">{field.get("name", "").strip()}</a>'

        for field in fields if isinstance(field, dict) and field.get("name")
    ])


def build_foreign_key_summary(table_schema, current_table_name=None):
    fks = table_schema.get("foreignKeys", [])
    if not fks:
        return ""

    fk_rows = []
    for fk in fks:
        predicate = fk.get("predicate", "")
        src_fields = fk.get("fields")
        ref = fk.get("reference", {}) or {}
        tgt_table = ref.get("resource", "")
        tgt_fields = ref.get("fields")

        # Normalize to lists
        src_fields = [src_fields] if isinstance(src_fields, str) else src_fields
        tgt_fields = [tgt_fields] if isinstance(tgt_fields, str) else tgt_fields

        # Self-referential FK: empty resource means same table
        tgt_table_display = tgt_table if (isinstance(tgt_table, str) and tgt_table.strip()) else (current_table_name or tgt_table)

        for src, tgt in zip(src_fields or [], tgt_fields or []):
            fk_rows.append((src, predicate, tgt_table_display, tgt))

        # Requiredness map
    # Coerce "required" to a real boolean (supports bool/int/str) and also check top-level field["required"]
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

    table_html = ['<div class="foreign-key-summary">']
    table_html.append('<h4>Relationships to Other Tables</h4>')
    table_html.append('<table class="term-table">')
    table_html.append('<tr><td class="label">Field</td><td>Predicate</td><td>Target Table</td><td>Target Field</td><td>Required</td></tr>')

    for src, predicate, tgt_table, tgt_field in fk_rows:
        required = "Yes" if field_required_map.get(src, False) else "No"
        table_html.append(f'<tr><td class="label">{src}</td><td>{predicate}</td><td>{tgt_table}</td><td>{tgt_field}</td><td>{required}</td></tr>')

    table_html.append('</table></div>')
    return '\n'.join(table_html)


def generate_qrg_with_separators():
    print(f"Loading index from {INDEX_JSON_PATH}...")
    with open(INDEX_JSON_PATH, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    tables = index_data.get('tableSchemas', [])
    table_map = {table['name']: table for table in tables}

    content = ''
    class_links = ''
    inline_links = ''

    all_predicates = []

    for group_idx, group in enumerate(ORDERED_GROUPS):
        print(f"Processing group {group_idx + 1} with tables: {group}")
        for table_name in group:
            table = table_map.get(table_name)
            if not table:
                print(f"Warning: table '{table_name}' not found in index.json")
                continue
            class_name = table.get('title', table_name)
            table_file = os.path.join(TABLE_SCHEMAS_DIR, f'{table_name}.json')
            if not os.path.isfile(table_file):
                print(f"Warning: schema file for '{table_name}' not found at {table_file}")
                continue
            print(f"Loading schema for {table_name}...")
            with open(table_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            fields = schema.get('fields', [])
            content += f'<div class="class-header-wrapper"><h2 id="{class_name}" class="class-header">{class_name}</h2></div>'
            if "identifier" in table and table["identifier"]:
                content += f'<p><strong>Identifier:</strong> {table.get("identifier")}</p>'
            content += f'<p><strong>Description:</strong> {table.get("description", "No description.")}</p>'
            if "comments" in table and table["comments"]:
                content += f'<p><strong>Comments:</strong> {table.get("comments")}</p>'

            if table.get("example"):
                content += f'<p><strong>Examples:</strong></p>'
                examples = [ex.strip() for ex in str(table.get("example")).split(';') if ex.strip()]
                value = ''
                for i, ex in enumerate(examples):
                    if i > 0:
                        value += '<div class="examples-separator"></div>'
                    value += f'<div class="examples-content">{ex}</div>'
                content += value
            # Table-level Source from "iri"
            if table.get("iri"):
                src = str(table.get("iri")).strip()
                try:
                    if src.startswith("http://") or src.startswith("https://"):
                        content += f'<p><strong>Source:</strong> <a href="{src}" target="_blank">{src}</a></p>'
                    else:
                        content += f'<p><strong>Source:</strong> {src}</p>'
                except Exception:
                    content += f'<p><strong>Source:</strong> {src}</p>'


            # Add FK summary block for the current class (only if table schema is available)
            table_schema_path = os.path.join(TABLE_SCHEMAS_DIR, f'{table_name}.json')
            if os.path.isfile(table_schema_path):
                with open(table_schema_path, 'r', encoding='utf-8') as tf:
                    table_schema = json.load(tf)
                # Collect predicate mappings for explorer/predicates.js
                for fk in (table_schema.get('foreignKeys') or []):
                    pred = fk.get('predicate', '')
                    src_fields = fk.get('fields')
                    ref = fk.get('reference', {}) or {}
                    tgt_table = ref.get('resource', '')
                    tgt_fields = ref.get('fields')
                    src_fields = [src_fields] if isinstance(src_fields, str) else src_fields
                    tgt_fields = [tgt_fields] if isinstance(tgt_fields, str) else tgt_fields
                    tgt_table_display = tgt_table if (isinstance(tgt_table, str) and tgt_table.strip()) else table_name
                    for s, t in zip(src_fields or [], tgt_fields or []):
                        all_predicates.append({
                            'subject_table': table_name,
                            'subject_field': s,
                            'predicate': pred,
                            'related_table': tgt_table_display,
                            'related_field': t
                        })

                content += build_foreign_key_summary(table_schema, table_name)

            field_links = generate_field_links(fields, class_name)
            if field_links:
                content += f'<nav class="field-index"><strong>Fields:</strong><br>{field_links}</nav>'
            for field in fields:
                term_html = build_term_section(field, class_name)
                if term_html:
                    content += term_html

            class_links +=  f'<a class="class-box" href="#{class_name}">{class_name}</a>'
            inline_links += f'<a class="class-box" href="#{class_name}">{class_name}</a>'
        class_links += '<div class="menu-separator"></div>'
        inline_links += '<div class="menu-separator"></div>'

        # Write explorer/indexJson.js with the tableSchemas currently loaded
    try:
        js_obj = {"tableSchemas": tables}
        js_str = 'const indexJson = ' + json.dumps(js_obj, ensure_ascii=False, indent=2) + ';\n'
        os.makedirs(os.path.dirname(JS_INDEX_JSON_PATH), exist_ok=True)
        with open(JS_INDEX_JSON_PATH, 'w', encoding='utf-8') as jsf:
            jsf.write(js_str)
        print(f"Wrote {JS_INDEX_JSON_PATH}")
    except Exception as e:
        print(f"Warning: could not write {JS_INDEX_JSON_PATH}: {e}")
    # Write explorer/indexJson.js and explorer/predicates.js
    try:
        # indexJson.js
        js_obj = {'tableSchemas': tables}
        js_str = 'const indexJson = ' + json.dumps(js_obj, ensure_ascii=False, indent=2) + ';\n'
        os.makedirs(os.path.dirname(JS_INDEX_JSON_PATH), exist_ok=True)
        with open(JS_INDEX_JSON_PATH, 'w', encoding='utf-8') as jsf:
            jsf.write(js_str)
        # predicates.js
        preds_str = 'let predicates = ' + json.dumps(all_predicates, ensure_ascii=False, indent=2) + ';\n'
        os.makedirs(os.path.dirname(JS_PREDICATES_PATH), exist_ok=True)
        with open(JS_PREDICATES_PATH, 'w', encoding='utf-8') as pf:
            pf.write(preds_str)
        print(f"Wrote {JS_INDEX_JSON_PATH} and {JS_PREDICATES_PATH}")
    except Exception as e:
        print(f"Warning: could not write explorer JS outputs: {e}")
    print("Assembling final HTML output...")
    html = TEMPLATE.format(content=content, class_links=class_links, inline_class_links=inline_links, version=args.version)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
        out.write(html)
    print(f"Quick Reference Guide generated at {OUTPUT_PATH}")

def main():
    # Stage 1
    # Expect acquisition of original CSV data in vocabulary/ to produce data package 
    # artifacts in INDEX_JSON_PATH
    make_index_stage(os.path.dirname(INDEX_JSON_PATH), args.version)

    # Stage 2
    # Expect generate_qrg_with_separators() to read index.json at INDEX_JSON_PATH 
    # and produce output
    if 'generate_qrg_with_separators' in globals():
        generate_qrg_with_separators()
    else:
        raise RuntimeError("generate_qrg_with_separators() not found in embedded QRG code.")

if __name__ == "__main__":
    main()
