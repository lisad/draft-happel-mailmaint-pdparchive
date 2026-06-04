#!/usr/bin/env python3
"""Validates JSON examples against local schemas matched by $schema/$id."""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)

ROOT = Path(__file__).parent
EXAMPLES_DIR = ROOT / "examples"
SCHEMAS_DIR = ROOT / "schemas"


def load_schemas():
    schemas = {}
    for path in sorted(SCHEMAS_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"SCHEMA PARSE ERROR: {path.name}: {e}")
            continue
        schema_id = data.get("$id")
        if schema_id:
            schemas[schema_id] = (data, path.name)
        else:
            print(f"SCHEMA WARNING: {path.name} has no $id, skipping")
    return schemas


def main():
    schemas = load_schemas()

    passed = failed = skipped = 0

    for path in sorted(EXAMPLES_DIR.glob("*.json")):
        name = path.name
        try:
            example = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"PARSE ERROR:  {name}: {e}")
            failed += 1
            continue

        schema_ref = example.get("$schema")
        if not schema_ref:
            print(f"SKIP:         {name} (no $schema)")
            skipped += 1
            continue

        if schema_ref not in schemas:
            print(f"SKIP:         {name} ($schema not matched locally: {schema_ref})")
            skipped += 1
            continue

        schema, schema_name = schemas[schema_ref]
        try:
            jsonschema.validate(instance=example, schema=schema)
            print(f"PASS:         {name}")
            passed += 1
        except jsonschema.ValidationError as e:
            path_str = " -> ".join(str(p) for p in e.absolute_path) or "(root)"
            print(f"::error file=examples/{name}::{e.message} [at {path_str}]")
            print(f"FAIL:         {name}: {e.message} [at {path_str}]")
            failed += 1
        except jsonschema.SchemaError as e:
            print(f"::error file=schemas/{schema_name}::{e.message}")
            print(f"SCHEMA ERROR: {schema_name}: {e.message}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
