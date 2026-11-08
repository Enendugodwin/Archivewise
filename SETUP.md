# ArchiveWise - Instructor Setup and Test Guide

This guide is for instructors and reviewers who want to run the local ArchiveWise demo and inspect the Round 1 submission. It is not required for the NAS Skill runtime.

## What this build includes

- **Separate pages** for Overview, Duplicates, Documents, Tags, Archive, and Needs attention.
- **Top 20 file type recognition**: PDF, DOCX, DOC, XLSX, XLS, PPTX, PPT, TXT, CSV, MD, JSON, XML, HTML, RTF, JPG, JPEG, PNG, GIF, MP4, and MP3.
- **Documents** extracts text, Word, Excel, PowerPoint, HTML, CSV, RTF, JSON, XML, and Markdown. PDF is optional via `pypdf`. Images, video, and audio appear under **Other files recognized**.
- **Tags** proposes project tags plus generic `image`, `video`, and `audio` type tags.
- **Archive** lists read-only archive suggestions and duplicate groups to resolve. No files are moved.
- **Browse** opens an in-app folder browser at the parent of the current folder. It lists local and removable drives only; disconnected network drives are excluded so the picker cannot hang.

## 1. Prerequisites

- Windows 10/11, macOS, or Linux
- Python 3.10 or newer (tested with Python 3.12)
- A modern browser (Edge, Chrome, or Firefox)
- Optional: Node.js 18+ for the static Skill checker
- Optional: Git for cloning the repository

The demo uses the Python standard library for text, Word, Excel, PowerPoint, HTML, CSV, RTF, JSON, XML, and Markdown. PDF extraction is optional and needs `pypdf`:

```powershell
python -m pip install -r demo\requirements.txt
```

Without `pypdf`, PDFs are reported under **Needs attention** rather than guessed.

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
- **2 archive ideas** (the two duplicate groups)
- **3 needs-attention items** (2 could not be reviewed, 1 without a tag proposal)

Walk through each page:

1. **Overview** - confirm the folder path, summary numbers, and the "Select a card to open its page" hint.
2. **Browse** - press **Browse**, use **Home** and the folder list, navigate to a folder, and press **Use this folder**. The folder should load in Overview.
3. **Duplicates** - confirm two groups: `Project-A_contract.txt` with its copy, and `Project-B_invoice.txt` with its duplicate.
4. **Documents** - confirm five rows with type, date, project, status, and an evidence excerpt. The "Other files recognized" section lists images, video, and audio in folders that contain them.
5. **Tags** - select all four tags and press **Approve selected**. Folders with images/media also show generic `image`, `video`, or `audio` type tags with a **TYPE** badge.
6. **Archive** - confirm two duplicate groups under "Duplicate groups to resolve" and no file-level suggestions. **Archive suggestions are read-only; no files are moved.**
7. **Needs attention** - confirm `broken.txt` and `scan.bin` under "Could not review", and `notes.txt` under "No tag proposal". `scan.bin` is identified as an unknown `.bin` file; legacy `.doc`, `.xls`, and `.ppt` files would also appear here with a conversion hint.
8. **Navigation** - switch pages from the left sidebar, the app dock, and (on narrow screens) the mobile chips. The active page should stay in sync.
9. **Window controls** - try minimize/restore, maximize, and close/reopen from the title bar.

### Test other document formats

Use **Change folder** to open:

```text
demo/formats-folder
```

Expected result: **6 files, 5 documents, 6 proposed tags, 4 archive suggestions, 1 other file**. The PNG appears under **Documents > Other files recognized** and gets an `image` type tag.

The folder contains `.docx`, `.xlsx`, `.html`, `.csv`, and `.rtf` files. Their fields should appear on **Documents**, tags on **Tags**, and destinations such as `Archive/2026/Project-C` on **Archive**.

### What the demo changes

The demo writes only one file, `archivewise-tags.json`, inside the reviewed folder. It never deletes, moves, renames, or rewrites a reviewed file. Archive suggestions are read-only.

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
| Browse shows no subfolders | The picker opens at the parent of the current folder. Use **Home** or **Up**, or select a subfolder. Disconnected network drives are not listed. |
| The page looks stale | Refresh; the server sends `Cache-Control: no-store`. |
| The tag file is missing | It is inside the reviewed folder, named `archivewise-tags.json`. |
| PDF is under "Needs attention" | Install optional PDF support: `python -m pip install -r demo\requirements.txt`. |
| A file says "unknown or unsupported file type" | The demo recognizes the top 20 common extensions. Images, video, and audio are identified; unknown extensions are flagged. |
| The checker command fails | Confirm Node.js is installed and the kit path is exactly as above. |

## 7. Instructor checklist

- [ ] `python demo\gui_server.py` starts and opens the GUI
- [ ] Overview shows 7 files, 2 duplicate groups, 5 documents, 4 proposed tags, 2 archive ideas
- [ ] Overview's File types card shows Documents 6 and Other 1
- [ ] Browse opens the in-app folder browser and loads a selected folder
- [ ] Duplicates shows two groups
- [ ] Documents shows five rows with evidence and no other files
- [ ] Tags accepts selection and shows the applied state
- [ ] Archive shows the two duplicate groups and no file-level suggestions
- [ ] `demo/formats-folder` shows 5 documents from DOCX, XLSX, HTML, CSV, and RTF
- [ ] `demo/formats-folder` shows 1 other file (PNG) under Documents
- [ ] `demo/formats-folder` shows 6 tags, including the `image` type tag
- [ ] `demo/formats-folder` shows 4 archive suggestions
- [ ] Needs attention shows 2 unresolved files and 1 file without a tag proposal
- [ ] `archivewise-tags.json` is created in the reviewed folder
- [ ] Reviewed files are unchanged
- [ ] Optional: the bundled checker returns `static-pass` with zero diagnostics

## Scope note

This is a local simulation of the ArchiveWise review flow, not the UGREEN NAS runtime. The submitted Skill runs on UGREEN NAS through the registered `file-agent` and `document-agent` experts. Round 1 does not claim NAS runtime evidence.
