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
import subprocess
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
    for path in files:
        if path.suffix.lower() not in core.TEXT_EXTS:
            skipped.append({"file": core.rel(folder, path), "reason": "not a text document in this demo"})
            continue
        fields, error = core.extract_fields(path)
        if error:
            skipped.append({"file": core.rel(folder, path), "reason": error})
            continue
        findings.append(
            {
                "file": core.rel(folder, path),
                "fields": {key: fields.get(key) for key in core.FIELDS},
                "excerpt": core.evidence_excerpt(path),
            }
        )
        project = fields.get("project")
        tag = core.tag_for(project) if project else None
        if tag:
            proposals.append(
                {
                    "id": len(proposals),
                    "file": core.rel(folder, path),
                    "tag": tag,
                    "reason": f"project: {project}",
                }
            )
        else:
            untagged.append(core.rel(folder, path))

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


def pick_folder() -> str | None:
    """Open a native folder picker on the machine running the server."""
    if os.name == "nt":
        script = (
            "Add-Type -AssemblyName System.Windows.Forms;"
            "$d = New-Object System.Windows.Forms.FolderBrowserDialog;"
            "$d.Description = 'Choose a folder for ArchiveWise';"
            "$d.ShowNewFolderButton = $false;"
            "if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {"
            "[Console]::Out.Write($d.SelectedPath) }"
        )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-STA", "-WindowStyle", "Hidden", "-Command", script],
                capture_output=True,
                text=True,
                timeout=300,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise RuntimeError(f"Folder picker unavailable: {error}") from error
        return result.stdout.strip() or None

    try:  # pragma: no cover - non-Windows fallback
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Choose a folder for ArchiveWise")
        root.destroy()
        return folder or None
    except Exception as error:  # pragma: no cover
        raise RuntimeError(f"Folder picker unavailable: {error}") from error


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

        if parsed.path == "/api/browse":
            try:
                self._json(200, {"folder": pick_folder()})
            except RuntimeError as error:
                self._error(501, str(error))
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
