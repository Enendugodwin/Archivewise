# Review format

Use this layout for every ArchiveWise review. Keep the wording tied to returned results, and mark uncertainty instead of filling gaps.

## 1. Scope

- **Folder reviewed:** the resolved folder the user confirmed, for example `/Downloads/2026-Projects`.
- **Purpose:** duplicates only, document review, or both.
- **Document fields:** the fields or question the user named.
- **Limits:** any depth limit, result limit, or media-type scope applied by the scan.

## 2. Duplicate groups

| Group | Member files | Reported size | Evidence |
|---|---|---|---|
| 1 | full paths from the scan | value returned for the group | the fact the scan returned, such as a shared content hash |

Report only groups returned by the duplicate scan. If the scan returned no groups, write "No duplicate groups were returned for this folder." Do not add groups from similar names or sizes.

Report each size value exactly as the scan returned it. Do not total the groups or present a storage-savings figure, because the returned evidence does not establish what a user would save.

Preserve every reviewed file. ArchiveWise does not move, delete, replace, or rename files in this version.

## 3. Document findings

| Source file | Field | Value | Evidence | Status |
|---|---|---|---|---|
| full path from the listing | type, date, project, status, or a user field | extracted value | short excerpt from the document | found, missing, or unreadable |

Keep "missing" separate from a negative finding. A document that does not state a value has a missing field; it does not prove that the value is false or absent from the project.

## 4. Proposed tags

| File | Proposed tag | Reason | Approval needed |
|---|---|---|---|
| full path | tag name, or no change | the returned evidence that supports it | yes or no |

Include the exact tag name for each file. Do not invent a tag identifier; the child expert resolves or creates the tag from the approved name. A file with no supporting evidence gets no tag and stays unchanged.

## 5. Unresolved items

List every file that could not be read, every document that could not be extracted, and every planned tag action that did not complete. State what evidence is missing and which recommendation depends on it.

## 6. Approval request

Ask a direct question that names the exact items:

> Approve tag A on these two files and tag B on this file?

A general request to clean up the folder is not approval. Wait for the explicit answer before any change.

## Status wording

| State | What the user sees |
|---|---|
| `waiting_user` | The review is ready; the named decision is still open. |
| `waiting_approval` | The platform approval gate is pending for the named action. |
| `completed` | The child expert returned a real result for the named action. |
| `failed` | The named action failed; partial results are listed separately. |
| `cancelled` | The workflow stopped; no further change was made. |

Never describe a planned or pending action as completed. Report the count of changed files only from the returned per-file result.
