#!/usr/bin/env python3
#
# Script to check that the table descriptions in the local ../dwc-dp/0.1/index.json file 
# are the same as the table descriptions in the table schema files in 
# ../dwc-dp/0.1/table-schemas.

import json
import os
import requests

path_to_index = "../dwc-dp/0.1/"
# Load index.json
with open(f"{path_to_index}index.json", 'r') as f:
    index_data = json.load(f)

# Define the local directory where the table schema JSON files are stored
local_table_schemas_dir = f"{path_to_index}table-schemas"

# Iterate over each tableSchema
for schema in index_data['tableSchemas']:
    name = schema['name']
    index_description = schema.get('description', '').strip()
    url = schema['url'].replace('blob/', '')  # Adjust URL to raw format
    raw_url = url.replace('github.com', 'raw.githubusercontent.com')
    local_schema_path = os.path.join(local_table_schemas_dir, f"{name}.json")

    print(f"Checking '{name}'...")

    # Compare with local copy (if it exists)
    if os.path.exists(local_schema_path):
        try:
            with open(local_schema_path, 'r') as lf:
                local_data = json.load(lf)
            local_description = local_data.get('description', '').strip()
            if index_description != local_description:
                print(f"❗ Discrepancy in local '{name}':")
                print(f"- index.json description: {index_description}")
                print(f"- Local schema description: {local_description}\n")
        except Exception as e:
            print(f"⚠️ Error reading local file '{local_schema_path}': {e}")
    else:
        print(f"ℹ️ Local schema file not found: {local_schema_path}")

#     # Compare with GitHub (online) copy
#     try:
#         response = requests.get(raw_url)
#         response.raise_for_status()
#         remote_data = response.json()
#         remote_description = remote_data.get('description', '').strip()
#         if index_description != remote_description:
#             print(f"❗ Discrepancy in GitHub '{name}':")
#             print(f"- index.json description: {index_description}")
#             print(f"- GitHub schema description: {remote_description}\n")
#     except Exception as e:
#         print(f"⚠️ Error fetching GitHub schema for '{name}': {e}")

print("✅ Comparison complete.")
