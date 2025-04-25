#!/usr/bin/env python3
#
# Script to bulk change schema identifiers and urls in data package index.json and schemas in table-schemas/.

# Syntax:
# $python data-package-migration.py ./path_to_files -i "old-id" -I "new-id" -u "old-url" -U "new-url"

# From ./:

# To change identifiers from GBIF to TDWG:
# python data-package-migration.py ./dwc-dp/0.1 -i "http://rs.gbif.org/data-packages/dwc-dp" -I "http://rs.tdwg.org/dwc/dwc-dp"
# python data-package-migration.py ./dwc-dp/0.1/table-schemas -i "http://rs.gbif.org/data-packages/dwc-dp" -I "http://rs.tdwg.org/dwc/dwc-dp"

# To change identifiers from TDWG to GBIF:
# python data-package-migration.py ./dwc-dp/0.1 -i "http://rs.tdwg.org/dwc/dwc-dp" -I "http://rs.gbif.org/data-packages/dwc-dp"
# python data-package-migration.py ./dwc-dp/0.1/table-schemas -i "http://rs.tdwg.org/dwc/dwc-dp" -I "http://rs.gbif.org/data-packages/dwc-dp"

# To change urls from sandox to local:
# python data-package-migration.py ./dwc-dp/0.1 -u "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1" -U "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/0.1"
# python data-package-migration.py ./dwc-dp/0.1/table-schemas -u "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1" -U "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/0.1"

# To change urls from local to sandbox:
# python data-package-migration.py ./dwc-dp/0.1 -u "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/0.1" -U "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1"
# python data-package-migration.py ./dwc-dp/0.1/table-schemas -u "https://github.com/gbif/dwc-dp/blob/master/dwc-dp/0.1" -U "http://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1"

import os
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

def main(directory, id_old, id_new, url_old, url_new):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {filename}")
                continue

            if recursive_replace(data, id_old, id_new, url_old, url_new):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"Updated: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Replace substrings in identifier and url fields at any nesting level in JSON files.')

    parser.add_argument('directory', help='Path to the directory containing JSON files')

    parser.add_argument('-i', '--id-old', help='Old substring in "identifier" fields')
    parser.add_argument('-I', '--id-new', help='New substring for "identifier" fields')

    parser.add_argument('-u', '--url-old', help='Old substring in "url" fields')
    parser.add_argument('-U', '--url-new', help='New substring for "url" fields')

    args = parser.parse_args()

    main(
        args.directory,
        args.id_old,
        args.id_new,
        args.url_old,
        args.url_new
    )
