#!/usr/bin/env python3
"""ArchiveWise local workflow simulator.

This is NOT the Uliya Skill runtime. It mirrors the ArchiveWise review and
approval flow on a local folder so the experience can be tried without a NAS.
No NAS capability is called, and reviewed files are never modified, moved,
renamed or deleted. Approved tags are recorded in archivewise-tags.json inside
the reviewed folder.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_DEPTH = 3
MAX_FILES = 200
TEXT_EXTS = {".txt", ".md", ".markdown", ".csv", ".log"}
TAG_FILE = "archivewise-tags.json"
FIELDS = ("type", "date", "project", "status")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.name == TAG_FILE:
            continue
        if len(path.relative_to(root).parts) - 1 > MAX_DEPTH:
            continue
        files.append(path)
        if len(files) >= MAX_FILES:
            break
    return files


def human_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KiB"
    return f"{size / (1024 * 1024):.1f} MiB"


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def extract_fields(path: Path) -> tuple[dict[str, str] | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, "not UTF-8 text (unsupported in this demo)"
    except OSError as error:
        return None, f"unreadable: {error}"
    found: dict[str, str] = {}
    for key in FIELDS:
        match = re.search(rf"(?im)^\s*{key}\s*:\s*(.+?)\s*$", text)
        if match:
            found[key] = match.group(1).strip()
    return found, None


def evidence_excerpt(path: Path, limit: int = 90) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return "not available"
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line if len(line) <= limit else line[: limit - 1] + "..."
    return "empty file"


def tag_for(project: str) -> str | None:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", project).strip("-")
    return slug or None


def print_scope(root: Path, files: list[Path]) -> None:
    print("=" * 78)
    print("ArchiveWise - local workflow simulator")
    print("NOT the Uliya Skill runtime. No NAS capability is called.")
    print("=" * 78)
    print()
    print("1. Scope")
    print(f"   Folder:   {root}")
    print("   Purpose:  duplicates, document review, and proposed tags")
    print(f"   Fields:   {', '.join(FIELDS)}")
    print(f"   Limits:   depth {MAX_DEPTH}, up to {MAX_FILES} files")
    print(f"   Files:    {len(files)}")
    print()


def print_groups(groups: dict[str, list[Path]], root: Path) -> None:
    print("2. Duplicate groups")
    if not groups:
        print("   No duplicate groups were returned for this folder.")
        print()
        return
    for index, (digest, members) in enumerate(sorted(groups.items()), start=1):
        size = members[0].stat().st_size
        print(f"   Group {index} | {human_size(size)} each | sha256 {digest[:16]}...")
        for member in members:
            print(f"     - {rel(root, member)}")
    print()


def print_findings(
    root: Path,
    findings: list[tuple[Path, dict[str, str], str]],
    skipped: list[tuple[Path, str]],
) -> None:
    print("3. Document findings")
    if not findings:
        print("   No text documents were found, so no document fields were extracted.")
    for path, fields, excerpt in findings:
        values = ", ".join(f"{key}={fields.get(key, 'missing')}" for key in FIELDS)
        print(f"   {rel(root, path)}")
        print(f"     {values}")
        print(f"     evidence: {excerpt}")
    if skipped:
        print("   Not reviewed:")
        for path, reason in skipped:
            print(f"     - {rel(root, path)}: {reason}")
    print()


def print_proposals(root: Path, proposals: list[tuple[Path, str]]) -> None:
    print("4. Proposed tags")
    if not proposals:
        print("   No tag is proposed; nothing has enough project evidence.")
    for index, (path, tag) in enumerate(proposals, start=1):
        print(f"   [{index}] {rel(root, path)}  ->  {tag}")
    print()
    print("   No file will be modified. Approved tags are recorded in")
    print(f"   {TAG_FILE} inside the reviewed folder.")
    print()


def ask_approval(count: int, approve_all: bool, no_input: bool) -> list[int] | None:
    if no_input:
        print("   --no-input: review complete, no changes made.")
        return None
    if approve_all:
        print("   --approve-all: approving every proposed tag.")
        return list(range(count))
    print("   Approve all (a), choose numbers (for example 1,3), or cancel (c).")
    while True:
        try:
            choice = input("   Your choice: ").strip().lower()
        except EOFError:
            print()
            print("   No input received; cancelling.")
            return None
        print()
        if choice in {"c", "cancel", "n", "no"}:
            return None
        if choice in {"a", "all", "y", "yes"}:
            return list(range(count))
        selected: list[int] = []
        valid = True
        for piece in choice.replace(" ", "").split(","):
            if not piece:
                continue
            if not piece.isdigit() or not (1 <= int(piece) <= count):
                valid = False
                break
            selected.append(int(piece) - 1)
        if valid and selected:
            return sorted(set(selected))
        print(f"   Enter a, c, or numbers from 1 to {count}.")


def load_tags(path: Path) -> dict[str, list[str]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def apply_tags(
    root: Path,
    proposals: list[tuple[Path, str]],
    selected: list[int],
) -> tuple[list[str], list[str]]:
    tag_path = root / TAG_FILE
    data = load_tags(tag_path)
    applied: list[str] = []
    failed: list[str] = []
    for index in selected:
        path, tag = proposals[index]
        key = rel(root, path)
        try:
            tags = data.setdefault(key, [])
            if tag not in tags:
                tags.append(tag)
            applied.append(key)
        except Exception as error:  # pragma: no cover - defensive
            failed.append(f"{key}: {error}")
    try:
        tag_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as error:
        failed.append(f"{TAG_FILE}: {error}")
    return applied, failed


def main() -> int:
    default_folder = Path(__file__).resolve().parent / "sample-folder"
    parser = argparse.ArgumentParser(
        description="Try the ArchiveWise review/approval flow on a local folder."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=str(default_folder),
        help="folder to review (default: demo/sample-folder)",
    )
    parser.add_argument(
        "--approve-all",
        action="store_true",
        help="approve every proposed tag without prompting",
    )
    parser.add_argument(
        "--no-input",
        action="store_true",
        help="show the review and stop without applying tags",
    )
    args = parser.parse_args()

    folder = Path(args.folder).expanduser()
    if not folder.is_absolute():
        folder = (Path.cwd() / folder).resolve()
    else:
        folder = folder.resolve()
    if not folder.is_dir():
        print(f"Folder not found: {folder}", file=sys.stderr)
        return 2

    files = collect_files(folder)
    if not files:
        print_scope(folder, files)
        print("No matching items were found. Stopping.")
        return 0

    print_scope(folder, files)

    hashes: dict[str, list[Path]] = {}
    for path in files:
        try:
            hashes.setdefault(sha256_file(path), []).append(path)
        except OSError as error:
            print(f"   Could not read {rel(folder, path)}: {error}")
    groups = {digest: members for digest, members in hashes.items() if len(members) > 1}
    print_groups(groups, folder)

    findings: list[tuple[Path, dict[str, str], str]] = []
    skipped: list[tuple[Path, str]] = []
    proposals: list[tuple[Path, str]] = []
    for path in files:
        if path.name == TAG_FILE or path.suffix.lower() not in TEXT_EXTS:
            skipped.append((path, "not a text document in this demo"))
            continue
        fields, error = extract_fields(path)
        if error:
            skipped.append((path, error))
            continue
        findings.append((path, fields, evidence_excerpt(path)))
        project = fields.get("project")
        if project:
            tag = tag_for(project)
            if tag:
                proposals.append((path, tag))

    print_findings(folder, findings, skipped)
    print_proposals(folder, proposals)

    if not proposals:
        print("No tags are available for approval. Stopping.")
        return 0

    selected = ask_approval(len(proposals), args.approve_all, args.no_input)
    if selected is None:
        print()
        print("No changes were made.")
        return 0

    applied, failed = apply_tags(folder, proposals, selected)
    print("5. Result")
    for key in applied:
        print(f"   tagged:  {key}")
    for item in failed:
        print(f"   failed:  {item}")
    print()
    print(f"   Tagged {len(applied)} file(s); {len(proposals) - len(applied)} proposal(s) left unchanged.")
    print(f"   Tag record: {folder / TAG_FILE}")
    print("   No reviewed file was modified, moved, renamed, or deleted.")
    print()
    print("Local simulation only. The submitted Skill delegates to UGREEN NAS experts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
