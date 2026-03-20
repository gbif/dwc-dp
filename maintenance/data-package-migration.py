#!/usr/bin/env python3
"""
Set data-package identifiers and URLs from -I and -U.

Rules
-----
- Copy source dir to dest (dest overwritten if exists).
- In dest/index.json (top-level):
    url         := <URL_BASE>/index.json
    identifier  := <ID_BASE>               (if -I provided)
- For each entry in dest/index.json["tableSchemas"]:
    url         := <URL_BASE>/table-schemas/<name>.json
    identifier  := <ID_BASE>/table-schemas/<name>   (no .json; if -I provided)
- For each JSON file under dest/table-schemas/:
    url         := <URL_BASE>/table-schemas/<name>.json
    identifier  := <ID_BASE>/table-schemas/<name>   (no .json; if -I provided)

Example
-------
python data-package-migration.py \
  -s ../dwc-dp \
  -d ./sandbox \
  -U https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1 \
  -I http://rs.tdwg.org/dwc/dwc-dp

This sets:
  index.json:
    url        -> https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1/index.json
    identifier -> http://rs.tdwg.org/dwc/dwc-dp
  table-schemas/event.json:
    url        -> https://rs.gbif.org/sandbox/experimental/data-packages/dwc-dp/0.1/table-schemas/event.json
    identifier -> http://rs.tdwg.org/dwc/dwc-dp/table-schemas/event
"""

import argparse
import json
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_base(s: str) -> str:
    """Remove any trailing slash from a base URL or identifier."""
    return s.rstrip('/') if s else s


def strip_json_suffix(rel: str) -> str:
    """Remove a trailing .json (case-sensitive) if present."""
    return rel[:-5] if rel.endswith('.json') else rel


def rel_from_tableschemas_entry(entry: dict | str) -> str | None:
    """
    Derive a relative schema path of the form 'table-schemas/<name>.json'
    from a tableSchemas entry.

    Entries are expected to be dicts containing at least one of:
      - 'url': a relative path ('table-schemas/foo.json') or absolute URL
      - 'name': a bare schema name ('foo')

    String entries are also accepted as a fallback.
    """
    if isinstance(entry, dict):
        url = entry.get('url', '')
        if url:
            if url.startswith('http'):
                # Absolute URL from a previous migration run — extract the
                # table-schemas/<name>.json tail from the URL path.
                path = urlparse(url).path
                if '/table-schemas/' in path:
                    return 'table-schemas/' + path.split('/table-schemas/', 1)[1]
            else:
                # Relative path — normalise and ensure the table-schemas/ prefix.
                rel = url.lstrip('./')
                if not rel.startswith('table-schemas/'):
                    rel = 'table-schemas/' + rel
                return rel

        # Fallback: construct from 'name'
        name = entry.get('name', '').strip()
        if name:
            return f'table-schemas/{name}.json'

    elif isinstance(entry, str) and entry.strip():
        s = entry.strip()
        if '/table-schemas/' in s:
            return 'table-schemas/' + s.split('/table-schemas/', 1)[1]
        if s.endswith('.json'):
            return s.lstrip('./')

    return None


def load_json(path: Path) -> dict | None:
    """
    Load and return parsed JSON from *path*.
    Prints a warning and returns None on parse failure or missing file.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[warn] File not found (skipped): {path}")
    except json.JSONDecodeError as exc:
        print(f"[warn] Skipping invalid JSON: {path} ({exc})")
    return None


def save_json(path: Path, data: dict) -> None:
    """Write *data* to *path* as pretty-printed UTF-8 JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')


# ---------------------------------------------------------------------------
# Migration steps
# ---------------------------------------------------------------------------

def copy_directory(src: str, dest: str, dry_run: bool) -> None:
    """
    Copy *src* to *dest*, removing *dest* first if it exists.
    Validates that *src* exists and contains an index.json before
    making any changes.
    """
    src_path = Path(src).resolve()
    dest_path = Path(dest).resolve()

    if src_path == dest_path:
        raise ValueError("Source and destination directories must be different.")
    if not src_path.exists():
        raise FileNotFoundError(f"Source directory not found: {src_path}")
    if not (src_path / 'index.json').exists():
        raise FileNotFoundError(f"Source directory has no index.json: {src_path}")

    if dry_run:
        if dest_path.exists():
            print(f"[dry-run] Would remove existing destination: {dest_path}")
        print(f"[dry-run] Would copy {src_path} -> {dest_path}")
        return

    if dest_path.exists():
        print(f"[info] Destination exists, removing: {dest_path}")
        shutil.rmtree(dest_path)

    print(f"[info] Copying {src_path} -> {dest_path} ...")
    shutil.copytree(src_path, dest_path)
    print("[info] Copy complete.")


