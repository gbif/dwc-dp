#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run DwC-DP build in two stages:
Stage 1) read the csv files in ../vocabulary and generate:
  ../dwc-dp/index.json
  ../dwc-dp/version.json
  ../dwc-dp/table-schemas/*.json

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
from datetime import date

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
INDEX_JSON_PATH = '../dwc-dp/index.json'
TABLE_SCHEMAS_DIR = '../dwc-dp/table-schemas'

print(f"Using INDEX_JSON_PATH: {INDEX_JSON_PATH}")
print(f"Using TABLE_SCHEMAS_DIR: {TABLE_SCHEMAS_DIR}")

# Ensure output dir exists
os.makedirs(os.path.dirname(INDEX_JSON_PATH), exist_ok=True)
os.makedirs(TABLE_SCHEMAS_DIR, exist_ok=True)

def _parse_scalar(s):
    """Coerce CSV cell text to proper JSON scalars (bool/int/float/None/str)."""
    if s is None:
        return None
    t = str(s).strip()
    if t == "":
        return None
    low = t.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    try:
        # try numbers (int first unless float-like)
        if "." in t or "e" in low:
            return float(t)
        return int(t)
    except ValueError:
        return t

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
            if iri == "":
                iri = f'http://example.com/term-pending/{namespace}/{name}'
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
                "dcterms:references": iri_version,
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
            if iri == "":
                iri = f'http://example.com/term-pending/{namespace}/{name}'
            iri_version = (row.get("dcterms:references", "") or "").strip()
            rdfs_comment = (row.get("rdfs:comment", "") or "").strip()

            # Track pk / fk
            key_val = (row.get("key", "") or "").strip().lower()
            if key_val == "pk":
                pk_names.append(name)
            elif key_val == "fk":
                fk_field_names.append(name)

            # Constraints (coerce CSV strings to proper JSON scalars)
            constraints_candidates = {
                "required": _parse_scalar(row.get("required")),
                "unique": _parse_scalar(row.get("unique")),
                "minimum": _parse_scalar(row.get("minimum")),
                "maximum": _parse_scalar(row.get("maximum")),
            }
            # Keep only keys with real values (None means "absent")
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
                "dcterms:references": iri_version,
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
#        resource = related_table
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
        "url": f"",
        "name": "dwc-dp",
        "version": version,
        "title": "Darwin Core Data Package",
        "shortTitle": "dwc-dp",
        "description": "A data package for sharing biodiversity data using Darwin Core.",
        "issued": date.today().strftime("%Y-%m-%d"),
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

#table1-scope ol{{margin:0;padding:0}}
#table1-scope table td, #table1-scope table th{{padding:0}}
#table1-scope .c3{{border-right-style:solid;padding:5pt 5pt 5pt 5pt;border-bottom-color:#000000;border-top-width:1pt;border-right-width:1pt;border-left-color:#000000;vertical-align:top;border-right-color:#000000;border-left-width:1pt;border-top-style:solid;background-color:#b6d7a8;border-left-style:solid;border-bottom-width:1pt;width:214.5pt;border-top-color:#000000;border-bottom-style:solid}}
#table1-scope .c6{{border-right-style:solid;padding:5pt 5pt 5pt 5pt;border-bottom-color:#000000;border-top-width:1pt;border-right-width:1pt;border-left-color:#000000;vertical-align:top;border-right-color:#000000;border-left-width:1pt;border-top-style:solid;border-left-style:solid;border-bottom-width:1pt;width:69.8pt;border-top-color:#000000;border-bottom-style:solid}}
#table1-scope .c11{{border-right-style:solid;padding:5pt 5pt 5pt 5pt;border-bottom-color:#000000;border-top-width:1pt;border-right-width:1pt;border-left-color:#000000;vertical-align:top;border-right-color:#000000;border-left-width:1pt;border-top-style:solid;border-left-style:solid;border-bottom-width:1pt;width:45%;border-top-color:#000000;border-bottom-style:solid}}
#table1-scope .c7{{border-right-style:solid;padding:5pt 5pt 5pt 5pt;border-bottom-color:#000000;border-top-width:1pt;border-right-width:1pt;border-left-color:#000000;vertical-align:top;border-right-color:#000000;border-left-width:1pt;border-top-style:solid;border-left-style:solid;border-bottom-width:1pt;width:45%;border-top-color:#000000;border-bottom-style:solid}}
#table1-scope .c17{{border-right-style:solid;padding:5pt 5pt 5pt 5pt;border-bottom-color:#000000;border-top-width:0pt;border-right-width:1pt;border-left-color:#000000;vertical-align:top;border-right-color:#000000;border-left-width:0pt;border-top-style:solid;border-left-style:solid;border-bottom-width:1pt;width:10%;border-top-color:#000000;border-bottom-style:solid}}
#table1-scope .c5{{background-color:#ffffff;padding-top:0pt;padding-bottom:1.3em;line-height:1.15;orphans:2;widows:2;text-align:left;height:1.2em}}
#table1-scope .c8{{color:#1f2328;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:1.3em;font-family:"Arial";font-style:normal}}
#table1-scope .c14{{color:#000000;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:1.2em;font-family:"Arial";font-style:normal}}
#table1-scope .c1{{color:#1f2328;font-weight:400;text-decoration:none;vertical-align:baseline;font-size:.90em;font-family:"Arial";font-style:normal}}
#table1-scope .c15{{background-color:#ffffff;padding-top:0pt;padding-bottom:1.3em;line-height:1.15;orphans:2;widows:2;text-align:left}}
#table1-scope .c0{{text-decoration-skip-ink:none;font-size:.90em;-webkit-text-decoration-skip:none;color:#1155cc;text-decoration:underline}}
#table1-scope .c2{{padding-top:0pt;padding-bottom:0pt;line-height:1.0;text-align:left}}
#table1-scope .c12{{border-spacing:0;border-collapse:collapse;margin-right:auto}}
#table1-scope .c9{{padding-top:0pt;padding-bottom:0pt;line-height:1.0;text-align:center}}
#table1-scope .c19{{text-decoration:none;vertical-align:baseline;font-family:"Arial";font-style:normal}}
#table1-scope .c13{{color:#1f2328;font-size:1.3em;font-weight:700}}
#table1-scope .c10{{background-color:#ffffff;max-width:468pt;padding:72pt 72pt 72pt 72pt}}
#table1-scope .c20{{color:inherit;text-decoration:inherit}}
#table1-scope .c16{{height:1.2em}}
#table1-scope .c4{{height:0pt}}
#table1-scope .c18{{background-color:#a2c4c9}}
#table1-scope .title{{padding-top:0pt;color:#000000;font-size:26pt;padding-bottom:3pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}}
#table1-scope .subtitle{{padding-top:0pt;color:#666666;font-size:15pt;padding-bottom:16pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}}
#table1-scope li{{color:#000000;font-size:1.2em;font-family:"Arial"}}
#table1-scope p{{margin:0;color:#000000;font-size:1.2em;font-family:"Arial"}}
#table1-scope h1{{padding-top:20pt;color:#000000;font-size:20pt;padding-bottom:6pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}}
#table1-scope h2{{padding-top:18pt;color:#000000;font-size:16pt;padding-bottom:6pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}}
#table1-scope h3{{padding-top:16pt;color:#434343;font-size:14pt;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}}
#table1-scope h4{{padding-top:14pt;color:#666666;font-size:1.3em;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}}
#table1-scope h5{{padding-top:1.3em;color:#666666;font-size:1.2em;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;orphans:2;widows:2;text-align:left}}
#table1-scope h6{{padding-top:1.3em;color:#666666;font-size:1.2em;padding-bottom:4pt;font-family:"Arial";line-height:1.15;page-break-after:avoid;font-style:italic;orphans:2;widows:2;text-align:left}}
    </style>
</head>
<body>
    <main>
        <h1 id="top">Darwin Core Data Package - Quick Reference Guide</h1>
        <h2 id="top">Introduction</h2>
        <div class="intro">
            <p>This guide is provided to assist users to understand the structure and content of Darwin Core Data Packages. The Darwin Core Data Package (DwC-DP) is an implementation of the Darwin Core Conceptual Model following the specifications in the <a href="https://gbif.github.io/dwc-dp/dp/" target="_blank">Darwin Core Data Package Guide</a>.</p>
            
This Quick Reference Guide is distinct from the classic <a href="https://dwc.tdwg.org/terms/" target="_blank">Darwin Core Quick Reference Guide</a> in that this guide contains information beyond the simple term definitions. It includes all the information about how to use Darwin Core in the context of a Darwin Core Data Package. That means it includes data types, value constraints, table relationship constraints and repeats these everywhere in the structure that a given term is found. This guide makes reference to numerous terms borrowed from standard vocabularies, both internal and external to TDWG, other than the Darwin Core. In general these terms are not in the classical Darwin Core reference guide nor in the Darwin Core list of terms as they are externally managed and reused in this context.

<p>DwC-DP is implemented using tables, most of which correspond directly to classes in Darwin Core. The sidebar at the right provides quick access to table definitions, and the definitions of available fields for each table. For an overview of the tables and their relationships, see the <a href="#model">Visual Summary</a>. Supplementary to this document is the <a href="https://gbif.github.io/dwc-dp/explorer/" target="_blank">Darwin Core Data Package Relationship Explorer</a>, which provides an interactive visual guide to the relationships between tables in DwC-DP.</p>
        </div>
        {content}
        <h1 id="model">Visual Summary</h1>
        <p>The diagram below shows an overview of the DwC-DP tables (boxes) and the relationships between them (arrows). To avoid clutter, the diagram simplifies the representation of the model in a variety of ways. First, myriad join tables (tables that connect two classes in many-to-many relationships, e.g., EventMedia, MaterialMedia, OccurrenceMedia, etc.) are represented with stacks of boxes by category (e.g., under the box labeled ...Media) rather than with separate boxes for each join table. The relationships to the tables connected through the join tables are represented by single arrows (e.g., to the Media table) and the label "join to" rather than the myriad arrows that would otherwise be required. 
        Second, the directionality of the relationships are shown with arrows, but the fields that connect the tables (keys), the cardinality of those connections (uniqueness and whether they are required), and the nature of the relationships (predicates) are not shown. The keys, cardinality and predicates are all shown in the sections for each table titled "Relationships to Other Tables".</p>
        <div class="intro">
            <img src="../images/dwc-dp-schema-overview.png" alt="How tables relate to each other.">
            <div class="figure-caption"><b>Figure 1</b>. Overview of the Darwin Core Data Package (DwC-DP), showing tables (classes) and their relationships to each other. To further explore the relationships between tables, see the <a href="https://gbif.github.io/dwc-dp/explorer/" target="_blank">Darwin Core Data Package Relationship Explorer</a>.</div>
        </div>
        <h1 id="dwca">Darwin Core Data Packages (DwC-DP) vs Darwin Core Archives (DwC-A)</h1>
        <p>Both Darwin Core Data Packages (DwC-DP) and Darwin Core Archives (DwC-A) are implementation schemas that use the Darwin Core Standard to share biodiversity-related data.</p>
        <p>DwC-DP fully supports non-checklist datasets traditionally published as DwC-As (observations and physical specimens, with extensions), but it goes far beyond, allowing richer data to be shared from these traditional datasets than was hitherto supported. Also, it empowers those who desire to share entirely new types of data (biotic surveys with inferred absence and abundance, hierarchical material entities, organism interactions, and nucleotide analyses, among others) via Darwin Core.</p>
        <p><b>Table 1</b>. Main differences between DwC-A and DwC-DP.</p>

<div id="table1-scope">
<!-- Begin Table 1 -->
<table class="c12">
  <tr class="c4">
    <td class="c17" colspan="1" rowspan="1">
      <p class="c2 c16">
        <span class="c1"></span>
      </p>
    </td>
    <td class="c7 c18" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c13 c19">DwC-A</span>
      </p>
    </td>
    <td class="c3" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c19 c13">DwC-DP</span>
      </p>
    </td>
  </tr>
  <tr class="c4">
    <td class="c6" colspan="1" rowspan="1">
      <p class="c2">
        <span class="c1">Guide</span>
      </p>
    </td>
    <td class="c7" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c0">
          <a class="c20" href="https://www.google.com/url?q=https://dwc.tdwg.org/text/&amp;sa=D&amp;source=editors&amp;ust=1757646648470339&amp;usg=AOvVaw0zaty2v3h6OXNdwceNwCNA">Darwin Core Text Guide</a>
        </span>
      </p>
    </td>
    <td class="c11" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c0">
          <a class="c20" href="https://www.google.com/url?q=https://gbif.github.io/dwc-dp/dp/&amp;sa=D&amp;source=editors&amp;ust=1757646648470904&amp;usg=AOvVaw3ra1ABtWFfnxHblBoA1JiV">Darwin Core Data Package Guide</a>
        </span>
      </p>
    </td>
  </tr>
  <tr class="c4">
    <td class="c6" colspan="1" rowspan="1">
      <p class="c2">
        <span class="c1">Data structure</span>
      </p>
    </td>
    <td class="c7" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c1">Limited&#58; &ldquo;Star schema&rdquo;, with a &ldquo;Core&rdquo; file and optional &ldquo;Extensions&rdquo;.<br><br>Relationships only <b>from</b> Extensions <b>to</b> the Core.<br><br>Flattened, &ldquo;spreadsheet-like&rdquo;<br><br>Defined in&#58; meta.xml</span>
      </p>
    </td>
    <td class="c11" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c1">Relational&#58; No &ldquo;Core&rdquo;, no &ldquo;Extensions&rdquo;, just tables.<br><br>Multiple relationships <b>between</b> tables (Figure 1), details in the table definitions.<br><br>Relational, &ldquo;database-like&rdquo;<br><br>Defined in&#58; datapackage.json</span>
      </p>
    </td>
  </tr>
  <tr class="c4">
    <td class="c6" colspan="1" rowspan="1"><p class="c2"><span class="c1">Table types</span></p></td>
    <td class="c7" colspan="1" rowspan="1"><p class="c9"><span class="c1">Cores&#58; Event, Occurrence, Taxon<br><br>Extensions&#58; Chronometric Age, DNA, Identification, Identifier, Literature Reference, Media, MeasurementsOrFact, Survey</span></p></td>
    <td class="c11" colspan="1" rowspan="1"><p class="c9"><span class="c1">Agent, Assertion, Bibliographic Resource, Chronometric Age, Event, Geological Context, Identification, Identifier, Material, Media, Molecular Protocol, Nucleotide Analysis, Nucleotide Sequence, Occurrence, Organism, Organism Interaction, Protocol, Provenance, Survey, Survey Target, Usage Policy</span></p></td>
  </tr>
  <tr class="c4">
    <td class="c6" colspan="1" rowspan="1">
      <p class="c2">
        <span class="c1">Semantics</span>
      </p>
    </td>
    <td class="c7" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c1">No explicit semantics</span>
      </p>
    </td>
        <td class="c11" colspan="1" rowspan="1">
      <p class="c9">
        <span class="c1"><a href="https://gbif.github.io/dwc-dp/dp/" target="_blank">Darwin Core Conceptual Model</a>
        </span>
      </p>
    </td>
  </tr>
  <tr class="c4">
    <td class="c6" colspan="1" rowspan="1"><p class="c2"><span class="c1">Dataset metadata</span></p></td>
    <td class="c7" colspan="1" rowspan="1"><p class="c9"><span class="c1">eml.xml</span></p></td>
    <td class="c11" colspan="1" rowspan="1"><p class="c9"><span class="c1">eml.xml</span></p></td>
  </tr>
  <tr class="c4">
    <td class="c6" colspan="1" rowspan="1"><p class="c2"><span class="c1">Data format</span></p></td>
    <td class="c7" colspan="1" rowspan="1"><p class="c9"><span class="c1">CSV, TSV</span></p></td>
    <td class="c11" colspan="1" rowspan="1"><p class="c9"><span class="c1">CSV, TSV</span></p></td>
  </tr>
</table>
  <!-- End Table 1 -->
</div>

        <div class="intro">
            <img src="../images/dwca_vs_dwcdp.png" alt="How tables relate to each other.">
            <div class="figure-caption"><b>Figure 2</b>. Schematic representations of DwC-A and DwC-DP. In DwC-A, "Extension" files can only be connected to "Core" file via the unique identifier for a row in the "Core" file. In DwC-DP, files can be connected in all of the ways shown in Figure 1.</div>
        </div>

        <footer>
            <p>Version: {version}</p>
        </footer>
    </main>
    <aside class="nav-menu">
        <a class="top-link" href="#top">&uarr; Top</a>
        <a class="top-link" href="#model">&darr; Visual Summary</a>
        <a class="top-link" href="#dwca">&darr; DwC-DP vs DwC-A</a>
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

    order = ["title", "namespace", "class", "description", 
        "comments", "examples", "type", "default", "constraints", "format", 
        "dcterms:isVersionOf", "dcterms:references"]

    labels = {"title": "Title (Label)", "class": "Table:", "namespace": "Namespace",
          "dcterms:isVersionOf": "dcterms:isVersionOf", "description": "Description",
          "comments": "Comments", 
          "examples": "Examples", "type": "Type", "default": "Default",
          "constraints": "Constraints", "format": "Format",
          "dcterms:references":"dcterms:references"}

    for key in order:
        value = field.get(key)
        # Hide Format if default
        if key == 'format' and str(value or '').strip().lower() == 'default':
            continue
        # Use field IRI for the dcterms:isVersionOf row
        if key == 'dcterms:isVersionOf':
            value = field.get('dcterms:isVersionOf')
        if value is None:
            if key == 'class':
                value = class_name
            else:
                continue
        if key == 'constraints' and isinstance(value, dict):
            # JSON renders booleans as lowercase true/false
            value = json.dumps(value, ensure_ascii=False)
        else:
            value = str(value).strip()
        if not value:
            continue
        if key in ('dcterms:isVersionOf', 'dcterms:references'):
            # Don’t link the generated placeholder IRI
            if not (value.startswith('http://example.com/term-pending/')
                    or value.startswith('https://example.com/term-pending/')):
                value = f'<a href="{value}" target="_blank">{value}</a>'
        if key == 'class':
            value = f'<a href="#{value}" target="_blank">{value}</a>'
        elif key == 'examples':
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
    table_html.append('<tr><td class="label">Field</td><td><b>Predicate</b></td><td><b>Target Table</b></td><td><b>Target Field</b></td><td><b>Required</b></td></tr>')

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

            ex_val = table.get("examples") or table.get("example")
            if ex_val:
                content += f'<p><strong>Examples:</strong></p>'
                examples = [ex.strip() for ex in str(ex_val).split(';') if ex.strip()]
                value = ''
                for i, ex in enumerate(examples):
                    if i > 0:
                        value += '<div class="examples-separator"></div>'
                    value += f'<div class="examples-content">{ex}</div>'
                content += value# Table-level Source from "dcterms:isVersionOf"

            if table.get("dcterms:isVersionOf"):
                src = str(table.get("dcterms:isVersionOf")).strip()
                try:
                    if src.startswith("http://") or src.startswith("https://"):
                        if "example.com" not in src:
                            content += f'<p><strong>dcterms:isVersionOf:</strong> <a href="{src}" target="_blank">{src}</a></p>'
                        else:
                            content += f'<p><strong>dcterms:isVersionOf:</strong> {src}</p>'
                    else:
                        content += f'<p><strong>dcterms:isVersionOf:</strong> {src}</p>'
                except Exception:
                        content += f'<p><strong>dcterms:isVersionOf:</strong> {src}</p>'

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
