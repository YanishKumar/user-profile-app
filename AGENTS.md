# Team Operating Guidelines & Agent Rules
*(Adapted from Google AI Studio & Antigravity Workflow Playbook)*

## 1. Operating Modes
- **Mode 1: Brainstorming & Architecture**
  - Triggered during planning, design, and discussion.
  - RULE: **Do not touch or modify source code.** Propose ideas, schemas, and workflows in chat or markdown notes.
- **Mode 2: Implementation & Slicing**
  - Triggered after a plan or task is agreed upon.
  - RULE: Implement in thin, verifiable slices (TDD).

## 2. Code & UI Preservation Rules
- **Preserve Existing Features**: Never overwrite or refactor unrelated working components without explicit instruction.
- **Scope Containment**: Keep changes localized to the active task.
- **Atomic Commits**: Ensure working code is committed before starting a new feature or complex refactor.

## 3. Rate Limit & Context Preservation
- **Persistent State**: Always keep `PROJECT_STATUS.md` updated with the active goal, recent commits, and next actions.
- **Context Refresh**: If rate limits hit, context resets, or we switch to Google AI Studio, read `PROJECT_STATUS.md` first to resume without repeating questions.
- **Model Efficiency**: Use fast models (Gemini Flash) for routine code, tests, and file operations. Use high-reasoning models for difficult algorithmic logic and security audits.

## 4. Verification Gate
- Every implementation slice must pass automated tests (`pytest`) before marking a task complete.
