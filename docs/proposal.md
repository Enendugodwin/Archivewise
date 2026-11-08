# ArchiveWise — Round 1 Project Proposal

**UGREEN NAS Skill Hackathon 2026 · Track: Automate Your Workflow**  
**Round 1 submission · Project Proposal (PDF)**  
**Ten substantive answers: 455 words (limit: 500)**  

---

## 1. One sentence: What does the Skill do?

ArchiveWise reviews one NAS folder, shows the duplicate groups and document facts it can prove, and, only after explicit approval, tags selected files.

## 2. Who is the target user and problem?

Home and small-team NAS users whose Downloads or project folders collect duplicates and documents they no longer recognize. They open files one by one to learn what they are, fearing cleanup will move or remove the wrong item.

## 3. What is your proposed solution?

One guided review replaces guesswork. ArchiveWise lists the folder, runs the NAS duplicate scan, optionally extracts requested document facts with source evidence, and presents duplicates, findings, and proposed tags. The user approves exact files and tags. ArchiveWise applies only those tags, reports per-file results, and changes nothing else.

## 4. What is the Core User Flow?

The user names a folder and goal. ArchiveWise confirms the folder, purpose, and fields. It lists files, scans duplicates, extracts fields from returned paths, and presents one review with proposed tags. It waits for approval, applies approved tags, and summarizes completed, failed, and unresolved items.

## 5. What substantive difference does your idea offer compared with existing tools or conventional AI solutions?

Dedupe utilities pick a keeper and push deletion; assistants cannot safely act on NAS files. ArchiveWise keeps the decision with the user and ties every recommendation to a NAS result. It preserves every file, never deletes or moves, and reports partial outcomes honestly. It unites duplicate review, document understanding, and approved tagging.

## 6. Which UGREEN AI NAS capabilities will be used, and at which step in the workflow?

Step 2: ug-filesystem (ls, find, stat) lists the scoped folder. Step 3: ug-filemgr (scan-dedupe) returns duplicate groups. Step 4: ug-document (extract, qa) extracts document facts with source evidence. Step 6: ug-filemgr (tag-get-by-name, tag-add, tag-add-file) applies approved tags.

## 7. What was your technical approach? Describe the planned Skill workflow, supported NAS CLI capabilities, expert agent orchestration, required inputs, permissions, AI model choices, and data handling, as applicable;

ArchiveWise is orchestration-only. SKILL.md delegates self-contained tasks to file-agent and document-agent; it never invokes NAS CLIs directly. Reads precede writes, and only real returned paths flow to extraction. Catalog approvals and permissions are respected; a pending gate is reported as waiting_approval, not assumed. Document understanding uses the NAS document capability and local AI; the Skill adds no external service, upload, or credential, and content stays local.

## 8. What is the current development status? Identify what was implemented already, not yet implemented, or is pending NAS validation if selected to be a Finalist.

Implemented: the complete Skill package, catalog mapping for three CLIs, the review template, three case definitions, and a clean bundled checker run. The Round 1 scope is fully implemented. Pending NAS validation: duplicate-group shape, tag idempotency, and approval timing. File moves are deferred.

## 9. What is your final validation plan? Name two core test cases and one edge case to validate if selected as a Finalist.

Core one: a folder with known duplicates must report only returned groups and change nothing before approval. Core two: sample project documents must yield fields with source names, and only approved files receive the proposed tag. Edge case: one unreadable file and one unextractable document must be disclosed, and dependent actions must stop.

## 10. Are there any known limitations of your Project? Describe current known limitations, technical risks, and any external dependencies.

Round 1 is statically validated, without NAS runtime evidence. Users choose the keeper. Extraction quality depends on NAS document support and file legibility. Tag creation and application depend on platform approvals. Moving or archiving files is deferred, and the Skill does not delete, compress, schedule, or scan the whole NAS.

---

## Third-party components, licenses, and data flows

*Excluded from the 500-word limit, per the Official Rules.*

- **UGREEN Uliya Skill Creation Tool, kit version 0.7.3.** Provided by UGREEN with the Hackathon Starter Kit (https://ai.ugreen.com/pages/hackathon-starter-kit). Used to structure the Skill and run the bundled static checker. Used under the UGREEN Hackathon developer package terms.
- **OpenCode AI coding assistant.** Source: https://github.com/sst/opencode. License: MIT. Used for drafting the Skill, reviewing catalog mappings, and running the local static checker.
- **Bundled third-party material.** No third-party SDKs, libraries, model weights, or datasets are bundled in the Skill package.
- **External services and data flows.** The Skill adds none. It delegates only to registered NAS experts and adds no network call, telemetry, credential, or API key. Document understanding uses the NAS document capability and local AI model; folder content remains on the NAS.
