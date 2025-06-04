import os
import json
import pandas as pd

# Set the directory containing your table schema JSON files
SCHEMA_DIR = "../dwc-dp/0.1/table-schemas"  # Adjust if your directory is different
OUTPUT_CSV = "summary_foreign_keys.csv"

records = []

# Process each JSON file in the directory
for filename in sorted(os.listdir(SCHEMA_DIR)):
    if filename.startswith("._") or not filename.endswith(".json"):
        continue
    filepath = os.path.join(SCHEMA_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    subject_table = filename.replace(".json", "")
    fields = schema.get("fields", [])
    field_order = {field["name"]: i for i, field in enumerate(fields) if "name" in field}

    foreign_keys = schema.get("foreignKeys", [])
    for fk in foreign_keys:
        subject_fields = fk.get("fields", [])
        reference = fk.get("reference", {})
        related_fields = reference.get("fields", [])
        related_table = reference.get("resource", "")

        # Ensure lists
        if not isinstance(subject_fields, list):
            subject_fields = [subject_fields]
        if not isinstance(related_fields, list):
            related_fields = [related_fields]

        for sub_f, rel_f in zip(subject_fields, related_fields):
            records.append({
                "subject_table": subject_table,
                "subject_field": sub_f,
                "predicate": f"{sub_f} → {rel_f}",
                "related_table": related_table,
                "related_field": rel_f,
                "field_order": field_order.get(sub_f, 9999)
            })

# Create DataFrame and sort
df = pd.DataFrame(records)
df.sort_values(by=["subject_table", "field_order"], inplace=True)
df.drop(columns=["field_order"], inplace=True)

# Write output
df.to_csv(OUTPUT_CSV, index=False)
print(f"Wrote {len(df)} rows to {OUTPUT_CSV}")
