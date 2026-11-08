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
import csv
import hashlib
import html as html_lib
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

MAX_DEPTH = 3
MAX_FILES = 200
TEXT_EXTS = {".txt", ".md", ".markdown", ".csv", ".log", ".json", ".xml", ".html", ".htm"}
OFFICE_EXTS = {".docx", ".xlsx", ".pptx"}
LEGACY_EXTS = {".doc", ".xls", ".ppt"}
FILE_TYPES = {
    ".pdf": ("document", "PDF"),
    ".docx": ("document", "Word"),
    ".doc": ("document", "Word (legacy)"),
    ".xlsx": ("document", "Excel"),
    ".xls": ("document", "Excel (legacy)"),
    ".pptx": ("document", "PowerPoint"),
    ".ppt": ("document", "PowerPoint (legacy)"),
    ".txt": ("document", "Text"),
    ".csv": ("document", "CSV"),
    ".md": ("document", "Markdown"),
    ".json": ("document", "JSON"),
    ".xml": ("document", "XML"),
    ".html": ("document", "HTML"),
    ".rtf": ("document", "RTF"),
    ".jpg": ("image", "JPEG image"),
    ".jpeg": ("image", "JPEG image"),
    ".png": ("image", "PNG image"),
    ".gif": ("image", "GIF image"),
    ".mp4": ("video", "MP4 video"),
    ".mp3": ("audio", "MP3 audio"),
}
DOCUMENT_EXTS = {ext for ext, (kind, _) in FILE_TYPES.items() if kind == "document"} | TEXT_EXTS
NON_DOCUMENT_KINDS = {"image", "video", "audio"}
ARCHIVE_STATUSES = {"signed", "paid", "final", "complete", "archived", "closed"}
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


def _safe_read_text(path: Path, encoding: str = "utf-8-sig") -> tuple[str, str | None]:
    try:
        return path.read_text(encoding=encoding), None
    except UnicodeDecodeError:
        return "", "not UTF-8 text"
    except OSError as error:
        return "", f"unreadable: {error}"


def _docx_text(path: Path) -> tuple[str, str | None]:
    try:
        with zipfile.ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
    except (KeyError, zipfile.BadZipFile, ET.ParseError) as error:
        return "", f"could not read Word document: {error}"
    lines = []
    for paragraph in root.iter():
        if paragraph.tag.endswith("}p"):
            text = "".join(node.text or "" for node in paragraph.iter() if node.tag.endswith("}t"))
            if text.strip():
                lines.append(text.strip())
    return "\n".join(lines), None


def _xlsx_text(path: Path) -> tuple[str, str | None]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            shared: list[str] = []
            if "xl/sharedStrings.xml" in names:
                root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
                for item in root.iter():
                    if item.tag.endswith("}si"):
                        shared.append(
                            "".join(
                                node.text or ""
                                for node in item.iter()
                                if node.tag.endswith("}t")
                            )
                        )
            lines: list[str] = list(shared)
            sheets = sorted(
                name
                for name in names
                if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
            )
            for sheet in sheets:
                root = ET.fromstring(archive.read(sheet))
                for cell in root.iter():
                    if not cell.tag.endswith("}c"):
                        continue
                    value = None
                    for child in cell:
                        if child.tag.endswith("}v") and child.text is not None:
                            value = child.text
                        elif child.tag.endswith("}is"):
                            value = "".join(
                                node.text or ""
                                for node in child.iter()
                                if node.tag.endswith("}t")
                            )
                    if value is None:
                        continue
                    if cell.get("t") == "s":
                        try:
                            value = shared[int(value)]
                        except (ValueError, IndexError):
                            pass
                    lines.append(value)
    except (zipfile.BadZipFile, ET.ParseError, KeyError) as error:
        return "", f"could not read Excel workbook: {error}"
    return "\n".join(lines), None


def _pptx_text(path: Path) -> tuple[str, str | None]:
    try:
        with zipfile.ZipFile(path) as archive:
            slides = sorted(
                name
                for name in archive.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            )
            lines: list[str] = []
            for slide in slides:
                root = ET.fromstring(archive.read(slide))
                for node in root.iter():
                    if node.tag.endswith("}t") and node.text:
                        lines.append(node.text)
    except (zipfile.BadZipFile, ET.ParseError) as error:
        return "", f"could not read PowerPoint deck: {error}"
    return "\n".join(lines), None


