# ArchiveWise - Instructor Setup and Test Guide

This guide is for instructors and reviewers who want to run the local ArchiveWise demo and inspect the Round 1 submission. It is not required for the NAS Skill runtime.

## 1. Prerequisites

- Windows 10/11, macOS, or Linux
- Python 3.10 or newer (tested with Python 3.12)
- A modern browser (Edge, Chrome, or Firefox)
- Optional: Node.js 18+ for the static Skill checker
- Optional: Git for cloning the repository

The demo uses only the Python standard library. There is nothing to `pip install`.

## 2. Get the project

```powershell
git clone https://github.com/Enendugodwin/Archivewise.git
cd Archivewise
```

If you received a ZIP instead, extract it and open a terminal in the `Archivewise` folder.

## 3. Start the demo

Windows PowerShell:

```powershell
python demo\gui_server.py
```

macOS or Linux:

```bash
python3 demo/gui_server.py
```

The GUI opens at <http://127.0.0.1:8765/>. If the browser does not open, visit that URL manually.

The server binds to `127.0.0.1` only. Press `Ctrl+C` to stop it.

Optional flags:

```powershell
# Do not open a browser automatically
python demo\gui_server.py --no-browser

# Try a different port first (it tries 20 ports from there)
python demo\gui_server.py --port 9000
```

## 4. Test the pages

The sample folder loads automatically. The expected summary is:

- **7 files**
- **2 duplicate groups**
- **5 documents**
- **4 proposed tags**
- **3 needs-attention items** (2 could not be reviewed, 1 without a tag proposal)

Walk through each page:

1. **Overview** - confirm the folder path, summary numbers, and the "Select a card to open its page" hint.
2. **Browse** - press **Browse**, use **Home** and the folder list, navigate to a folder, and press **Use this folder**. The folder should load in Overview.
3. **Duplicates** - confirm two groups: `Project-A_contract.txt` with its copy, and `Project-B_invoice.txt` with its duplicate.
4. **Documents** - confirm five rows with type, date, project, status, and an evidence excerpt.
5. **Tags** - select all four tags and press **Approve selected**. Confirm the applied state and the result path to `archivewise-tags.json`.
6. **Needs attention** - confirm `broken.txt` and `scan.bin` under "Could not review", and `notes.txt` under "No tag proposal".
7. **Navigation** - switch pages from the left sidebar, the app dock, and (on narrow screens) the mobile chips. The active page should stay in sync.
8. **Window controls** - try minimize/restore, maximize, and close/reopen from the title bar.

### What the demo changes

The demo writes only one file, `archivewise-tags.json`, inside the reviewed folder. It never deletes, moves, renames, or rewrites a reviewed file.

To reset the sample:

```powershell
Remove-Item demo\sample-folder\archivewise-tags.json -ErrorAction SilentlyContinue
```

On macOS or Linux:

```bash
rm -f demo/sample-folder/archivewise-tags.json
```

## 5. Validate the submitted package

| Artifact | Expected |
|---|---|
| `dist/archivewise.zip` | Pre-test Skill package: 3 files, 6,622 bytes |
| `dist/ArchiveWise-Round1-Proposal.pdf` | Round 1 proposal: 2 pages, 445 words for the ten prompts |

Optional static checker:

1. Install Node.js 18 or newer and confirm with `node --version`.
2. Download the UGREEN Uliya Skill Creation Tool from the [Hackathon Starter Kit](https://ai.ugreen.com/pages/hackathon-starter-kit).
3. Extract it so this path exists at the repository root:

   ```text
   uliya-skill-kit-0.7.3-en/uliya-skill-kit/scripts/check-skill.mjs
   ```

   The kit is intentionally not redistributed in this repository.

4. Run the checker:

   ```powershell
   node uliya-skill-kit-0.7.3-en/uliya-skill-kit/scripts/check-skill.mjs archivewise
   ```

5. Expected result:

   ```text
   status: static-pass
   errors: 0
   warnings: 0
   info: 0
   ```

The checker is read-only. It validates the package structure and catalog mapping; it does not prove installation or behavior on a NAS device.

## 6. Troubleshooting

| Problem | Fix |
|---|---|
| `python` is not recognized | Install Python 3.12 and enable "Add python.exe to PATH". Try `py -3` instead. |
| Port 8765 is already in use | Run `python demo\gui_server.py --port 9000`. |
| The browser does not open | Open <http://127.0.0.1:8765/> manually, or use `--no-browser`. |
| Browse shows no subfolders | That folder has no subfolders. Use **Home** or **Up**, or paste a path. |
| The page looks stale | Refresh; the server sends `Cache-Control: no-store`. |
| The tag file is missing | It is inside the reviewed folder, named `archivewise-tags.json`. |
| The checker command fails | Confirm Node.js is installed and the kit path is exactly as above. |

## 7. Instructor checklist

- [ ] `python demo\gui_server.py` starts and opens the GUI
- [ ] Overview shows 7 files, 2 duplicate groups, 5 documents, 4 proposed tags
- [ ] Browse opens the in-app folder browser and loads a selected folder
- [ ] Duplicates shows two groups
- [ ] Documents shows five rows with evidence
- [ ] Tags accepts selection and shows the applied state
- [ ] Needs attention shows 2 unresolved files and 1 file without a tag proposal
- [ ] `archivewise-tags.json` is created in the reviewed folder
- [ ] Reviewed files are unchanged
- [ ] Optional: the bundled checker returns `static-pass` with zero diagnostics

## Scope note

This is a local simulation of the ArchiveWise review flow, not the UGREEN NAS runtime. The submitted Skill runs on UGREEN NAS through the registered `file-agent` and `document-agent` experts. Round 1 does not claim NAS runtime evidence.
