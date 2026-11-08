# Planned manual walkthrough — 2026-11-12

This walkthrough was drafted on 2026-11-08 for a planned review on 2026-11-12. It has not yet been performed; all example NAS outputs below are hypothetical. It is a paper review of `archivewise/SKILL.md` against catalog version 2.0.0, not NAS runtime testing. It reflects the current build decision in `build.md`: tags only, no file moves.

## Delegation map check

| Skill step | Delegate target | CLI / action used by the child | Effect | Approval |
|---|---|---|---|---|
| Step 2 listing | `file-agent` | `ug-filesystem` `ls` / `find` | read | none |
| Step 3 duplicate scan | `file-agent` | `ug-filemgr` `scan-dedupe` | read | none |
| Step 4 extraction | `document-agent` | `ug-document` `extract` / `qa` | read | none |
| Step 6 tags | `file-agent` | `ug-filemgr` `tag-get-by-name` / `tag-add` / `tag-add-file` | read then state-change | gateway and conditional |

All four delegations resolve to a registered agent. Reads precede writes. No delegation asks the user for a private parameter. `file-workflow` is not selected in this version, so no plan, run, or move capability appears.

## Case 1 — Duplicate review (happy path)

1. User: "Review my `/Downloads/2026-Projects` folder for duplicates."
2. Step 1 confirms folder and purpose. No follow-up needed.
3. Step 2 delegates listing. Suppose it returns 42 files and resolved path `/Downloads/2026-Projects`.
4. Step 3 delegates `scan-dedupe` on that resolved path. Suppose it returns two groups: G1 with 3 members (120 MB each) and G2 with 2 members (8 MB each).
5. Step 5 presents both groups with all member paths and the returned evidence. It proposes no deletion and preserves every file. If the user asked only for duplicate review, each file may be shown as "no change" with an optional tag suggestion.
6. The review asks for a decision. State: `waiting_user`.
7. If the user approves one tag for G1 only, Step 6 runs for those three paths.
8. The summary lists the tag result per file and states that G2 is unchanged.

**Check:** the Skill never says "you can free 256 MB". It reports the per-group returned sizes and does not total them.

## Case 2 — Document review and tagging

1. User: "Review `/Downloads/2026-Projects` for duplicates. For the PDFs, pull project and status. Then suggest a tag I can apply."
2. Step 1 confirms folder, purpose, fields, and that the goal is tagging.
3. Steps 2 and 3 return files and duplicate groups.
4. Step 4 passes only the PDF paths from the listing to `document-agent`. Suppose 5 PDFs return values and 1 cannot be read.
5. Step 5 presents findings and a proposed tag name per supported file. The unreadable PDF is listed as unresolved and gets no tag proposal.
6. The user approves tags for 4 PDFs. State: `waiting_user` until then.
7. Step 6 applies only the 4 approved tags. If the platform gate is pending, the Skill reports `waiting_approval` and stops.
8. Step 7 reports which files were tagged, which failed, and the one unreadable file.

**Check:** no file is moved, renamed, or deleted. Tag creation is delegated by name; the parent does not invent a tag identifier. The unapproved PDFs remain unchanged.

## Case 3 — Incomplete access or extraction

1. The listing returns one unreadable file and marks it as unresolved.
2. The duplicate scan returns only accessible files. The unreadable file is not invented into a group.
3. `document-agent` returns one failed extraction. Step 4 keeps it separate from a missing field.
4. Step 5 withholds any tag that depends on the missing evidence.
5. If enough evidence remains, the review may propose tags for the unaffected files.
6. The summary separates completed, failed, and unresolved items.

**Check:** "cannot read" is never rendered as "no value" and never as "not a duplicate".

## Case 4 — Empty results

- Empty folder: Step 2 returns no files; the Skill reports that no matching items were found and stops before the scan.
- No duplicate groups: Step 3 returns an empty group list; the Skill says no duplicate groups were found and proposes no duplicate-based tags.
- No usable extraction: Step 4 returns nothing usable; the Skill reports the empty result and proposes no document-based tags.

## Case 5 — Failed, cancelled, and blocked states

| Event | Expected behavior |
|---|---|
| Listing fails | Report the failure; do not scan a different folder; stop. |
| Duplicate scan fails | Report the failure; no inferred groups; stop duplicate-based tag proposals. |
| Extraction fails for some files | Keep the successful results and list the failures; do not guess. |
| Tag action fails after approval | Report which files failed; do not retry with a wider set. |
| Tag action partially succeeds | Report `failed` or partial with per-file results; never call the batch complete. |
| User cancels at approval | State `cancelled`; make no change; report any earlier completed tag action. |
| Approval gate pending | Stop at `waiting_approval`; do not repeat or assume the action. |
| Missing folder input | Ask once; state `waiting_user`; do not scan a default location. |

## Case 6 — Out-of-scope requests

| Request | Response |
|---|---|
| "Delete the extra copies." | ArchiveWise does not delete. Offer to tag the group for review; no file is removed. |
| "Move the old files to an archive folder." | File moves are not in this version. Explain that the move workflow is deferred and offer tagging instead. |
| "Scan my whole NAS." | Ask for one folder. The Skill does not scan the whole NAS. |
| "Compress the folder." | Unsupported in this version; do not claim it. |
| "Make a share link." | Unsupported in this scope. |
| "Clean up everything." | Treat as a request for a review of a named folder, not as approval for any tag change. |

## Authoring issues corrected before the planned walkthrough

1. **Archive moves were removed from the build.** The plan now says the first version tags only. Steps 5, 7, and 8 from the earlier draft were removed, and `file-workflow` was dropped from the capability evidence.
2. **Relative folder names were underspecified.** Step 2 resolves a relative name inside the user directory and returns the resolved path; later steps use that real path.
3. **Duplicate scan previously said "same confirmed folder".** It now consumes the resolved path returned by the listing delegation.
4. **Tag identifiers.** The Skill passes tag names, not invented identifiers; the child resolves or creates the tag.

## Residual risks for NAS validation

- Duplicate group shape and representative-file semantics.
- Tag creation idempotency when a name already exists.
- Approval gate timing for `tag-add` and `tag-add-file`.
- Per-file failure reporting for tag application.
- Move workflow behavior, deferred until it can be tested separately.

No NAS runtime claim is made anywhere in the Skill or this walkthrough.
