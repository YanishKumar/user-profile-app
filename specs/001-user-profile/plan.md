# Implementation Plan: User Profile Page with Avatar Upload and Bio

**Branch**: `001-user-profile` | **Date**: 2026-11-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-user-profile/spec.md`

## Summary

Build an authenticated User Profile management and public display system. The feature enables users to view and update their biography (max 500 characters) and display name (User Story 1, P1 MVP), upload and preview avatar images with automatic server-side validation and WebP normalization to 256x256 (User Story 2, P2), and provide a read-only public profile view for external visitors (User Story 3, P3).

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2, Pillow (PIL)
**Storage**: SQLite with SQLAlchemy ORM (local dev); filesystem storage for processed WebP avatars (`uploads/avatars/`)
**Testing**: `pytest`, `httpx` (async API testing)
**Target Platform**: Linux server / Windows / cross-platform web service
**Project Type**: Web service / REST API
**Performance Goals**: <50ms profile reads (p95), <200ms avatar upload and WebP transformation (p95)
**Constraints**: Avatar upload <= 5MB; Output avatar 256x256 WebP; Max bio length 500 UTF-8 characters; XSS sanitization
**Scale/Scope**: Modular architecture supporting single-tenant development with cloud-readiness for S3/Postgres

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Gate | Requirement | Status | Verification Notes |
| :--- | :--- | :--- | :--- |
| **G-001** | Prioritized User Stories | **PASS** | US1 (P1 MVP), US2 (P2), US3 (P3) clearly separated by value increment. |
| **G-002** | Mark & Resolve Ambiguities | **PASS** | Bio length (500 chars) and avatar size (5MB) resolved in [research.md](research.md). |
| **G-003** | Independent Testability | **PASS** | Each user story defines standalone acceptance scenarios and test procedures. |
| **G-004** | File Upload Security Gates | **PASS** | Client and server-side MIME check, 5MB limit, EXIF stripping, and WebP re-encoding specified. |

## Project Structure

### Documentation (this feature)

```text
specs/001-user-profile/
├── spec.md              # Feature specification
├── plan.md              # This implementation plan
├── research.md          # Phase 0 research output (resolved ambiguities & tech stack)
├── data-model.md        # Phase 1 data models & entity relationship diagrams
├── quickstart.md        # Phase 1 runnable end-to-end validation guide
├── contracts/
│   └── profile-api.yaml # Phase 1 OpenAPI 3.0 REST contract
├── checklists/
│   └── requirements.md  # Specification quality checklist
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── base.py          # SQLAlchemy declarative base & session setup
│   ├── profile.py       # UserProfile database model
│   └── avatar.py        # AvatarAsset database model
├── schemas/
│   ├── profile.py       # Pydantic request/response schemas
│   └── avatar.py        # Avatar upload schemas
├── services/
│   ├── profile_service.py # Profile business logic & bio sanitization
│   └── image_service.py   # Avatar image decoding, resizing, WebP conversion
├── api/
│   ├── dependencies.py  # Auth & database session dependency injection
│   └── routes.py        # Profile & avatar endpoints per OpenAPI contract
└── main.py              # FastAPI application bootstrap & static media mounting

tests/
├── contract/
│   └── test_profile_contract.py # Contract compliance tests against profile-api.yaml
├── integration/
│   ├── test_profile_flow.py     # P1 MVP bio view and update integration test
│   ├── test_avatar_upload.py    # P2 avatar upload, format validation, and delete test
│   └── test_public_profile.py   # P3 public read-only access test
└── unit/
    ├── test_image_processing.py # Unit tests for EXIF stripping and resize logic
    └── test_sanitization.py     # Unit tests for bio character limits and XSS guards
```

**Structure Decision**: Selected a modular single-project structure with distinct `models/`, `schemas/`, `services/`, and `api/` layers, accompanied by dedicated contract, integration, and unit tests under `tests/`.

## Complexity Tracking

*No constitutional violations; no additional architectural complexity justification required.*

## Key Artifacts Generated in Phase 0 & Phase 1

1. **[research.md](research.md)**: Resolved bio limits (500 chars), avatar boundaries (5MB -> 256x256 WebP), and tech stack selection.
2. **[data-model.md](data-model.md)**: Conceptual schema, field constraints, ER diagram, and avatar state machine.
3. **[contracts/profile-api.yaml](contracts/profile-api.yaml)**: Complete OpenAPI 3.0 contract defining `/api/profile/me`, avatar upload/delete endpoints, and `/api/profile/{username}`.
4. **[quickstart.md](quickstart.md)**: Runnable curl walkthrough and test suite instructions.
