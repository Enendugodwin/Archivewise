# ArchiveWise — Round 1 Project Proposal

**UGREEN NAS Skill Hackathon 2026 · Track: Automate Your Workflow**  
**Round 1 submission · Project Proposal (PDF)**  
**Ten substantive answers: 445 words (limit: 500)**

---

## 1. One sentence: What does the Skill do?

ArchiveWise reviews one NAS folder, reports duplicate scan results and requested document facts with source evidence, and tags selected files only after explicit approval.

## 2. Who is the target user and problem?

Home and small-team NAS users whose Downloads or project folders collect duplicates and documents they no longer recognize. They open files one by one to learn what they are, fearing cleanup will move or remove the wrong item.

## 3. What is your proposed solution?

One guided review replaces guesswork. ArchiveWise lists the folder, runs the NAS duplicate scan, optionally extracts requested document facts with source evidence, and presents duplicates, findings, and proposed tags. The user approves exact files and tags. ArchiveWise applies only those tags, reports per-file results, and changes nothing else.

## 4. What is the Core User Flow?

The user names a folder and goal. ArchiveWise confirms the folder, purpose, and fields. It lists files, scans duplicates, extracts fields from returned paths, and presents one review with proposed tags. It waits for approval, applies approved tags, and summarizes completed, failed, and unresolved items.

## 5. What substantive difference does your idea offer compared with existing tools or conventional AI solutions?

Existing NAS file tools can list and detect duplicates. ArchiveWise adds one guided, folder-scoped review that combines returned duplicate results with source-backed document details before it proposes tags. It preserves all files, requires approval for the exact tag and files, and reports partial results honestly.

## 6. Which UGREEN AI NAS capabilities will be used, and at which step in the workflow?

Step 1: file-workflow (get-user-dir) resolves relative folder names. Step 2: ug-filesystem (ls, find, stat) verifies and lists the scope. Step 3: ug-filemgr (scan-dedupe) finds duplicates. Step 4: ug-document (extract, qa) extracts sourced facts. Step 6: ug-filemgr (tag-list, tag-get-by-name, tag-add, tag-add-file) looks up and applies tags after explicit approval, including approval to create a new tag if needed.

## 7. What was your technical approach? Describe the planned Skill workflow, supported NAS CLI capabilities, expert agent orchestration, required inputs, permissions, AI model choices, and data handling, as applicable;

ArchiveWise is orchestration-only. SKILL.md delegates scoped tasks to file-agent and document-agent; it does not invoke NAS CLIs directly. Read steps pass real returned paths to later steps. Writes require explicit user approval and UGREEN approval gates. Model use is provided by UGREEN experts; the Skill adds no external model, service, or credential.

## 8. What is the current development status? Identify what was implemented already, not yet implemented, or is pending NAS validation if selected to be a Finalist.

Implemented: the pre-test Skill package, four-CLI mapping, review template, core cases, and a clean static-checker run. NAS validation remains for duplicate-result details, relative-path resolution, tag behavior, and approvals. File moves are deferred.

## 9. What is your final validation plan? Name two core test cases and one edge case to validate if selected as a Finalist.

Core one: report only duplicate groups returned for a test folder; change nothing before approval. Core two: extract sourced fields from sample documents and tag only approved files. Edge case: disclose an unreadable file and failed extraction; stop actions that depend on missing evidence.

## 10. Are there any known limitations of your Project? Describe current known limitations, technical risks, and any external dependencies.

Round 1 is statically validated, without NAS runtime evidence. Duplicate-group details may vary by NAS result; ArchiveWise does not decide which copy to keep. Extraction quality depends on document support and file legibility. Tag creation and application depend on platform approvals. Moving or archiving files is deferred, and the Skill does not delete, compress, schedule, or scan the whole NAS.

---

## Third-party components, licenses, and data flows

*Excluded from the 500-word limit, per the Official Rules.*

- **UGREEN Uliya Skill Creation Tool, kit version 0.7.3.** Provided by UGREEN with the Hackathon Starter Kit (https://ai.ugreen.com/pages/hackathon-starter-kit). Used to structure the Skill and run the bundled static checker. Used under the UGREEN Hackathon developer package terms.
- **OpenCode AI coding assistant.** Source: https://github.com/sst/opencode. License: MIT. Used during initial Skill drafting and catalog review.
- **OpenAI Codex.** Source: https://openai.com/codex/. Used in this session to review and revise the Skill and submission documents. No OpenAI code, SDK, API, or model is bundled.
- **Bundled third-party material.** No third-party SDKs, libraries, model weights, or datasets are bundled in the Skill package.
- **External services and data flows.** The Skill defines no external service integration, API, or telemetry. It delegates authorized NAS operations to UGREEN's registered experts. Model selection and runtime data handling are provided by that environment and require NAS validation. No credentials or API keys are included.
