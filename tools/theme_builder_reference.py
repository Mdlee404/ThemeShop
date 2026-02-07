#!/usr/bin/env python3
"""Reference Python theme builder (CLI).

Usage examples:
  python tools/theme_builder_reference.py init --id aurora --name 极光 --author Mindrift
  python tools/theme_builder_reference.py validate --file ./aurora/theme.json
  python tools/theme_builder_reference.py pack --dir ./aurora --out ./packages/aurora.zip
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path


SCHEMA_VERSION = "1.0"
ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
REQUIRED_COLOR_KEYS = [
    "theme",
    "background",
    "text_primary",
    "text_secondary",
    "slider_selected",
    "slider_block",
    "slider_unselected",
]
DEFAULT_COLORS = {
    "theme": "#00E5FF",
    "background": "#0D1221",
    "text_primary": "rgba(255,244,220,0.92)",
    "text_secondary": "rgba(255,244,220,0.65)",
    "slider_selected": "#00E5FF",
    "slider_block": "#00E5FF",
    "slider_unselected": "rgba(255,244,220,0.2)",
}


def default_theme(theme_id: str, name: str, author: str, description: str) -> dict:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "id": theme_id,
        "name": name,
        "version": "1.0.0",
        "author": author,
        "description": description,
        "minAppVersion": "1.0.0",
        "minPlatformVersion": 1000,
        "colors": dict(DEFAULT_COLORS),
        "text": {
            "title": "rgba(255,244,220,0.92)",
            "body": "rgba(255,244,220,0.82)",
            "caption": "rgba(255,244,220,0.6)",
            "danger": "#E35A5A",
        },
        "backgrounds": {
            "app": {"type": "color", "value": "#0D1221"},
            "card": {"type": "color", "value": "rgba(13,18,33,0.55)"},
        },
        "buttons": {
            "primary": {
                "bg": "rgba(0,229,255,0.18)",
                "text": "#E6FCFF",
                "border": "rgba(0,229,255,0.4)",
                "image": "buttons/primary.png",
            },
            "danger": {
                "bg": "rgba(227,90,90,0.2)",
                "text": "#E35A5A",
                "border": "rgba(227,90,90,0.4)",
                "image": "buttons/danger.png",
            },
        },
        "lyric": {
            "active": "#00E5FF",
            "normal": "#FFF2D9",
            "active_bg": "rgba(0,229,255,0.25)",
        },
        "icons": {"dark_mode": False, "path": "icons"},
        "assets": {"base": ".", "images": "images", "buttons": "buttons"},
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("theme.json must be a JSON object")
    return data


def validate_theme_data(data: dict) -> list[str]:
    errors: list[str] = []
    if str(data.get("schemaVersion", "")) != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION}")

    theme_id = str(data.get("id", ""))
    if not ID_PATTERN.match(theme_id):
        errors.append("id must match ^[a-z0-9_]+$")

    if not str(data.get("name", "")).strip():
        errors.append("name is required")

    colors = data.get("colors")
    if not isinstance(colors, dict):
        errors.append("colors must be object")
    else:
        for key in REQUIRED_COLOR_KEYS:
            if key not in colors or not str(colors.get(key, "")).strip():
                errors.append(f"colors.{key} is required")

    return errors


def cmd_init(args: argparse.Namespace) -> int:
    theme_id = args.id.strip().lower()
    if not ID_PATTERN.match(theme_id):
        print("error: --id must match ^[a-z0-9_]+$", file=sys.stderr)
        return 1

    theme_dir = Path(args.dir or theme_id).resolve()
    theme_json = theme_dir / "theme.json"
    preview = theme_dir / "preview.png"

    if theme_json.exists() and not args.force:
        print(f"error: {theme_json} already exists, use --force", file=sys.stderr)
        return 1

    data = default_theme(theme_id, args.name, args.author, args.description)
    write_json(theme_json, data)

    for child in ("icons", "images", "buttons"):
        (theme_dir / child).mkdir(parents=True, exist_ok=True)

    if not preview.exists():
        preview.write_bytes(b"")

    print(f"created theme template: {theme_dir}")
    print(f"- {theme_json}")
    print("- preview.png")
    print("- icons/")
    print("- images/")
    print("- buttons/")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.file).resolve()
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        data = read_json(path)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"error: invalid json: {exc}", file=sys.stderr)
        return 1

    errors = validate_theme_data(data)
    if errors:
        print("validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print("validation passed")
    return 0


def cmd_pack(args: argparse.Namespace) -> int:
    source_dir = Path(args.dir).resolve()
    output = Path(args.out).resolve()

    if not source_dir.exists() or not source_dir.is_dir():
        print(f"error: invalid --dir: {source_dir}", file=sys.stderr)
        return 1

    theme_json = source_dir / "theme.json"
    if not theme_json.exists():
        print("error: theme.json is required", file=sys.stderr)
        return 1

    try:
        data = read_json(theme_json)
        errors = validate_theme_data(data)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"error: cannot validate theme.json: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
        root_name = source_dir.name
        for file_path in source_dir.rglob("*"):
            if file_path.is_dir():
                continue
            arcname = f"{root_name}/{file_path.relative_to(source_dir).as_posix()}"
            zip_file.write(file_path, arcname)

    print(f"packed: {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reference CLI for theme package workflow")
    sub = parser.add_subparsers(dest="command", required=True)

    init_parser = sub.add_parser("init", help="create a new theme directory")
    init_parser.add_argument("--id", required=True, help="theme id, e.g. aurora")
    init_parser.add_argument("--name", default="新主题", help="theme display name")
    init_parser.add_argument("--author", default="", help="theme author")
    init_parser.add_argument("--description", default="", help="theme description")
    init_parser.add_argument("--dir", default="", help="output directory")
    init_parser.add_argument("--force", action="store_true", help="overwrite existing theme.json")
    init_parser.set_defaults(func=cmd_init)

    validate_parser = sub.add_parser("validate", help="validate a theme.json file")
    validate_parser.add_argument("--file", required=True, help="path to theme.json")
    validate_parser.set_defaults(func=cmd_validate)

    pack_parser = sub.add_parser("pack", help="zip a theme directory")
    pack_parser.add_argument("--dir", required=True, help="theme directory containing theme.json")
    pack_parser.add_argument("--out", required=True, help="zip output path")
    pack_parser.set_defaults(func=cmd_pack)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

