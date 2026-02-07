#!/usr/bin/env python3
"""Build a theme catalog for the static Cloudflare Pages site.

Workflow:
1. Scan `packages/*.zip`
2. Extract each package into `public/themes/<theme_id>/`
3. Copy package zip into `public/downloads/`
4. Generate `public/data/themes.json`
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Iterable


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
PREVIEW_CANDIDATES = (
    "preview.png",
    "preview.jpg",
    "preview.jpeg",
    "preview.webp",
    "preview.gif",
)
THEME_JSON_NAME = "theme.json"
THEME_ID_ALLOWED = re.compile(r"[^a-z0-9_]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_member_path(member_name: str) -> str:
    return PurePosixPath(member_name.replace("\\", "/")).as_posix()


def decode_text(raw_bytes: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gbk"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="replace")


def clean_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def sanitize_theme_id(raw_value: str, fallback: str) -> str:
    value = (raw_value or "").strip().lower().replace("-", "_")
    value = THEME_ID_ALLOWED.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or fallback


def unique_theme_id(base_id: str, used_ids: set[str]) -> str:
    if base_id not in used_ids:
        return base_id
    suffix = 2
    while f"{base_id}_{suffix}" in used_ids:
        suffix += 1
    return f"{base_id}_{suffix}"


def detect_single_root(file_members: Iterable[str]) -> str | None:
    roots: set[str] = set()
    for member in file_members:
        normalized = normalize_member_path(member)
        path_obj = PurePosixPath(normalized)
        if not path_obj.parts:
            continue
        roots.add(path_obj.parts[0])
        if len(roots) > 1:
            return None
    return next(iter(roots), None)


def find_theme_json_member(zip_file: zipfile.ZipFile, root_prefix: str | None) -> str:
    normalized_map = {normalize_member_path(name): name for name in zip_file.namelist()}
    candidates: list[str] = []

    if root_prefix:
        candidates.append(f"{root_prefix}/{THEME_JSON_NAME}")
    candidates.append(THEME_JSON_NAME)

    for normalized_name in normalized_map:
        if normalized_name.lower().endswith(f"/{THEME_JSON_NAME}"):
            candidates.append(normalized_name)

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate in normalized_map:
            return normalized_map[candidate]
    raise FileNotFoundError("Package is missing theme.json")


def strip_root_prefix(member_name: str, root_prefix: str | None) -> str:
    normalized = normalize_member_path(member_name)
    if not normalized:
        return ""

    path_obj = PurePosixPath(normalized)
    parts = list(path_obj.parts)
    if root_prefix and parts and parts[0] == root_prefix:
        parts = parts[1:]

    if not parts:
        return ""
    if any(part in ("..", "") for part in parts):
        return ""
    return PurePosixPath(*parts).as_posix()


def ensure_safe_target(base_dir: Path, target_path: Path) -> bool:
    try:
        target_path.resolve().relative_to(base_dir.resolve())
        return True
    except ValueError:
        return False


def read_theme_json(zip_path: Path) -> tuple[dict, str | None]:
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        file_members = [info.filename for info in zip_file.infolist() if not info.is_dir()]
        root_prefix = detect_single_root(file_members)
        theme_json_member = find_theme_json_member(zip_file, root_prefix)
        theme_data = json.loads(decode_text(zip_file.read(theme_json_member)))
    if not isinstance(theme_data, dict):
        raise ValueError("theme.json must be a JSON object")
    return theme_data, root_prefix


def extract_package(zip_path: Path, output_dir: Path, root_prefix: str | None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        for info in zip_file.infolist():
            if info.is_dir():
                continue

            relative_path = strip_root_prefix(info.filename, root_prefix)
            if not relative_path:
                continue

            target_file = output_dir / relative_path
            if not ensure_safe_target(output_dir, target_file):
                continue

            target_file.parent.mkdir(parents=True, exist_ok=True)
            with zip_file.open(info, "r") as source, target_file.open("wb") as target:
                shutil.copyfileobj(source, target)


def collect_images(theme_dir: Path) -> list[str]:
    images: list[str] = []
    for file_path in theme_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        images.append(file_path.relative_to(theme_dir).as_posix())
    return sorted(images)


def pick_preview(images: list[str]) -> str | None:
    lowered = {image.lower(): image for image in images}
    for candidate in PREVIEW_CANDIDATES:
        if candidate in lowered:
            return lowered[candidate]

    for image in images:
        if "preview" in image.lower():
            return image
    return images[0] if images else None


def build_gallery(images: list[str], preview_image: str | None) -> list[str]:
    def score(item: str) -> tuple[int, str]:
        lowered = item.lower()
        if preview_image and item == preview_image:
            return (0, lowered)
        if "preview" in lowered:
            return (1, lowered)
        if "bg" in lowered or "background" in lowered:
            return (2, lowered)
        if lowered.startswith("images/"):
            return (3, lowered)
        return (4, lowered)

    ordered = sorted(images, key=score)
    return ordered[:8]


def to_public_url(path: Path, public_root: Path) -> str:
    return "/" + path.relative_to(public_root).as_posix()


def process_zip_package(
    zip_path: Path,
    public_root: Path,
    themes_root: Path,
    downloads_root: Path,
    used_ids: set[str],
) -> dict:
    theme_data, root_prefix = read_theme_json(zip_path)

    fallback_id = sanitize_theme_id(zip_path.stem, "theme")
    proposed_id = sanitize_theme_id(str(theme_data.get("id", "")), fallback_id)
    theme_id = unique_theme_id(proposed_id, used_ids)
    used_ids.add(theme_id)

    theme_dir = themes_root / theme_id
    extract_package(zip_path, theme_dir, root_prefix)

    download_target = downloads_root / zip_path.name
    shutil.copy2(zip_path, download_target)

    images = collect_images(theme_dir)
    preview_rel = pick_preview(images)
    gallery_rel = build_gallery(images, preview_rel)

    zip_stat = zip_path.stat()
    metadata = {
        "id": theme_id,
        "sourceId": theme_data.get("id", theme_id),
        "name": theme_data.get("name", theme_id),
        "version": theme_data.get("version", "1.0.0"),
        "author": theme_data.get("author", "未知作者"),
        "description": theme_data.get("description", "暂无描述"),
        "schemaVersion": theme_data.get("schemaVersion", "1.0"),
        "minAppVersion": theme_data.get("minAppVersion", "1.0.0"),
        "minPlatformVersion": theme_data.get("minPlatformVersion", 1000),
        "tags": theme_data.get("tags", []),
        "updatedAt": datetime.fromtimestamp(zip_stat.st_mtime, tz=timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "package": {
            "fileName": zip_path.name,
            "sizeBytes": zip_stat.st_size,
            "downloadUrl": to_public_url(download_target, public_root),
        },
        "paths": {
            "themeDir": to_public_url(theme_dir, public_root),
            "themeJson": to_public_url(theme_dir / THEME_JSON_NAME, public_root),
            "preview": to_public_url(theme_dir / preview_rel, public_root) if preview_rel else None,
            "gallery": [to_public_url(theme_dir / item, public_root) for item in gallery_rel],
        },
    }
    return metadata


def build_catalog(repo_root: Path) -> dict:
    packages_root = repo_root / "packages"
    public_root = repo_root / "public"
    themes_root = public_root / "themes"
    downloads_root = public_root / "downloads"
    data_root = public_root / "data"

    clean_directory(themes_root)
    clean_directory(downloads_root)
    data_root.mkdir(parents=True, exist_ok=True)

    zip_files = sorted(packages_root.glob("*.zip"))

    used_ids: set[str] = set()
    themes: list[dict] = []
    warnings: list[str] = []

    for zip_file in zip_files:
        try:
            metadata = process_zip_package(zip_file, public_root, themes_root, downloads_root, used_ids)
            themes.append(metadata)
        except Exception as exc:  # pylint: disable=broad-except
            warnings.append(f"{zip_file.name}: {exc}")

    themes.sort(key=lambda item: str(item.get("name", "")).lower())

    catalog = {
        "schemaVersion": "1.0",
        "generatedAt": utc_now(),
        "count": len(themes),
        "themes": themes,
        "warnings": warnings,
    }

    output_path = data_root / "themes.json"
    output_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    return catalog


def main() -> None:
    parser = argparse.ArgumentParser(description="Build static theme catalog data")
    parser.add_argument(
        "--repo-root",
        default=Path(__file__).resolve().parent.parent,
        type=Path,
        help="Project root containing packages/ and public/",
    )
    args = parser.parse_args()

    repo_root: Path = args.repo_root.resolve()
    catalog = build_catalog(repo_root)

    print(f"Built catalog with {catalog['count']} theme(s)")
    if catalog["warnings"]:
        print("Warnings:")
        for item in catalog["warnings"]:
            print(f"- {item}")


if __name__ == "__main__":
    main()
