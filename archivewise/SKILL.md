---
name: archivewise
description: ArchiveWise produces an evidence-based cleanup review of one chosen NAS folder, covering duplicate groups and document details, and prepares tags for the user to approve. Use when a user asks to review, deduplicate, or tag files in a specific folder and wants a clear plan before anything changes.
---

# Goal

ArchiveWise gives a NAS user one folder-level review before any file is changed. For the folder the user names, it lists the files, reports only the duplicate groups returned by the NAS duplicate scan, extracts requested document facts with source file names, and proposes tags. The user approves the exact tags and files, and ArchiveWise then delegates only those actions and reports what actually happened.

ArchiveWise does not move, delete, compress, or decompress files in this version, and it preserves every reviewed file. It never scans the whole NAS, and it never claims a storage saving that the returned results do not support. A planned, pending, or partial step is never described as complete.

# Required input

Ask only for what is missing, in one focused follow-up:

- **Folder to review.** The exact folder path the user names. If the folder is missing from the request, ask for it. Do not substitute a default folder, a parent folder, or a wider search area.
- **Review purpose.** Duplicates only, document review, or both. If the user asks for documents, collect the fields or question they care about, such as document type, date, project, or status.
- **Approval.** An explicit selection of files and tags. A general request to clean up the folder is not approval for any tag change.

Do not ask the user for CLI names, tag identifiers, or other values that a child expert owns and returns.

# Safety rules

- Work only inside the confirmed folder and only on files observed in the listing step.
- Treat a duplicate group as evidence only when the duplicate scan returns it. Never infer duplicates from similar names, sizes, or dates alone.
- Preserve every reviewed file. ArchiveWise does not move, delete, replace, or rename files in this version.
- Use read-only steps first, and pass only real results from one delegation into the next.
- Ask for explicit approval before any tag is added. Name each file and tag in the approval request.
- Respect the platform approval gates that the child experts apply. Wait for the returned state instead of assuming that an action was approved.
- Do not report a storage-savings total. Report duplicate sizes only as values the scan returned, with the exact files they cover.
- When a file is inaccessible or a document cannot be extracted, disclose the gap and continue only for recommendations that do not depend on the missing evidence.

# Workflow

## Step 1 — Confirm the review scope

Restate the folder, the purpose, and the document fields in one message. Ask for any missing item. Do not begin a scan until the folder is confirmed.

## Step 2 — List the selected folder

Delegate a read-only listing to `file-agent`. Use the exact folder the user confirmed.

```
delegate --target file-agent --instruction 'List the contents of the folder the user named, using a read-only listing with a bounded recursion depth and a result limit. If the user gave a relative folder name, resolve it inside the user directory first. Return the resolved folder path, then each file path, name, size, and modified time, and separate directories from files. Do not widen the scope. If the folder is missing or unreadable, report that and return no files. Change nothing.'
```

If the listing fails or the folder is empty, follow the completion-and-failure rules below and stop before the duplicate scan. Use the resolved folder path returned by the listing for every later step, and show that path in the review.

## Step 3 — Run the duplicate scan

Delegate a read-only duplicate scan to `file-agent` for the resolved folder path returned by the listing step.

```
delegate --target file-agent --instruction 'Run a read-only duplicate scan on the resolved folder path returned by the listing delegation, with scope all unless the user asked for one media type. Return only the duplicate groups the scan reports, including every member path, the reported size, and the representative file if the result names one. Do not infer duplicates from similar names. Change nothing.'
```

Use only the returned groups. If the scan returns no groups, report that no duplicate groups were found and do not propose duplicate-based tags.

## Step 4 — Extract document facts

Run this step only when the user asked for document review. Delegate to `document-agent` with the real file paths returned by the listing step. Choose document files from the listing; do not invent paths.

```
delegate --target document-agent --instruction 'Extract the requested facts from the document files returned by the listing step. Use the fields the user named when given, otherwise extract document type, date, project, and status. For every value, return the source file path and a short evidence excerpt. Mark absent fields as missing, list every file that could not be read or extracted, and do not guess content. Return only real extraction results.'
```

Keep missing fields separate from negative findings. A field that is absent is missing, not false.

## Step 5 — Present the review and ask for approval

Use the layout in [references/review-format.md](references/review-format.md). Include:

- the confirmed folder and the review purpose;
- each duplicate group with every member path and the evidence that the scan returned;
- each document finding with its source path, extracted value, and evidence excerpt, plus missing or unreadable items;
- the proposed tag for each file, with a short reason for each, or no change;
- an explicit list of the tag and file pairs waiting for approval.

Ask the user to approve or reject specific tag and file pairs. Wait for the answer. This is a `waiting_user` state, and no change may be made while it is open.

## Step 6 — Apply approved tags

Run this step only for tags the user approved. Delegate to `file-agent` with the exact approved paths and tag names.

```
delegate --target file-agent --instruction 'Apply the approved tags to the exact approved file paths. Reuse an existing tag with the approved name, or create that tag first if it does not exist, then attach it to the approved paths. Apply only the approved file and tag pairs, and report the outcome for each file, including failures.'
```

If the child expert reports `waiting_approval`, stop and tell the user which tag actions are pending. Do not repeat the request.

## Step 7 — Summarize the outcome

Report what changed, what failed, and what still needs a decision. Keep the summary tied to returned results. Do not claim a completed tag action that the child expert did not confirm.

# Completion and failure

A delegated step counts only when the child expert returns `completed` with a real business result. Pass only that real result into the next delegation, and stop dependent steps when the required result is unavailable.

- **`completed`** — use the returned business result, then continue with the next planned step.
- **`failed`** — report the failure, preserve any partial result, and do not retry with a wider scope or a different folder.
- **`cancelled`** — stop, state that no further change was made, and list any action that had already completed.
- **`waiting_user`** — ask the one missing question or approval request, then stop. Do not start dependent work.
- **`waiting_approval`** — report the pending approval, stop, and treat the action as not done.

## Empty results

If the listing returns no matching items, report that no matching items were found and stop. If the duplicate scan returns no groups, report that no duplicate groups were found and do not propose duplicate-based tags. If document review returns no usable extraction, report the empty result and do not propose document-based tags.

## Partial results

If some files are unreadable, some documents cannot be extracted, or only part of an approved tag action succeeds, report the completed items, the failed items, and the unresolved items separately. Do not fill gaps with guesses, and do not apply a tag that depends on missing evidence.

# Generation-time capability evidence

- `ug-filesystem` → `file-agent`
- `ug-filemgr` → `file-agent`
- `ug-document` → `document-agent`

# Boundary and disclosure

This Skill orchestrates catalog capabilities through registered experts only. It adds no deletion, move, compression, background scheduling, whole-NAS scanning, streaming, sharing, database hosting, or custom interfaces. Moving or archiving files is deferred until the file move workflow can be validated on a NAS. Local static checks do not prove installation, compatibility, or device runtime behavior.

Built with the UGREEN Uliya Skill Creation Tool (kit version 0.7.3) and the OpenCode AI coding assistant. No third-party components are bundled with this Skill.
