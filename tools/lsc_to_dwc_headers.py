#!/usr/bin/env python3
# Python script to rewrite tables CSV/TSV files having lower_snake_case headers
# to CSV/TSV output having valid DwC property names
# Assumes files to process have lowercased extension in {.csv, .tsv, .txt}
#
# Usage: python lsc_to_dwc_headers.py -i path_to_input_table_files -o path_to_ouput_table_files

import os
import csv
import argparse
import json
import urllib.request

SCHEMA_BASE_URL = "https://raw.githubusercontent.com/gbif/rs.gbif.org/master/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas"

def normalize_fieldname(field):
    return field.lower().replace("-", "").replace("_", "")

def fetch_model_schema(table_name):
    url = f"{SCHEMA_BASE_URL}/{table_name}.json"
    try:
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    except Exception as e:
        print(f"Warning: Schema not found for '{table_name}' at URL: {url}")
        return None

def normalize_csv_headers(input_path, output_path):
    os.makedirs(output_path, exist_ok=True)

    for filename in os.listdir(input_path):
        input_file = os.path.join(input_path, filename)

        # Skip directories and JSON files
        if os.path.isdir(input_file) or filename.endswith(".json"):
            continue

        if filename.lower().endswith((".csv", ".tsv", ".txt")):
            table_name = os.path.splitext(filename)[0]
            schema = fetch_model_schema(table_name)
            if not schema:
                print(f"Skipping {filename}, no schema available.")
                continue

            output_file = os.path.join(output_path, filename)
            delimiter = "," if filename.endswith(".csv") else "\t"

            with open(input_file, newline='\n', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)

            if not rows:
                print(f"Skipping empty file: {filename}")
                continue

            original_headers = rows[0]
            normalized_headers = [normalize_fieldname(h) for h in original_headers]

            # Build mapping from normalized to Darwin Core names
            schema_fields = schema.get("fields", [])
            dwc_mapping = {normalize_fieldname(field["name"]): field["name"] for field in schema_fields}
            final_headers = [dwc_mapping.get(h, h) for h in normalized_headers]

            with open(output_file, "w", newline='\n', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=delimiter, lineterminator='\n')
                writer.writerow(final_headers)
                writer.writerows(rows[1:])

            print(f"Normalized and mapped headers in {filename} -> {output_path}")
        else:
            print(f"Skipping unsupported file: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize headers of CSV/TSV files to match Darwin Core names via schema lookup")
    parser.add_argument("-i", "--input", required=True, help="Path to folder containing input CSV/TSV files")
    parser.add_argument("-o", "--output", required=True, help="Path to folder for writing normalized output")

    args = parser.parse_args()
    normalize_csv_headers(args.input, args.output)
