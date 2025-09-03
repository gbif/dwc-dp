#!/usr/bin/env python3
#
# Script to bulk change schema identifiers and urls in data package index.json and schemas in table-schemas/.

# Syntax:
# python data-package-migration.py
# -i "http://rs.gbif.org/data-packages/dwc-dp" \
# -I "http://rs.tdwg.org/dwc/dwc-dp" \
# -u "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/2025-09-03" \
# -U "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/2025-09-03"

#python data-package-migration.py -i "http://rs.gbif.org/data-packages/dwc-dp" -I "http://rs.tdwg.org/dwc/dwc-dp" -u "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/2025-09-03" -U "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/2025-09-03"

import os
import shutil
import json
import argparse

def recursive_replace(data, id_old, id_new, url_old, url_new):
    modified = False

    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                if recursive_replace(value, id_old, id_new, url_old, url_new):
                    modified = True
            elif key == 'identifier' and isinstance(value, str) and id_old and id_new and id_old in value:
                data[key] = value.replace(id_old, id_new)
                modified = True
            elif key == 'url' and isinstance(value, str) and url_old and url_new and url_old in value:
                data[key] = value.replace(url_old, url_new)
                modified = True
    elif isinstance(data, list):
        for item in data:
            if recursive_replace(item, id_old, id_new, url_old, url_new):
                modified = True

    return modified

def copy_directory(src, dest):
    if os.path.exists(dest):
        print(f"Destination {dest} already exists. Removing it first.")
        shutil.rmtree(dest)
    print(f"Copying {src} to {dest}...")
    shutil.copytree(src, dest)
    print("Copy complete.")

def apply_substitutions(directory, id_old, id_new, url_old, url_new):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {file_path}")
                    continue

                if recursive_replace(data, id_old, id_new, url_old, url_new):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"Updated: {file_path}")

def main(id_old, id_new, url_old, url_new):
    source_dir ='../dwc-dp/0.1'
    dest_dir = '../sandbox'
    copy_directory(source_dir, dest_dir)
    apply_substitutions(dest_dir, id_old, id_new, url_old, url_new)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Copy a data package directory and apply substring replacements in identifier and url fields of JSON files.')

    parser.add_argument('-i', '--id-old', help='Old substring in "identifier" fields')
    parser.add_argument('-I', '--id-new', help='New substring for "identifier" fields')

    parser.add_argument('-u', '--url-old', help='Old substring in "url" fields')
    parser.add_argument('-U', '--url-new', help='New substring for "url" fields')

    args = parser.parse_args()

    main(
        args.id_old,
        args.id_new,
        args.url_old,
        args.url_new
    )
