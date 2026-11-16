# Project Status & Living State

> This document is the source of truth for current project progress, allowing instant resumption across sessions, rate limits, or context switches between Google AI Studio and Antigravity.

## Current Project
- **Name**: `user-profile-app`
- **Goal**: User Profile Page with Avatar Upload and Bio
- **Active Feature Branch**: `001-user-profile`
- **Tech Stack**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Pillow, pytest

## Status Summary
- [x] Feature Specification (`specs/001-user-profile/spec.md`)
- [x] Phase 0 Research & Tech Stack Selection (`specs/001-user-profile/research.md`)
- [x] Phase 1 Data Model (`specs/001-user-profile/data-model.md`)
- [x] Phase 1 REST Contract (`specs/001-user-profile/contracts/profile-api.yaml`)
- [x] Phase 1 Implementation Plan (`specs/001-user-profile/plan.md`)
- [x] Team Operating Rules & Git Checkpoint Setup (`AGENTS.md`)
- [ ] Dependency Installation & Virtualenv Setup (`uv venv`)
- [ ] Task Breakdown (`specs/001-user-profile/tasks.md`)
- [ ] User Story 1 (P1 MVP): Bio & Profile Info CRUD
- [ ] User Story 2 (P2): Avatar Image Upload & WebP Processing
- [ ] User Story 3 (P3): Public Read-Only Profile View

## Next Action
1. Set up virtual environment and install project dependencies with `uv`.
2. Generate ordered task list (`tasks.md`).
3. Connect GitHub repository for cloud sync / Google AI Studio bridge.