def _pdf_text(path: Path) -> tuple[str, str | None]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return "", "PDF extraction needs pypdf; install demo/requirements.txt"
    try:
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as error:
        return "", f"could not read PDF: {error}"
    if not text.strip():
        return "", "PDF has no extractable text"
    return text, None


def _rtf_text(path: Path) -> tuple[str, str | None]:
    try:
        raw = path.read_text(encoding="latin-1", errors="replace")
    except OSError as error:
        return "", f"unreadable: {error}"
    raw = re.sub(r"\\'([0-9a-fA-F]{2})", lambda match: chr(int(match.group(1), 16)), raw)
    raw = raw.replace("\\par", "\n").replace("\\line", "\n")
    raw = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", raw)
    raw = raw.replace("{", "").replace("}", "")
    return raw, None


def _html_text(path: Path) -> tuple[str, str | None]:
    text, error = _safe_read_text(path)
    if error:
        return "", error
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<br\s*/?>|</p>|</div>|</h[1-6]>|</li>|</tr>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return html_lib.unescape(text), None


def _xml_text(path: Path) -> tuple[str, str | None]:
    text, error = _safe_read_text(path)
    if error:
        return "", error
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return re.sub(r"<[^>]+>", " ", text), None
    lines = []
    for element in root.iter():
        if len(element) == 0 and element.text and element.text.strip():
            tag = element.tag.split("}")[-1]
            lines.append(f"{tag}: {element.text.strip()}")
    return "\n".join(lines), None


def _json_text(path: Path) -> tuple[str, str | None]:
    text, error = _safe_read_text(path)
    if error:
        return "", error
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        return "", f"invalid JSON: {error}"
    lines: list[str] = []

    def walk(value) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if isinstance(item, (dict, list)):
                    walk(item)
                else:
                    lines.append(f"{key}: {item}")
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    return "\n".join(lines), None


def _csv_text(path: Path) -> tuple[str, str | None]:
    text, error = _safe_read_text(path)
    if error:
        return "", error
    try:
        rows = list(csv.reader(io.StringIO(text)))
    except csv.Error:
        return text, None
    if not rows:
        return "", None
    header = [cell.strip() for cell in rows[0]]
    lines = []
    for row in rows[1:]:
        for key, value in zip(header, row):
            if key and value.strip():
                lines.append(f"{key}: {value.strip()}")
    return "\n".join(lines) or text, None


def extract_text(path: Path) -> tuple[str, str | None]:
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return _html_text(path)
    if suffix == ".xml":
        return _xml_text(path)
    if suffix == ".json":
        return _json_text(path)
    if suffix == ".csv":
        return _csv_text(path)
    if suffix == ".docx":
        return _docx_text(path)
    if suffix == ".xlsx":
        return _xlsx_text(path)
    if suffix == ".pptx":
        return _pptx_text(path)
    if suffix == ".pdf":
        return _pdf_text(path)
    if suffix == ".rtf":
        return _rtf_text(path)
    if suffix in LEGACY_EXTS:
        modern = {".doc": ".docx", ".xls": ".xlsx", ".ppt": ".pptx"}[suffix]
        return "", f"legacy {suffix} file; save as {modern} to extract fields"
    if suffix in TEXT_EXTS:
        return _safe_read_text(path)
    return "", f"not a supported document format ({suffix or 'no extension'})"


def extract_fields(path: Path) -> tuple[dict[str, str] | None, str | None]:
    text, error = extract_text(path)
    if error:
        return None, error
    found: dict[str, str] = {}
    for key in FIELDS:
        match = re.search(rf"(?im)^\s*{key}\s*:\s*(.+?)\s*$", text)
        if match:
            found[key] = match.group(1).strip()
    return found, None


def evidence_excerpt(path: Path, limit: int = 90) -> str:
    text, error = extract_text(path)
    if error:
        return "not available"
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line if len(line) <= limit else line[: limit - 1] + "..."
    return "empty document"


