# Round 1 submission checklist

Based on the Official Rules at https://ugreenhackathon.devpost.com/rules (accessed 2026-11-08), `build.md`, and the bundled checker.

## Project proposal PDF

- [x] Separate PDF file: `dist/ArchiveWise-Round1-Proposal.pdf`
- [x] At most 1 MB (46,734 bytes)
- [x] Answers all ten required prompts, in order
- [x] Ten substantive answers at most 500 English words (445 by whitespace token count)
- [x] Team names, signatures, and third-party license information are outside the word count
- [x] Third-party components, sources, licenses, and data flows disclosed
- [x] English only
- [x] Generated locally; no NAS runtime claim

## Initial Skill package

- [x] One ZIP: `dist/archivewise.zip`
- [x] At most 10 MB (6,622 bytes)
- [x] Uncompressed contents at most 10 MB (15,609 bytes)
- [x] At most 100 files (3)
- [x] Each file at most 1 MB (largest 10,627 bytes)
- [x] `SKILL.md` at the package root
- [x] Supporting Markdown only under `references/`, directly linked from `SKILL.md`
- [x] Name `archivewise`: lowercase, 2-64 characters, directory name matches
- [x] Description at most 1,024 characters
- [x] All five delegation states covered
- [x] Capability evidence uses the exact `- <cli>` → `<agent>` format
- [x] No scripts, executables, binaries, manifests, credentials, API keys, or personal data
- [x] No TODOs, TBDs, or placeholders
- [x] ZIP reopened and extracted copy re-checked: `static-pass`, 0 errors, 0 warnings
- [x] No password protection

## Submission mechanics

- [ ] Upload the PDF and ZIP on Devpost before **2026-11-15, 11:45 p.m. Pacific Time**
- [ ] Save the submission confirmation
- [ ] Retain the exact uploaded PDF and ZIP
- [ ] Complete any Devpost project-form fields (name, tagline, track)

## Notes

- **Track:** Automate Your Workflow.
- **Scope:** This version tags approved files only. It does not move, delete, replace, or rename any file. Archive moves are deferred until the move workflow can be validated on a NAS.
- **Round 1 does not require a code repository, demo video, screenshots, test reports, or NAS access.** The Official Rules state this explicitly. The event landing page also mentions a prototype video; the Official Rules say they control in case of conflict, so the PDF and ZIP are the required Round 1 materials.
- The Skill is not claimed to be installable or operational on a NAS yet. Round 1 permits a pre-test package; finalist testing covers runtime behavior.
- Do not add a root `README.md` to the ZIP. The starter kit recommends one in general, but the checker allows only `SKILL.md` and `references/` at the package root.
