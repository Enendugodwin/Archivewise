# Try ArchiveWise locally

The submitted Skill (`archivewise/`) is a Uliya orchestration package. Its real runtime is the UGREEN NAS expert environment, which provides `file-agent`, `document-agent`, and the `delegate` interface.

This folder is a **local simulator** of the review and approval experience. It calls no NAS capability, and it is not part of the submitted ZIP. It exists so you can try the flow on this PC before NAS access is available. The preview is styled after the UGREEN UGOS desktop.

![ArchiveWise local GUI showing duplicate groups, document findings, and proposed tags](archivewise-gui.png)

## Launch the GUI

```powershell
python demo\gui_server.py
```

The browser opens at <http://127.0.0.1:8765/>.

1. The sample folder loads automatically.
2. Or paste any local folder path and press **Analyze**; **Browse** opens a native folder picker.
3. Review duplicate groups, document findings, proposed tags, and unresolved files.
4. Tick the tags you approve and press **Approve selected**.
5. Approved tags are recorded in `archivewise-tags.json` inside the reviewed folder.

Options:

```powershell
# Do not open a browser automatically
python demo\gui_server.py --no-browser

# Start on a different port (tries 20 ports from there)
python demo\gui_server.py --port 9000
```

The server binds to `127.0.0.1` only. Press `Ctrl+C` to stop it.

## Command line (optional)

```powershell
# Interactive review of the sample folder
python demo\archivewise_demo.py

# Review only, no changes
python demo\archivewise_demo.py --no-input

# Approve every proposal automatically
python demo\archivewise_demo.py --approve-all

# Review your own folder
python demo\archivewise_demo.py "C:\Users\user\Documents\some-folder"
```

## What it does

1. Resolves the folder and lists files (depth 3, up to 200 files).
2. Groups byte-identical files by SHA-256.
3. Reads text documents and extracts `Type`, `Date`, `Project`, and `Status`.
4. Presents duplicate groups, document findings, proposed tags, and unresolved items.
5. Asks for approval of exact file and tag pairs.
6. Records approved tags in `archivewise-tags.json` inside the reviewed folder.

It never deletes, moves, renames, or rewrites a reviewed file. Re-run it and the sidecar is skipped from the file list. Delete `archivewise-tags.json` to reset.

## What the sample folder shows

| File | Purpose |
|---|---|
| `Project-A_contract.txt` + `Project-A_contract_copy.txt` | One duplicate group; both propose the `Project-A` tag |
| `Project-B_invoice.txt` + `Project-B_invoice_duplicate.txt` | One duplicate group; both propose the `Project-B` tag |
| `notes.txt` | Missing project field, so no tag is proposed |
| `broken.txt` | Invalid UTF-8, reported as unresolved |
| `scan.bin` | Not a text document, reported as not reviewed |

## Honest limits

- This is a **simulation**, not the Uliya Skill runtime.
- Duplicate detection uses local SHA-256, not UGREEN `scan-dedupe`.
- Only text-like files are read (`.txt`, `.md`, `.markdown`, `.csv`, `.log`). PDF and Office extraction are not implemented here.
- Tags are written to a JSON sidecar, not applied as NAS tags.
- There are no platform approval gates or registered NAS experts in this demo.
- The submitted package remains `dist/archivewise.zip`, built only from `archivewise/SKILL.md` and its linked references.

## Try the real Skill

Upload `dist/archivewise.zip` to UGREEN SkillHub or submit it through the hackathon, then run the trigger on a NAS:

> Review my `Downloads/2026-Projects` folder for duplicates and documents I should keep or tag.