def review_file(path: Path) -> dict:
    if path.suffix.lower() not in DOCUMENT_EXTS:
        return {
            "supported": False,
            "fields": {},
            "excerpt": "",
            "error": "not a supported document format",
        }
    fields, error = extract_fields(path)
    if error:
        return {"supported": False, "fields": {}, "excerpt": "", "error": error}
    return {
        "supported": True,
        "fields": fields,
        "excerpt": evidence_excerpt(path),
        "error": None,
    }


def classify_file(path: Path) -> dict:
    suffix = path.suffix.lower()
    if suffix in FILE_TYPES:
        kind, label = FILE_TYPES[suffix]
    elif suffix in TEXT_EXTS:
        kind, label = "document", "Text"
    else:
        kind, label = "other", "Unknown file"
    return {"kind": kind, "label": label, "extension": suffix or "(none)"}


def file_metadata(path: Path) -> dict:
    info = classify_file(path)
    try:
        size = path.stat().st_size
    except OSError:
        size = 0
    return {
        "kind": info["kind"],
        "label": info["label"],
        "size": size,
        "detail": f"{info['label']} - {human_size(size)}",
    }


def archive_suggestion(fields: dict[str, str]) -> dict | None:
    project = fields.get("project")
    if not project:
        return None
    status = (fields.get("status") or "").strip().lower()
    folder = tag_for(project) or "Unsorted"
    date_text = fields.get("date") or ""
    if status in ARCHIVE_STATUSES:
        year = date_text[:4] if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_text) else "Unsorted"
        return {
            "destination": f"Archive/{year}/{folder}",
            "reason": f"Status is {status}",
            "confidence": "high",
        }
    match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", date_text)
    if match:
        try:
            document_date = date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            age_days = (date.today() - document_date).days
        except ValueError:
            age_days = 0
        if age_days > 365:
            return {
                "destination": f"Archive/{match.group(1)}/{folder}",
                "reason": "Document date is older than 12 months",
                "confidence": "medium",
            }
    return None


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


def print_other_files(root: Path, other_files: list[tuple[Path, dict]]) -> None:
    print("3b. Other files recognized")
    if not other_files:
        print("   No image, video, or audio files.")
        print()
        return
    for path, info in other_files:
        print(f"   {rel(root, path)}  |  {info['label']}  |  {human_size(info['size'])}")
    print()


def print_archive(root: Path, groups: dict[str, list[Path]], suggestions: list[tuple[Path, dict]]) -> None:
    print("5. Archive suggestions (read-only)")
    if not suggestions and not groups:
        print("   No archive suggestions.")
        print()
        return
    for path, suggestion in suggestions:
        print(f"   {rel(root, path)}  ->  {suggestion['destination']}")
        print(f"     {suggestion['reason']}")
    for members in groups.values():
        print("   Duplicate group: keep one copy; the others are archive candidates.")
        for member in members:
            print(f"     - {rel(root, member)}")
    print("   No files are moved by this demo.")
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
    archive_suggestions: list[tuple[Path, dict]] = []
    other_files: list[tuple[Path, dict]] = []
    duplicate_members = {member for members in groups.values() for member in members}
    for path in files:
        if path.name == TAG_FILE:
            continue
        info = classify_file(path)
        if info["kind"] == "document":
            review = review_file(path)
            if not review["supported"]:
                skipped.append((path, review["error"] or "could not review"))
                continue
            fields = review["fields"]
            findings.append((path, fields, review["excerpt"]))
            project = fields.get("project")
            if project:
                tag = tag_for(project)
                if tag:
                    proposals.append((path, tag))
            if path not in duplicate_members:
                suggestion = archive_suggestion(fields)
                if suggestion:
                    archive_suggestions.append((path, suggestion))
        elif info["kind"] in NON_DOCUMENT_KINDS:
            other_files.append((path, file_metadata(path)))
            proposals.append((path, info["kind"]))
        else:
            skipped.append((path, f"unknown or unsupported file type ({info['extension']})"))

    print_findings(folder, findings, skipped)
    print_other_files(folder, other_files)
    print_proposals(folder, proposals)
    print_archive(folder, groups, archive_suggestions)

    if not proposals:
        print("No tags are available for approval. Stopping.")
        return 0

    selected = ask_approval(len(proposals), args.approve_all, args.no_input)
    if selected is None:
        print()
        print("No changes were made.")
        return 0

    applied, failed = apply_tags(folder, proposals, selected)
    print("6. Result")
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
