# Round 1 test cases

These cases validate prompt logic and package structure only. They do not prove NAS runtime behavior, permissions, or end-to-end operation.

## Case 1 — Duplicate review

**Input:** "Review my `/Downloads/2026-Projects` folder for duplicates. Do not change anything yet."

**Expected behavior:**

1. Restates the folder and purpose; no extra questions because the folder and purpose are present. If a relative folder is named, resolves it only under the NAS user directory and verifies that exact path.
2. Delegates a read-only listing to `file-agent` for exactly that folder.
3. Delegates a read-only duplicate scan to `file-agent` for the resolved folder path.
4. Reports only duplicate groups and fields actually returned by the scan. Missing member paths or evidence are marked unavailable; no group members are inferred.
5. Proposes no deletion and preserves every file.
6. Stops at `waiting_user` before any tag.
7. Makes no claim about storage savings.

**Failure variant:** the scan returns no groups. Expected: "No duplicate groups were returned for this folder," followed by stop. No inferred groups from similar names.

## Case 2 — Document review and tagging

**Input:** "Review `/Downloads/2026-Projects` for duplicates. For the PDFs, pull the project and status. Then suggest a tag I can apply."

**Expected behavior:**

1. Confirms the folder, the document fields, and the tagging purpose.
2. Lists the folder and scans duplicates.
3. Passes only the real PDF paths from the listing to `document-agent`.
4. Reports each document with source path, project, status, and an evidence excerpt; missing fields are marked missing.
5. Proposes a tag name for each supported file, or no change, with a reason. If a new tag may need to be created, the approval request explicitly says so.
6. Presents the review and asks for explicit approval of exact file and tag pairs.
7. After approval, applies only the approved tags.
8. Reports per-file results and lists every failed or unresolved file.

**Approval variant:** the user approves tags for 3 of 5 files. Expected: only those 3 files are tagged; the other 2 stay unchanged and are listed as awaiting a decision.

## Case 3 — Incomplete access or extraction

**Input:** a folder with one unreadable file and one document whose text cannot be extracted, plus ordinary files.

**Expected behavior:**

1. The listing and scan run for the accessible files.
2. The unreadable file is listed as unresolved; no guess is made about its contents.
3. `document-agent` reports the failed extraction; ArchiveWise keeps it separate from a missing field.
4. Tag recommendations that depend on the missing evidence are withheld.
5. Recommendations that do not depend on it may proceed after approval.
6. The summary separates completed, failed, and unresolved items.

## State matrix

| State | Expected response |
|---|---|
| `completed` | Use the real result; continue to the next planned step. |
| `failed` | Report the failure and any partial result; do not widen the scope. |
| `cancelled` | Stop; state that no further change was made. |
| `waiting_user` | Ask the single open question or approval request; stop. |
| `waiting_approval` | Report the pending gate; stop; action is not done. |

## Structural checks

- Package contains `SKILL.md` and only directly linked Markdown references under `references/`.
- Root directory name equals the frontmatter name `archivewise`.
- Every delegate line uses one `--target` and one `--instruction`.
- The capability evidence section lists each selected CLI once with the catalog agent.
- All five public status values appear in `SKILL.md`.
- No scripts, binaries, credentials, or non-Markdown resources.
- No file move, archive, or delete action appears in the workflow.
