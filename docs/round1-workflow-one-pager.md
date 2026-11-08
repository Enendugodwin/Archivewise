# ArchiveWise — one-page workflow definition

**Date:** 2026-11-08
**Purpose:** Define the user story, triggers, inputs, safety rules, outputs, and the document-extraction decision before finalizing the Skill. This is the Nov 8 milestone from `build.md`.

## User and problem

Home and small-team NAS users accumulate duplicate files and old documents in folders such as Downloads and 2026-Projects. They must open files to understand them, and they worry that automated cleanup could move or remove the wrong item.

## User stories

1. As a user with a crowded Downloads folder, I want to see which files are true duplicates before I decide what to keep, so I do not keep two copies of the same file.
2. As a project owner, I want to know what each old document is about without opening every file, so I can tag the right ones.
3. As a cautious user, I want to approve each tag and each file, so nothing changes without my consent.
4. As a user with an unreadable file, I want to be told what could not be checked, so I do not trust a false all-clear.

## Trigger phrases

- "Review my Downloads folder for duplicates."
- "Find duplicate files in 2026-Projects and show me what I can tag."
- "Which project PDFs should get the 2026-Projects tag?"
- "Tag these contracts by project after I approve the list."
- "Clean up this folder." (starts a review, not an action)

## Required inputs

| Input | Required | Behavior when missing |
|---|---|---|
| Folder to review | Yes | Accept a NAS path or relative folder; resolve relative names only under the user directory. Ask if missing; never substitute a parent or wider area. |
| Purpose (duplicates, documents, or both) | Yes | Ask one focused question; default to duplicate review only after the user answers. |
| Document fields or question | Only for document review | Use `auto` schema and the common fields: type, date, project, status. |
| Explicit approval | Before any tag | Show exact files and tag names, then wait. |

Do not ask for CLI names, tag identifiers, or other values the child experts resolve.

## Safety rules

1. Work only inside the confirmed folder and on files observed in the listing.
2. Accept a duplicate group only from the NAS duplicate scan; never from names, sizes, or dates alone.
3. Preserve every reviewed file. No move, deletion, replacement, or rename.
4. Read first; write only after explicit approval of named tag and file pairs. If creation of a new tag is needed, name that in the approval request too.
5. Report `waiting_user`, `waiting_approval`, `completed`, `failed`, and `cancelled` accurately.
6. Disclose inaccessible files and failed extractions; do not guess.
7. Do not compute a storage-savings total from unverified data.
8. Do not scan the whole NAS, compress, schedule, share, stream, or archive files.

## Expected outputs

- A scope block: resolved folder, purpose, fields, limits.
- Duplicate groups with every member path, reported size, and returned evidence.
- Document findings with source path, value, evidence excerpt, and status (found, missing, unreadable).
- Proposed tags per file, each with a reason, or no change.
- An explicit approval request naming the exact file and tag pairs.
- A final summary: tagged, failed, unresolved, and awaiting decision.

## Decision: is document extraction essential?

**Decision:** Document extraction is an **optional second pass**, not the critical path.

Rationale:

- Duplicate review plus approval safety is the core value and works with two read-only capabilities.
- Extraction depends on NAS document support, file format, and legibility, so it has more failure modes.
- Making it opt-in lets a failed extraction degrade gracefully: the duplicate review still completes and the gap is disclosed.
- The Skill keeps extraction in scope because it supports the tagging decision, but no duplicate recommendation depends on it.

## Build decision for this version

The first Skill version **tags approved files only**. It does not move, delete, replace, or rename any file. The file move workflow is deferred until it can be validated on a NAS. This follows the current build decision in `build.md`.

## Two core test cases

1. **Duplicate review:** known duplicates plus unrelated files; report only returned groups; change nothing before approval.
2. **Document review and tagging:** sample documents; extract requested fields with source names; tag only the exact approved files.

Full cases, including the incomplete-access edge case, are in `docs/round1-test-cases.md`.
