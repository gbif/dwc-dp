#!/usr/bin/env python3
"""Generate PostgreSQL DDL from DwC-DP-style table schemas and a YAML sidecar.

The YAML sidecar (default: generate_sql.yaml) supports:
- metadata: header comment block
- enums: PostgreSQL enum definitions, either inline `values` or remote `vocabulary_url`
- defaults: column defaults
- checks: extra CHECK constraints
- types: explicit PostgreSQL type overrides
- enum_bindings: column-to-enum bindings

The script treats Frictionless-style `foreignKeys` as hard foreign keys and
`weakForeignKeys` as weak links that receive columns and indexes but no
REFERENCES constraints.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import tarfile
import tempfile
from urllib.error import URLError
from urllib.request import Request, urlopen
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required. Install with: pip install pyyaml") from exc

POSTGRES_RESERVED = {
    "all", "analyse", "analyze", "and", "any", "array", "as", "asc", "asymmetric",
    "authorization", "between", "bigint", "binary", "bit", "boolean", "both", "case",
    "cast", "char", "character", "check", "coalesce", "collate", "column", "constraint",
    "create", "cross", "current_catalog", "current_date", "current_role", "current_schema",
    "current_time", "current_timestamp", "current_user", "default", "deferrable", "desc",
    "distinct", "do", "else", "end", "except", "exists", "extract", "false", "fetch",
    "for", "foreign", "freeze", "from", "full", "grant", "group", "having", "ilike",
    "in", "initially", "inner", "intersect", "into", "is", "isnull", "join", "lateral",
    "leading", "left", "like", "limit", "localtime", "localtimestamp", "natural", "not",
    "notnull", "null", "offset", "on", "only", "or", "order", "outer", "overlaps",
    "placing", "primary", "references", "returning", "right", "select", "session_user",
    "similar", "smallint", "some", "symmetric", "table", "then", "to", "trailing", "true",
    "union", "unique", "user", "using", "variadic", "verbose", "when", "where", "window",
    "with", "class",
}


@dataclass
class Column:
    logical_name: str
    sql_name: str
    logical_type: str
    constraints: dict[str, Any] = field(default_factory=dict)
    description: str | None = None


@dataclass
class ForeignKey:
    source_fields: list[str]
    target_resource: str
    target_fields: list[str]
    weak: bool = False


@dataclass
class Table:
    logical_name: str
    sql_name: str
    columns: list[Column]
    primary_key: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    weak_foreign_keys: list[ForeignKey] = field(default_factory=list)
    title: str | None = None
    description: str | None = None


class GeneratorError(Exception):
    pass


def snake_case(name: str) -> str:
    name = name.replace("-", "_")
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"__+", "_", name)
    return name.lower()


def quote_ident(name: str) -> str:
    if re.fullmatch(r"[a-z_][a-z0-9_]*", name) and name not in POSTGRES_RESERVED:
        return name
    return '"' + name.replace('"', '""') + '"'


def make_constraint_name(table: str, base: str) -> str:
    raw = f"{table}_{base}"
    if len(raw) <= 63:
        return raw
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    head = raw[: 63 - 1 - len(digest)]
    return f"{head}_{digest}"


def normalize_listish(value: Any) -> list[str]:
    """Coerce None, a scalar, or a list into a flat list of strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


def fetch_url_text(url: str) -> str:
    headers = {
        "Accept": "text/csv, text/plain;q=0.9, */*;q=0.8",
        "User-Agent": "generate_sql.py/1.0",
    }
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:  # nosec B310
            raw = response.read()
            charset = response.headers.get_content_charset() or "utf-8"
            return raw.decode(charset, errors="replace")
    except URLError as exc:  # pragma: no cover
        raise GeneratorError(f"Failed to fetch vocabulary URL {url}: {exc}") from exc


