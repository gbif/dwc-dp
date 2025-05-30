# Python script to generate the Quick Reference Guide HTML (custom order with separators)
# Usage: python generate_qrg.py

import json
import os

ordered_groups = [
    ['event', 'occurrence', 'organism-interaction', 'survey', 'survey-target'],
    ['identification', 'identification-taxon'],
    ['material', 'collection'],
    ['nucleotide-analysis', 'molecular-protocol', 'nucleotide-sequence'],
    ['phylogenetic-tree', 'phylogenetic-tree-tip'],
    ['agent', 'agent-agent-role', 'chronometric-age-agent-role', 'collection-agent-role', 'event-agent-role',
     'identification-agent-role', 'material-agent-role', 'media-agent-role', 'molecular-protocol-agent-role',
     'nucleotide-analysis-agent-role', 'occurrence-agent-role', 'organism-interaction-agent-role', 'survey-agent-role'],
    ['media', 'agent-media', 'chronometric-age-media', 'collection-media', 'event-media', 'geological-context-media',
     'material-media', 'occurrence-media', 'organism-interaction-media', 'phylogenetic-tree-media', 'survey-media'],
    ['protocol', 'chronometric-age-protocol', 'event-protocol', 'material-protocol', 'occurrence-protocol',
     'phylogenetic-tree-protocol', 'survey-protocol'],
    ['reference', 'chronometric-age-reference', 'event-reference', 'material-reference', 'molecular-protocol-reference',
     'organism-interaction-reference', 'phylogenetic-tree-reference', 'survey-reference'],
    ['chronometric-age-assertion', 'collection-assertion', 'event-assertion', 'identification-assertion',
     'material-assertion', 'media-assertion', 'molecular-protocol-assertion', 'nucleotide-analysis-assertion',
     'occurrence-assertion', 'organism-interaction-assertion', 'phylogenetic-tree-assertion',
     'phylogenetic-tree-tip-assertion', 'survey-assertion'],
    ['agent-identifier', 'event-identifier', 'material-identifier', 'media-identifier', 'occurrence-identifier',
     'phylogenetic-tree-identifier', 'survey-identifier'],
    ['relationship']
]

INDEX_JSON_PATH = '../dwc-dp/0.1/index.json'
TABLE_SCHEMAS_DIR = '../dwc-dp/0.1/table-schemas'
OUTPUT_PATH = '../qrg/index.html'

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
        .figure-caption {{ font-size: 0.88em; color: #555; text-align: center; margin-top: 4px; }}
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
        <div class="intro">
            <p>This Quick Reference Guide provides an exploratory overview of tables and fields defined in the <a href="https://gbif.github.io/dwc-dp/">Darwin Core Data Package</a> (DwC-DP). The guide at the right provides quick access to table definitions, under each of which are listed the possible fields in the table and their definitions.</p>
        </div>
        {content}
        <h1 id="model">Table Relationships</h1>
        <div class="intro">
            <img src="../images/overview_model_2025-05-07.png" alt="How tables relate to each other.">
            <div class="figure-caption">Figure 1. Overview of the Darwin Core Data Package (DwC-DP), showing tables (classes) and their relationships to each other.</div>
        </div>
        <footer>
            <p>This guide is part of the Darwin Core Data Package project and is provided to assist users in applying the standard consistently. For authoritative definitions and updates, visit the <a href="https://dwc.tdwg.org/">Darwin Core website</a>.</p>
        </footer>
    </main>
    <aside class="nav-menu">
        <a class="top-link" href="#top">&uarr; Back to Top</a>
        <a class="top-link" href="#model">&darr; Table Relationships</a>
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
    order = ["title", "namespace", "class", "iri", "description", "comments", "examples", "type", "default", "constraints", "format"]
    labels = {"title": "Title (Label)", "class": "Table:", "namespace": "Namespace", "iri": "IRI", "description": "Description",
              "comments": "Comments", "examples": "Examples", "type": "Type", "default": "Default", "constraints": "Constraints", "format": "Format"}

    for key in order:
        value = field.get(key)
        if value is None:
            if key == 'class':
                value = class_name
            else:
                continue
        value = str(value).strip()
        if not value:
            continue
        if key == 'iri':
            value = f'<a href="{value}">{value}</a>'
        if key == 'class':
            value = f'<a href="#{value}">{value}</a>'
        elif key == 'examples':
            examples = [ex.strip() for ex in value.split(';') if ex.strip()]
            value = ''
            for i, ex in enumerate(examples):
                if i > 0:
                    value += '<div class="examples-separator"></div>'
                value += f'<div class="examples-content">{ex}</div>'
        rows.append(f'<tr><td class="label">{labels[key]}</td><td>{value}</td></tr>')
    if not rows:
        return ''
    return f'<section class="term" id="{field.get("name", "").strip()}">\n<div class="field-header-wrapper"><h3 id="{field.get("name", "").strip()}">{field.get("name", "(no name)")}</h3></div>\n<table class="term-table">' + ''.join(rows) + '</table>\n</section>'

def generate_qrg_with_separators():
    print(f"Loading index from {INDEX_JSON_PATH}...")
    with open(INDEX_JSON_PATH, 'r', encoding='utf-8') as f:
        index_data = json.load(f)

    tables = index_data.get('tableSchemas', [])
    table_map = {table['name']: table for table in tables}

    content = ''
    class_links = ''
    inline_links = ''

    for group_idx, group in enumerate(ordered_groups):
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
            content += f'<p><strong>Description:</strong> {table.get("description", "No description.")}</p>'
            field_links = ''.join([f'<a class="field-box" href="#{field.get("name", "").strip()}">{field.get("name", "").strip()}</a>' for field in fields if isinstance(field, dict) and field.get("name")])
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

    print("Assembling final HTML output...")
    html = TEMPLATE.format(content=content, class_links=class_links, inline_class_links=inline_links)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out:
        out.write(html)
    print(f"Quick Reference Guide generated at {OUTPUT_PATH}")

if __name__ == '__main__':
    generate_qrg_with_separators()
