# Development and component disclosures

## Functionality developed

The project team developed the ArchiveWise orchestration workflow: scope one user-selected NAS folder, inspect it, request duplicate detection, optionally extract document facts with source evidence, present a review, and wait for approval before applying tags. The Skill preserves all reviewed files; it does not delete, move, compress, or share them.

## Development tools and sources

- **UGREEN Uliya Skill Creation Tool, kit version 0.7.3:** UGREEN's [Hackathon Starter Kit](https://ai.ugreen.com/pages/hackathon-starter-kit), used as the Skill authoring guide and source of the capability catalog and static checker. The tool and kit are not redistributed in this package; use is subject to UGREEN's Hackathon developer package terms.
- **OpenCode AI coding assistant:** [source](https://github.com/sst/opencode), MIT License. Used during the initial Skill draft and catalog review.
- **OpenAI Codex:** [product information](https://openai.com/codex/). Used in this session to review and revise the Skill and submission documents. No OpenAI code, SDK, API, or model is included in the package.

## Components and runtime data flow

- No third-party code, libraries, datasets, or model weights are bundled.
- The Skill defines no external service integration, API, or telemetry. It delegates authorized NAS operations to UGREEN's registered experts. Model selection and runtime data handling are provided by that environment and require validation on a NAS; this package does not claim runtime results.
- No credentials, API keys, or personal data are included.