def extract_controlled_values_from_csv(text: str, url: str) -> list[str]:
    """Extract controlled value strings from a TDWG rs.tdwg.org CSV vocabulary file.

    Expects a header row containing 'controlled_value_string' and 'type' columns.
    Rows where type is skos:Concept and the term is not deprecated are included.
    """
    skos_concept = "http://www.w3.org/2004/02/skos/core#Concept"
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or "controlled_value_string" not in reader.fieldnames:
        raise GeneratorError(
            f"CSV at {url} has no 'controlled_value_string' column — "
            "check that the vocabulary_url points to a TDWG rs.tdwg.org CSV file"
        )
    values: list[str] = []
    for row in reader:
        if row.get("term_deprecated", "").strip():
            continue
        if row.get("type", "").strip() != skos_concept:
            continue
        cv = row.get("controlled_value_string", "").strip()
        if cv:
            values.append(cv)
    return values


def parse_fk_items(items: list[dict[str, Any]], *, weak: bool) -> list[ForeignKey]:
    output: list[ForeignKey] = []
    for item in items or []:
        ref = item.get("reference", {})
        source_fields = normalize_listish(item.get("fields"))
        target_resource = ref.get("resource", "")
        target_fields = normalize_listish(ref.get("fields"))
        if not source_fields or not target_fields:
            raise GeneratorError(f"Malformed foreign key entry: {item}")
        output.append(
            ForeignKey(
                source_fields=source_fields,
                target_resource=str(target_resource),
                target_fields=target_fields,
                weak=weak,
            )
        )
    return output


