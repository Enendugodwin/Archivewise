# Validation record — 2026-11-08

**Checker:** `uliya-skill-kit-0.7.3-en/uliya-skill-kit/scripts/check-skill.mjs`  
**Catalog checked:** 2.0.0  
**Target:** `archivewise/`  
**Status:** `static-pass`  
**Diagnostics:** 0 errors, 0 warnings, 0 info  
**Build scope:** folder-scoped review and approved tags; file moves and deletes are excluded.

The latest raw JSON result is saved as `docs/check-result-2026-11-08.json`. The 2026-11-07 record is retained for history.

## Files checked

| Package path | Bytes | SHA-256 |
|---|---:|---|
| `SKILL.md` | 10,627 | `066bfb9397838dbaaf505dbecf9487631200c09f5f36ee7b320d10729a6a849c` |
| `references/disclosures.md` | 1,637 | `b11045bdbf37ad1ad9e7bd5b0b8ea762e9a3d11296fdcbe41ead53d45a14887e` |
| `references/review-format.md` | 3,345 | `3128e64893d191ef7156e37ea92d0f018ff98047d796254d432286cb38cfb811` |

## Package limits

| Limit | Requirement | Actual |
|---|---|---|
| Files | at most 100 | 3 |
| Per file | at most 1 MB | 10,627 bytes (largest) |
| Uncompressed total | at most 10 MB | 15,609 bytes |
| ZIP | at most 10 MB | 6,622 bytes |

## ZIP verification

`dist/archivewise.zip` was reopened to confirm these entries:

- `archivewise/SKILL.md`
- `archivewise/references/disclosures.md`
- `archivewise/references/review-format.md`

The extracted `archivewise/` directory returned the same `static-pass` result and file hashes as the source directory.

## Proposal PDF

| Check | Requirement | Actual |
|---|---|---|
| File | separate PDF, at most 1 MB | `dist/ArchiveWise-Round1-Proposal.pdf`, 46,734 bytes |
| Pages | none stated | 2 |
| Ten substantive answers | at most 500 English words | 445 |
| Prompts covered | all ten from the Official Rules | 10 of 10 |
| Disclosures | tools, sources, licenses, components, and runtime data-flow limits | Included outside the word count |

The word count uses whitespace-separated English tokens in the ten answers only, excluding headings, title, and the disclosure section.

## Scope of this evidence

A static pass confirms the Skill package structure and catalog mapping only. It does not prove upload, installation, permissions, compatibility, or behavior on a NAS device. Those require finalist testing. The PDF was generated from the proposal Markdown and visually reviewed after rendering; it has not been uploaded to Devpost.
