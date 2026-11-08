#!/usr/bin/env python3
"""Local web GUI for the ArchiveWise workflow simulator.

This serves a browser UI on 127.0.0.1 only. It is a simulation of the review
and approval flow, not the Uliya Skill runtime. Reviewed files are never
modified; approved tags are written to archivewise-tags.json.
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    import archivewise_demo as core
except ImportError:  # pragma: no cover - module execution fallback
    from . import archivewise_demo as core  # type: ignore

HERE = Path(__file__).resolve().parent
GUI_INDEX = HERE / "gui" / "index.html"
SAMPLE = HERE / "sample-folder"


def resolve_folder(raw: str | None) -> Path:
    value = (raw or "").strip()
    folder = Path(value).expanduser() if value else SAMPLE
    if not folder.is_absolute():
        folder = (Path.cwd() / folder).resolve()
    else:
        folder = folder.resolve()
    if not folder.is_dir():
        raise ValueError(f"Folder not found: {folder}")
    return folder


def build_review(folder: Path) -> dict:
    files = core.collect_files(folder)
    hashes: dict[str, list[Path]] = {}
    unreadable: list[dict[str, str]] = []
    for path in files:
        try:
            hashes.setdefault(core.sha256_file(path), []).append(path)
        except OSError as error:
            unreadable.append({"file": core.rel(folder, path), "reason": f"unreadable: {error}"})

    groups = []
    for digest, members in hashes.items():
        if len(members) > 1:
            groups.append(
                {
                    "hash": digest,
                    "size": members[0].stat().st_size,
                    "members": [core.rel(folder, member) for member in members],
                }
            )
    groups.sort(key=lambda item: item["size"], reverse=True)

    findings = []
    skipped = list(unreadable)
    proposals = []
    untagged = []
    archive_suggestions = []
    other_files = []
    type_counts = {}
    duplicate_members = {
        core.rel(folder, member)
        for members in (group for group in hashes.values() if len(group) > 1)
        for member in members
    }
    for path in files:
        info = core.classify_file(path)
        type_counts[info["kind"]] = type_counts.get(info["kind"], 0) + 1
        item = core.rel(folder, path)
        if info["kind"] == "document":
            review = core.review_file(path)
            if not review["supported"]:
                skipped.append({"file": item, "reason": review["error"] or "could not review"})
                continue
            fields = review["fields"]
            findings.append(
                {
                    "file": item,
                    "fields": {key: fields.get(key) for key in core.FIELDS},
                    "excerpt": review["excerpt"],
                }
            )
            project = fields.get("project")
            tag = core.tag_for(project) if project else None
            if tag:
                proposals.append(
                    {
                        "id": len(proposals),
                        "file": item,
                        "tag": tag,
                        "reason": f"project: {project}",
                        "kind": "project",
                    }
                )
            else:
                untagged.append(item)
            if item not in duplicate_members:
                suggestion = core.archive_suggestion(fields)
                if suggestion:
                    archive_suggestions.append({"file": item, **suggestion})
        elif info["kind"] in core.NON_DOCUMENT_KINDS:
            metadata = core.file_metadata(path)
            other_files.append(
                {
                    "file": item,
                    "kind": info["kind"],
                    "label": info["label"],
                    "size": metadata["size"],
                    "detail": metadata["detail"],
                }
            )
            proposals.append(
                {
                    "id": len(proposals),
                    "file": item,
                    "tag": info["kind"],
                    "reason": f"file type: {info['label']}",
                    "kind": "type",
                }
            )
        else:
            skipped.append(
                {"file": item, "reason": f"unknown or unsupported file type ({info['extension']})"}
            )

    labels = {
        "document": "Documents",
        "image": "Images",
        "video": "Video",
        "audio": "Audio",
        "other": "Other",
    }
    file_types = [
        {"kind": kind, "label": labels[kind], "count": type_counts[kind]}
        for kind in ("document", "image", "video", "audio", "other")
        if type_counts.get(kind)
    ]

    return {
        "folder": str(folder),
        "sample": folder == SAMPLE.resolve(),
        "limits": {"depth": core.MAX_DEPTH, "max_files": core.MAX_FILES},
        "files": len(files),
        "groups": groups,
        "findings": findings,
        "proposals": proposals,
        "skipped": skipped,
        "untagged": untagged,
        "archive_suggestions": archive_suggestions,
        "other_files": other_files,
        "file_types": file_types,
    }


def apply_selection(folder: Path, selected: list[int]) -> dict:
    review = build_review(folder)
    by_id = {item["id"]: item for item in review["proposals"]}
    chosen = [by_id[item] for item in sorted(set(selected)) if item in by_id]
    tag_path = folder / core.TAG_FILE
    data = core.load_tags(tag_path)
    applied = []
    failed = []
    for proposal in chosen:
        key = proposal["file"]
        tags = data.setdefault(key, [])
        if proposal["tag"] not in tags:
            tags.append(proposal["tag"])
        applied.append({"file": key, "tag": proposal["tag"]})
    try:
        tag_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except OSError as error:
        failed.append({"file": core.TAG_FILE, "reason": str(error)})
    return {"applied": applied, "failed": failed, "tag_file": str(tag_path)}


def list_directories(raw: str | None) -> dict:
    """List subdirectories for the in-app folder browser."""
    value = (raw or "").strip()
    path = Path(value).expanduser() if value else Path.home()
    path = path.resolve()
    if not path.is_dir():
        raise ValueError(f"Not a folder: {path}")
    directories = []
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        directories.append({"name": entry.name, "path": entry.path})
                        if len(directories) >= 500:
                            break
                except OSError:
                    continue
    except OSError as error:
        raise ValueError(f"Cannot read folder: {error}") from error
    directories.sort(key=lambda item: item["name"].casefold())
    drives = []
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            mask = kernel32.GetLogicalDrives()
            for index, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                if not (mask & (1 << index)):
                    continue
                root = f"{letter}:\\"
                try:
                    drive_type = kernel32.GetDriveTypeW(ctypes.c_wchar_p(root))
                except Exception:
                    drive_type = 3
                if drive_type in (2, 3, 6):
                    drives.append(root)
        except Exception:
            drives = [f"{letter}:\\" for letter in ("C", "D") if Path(f"{letter}:\\").is_dir()]
    parent = str(path.parent) if path.parent != path else None
    return {
        "path": str(path),
        "parent": parent,
        "directories": directories[:500],
        "drives": drives,
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "ArchiveWiseDemo/1.0"

    def log_message(self, fmt: str, *args) -> None:  # noqa: N802
        pass

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(status, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")

    def _error(self, status: int, message: str) -> None:
        self._json(status, {"error": message})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            try:
                body = GUI_INDEX.read_bytes()
            except OSError:
                self._error(500, "GUI file not found: demo/gui/index.html")
                return
            self._send(200, body, "text/html; charset=utf-8")
            return
        if parsed.path == "/api/browse":
            path_value = parse_qs(parsed.query).get("path", [""])[0]
            try:
                self._json(200, list_directories(path_value))
            except ValueError as error:
                self._error(400, str(error))
            return
        if parsed.path == "/api/review":
            folder_value = parse_qs(parsed.query).get("folder", [""])[0]
            try:
                folder = resolve_folder(folder_value)
                self._json(200, build_review(folder))
            except ValueError as error:
                self._error(400, str(error))
            return
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return
        self._error(404, "Not found")

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length > 1_000_000:
            self._error(413, "Request too large")
            return
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._error(400, "Invalid JSON")
            return

        if parsed.path == "/api/apply":
            try:
                folder = resolve_folder(payload.get("folder"))
            except ValueError as error:
                self._error(400, str(error))
                return
            selected = payload.get("selected", [])
            if not isinstance(selected, list) or any(not isinstance(item, int) for item in selected):
                self._error(400, "selected must be a list of integer proposal ids")
                return
            self._json(200, apply_selection(folder, selected))
            return

        self._error(404, "Not found")


def main() -> int:
    parser = argparse.ArgumentParser(description="Launch the ArchiveWise local GUI.")
    parser.add_argument("--port", type=int, default=8765, help="first port to try (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", help="do not open a browser")
    args = parser.parse_args()

    server = None
    for port in range(args.port, args.port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            continue
    if server is None:
        print(f"No free port between {args.port} and {args.port + 19}.", flush=True)
        return 1

    url = f"http://127.0.0.1:{server.server_port}/"
    print("ArchiveWise local GUI", flush=True)
    print(f"  {url}", flush=True)
    print("  Local simulation only. Press Ctrl+C to stop.", flush=True)
    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
