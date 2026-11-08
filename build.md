# ArchiveWise — Round 1 Project Plan

**Plan date:** November 8, 2026  
**Round 1 submission deadline:** Sunday, November 15, 2026 at 11:45 p.m. Pacific Time, per the supplied hackathon brief  
**Project type:** Uliya Skill for UGREEN AI NAS (a natural-language workflow, not a standalone NAS application)

## 1. Project goal

Build ArchiveWise, a Uliya Skill that helps a NAS user review a chosen folder before organizing it. It finds duplicate files, extracts relevant details from documents, presents evidence-based recommendations, and—only after the user approves—tags selected files.

ArchiveWise should make cleanup easier to understand and safer to carry out. It will not delete files, compress files, or claim a storage-savings figure unless the capability output provides enough evidence to calculate one.

## 2. User and problem

**Target user:** A home or small-team NAS user with a growing Downloads, projects, or document folder.

**Problem:** Duplicate files and old documents accumulate. Users spend time opening files to understand them, and worry that automated cleanup could move or remove the wrong item.

**Value:** One review workflow combines duplicate detection, document extraction, a clear proposed action list, and user-approved organization.

## 3. Round 1 MVP

### In scope

1. Accept a folder or a narrow search request from the user. Ask for the folder if it is missing; do not scan the whole NAS by default.
2. Inspect the authorized folder and find files using the supported file CLI.
3. Run the NAS duplicate scan for that folder. Treat the returned duplicate groups as evidence; do not infer duplicates from similar names alone.
4. For relevant documents, extract requested facts such as document type, date, project, or status using the document expert. Include source file names and extracted evidence in the review.
5. Show a proposed plan: duplicate groups to review, document-based findings, and suggested tags. Preserve all files.
6. Ask for clear approval before tagging. Apply only approved tags and report completed, failed, partial, or waiting states accurately.
7. On an empty result, report that no matching items were found and stop. On inaccessible or unextractable files, disclose the gap and continue only where remaining evidence is sufficient.

### Out of scope for Round 1

- Compression, decompression, deletion, automatic cleanup, background scheduling, or whole-NAS scans.
- Storage savings promises. The catalog includes size filtering and file metadata operations, but ArchiveWise will only report a numeric total if the exact results support a correct calculation.
- Streaming, public link creation, database hosting, custom web/mobile interfaces, external services, and unsupported scripts.
- Claiming runtime or NAS testing before finalists receive device access.

**Current build decision:** The first Skill version tags approved files but does not move or delete files. The file move workflow needs closer runtime validation before ArchiveWise can safely offer it.

## 4. Capability and implementation map

Use the downloaded package's `data/capability-catalog.json` as the source of truth. Its catalog version is 2.0.0 (generated September 1, 2026). Current candidate operations are:

| Workflow step | Catalog capability | Expert | Use |
|---|---|---|---|
| Inspect/search the user-selected folder | `ug-filesystem` (`ls`, `find`, optionally `stat`) | `file-agent` | Read-only listing and scoped search; pass the exact folder and filters. |
| Detect duplicates | `ug-filemgr` (`scan-dedupe`) | `file-agent` | Read-only scan in the selected scope; display only returned groups. |
| Extract document facts | `ug-document` (`extract` or `qa`) | `document-agent` | Read-only extraction with a user-defined query/schema and source evidence. |
| Add an approved tag | `ug-filemgr` (`tag-add-file`) | `file-agent` | State-changing; requires the catalog's conditional approval workflow. |
 |

Before authoring, verify exact parameters, action effects, approval values, return evidence, and prerequisites for every selected action in the catalog. If a required action is unavailable or unclear, remove it from the MVP rather than inventing support. The parent Skill must delegate through `delegate --target <agent-id> --instruction '<self-contained task>'`; it must not directly invoke NAS CLIs.

Record the mappings in the generated Skill as required by the kit:

- `ug-filesystem` -> `file-agent`
- `ug-filemgr` -> `file-agent`
- `ug-document` -> `document-agent`
- `file-workflow` -> `file-agent`

## 5. User flow and safety rules

**Trigger example:** “Review my `Downloads/2026-Projects` folder for duplicates and documents I should keep or tag.”

1. Confirm the target folder, review purpose, and any document criteria. Ask a focused follow-up when needed.
2. Delegate a scoped read-only file listing/search and duplicate scan to `file-agent`.
3. If the user asked for document review, pass the actual returned file paths to `document-agent` for extraction. Do not manufacture paths or facts.
4. Combine only verified results into a concise review with file paths, why each item was flagged, and the proposed action. Mark uncertainty clearly.
5. Ask the user to approve the exact tag and file paths. This version does not move or delete files. A general request to “clean up” is not approval for a tag change.
6. Delegate approved changes to `file-agent`; respect platform approval gates. If approval is pending, stop and report `waiting_approval`.
7. Summarize what changed, what failed, and what needs the user's decision. Never describe a planned or partial operation as complete.

## 6. Build schedule

