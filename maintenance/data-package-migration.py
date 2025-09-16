#!/usr/bin/env python3
"""
Set data‑package identifiers and URLs from -I and -U (no pattern matching).

Rules
-----
- Copy source dir to dest (dest overwritten if exists).
- In dest/index.json (top-level):
    url         := <URL_BASE>/index.json
    identifier  := <ID_BASE>               (if -I provided)
- For each entry in dest/index.json["tableSchemas"]:
    url         := <URL_BASE>/table-schemas/<name>.json
    identifier  := <ID_BASE>/table-schemas/<name>   (no .json; if -I provided)
    (Derive <name>.json from item.path, item.url, item.name, or the string itself)
- For each JSON file under dest/table-schemas/**:
    url         := <URL_BASE>/<rel>                (rel like table-schemas/foo.json)
    identifier  := <ID_BASE>/<rel-without-.json>   (if -I provided)

Example
-------
python data-package-migration.v3.py \
  -s ../dwc-dp \
  -d ../sandbox \
  -U https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1 \
  -I http://rs.tdwg.org/dwc/dwc-dp

python data-package-migration.py -s ../dwc-dp -d ../sandbox -U https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1 -I http://rs.tdwg.org/dwc/dwc-dp

This sets:
  index.json.url                      -> https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1/index.json
  index.json.identifier               -> http://rs.tdwg.org/dwc/dwc-dp
  table-schemas/event.json.url        -> https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas/event.json
  table-schemas/event.json.identifier -> http://rs.tdwg.org/dwc/dwc-dp/table-schemas/event
"""

import argparse
import json
import os
import shutil
from typing import Optional


def copy_directory(src: str, dest: str) -> None:
    if os.path.abspath(src) == os.path.abspath(dest):
        raise ValueError("Source and destination directories must be different.")
    if os.path.exists(dest):
        print(f"[info] Destination exists, removing: {dest}")
        shutil.rmtree(dest)
    print(f"[info] Copying {src} -> {dest} ...")
    shutil.copytree(src, dest)
    print("[info] Copy complete.")


def load_json(path: str) -> Optional[dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[warn] Skipping invalid JSON: {path} ({e})")
        return None
    except FileNotFoundError:
        print(f"[warn] File not found (skipped): {path}")
        return None


def save_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def normalize_base(s: str) -> str:
    """Remove any trailing slash from a base URL."""
    if not s:
        return s
    return s[:-1] if s.endswith("/") else s


def to_posix(p: str) -> str:
    return p.replace("\\", "/")


def strip_json_suffix(rel: str) -> str:
    """Remove a trailing .json (case-sensitive) if present."""
    return rel[:-5] if rel.endswith(".json") else rel


def schema_rel_from_tableschemas_item(item) -> Optional[str]:
    """
    Infer a relative schema path like 'table-schemas/<name>.json' from a
    tableSchemas entry (dict or string). Returns None if it can't.
    """
    # Dict entry
    if isinstance(item, dict):
        # 1) path
        path = item.get("path")
        if isinstance(path, str) and path.strip():
            rel = to_posix(path.strip()).lstrip("./")
            if not rel.startswith("table-schemas/"):
                rel = f"table-schemas/{rel}"
            return rel
        # 2) url containing /table-schemas/
        url = item.get("url")
        if isinstance(url, str) and "/table-schemas/" in url:
            tail = url.split("/table-schemas/", 1)[1]
            return "table-schemas/" + tail
        # 3) name
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            return f"table-schemas/{name.strip()}.json"
        # 4) id/identifier as a last resort (if it looks like a bare name)
        maybe = item.get("id") or item.get("identifier")
        if isinstance(maybe, str) and maybe.strip() and not maybe.startswith("http"):
            return f"table-schemas/{maybe.strip()}.json"

    # String entry
    if isinstance(item, str) and item.strip():
        s = item.strip()
        if "/table-schemas/" in s:
            tail = s.split("/table-schemas/", 1)[1]
            return "table-schemas/" + tail
        if s.endswith(".json"):
            return to_posix(s).lstrip("./")

    return None


def update_index_json(dest_root: str, url_base: str, id_base: Optional[str]) -> None:
    index_path = os.path.join(dest_root, "index.json")
    data = load_json(index_path)
    if data is None:
        print(f"[warn] No index.json at {index_path}; skipping.")
        return

    # Top-level properties
    data["url"] = f"{url_base}/index.json"
    if id_base:
        data["identifier"] = id_base

    # tableSchemas entries
    ts_list = data.get("tableSchemas", [])
    if isinstance(ts_list, list):
        for i, item in enumerate(ts_list):
            rel = schema_rel_from_tableschemas_item(item)
            if not rel:
                continue
            rel = to_posix(rel).lstrip("./")
            if not rel.startswith("table-schemas/"):
                rel = f"table-schemas/{rel}"
            url_val = f"{url_base}/{rel}"
            id_val = f"{id_base}/{strip_json_suffix(rel)}" if id_base else None

            if isinstance(item, dict):
                item["url"] = url_val
                if id_base:
                    item["identifier"] = id_val
            else:
                # Convert string entry into object
                new_entry = {"url": url_val}
                if id_base:
                    new_entry["identifier"] = id_val
                ts_list[i] = new_entry

        data["tableSchemas"] = ts_list

    save_json(index_path, data)
    print(f"[ok] Updated index.json") #": url={data['url']}")


def update_table_schemas(dest_root: str, url_base: str, id_base: Optional[str]) -> int:
    updated = 0
    for root, _, files in os.walk(dest_root):
        for name in files:
            if not name.endswith(".json"):
                continue
            full_path = os.path.join(root, name)
            rel_from_root = os.path.relpath(full_path, start=dest_root)
            parts = rel_from_root.split(os.sep)
            if not parts or parts[0] != "table-schemas":
                continue

            data = load_json(full_path)
            if data is None:
                continue

            rel_posix = to_posix(rel_from_root.lstrip("./"))
            data["url"] = f"{url_base}/{rel_posix}"
            if id_base:
                data["identifier"] = f"{id_base}/{strip_json_suffix(rel_posix)}"

            save_json(full_path, data)
            updated += 1
            msg = f"[ok] Updated {rel_from_root}" # " : url -> {data['url']}"
#            if id_base:
#                msg += f"; identifier -> {data['identifier']}"
            print(msg)
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Set identifiers and urls from -I and -U across a copied data package.")
    parser.add_argument("-s", "--source", required=True, help="Source data-package directory (contains index.json and table-schemas/)")
    parser.add_argument("-d", "--dest", required=True, help="Destination directory to write (will be overwritten)")
    parser.add_argument("-U", "--url-base", required=True, help="Base URL to set (no trailing slash).")
    parser.add_argument("-I", "--id-base", help="Base Identifier to set (no trailing slash).")

    args = parser.parse_args()
    url_base = normalize_base(args.url_base)
    id_base = normalize_base(args.id_base) if args.id_base else None

    copy_directory(args.source, args.dest)
    update_index_json(args.dest, url_base, id_base)
    n = update_table_schemas(args.dest, url_base, id_base)
    print(f"[done] Updated {n} table schema file(s).")


if __name__ == "__main__":
    main()