def update_index_json(
    dest_root: str,
    url_base: str,
    id_base: str | None,
    dry_run: bool,
    verbose: bool,
) -> None:
    """
    Update url and (optionally) identifier on the top-level index.json and
    on each of its tableSchemas entries.
    """
    index_path = Path(dest_root) / 'index.json'

    if dry_run:
        data = load_json(index_path)
        if data is None:
            print(f"[dry-run] [warn] No index.json at {index_path}; would skip.")
            return
    else:
        data = load_json(index_path)
        if data is None:
            print(f"[warn] No index.json at {index_path}; skipping.")
            return

    new_index_url = f'{url_base}/index.json'
    new_index_id  = id_base  # may be None

    ts_list = data.get('tableSchemas', [])
    planned: list[tuple] = []  # (rel, new_url, new_id) for each entry

    for item in ts_list if isinstance(ts_list, list) else []:
        rel = rel_from_tableschemas_entry(item)
        if not rel:
            print(f"[warn] Could not determine schema path for entry: {item!r}")
            continue
        new_url = f'{url_base}/{rel}'
        new_id  = f'{id_base}/{strip_json_suffix(rel)}' if id_base else None
        planned.append((item, rel, new_url, new_id))

    if dry_run:
        print(f"[dry-run] index.json: url -> {new_index_url}")
        if new_index_id:
            print(f"[dry-run] index.json: identifier -> {new_index_id}")
        for _, rel, new_url, new_id in planned:
            print(f"[dry-run] tableSchemas/{rel}: url -> {new_url}")
            if new_id:
                print(f"[dry-run] tableSchemas/{rel}: identifier -> {new_id}")
        return

    # Apply changes
    data['url'] = new_index_url
    if id_base:
        data['identifier'] = new_index_id

    for i, (item, rel, new_url, new_id) in enumerate(planned):
        if isinstance(item, dict):
            item['url'] = new_url
            if id_base:
                item['identifier'] = new_id
        else:
            new_entry = {'url': new_url}
            if id_base:
                new_entry['identifier'] = new_id
            ts_list[i] = new_entry

    data['tableSchemas'] = ts_list
    save_json(index_path, data)

    if verbose:
        print(f"[ok] index.json: url -> {new_index_url}")
        if new_index_id:
            print(f"[ok] index.json: identifier -> {new_index_id}")
        for _, rel, new_url, new_id in planned:
            print(f"[ok] tableSchemas entry {rel}: url -> {new_url}")
            if new_id:
                print(f"[ok] tableSchemas entry {rel}: identifier -> {new_id}")
    else:
        print("[ok] Updated index.json")


def update_table_schemas(
    dest_root: str,
    url_base: str,
    id_base: str | None,
    dry_run: bool,
    verbose: bool,
) -> int:
    """
    Update url and (optionally) identifier in every JSON file directly under
    dest_root/table-schemas/. Returns the number of files updated (or that
    would be updated in dry-run mode).
    """
    table_schemas_path = Path(dest_root) / 'table-schemas'
    updated = 0

    for json_file in sorted(table_schemas_path.glob('*.json')):
        rel_posix = f'table-schemas/{json_file.name}'
        new_url = f'{url_base}/{rel_posix}'
        new_id  = f'{id_base}/{strip_json_suffix(rel_posix)}' if id_base else None

        if dry_run:
            print(f"[dry-run] {rel_posix}: url -> {new_url}")
            if new_id:
                print(f"[dry-run] {rel_posix}: identifier -> {new_id}")
            updated += 1
            continue

        data = load_json(json_file)
        if data is None:
            continue

        data['url'] = new_url
        if id_base:
            data['identifier'] = new_id

        save_json(json_file, data)
        updated += 1

        if verbose:
            print(f"[ok] {rel_posix}: url -> {new_url}")
            if new_id:
                print(f"[ok] {rel_posix}: identifier -> {new_id}")
        else:
            print(f"[ok] Updated {rel_posix}")

    return updated


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set identifiers and URLs across a copied data package.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        '-s', '--source', required=True,
        help="Source data-package directory (must contain index.json and table-schemas/).",
    )
    parser.add_argument(
        '-d', '--dest', required=True,
        help="Destination directory (will be overwritten if it exists).",
    )
    parser.add_argument(
        '-U', '--url-base', required=True,
        help="Base URL to set (trailing slash is stripped automatically).",
    )
    parser.add_argument(
        '-I', '--id-base',
        help="Base identifier to set (trailing slash is stripped automatically).",
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help="Print what would be changed without copying or modifying any files.",
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help="Print each url/identifier change as it is applied.",
    )

    args = parser.parse_args()
    url_base = normalize_base(args.url_base)
    id_base  = normalize_base(args.id_base) if args.id_base else None
    dry_run  = args.dry_run
    verbose  = args.verbose

    if dry_run:
        print("[dry-run] No files will be copied or modified.\n")

    copy_directory(args.source, args.dest, dry_run)
    update_index_json(args.dest, url_base, id_base, dry_run, verbose)
    n = update_table_schemas(args.dest, url_base, id_base, dry_run, verbose)

    action = "Would update" if dry_run else "Updated"
    print(f"[done] {action} {n} table schema file(s).")


if __name__ == '__main__':
    main()
