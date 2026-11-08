# Validation record — 2026-11-08

**Checker:** `uliya-skill-kit-0.7.3-en/uliya-skill-kit/scripts/check-skill.mjs`
**Catalog checked:** 2.0.0
**Target:** `archivewise/`
**Status:** `static-pass`
**Diagnostics:** 0 errors, 0 warnings, 0 info
**Build scope:** tag-only review; file moves deferred per `build.md`.

The latest raw JSON result is saved as `docs/check-result-2026-11-08.json`. The 2026-11-07 record is kept for history.

## Files checked

| Package path | SHA-256 |
|---|---|
| `SKILL.md` | `a5bfc0ad0344891518157922dde20265cc7062552babd595b9fe000a7e63f322` |
| `references/review-format.md` | `2ae0ff78eb9785ddca770190154d95f5580f334a6ab8fea4157b1def7d7b014d` |

## Package limits

| Limit | Requirement | Actual |
|---|---|---|
| Files | at most 100 | 2 |
| Per file | at most 1 MB | 9,088 bytes (largest) |
| Uncompressed total | at most 10 MB | 12,163 bytes |
| ZIP | at most 10 MB | 4,999 bytes |

## ZIP verification

`dist/archivewise.zip` was rebuilt with forward-slash entry names and reopened to confirm contents:

- `archivewise/SKILL.md`
- `archivewise/references/review-format.md`

The extracted copy was checked again and returned the same `static-pass` result with identical SHA-256 values.

## Proposal PDF

| Check | Requirement | Actual |
|---|---|---|
| File | separate PDF, at most 1 MB | `dist/ArchiveWise-Round1-Proposal.pdf`, 72,543 bytes |
| Pages | none stated | 2 |
| Ten substantive answers | at most 500 English words | 455 |
| Prompts covered | all ten from the Official Rules | 10 of 10 |
| Disclosures | third-party components, sources, licenses, data flows | Included outside the word count |

The word count uses whitespace-separated English tokens in the ten answers only, excluding headings, title, and the disclosure section, matching the Official Rules exclusion.

## Scope of this evidence

A static pass proves package structure and catalog mapping only. It does not prove upload, installation, compatibility, permissions, or behavior on a NAS device. Those remain finalist testing tasks. The proposal PDF was generated locally from HTML; it was not uploaded to Devpost.
