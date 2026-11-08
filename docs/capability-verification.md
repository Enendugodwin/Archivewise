# Capability verification record

**Catalog:** `uliya-skill-kit-0.7.3-en/uliya-skill-kit/data/capability-catalog.json`
**Catalog version:** 2.0.0 (generated 2026-09-01)
**Verified:** 2026-11-08 against the local catalog file only. No NAS device was contacted.
**Build scope:** tag-only review. File moves are deferred per the current build decision in `build.md`.

Only catalog entries used by ArchiveWise are listed. Effect and approval values are copied from the catalog and are generation-time facts.

## file-workflow -> file-agent

| Action | Effect | Approval | Key parameters | Used for |
|---|---|---|---|---|
| `get-user-dir` | read | none | none | Resolve a relative folder under the actual NAS user directory. |

Completion evidence: `ok=true` with the real directory path. File move and delete actions are not selected.

## ug-filesystem -> file-agent

| Action | Effect | Approval | Key parameters | Used for |
|---|---|---|---|---|
| `ls` | read | none | `path` (required), `recursive`, `max-depth`, `limit` | Listing the confirmed folder. |
| `find` | read | none | `path` (required), `pattern`, `type`, `min-size`, `max-size`, `date-type`, `start-timestamp`, `end-timestamp`, `max-depth`, `limit` | Narrow listing when the user gives a pattern, type, or date range. |
| `stat` | read | none | `path` (required) | Confirming a specific path exists when the listing is ambiguous. |

Completion evidence: `ok=true` with a real listing or stat result. All three actions are read-only.

## ug-filemgr -> file-agent

| Action | Effect | Approval | Key parameters | Used for |
|---|---|---|---|---|
| `scan-dedupe` | read | none | `path` (required, repeatable), `scope` (`all`, `documents`, `images`, `videos`, `audio`) | Duplicate groups for the confirmed folder. |
| `tag-list` | read | none | none | Reading existing tags before proposing a tag name. |
| `tag-get-by-name` | read | none | `name` (required) | Reusing an existing tag with the approved name. |
| `tag-add` | state-change | gateway | `tag-id` (required), `colour` | Creating an approved tag when no tag with that name exists. |
| `tag-add-file` | state-change | conditional | `path` (required, repeatable), `tag-id` (required) | Attaching an approved tag to approved files. |

`tag-add` takes the tag name in `tag-id` (catalog example uses a display name). The parent Skill passes tag names and delegates resolution or creation to `file-agent`; it does not invent tag identifiers.

## ug-document -> document-agent

| Action | Effect | Approval | Key parameters | Used for |
|---|---|---|---|---|
| `extract` | read | none | `query` (required), `file` (repeatable), `schema` (`auto`, `invoice`, `contract`, `expense`, `receipt`, `medical-report`, `purchase_order`, `mixed`, `mixed_reconciliation`), `content-scope`, `max-files`, `body-cap`, `dedupe` | Structured facts with source evidence. |
| `qa` | read | none | `query` (required), `file` (repeatable), `intent`, `content-scope`, `top-k`, `entities`, `answer-mode`, `evidence-mode`, `max-files`, `body-cap` | A specific question about the documents when the user asks one. |

Both actions are read-only. The Skill passes only real file paths returned by the listing step.

## Deliberately excluded

- `file-workflow` `start`, `run`, and `batch-move`: file moves are deferred until the workflow can be validated on a NAS.
- `ug-filesystem` `del`, `cpmv`, `rename`, `mkdir`, `chtimes`, `touch`: direct state changes outside the review.
- `ug-filemgr` `tag-delete`, `tag-delete-file`: removal is out of scope.
- `file-workflow` `batch-del`: deletion is out of scope.
- Compression, streaming, sharing, database hosting, and whole-NAS scanning: no catalog action is used for these.

The Skill selects only `file-workflow` `get-user-dir` for safe relative-path resolution. File move and delete actions remain excluded.

## Open verification items for finalist testing

- Exact duplicate group shape, including member order and representative file.
- Whether `tag-add` with an existing name is idempotent or returns an error.
- Approval gate timing for `tag-add` and `tag-add-file`.
- Per-file failure reporting for tag application.
- Deferred: `file-workflow` plan and execution semantics.