def read_schema_file(path: Path) -> Table:
    with path.open("r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            raise GeneratorError(f"Invalid JSON in schema file {path}: {exc}") from exc

    try:
        logical_name = data["name"]
        sql_name = snake_case(logical_name)
        columns: list[Column] = []
        for field_obj in data.get("fields", []):
            logical_field = field_obj["name"]
            sql_field = snake_case(logical_field)
            columns.append(
                Column(
                    logical_name=logical_field,
                    sql_name=sql_field,
                    logical_type=field_obj.get("type", "string"),
                    constraints=field_obj.get("constraints", {}) or {},
                    description=field_obj.get("description"),
                )
            )
    except KeyError as exc:
        raise GeneratorError(f"Schema file {path} is missing required key {exc}") from exc

    return Table(
        logical_name=logical_name,
        sql_name=sql_name,
        columns=columns,
        primary_key=normalize_listish(data.get("primaryKey")),
        foreign_keys=parse_fk_items(data.get("foreignKeys", []), weak=False),
        weak_foreign_keys=parse_fk_items(data.get("weakForeignKeys", []), weak=True),
        title=data.get("title"),
        description=data.get("description"),
    )


def collect_schema_files(input_path: Path, temp_dir: Path | None = None) -> list[Path]:
    if input_path.is_dir():
        base = input_path
    elif input_path.is_file() and input_path.suffixes[-2:] == [".tar", ".gz"]:
        if temp_dir is None:
            raise GeneratorError("temp_dir must be provided for .tar.gz input")
        with tarfile.open(input_path, "r:gz") as tf:
            tf.extractall(temp_dir, filter="data")
        subdir = temp_dir / "table-schemas"
        base = subdir if subdir.is_dir() else temp_dir
    else:
        raise GeneratorError("--schemas must be a directory or a .tar.gz archive")

    files = [
        p for p in base.rglob("*.json")
        if p.is_file() and not p.name.startswith("._") and "__MACOSX" not in p.as_posix()
    ]
    if not files:
        raise GeneratorError(f"No JSON schema files found in {input_path}")
    return sorted(files)


def load_tables(input_path: Path) -> dict[str, Table]:
    with tempfile.TemporaryDirectory(prefix="table_schemas_") as _tmp:
        tables: dict[str, Table] = {}
        for path in collect_schema_files(input_path, Path(_tmp)):
            table = read_schema_file(path)
            if table.logical_name in tables:
                raise GeneratorError(f"Duplicate table name found: {table.logical_name}")
            tables[table.logical_name] = table
    return tables


def load_sidecar(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise GeneratorError("YAML sidecar root must be a mapping/object")
    return data


class SqlGenerator:
    def __init__(self, tables: dict[str, Table], config: dict[str, Any]) -> None:
        self.tables = tables
        self.config = config
        self.column_name_map = {
            table.logical_name: {column.logical_name: column.sql_name for column in table.columns}
            for table in tables.values()
        }
        self.validate_references()

    def validate_references(self) -> None:
        for table in self.tables.values():
            column_names = {column.logical_name for column in table.columns}
            for logical_pk in table.primary_key:
                if logical_pk not in column_names:
                    raise GeneratorError(
                        f"Table {table.logical_name}: primaryKey references missing field {logical_pk}"
                    )
            for fk in [*table.foreign_keys, *table.weak_foreign_keys]:
                for source in fk.source_fields:
                    if source not in column_names:
                        raise GeneratorError(
                            f"Table {table.logical_name}: FK source field {source} does not exist"
                        )
                target_table_name = table.logical_name if fk.target_resource == "" else fk.target_resource
                if target_table_name not in self.tables:
                    raise GeneratorError(
                        f"Table {table.logical_name}: FK target resource {target_table_name} does not exist"
                    )
                target_table = self.tables[target_table_name]
                target_columns = {column.logical_name for column in target_table.columns}
                for target in fk.target_fields:
                    if target not in target_columns:
                        raise GeneratorError(
                            f"Table {table.logical_name}: FK target field {target_table_name}.{target} does not exist"
                        )
                # Check that target fields form a key (primary key or unique) on the target table.
                target_fields_set = set(fk.target_fields)
                is_pk = target_fields_set == set(target_table.primary_key)
                unique_cols = {
                    col.logical_name
                    for col in target_table.columns
                    if (col.constraints or {}).get("unique")
                }
                is_unique = len(fk.target_fields) == 1 and fk.target_fields[0] in unique_cols
                if not (is_pk or is_unique):
                    msg = (
                        f"Table {table.logical_name}: FK target fields {fk.target_fields} "
                        f"on {target_table_name} are not a primary key or unique column"
                    )
                    if fk.weak:
                        print(f"Warning: {msg}", file=sys.stderr)
                    else:
                        raise GeneratorError(msg)

    def type_override(self, table: str, column: str) -> str | None:
        return (
            self.config.get("types", {})
            .get("columns", {})
            .get(table, {})
            .get(column, {})
            .get("sql_type")
        )

    def enum_binding(self, table: str, column: str) -> str | None:
        return (
            self.config.get("enum_bindings", {})
            .get(table, {})
            .get(column, {})
            .get("enum")
        )

    def default_value(self, table: str, column: str) -> Any:
        return (
            self.config.get("defaults", {})
            .get("columns", {})
            .get(table, {})
            .get(column, {})
            .get("value")
        )

    def pg_type_for_column(self, table: str, column: Column) -> str:
        enum_name = self.enum_binding(table, column.logical_name)
        if enum_name:
            if enum_name not in self.config.get("enums", {}):
                raise GeneratorError(
                    f"Column {table}.{column.logical_name} binds to undefined enum {enum_name}"
                )
            return quote_ident(snake_case(enum_name))

        override = self.type_override(table, column.logical_name)
        if override:
            return override

        type_map = {
            "string": "TEXT",
            "integer": "INTEGER",
            "number": "NUMERIC",
            "boolean": "BOOLEAN",
        }
        try:
            return type_map[column.logical_type]
        except KeyError as exc:
            raise GeneratorError(
                f"Unsupported logical type {column.logical_type!r} for {table}.{column.logical_name}"
            ) from exc

    def column_checks_from_schema(self, column: Column) -> list[str]:
        checks: list[str] = []
        constraints = column.constraints or {}
        minimum = constraints.get("minimum")
        maximum = constraints.get("maximum")
        if minimum is not None:
            checks.append(f"value >= {minimum}")
        if maximum is not None:
            checks.append(f"value <= {maximum}")
        return checks

    def render_header_comment(self) -> str:
        metadata = self.config.get("metadata", {})
        lines = ["/*"]
        preferred_order = ["title", "version", "source_table_schemas", "generated_by"]
        seen: set[str] = set()
        for key in preferred_order:
            if key in metadata:
                label = key.replace("_", " ").capitalize()
                lines.append(f"{label}: {metadata[key]}")
                seen.add(key)
        for key, value in metadata.items():
            if key in ("notes", "example_run") or key in seen:
                continue
            label = key.replace("_", " ").capitalize()
            lines.append(f"{label}: {value}")
        notes = metadata.get("notes", [])
        if notes:
            lines.append("")
            lines.append("Notes:")
            for note in notes:
                lines.append(f"- {note}")
        example_run = metadata.get("example_run", "").strip()
        if example_run:
            lines.append("")
            lines.append("Example run:")
            for run_line in example_run.splitlines():
                lines.append(f"  {run_line}")
        lines.append("*/")
        return "\n".join(lines)

    def resolve_enum_values(self, enum_name: str, spec: dict[str, Any]) -> list[str]:
        values = [str(v) for v in spec.get("values", []) or []]
        if values:
            return values

        vocabulary_url = spec.get("vocabulary_url")
        if vocabulary_url:
            text = fetch_url_text(str(vocabulary_url))
            values = extract_controlled_values_from_csv(text, str(vocabulary_url))
            if values:
                print(
                    f"Enum '{enum_name}': fetched {len(values)} value(s) from {vocabulary_url}",
                    file=sys.stderr,
                )
                return values
            raise GeneratorError(
                f"Enum {enum_name} could not extract controlled values from {vocabulary_url}"
            )

        raise GeneratorError(
            f"Enum {enum_name} must define either 'values' or 'vocabulary_url'"
        )

    def render_enums(self) -> str:
        enums = self.config.get("enums", {})
        if not enums:
            return ""
        statements: list[str] = []
        for enum_name, spec in enums.items():
            values = self.resolve_enum_values(enum_name, spec)
            if not values:
                raise GeneratorError(f"Enum {enum_name} has no values")
            qname = quote_ident(snake_case(enum_name))
            literal_list = ",\n  ".join("'" + str(v).replace("'", "''") + "'" for v in values)
            statements.append(f"CREATE TYPE {qname} AS ENUM (\n  {literal_list}\n);")
        return "\n\n".join(statements)

    def render_create_table(self, table: Table) -> str:
        lines: list[str] = []
        if table.title or table.description:
            if table.title:
                lines.append(f"-- {table.title}")
            if table.description:
                for desc_line in str(table.description).splitlines():
                    lines.append(f"-- {desc_line}")
        column_defs: list[str] = []
        pk_sql_names = [self.column_name_map[table.logical_name][name] for name in table.primary_key]
        single_pk = pk_sql_names[0] if len(pk_sql_names) == 1 else None

        for column in table.columns:
            parts = [quote_ident(column.sql_name), self.pg_type_for_column(table.logical_name, column)]
            constraints = column.constraints or {}
            if constraints.get("required"):
                parts.append("NOT NULL")
            if constraints.get("unique") and column.sql_name != single_pk:
                parts.append("UNIQUE")
            default_value = self.default_value(table.logical_name, column.logical_name)
            if default_value is not None:
                parts.append(f"DEFAULT {default_value}")
            checks = self.column_checks_from_schema(column)
            for expr in checks:
                parts.append(f"CHECK ({expr})")
            if column.sql_name == single_pk:
                parts.append("PRIMARY KEY")
            column_defs.append("  " + " ".join(parts))

        if len(pk_sql_names) > 1:
            pk_expr = ", ".join(quote_ident(name) for name in pk_sql_names)
            column_defs.append(f"  PRIMARY KEY ({pk_expr})")

        lines.append(f"CREATE TABLE {quote_ident(table.sql_name)} (")
        lines.append(",\n".join(column_defs))
        lines.append(");")
        return "\n".join(lines)

    def per_table_foreign_key_statements(self, table: Table) -> list[str]:
        statements: list[str] = []
        for fk in table.foreign_keys:
            src_cols = [self.column_name_map[table.logical_name][name] for name in fk.source_fields]
            target_table_logical = table.logical_name if fk.target_resource == "" else fk.target_resource
            target_table = self.tables[target_table_logical]
            tgt_cols = [self.column_name_map[target_table_logical][name] for name in fk.target_fields]
            base = "_".join(src_cols + ["fkey"])
            cname = make_constraint_name(table.sql_name, base)
            statements.append(
                "ALTER TABLE {table_name} ADD CONSTRAINT {cname} FOREIGN KEY ({src}) "
                "REFERENCES {target} ({tgt}) ON DELETE CASCADE DEFERRABLE;".format(
                    table_name=quote_ident(table.sql_name),
                    cname=quote_ident(cname),
                    src=", ".join(quote_ident(c) for c in src_cols),
                    target=quote_ident(target_table.sql_name),
                    tgt=", ".join(quote_ident(c) for c in tgt_cols),
                )
            )
        return statements

    def per_table_extra_check_statements(self, table: Table) -> list[str]:
        checks_cfg = self.config.get("checks", {})
        statements: list[str] = []

        for item in checks_cfg.get("tables", {}).get(table.logical_name, []):
            name = item["name"]
            sql_expr = item["sql"]
            statements.append(
                f"ALTER TABLE {quote_ident(table.sql_name)} "
                f"ADD CONSTRAINT {quote_ident(make_constraint_name(table.sql_name, name))} "
                f"CHECK ({sql_expr});"
            )

        for logical_col, items in checks_cfg.get("columns", {}).get(table.logical_name, {}).items():
            if logical_col not in self.column_name_map[table.logical_name]:
                raise GeneratorError(f"Unknown column in checks.columns: {table.logical_name}.{logical_col}")
            for item in items:
                name = item["name"]
                sql_expr = item["sql"]
                statements.append(
                    f"ALTER TABLE {quote_ident(table.sql_name)} "
                    f"ADD CONSTRAINT {quote_ident(make_constraint_name(table.sql_name, name))} "
                    f"CHECK ({sql_expr});"
                )
        return statements

    def per_table_index_statements(self, table: Table) -> list[str]:
        statements: list[str] = []
        seen: set[tuple[str, ...]] = set()
        for fk in [*table.foreign_keys, *table.weak_foreign_keys]:
            src_cols = tuple(self.column_name_map[table.logical_name][name] for name in fk.source_fields)
            if src_cols in seen:
                continue
            seen.add(src_cols)
            idx_name = make_constraint_name(table.sql_name, "_".join([*src_cols, "idx"]))
            statements.append(
                f"CREATE INDEX {quote_ident(idx_name)} ON {quote_ident(table.sql_name)} "
                f"({', '.join(quote_ident(c) for c in src_cols)});"
            )
        return statements

    def render_table_section(self, table: Table) -> str:
        parts = [self.render_create_table(table)]
        fk_statements = self.per_table_foreign_key_statements(table)
        if fk_statements:
            parts.append("\n".join(fk_statements))
        check_statements = self.per_table_extra_check_statements(table)
        if check_statements:
            parts.append("\n".join(check_statements))
        index_statements = self.per_table_index_statements(table)
        if index_statements:
            parts.append("\n".join(index_statements))
        return "\n\n".join(parts)

    def generate(self) -> str:
        sections = [self.render_header_comment()]
        enums = self.render_enums()
        if enums:
            sections.extend(["", "-- ENUMs", enums])
        sections.append("")
        sections.append("-- Tables, constraints, and indexes")
        sections.append(
            "\n\n".join(
                self.render_table_section(table)
                for table in sorted(self.tables.values(), key=lambda t: t.sql_name)
            )
        )
        return "\n".join(sections)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate PostgreSQL DDL from DwC-DP table schemas and generate_sql.yaml"
    )
    parser.add_argument(
        "--schemas",
        required=True,
        help="Path to the table-schemas directory or a table-schemas.tar.gz archive",
    )
    parser.add_argument(
        "--config",
        default="generate_sql.yaml",
        help="Path to YAML sidecar configuration (default: generate_sql.yaml)",
    )
    parser.add_argument(
        "--output",
        default="-",
        help="Output .sql file path, or '-' for stdout (default)",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        tables = load_tables(Path(args.schemas))
        config = load_sidecar(Path(args.config))
        generator = SqlGenerator(tables, config)
        sql = generator.generate() + "\n"
    except GeneratorError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.output == "-":
        sys.stdout.write(sql)
    else:
        Path(args.output).write_text(sql, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
