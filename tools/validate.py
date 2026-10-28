#!/usr/bin/env python3
"""Validate front matter of notes and spec-gap files against the schemas in schema/.

  python3 tools/validate.py              # notes/*.md against schema/note.json, spec/R[0-9]*.md against schema/spec.json
  python3 tools/validate.py FILE ...     # validate given note files
  python3 tools/validate.py --self-test  # schema/examples: valid-* must pass, invalid-* must fail

No third-party packages. The front-matter reader supports the subset used here: `key: value`, `key: [a, b]` and
`key: []`. The validator supports the JSON Schema keywords used in schema/: type, enum, pattern, minLength, maxLength,
required, additionalProperties, items.

Exit 0 = all valid; 1 = at least one error; 2 = usage error.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def front_matter(text):
    if not text.startswith("---\n"):
        raise ValueError("no front matter (the file must start with ---)")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("front matter is not closed with ---")
    data = {}
    for n, line in enumerate(text[4:end].splitlines(), 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$", line)
        if not m:
            raise ValueError(f"line {n}: expected 'key: value'")
        key, value = m.group(1), m.group(2).strip()
        if key in data:
            raise ValueError(f"line {n}: duplicate key {key}")
        if value.startswith("["):
            if not value.endswith("]"):
                raise ValueError(f"line {n}: list must close on the same line")
            inner = value[1:-1].strip()
            data[key] = [x.strip().strip('"\'') for x in inner.split(",")] if inner else []
        else:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            data[key] = value
    return data


def check(value, schema, path):
    errors = []
    t = schema.get("type")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if t == "string" or (t is None and isinstance(value, str)):
        if not isinstance(value, str):
            return errors + [f"{path}: expected a string"]
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    elif t == "array":
        if not isinstance(value, list):
            return errors + [f"{path}: expected a list"]
        for i, item in enumerate(value):
            errors += check(item, schema.get("items", {}), f"{path}[{i}]")
    elif t == "object":
        if not isinstance(value, dict):
            return errors + [f"{path}: expected an object"]
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required field {key}")
        props = schema.get("properties", {})
        for key, v in value.items():
            if key not in props:
                if schema.get("additionalProperties", True) is False:
                    errors.append(f"{path}: unknown field {key}")
                continue
            errors += check(v, props[key], f"{path}.{key}")
    return errors


def note_rules(data):
    """Rules that JSON Schema keywords here cannot express."""
    errors = []
    if data.get("impact") in ("MEDIUM", "HIGH"):
        for key in ("impact_axes", "reach_measure"):
            if not data.get(key):
                errors.append(f"$.{key}: required for impact {data['impact']} (RATING.md section 6)")
    if data.get("disclosure") == "class-level":
        for key in ("addresses", "repos"):
            if data.get(key):
                errors.append(f"$.{key}: must be empty while disclosure is class-level")
    cid = data.get("id", "")
    if data.get("class") and cid and not cid.startswith(data["class"] + "-"):
        errors.append("$.id: must start with the class ID")
    return errors


def validate_file(path, schema, extra=None):
    try:
        data = front_matter(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"$: {e}"]
    return check(data, schema, "$") + (extra(data) if extra else [])


def run(pairs):
    bad = 0
    for path, schema, extra in pairs:
        errs = validate_file(path, schema, extra)
        rel = Path(path).resolve().relative_to(ROOT) if ROOT in Path(path).resolve().parents else path
        if errs:
            bad += 1
            for e in errs:
                print(f"{rel}: {e}")
        else:
            print(f"{rel}: valid")
    return bad


def main(argv):
    note_schema = json.loads((ROOT / "schema" / "note.json").read_text(encoding="utf-8"))
    spec_schema = json.loads((ROOT / "schema" / "spec.json").read_text(encoding="utf-8"))
    if "--self-test" in argv:
        ok = True
        for f in sorted((ROOT / "schema" / "examples").glob("*.md")):
            errs = validate_file(f, note_schema, note_rules)
            want_valid = f.name.startswith("valid-")
            if want_valid and errs:
                ok = False
                print(f"FAIL {f.name}: expected valid, got {errs}")
            elif not want_valid and not errs:
                ok = False
                print(f"FAIL {f.name}: expected errors, got none")
            else:
                print(f"ok   {f.name}: {'valid' if not errs else f'{len(errs)} expected error(s)'}")
        print(f"validate self-test: {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    files = [a for a in argv if not a.startswith("-")]
    if files:
        pairs = [(f, note_schema, note_rules) for f in files]
    else:
        pairs = [(f, note_schema, note_rules) for f in sorted((ROOT / "notes").glob("*.md")) if f.name != "README.md"]
        pairs += [(f, spec_schema, None) for f in sorted((ROOT / "spec").glob("R[0-9]*.md"))]
    bad = run(pairs)
    print(f"validate: {len(pairs) - bad} valid, {bad} invalid")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