| Date | Milestone and work | Done when |
|---|---|---|
| **Nov 7** | Read the kit, catalog, standards, examples, and hackathon submission rules. Confirm ArchiveWise scope and supported actions. | Capability map and MVP boundaries are agreed. |
| **Nov 8** | Write user stories, trigger phrases, input requirements, safety rules, and expected outputs. Decide whether document extraction is essential or an optional second pass. | One-page workflow and two core test cases are defined. |
| **Nov 9** | Draft `SKILL.md`: frontmatter, goal, inputs, CLI-to-agent mapping, ordered delegation instructions, confirmation gates, and state handling. | A reviewer can follow the complete flow without guessing. |
| **Nov 10** | Inspect catalog entries for selected actions and tighten instructions to exact parameters and evidence. Draft linked reference(s) only if needed. | Every operation is present in the catalog; no invented capability remains. |
| **Nov 11** | Run the bundled checker against the Skill directory. Review every diagnostic and update the draft. | No unresolved required checker findings; keep diagnostic record. |
| **Nov 12** | Walk through core cases and edge case manually against the catalog and written workflow. Refine empty, partial, failed, cancelled, waiting-user, and waiting-approval responses. | Each path has explicit expected behavior; no NAS runtime claims. |
| **Nov 13** | Finalize the project proposal at 500 words or fewer and include third-party component/license and AI-tool disclosures. Review package limits. | Proposal answers all ten required prompts. Skill includes required disclosures. |
| **Nov 14** | Package only required Markdown files and linked references into the ZIP. Check ZIP/uncompressed limits, file count, per-file limit, names, and absence of credentials or prohibited files. Reopen the ZIP and verify contents. | Round 1 PDF and ZIP are ready to upload; both open and meet stated limits. |
| **Nov 15** | Upload the PDF and Pre-test Skill Package before **11:45 p.m. PT**. Confirm submission receipt and retain the submitted files. | Submission confirmation is saved; Round 1 materials are preserved. |

## 7. Acceptance criteria

- Skill name is lowercase and hyphenated, 2–64 characters; description is at most 1,024 characters.
- `SKILL.md` fully describes the user goal, required inputs, supported CLI actions, expert orchestration, and completion/failure handling.
- Every selected CLI is mapped as `- <cli> -> <agent>`; only the registered agent for that CLI is used.
- All operations map to catalog entries; reads precede dependent actions; actual outputs are passed forward.
- User approval precedes each state-changing action. No deletion or overwrite is included in the MVP.
- No NAS data is invented; empty results and partial results are reported honestly.
- Package contains no separate manifests, scripts, executables, binaries, credentials, personal data, or API keys. Only required Markdown and directly linked Markdown references are included.
- ZIP and uncompressed package are each at most 10 MB; each file at most 1 MB; no more than 100 files.
- Proposal is a separate PDF, at most 1 MB and at most 500 English words for the ten substantive answers.

## 8. Round 1 test cases

1. **Duplicate review:** In a test folder with known duplicate files and unrelated files, ArchiveWise reports only duplicate groups returned by the NAS capability, explains the evidence, and proposes actions without changing files before approval.
2. **Document review and tagging:** Given a folder with a small set of sample project documents, it extracts requested fields with source filenames, proposes an existing tag, and tags only the exact approved files after approval.
3. **Edge case — incomplete access or extraction:** A folder includes an inaccessible file or an unreadable document. ArchiveWise reports the gap, does not guess its contents, and does not proceed with actions that depend on missing evidence.

Round 1 local tests can validate prompt logic and static package structure only. Real NAS behavior, permissions, and end-to-end operation remain finalist testing tasks.

## 9. Round 2 preparation

If selected as a finalist, use the assigned NAS day to validate the exact installed capability versions and permissions; exercise the three cases above with non-sensitive test data; record actual results and failures; fix any runtime issues; and record a concise demo showing the user request, evidence-based review, approval, and resulting NAS action. Submit the final version of the same Skill and a public demo video by November 30, 2026 at 11:45 p.m. PT, per the supplied brief.

## 10. Risks and decisions to track

- **Duplicate scan semantics:** Confirm how groups and representative files are returned; never select a “best” copy without user criteria.
- **Document extraction quality:** Require source evidence; distinguish missing fields from negative findings.
- **Approval behavior:** Conditional approvals are governed by the child expert/runtime. The Skill must wait for the returned state and respect the gate.
- **Scope creep:** Keep streaming, music, sharing, compression, and database hosting as separate future concepts.
- **Schedule:** The deadline is close. Cut optional document review first if catalog research or checker fixes take longer than expected; retain duplicate review, transparent recommendations, and approval safety.
- **Disclosure:** In the submitted Skill, disclose the UGREEN Uliya Skill Creation Tool and any AI assistant used, with source and applicable license details for third-party components. Keep the proposal's license disclosure outside the 500-word response count as allowed by the brief.

## References

- [UGREEN Hackathon Starter Kit](https://ai.ugreen.com/pages/hackathon-starter-kit)
- [UGREEN Files guide](https://support.ugnas.com/detail/article/en-US/224)
- [Downloaded Uliya Skill Kit — SKILL.md](C:/Users/user/Downloads/uliya-skill-kit-0.7.3-en/uliya-skill-kit/SKILL.md)
- [Downloaded capability catalog](C:/Users/user/Downloads/uliya-skill-kit-0.7.3-en/uliya-skill-kit/data/capability-catalog.json)
- [Downloaded Skill Development Standard](C:/Users/user/Downloads/uliya-skill-kit-0.7.3-en/uliya-skill-kit/docs/skill-development-standard.md)



