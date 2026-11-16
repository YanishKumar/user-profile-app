# Phase 0 Research: User Profile & Avatar System

**Feature**: `001-user-profile` | **Date**: 2026-11-16

This document resolves the technical unknowns and clarifications identified during specification intake.

---

## Decision 1: Bio Character Limit and Formatting

- **Decision**: Set the maximum bio length to **500 characters** with support for UTF-8 (multilingual text, standard emojis) and preserved newline formatting (up to 6 consecutive line breaks collapsed to 2).
- **Rationale**:
  - 250 characters is often too restrictive for users to include professional backgrounds, links, or multi-line introductions.
  - 500 characters strikes the ideal balance between expressiveness and keeping profile cards clean and readable.
- **Alternatives Considered**:
  - *250 characters (Twitter-style)*: Rejected because users frequently want at least a short paragraph plus social handles.
  - *1000+ characters / Rich HTML*: Rejected due to layout clutter and heightened XSS attack surface for simple profile views.

---

## Decision 2: Avatar File Upload Limits and Processing

- **Decision**: Accept JPEG, PNG, and WebP images up to **5MB**; server-side normalize and resize all accepted images to standardized **256x256 WebP** square format.
- **Rationale**:
  - 5MB accommodates uncompressed modern smartphone photos without forcing the user to preprocess on their phone before upload.
  - Converting to standardized 256x256 WebP reduces disk footprint from megabytes to ~15KB-30KB per avatar, ensuring lightning-fast page load times and consistent circular UI rendering.
  - Strips EXIF metadata during processing, safeguarding user privacy (GPS coordinates, camera metadata).
- **Alternatives Considered**:
  - *2MB limit without server-side resize*: Rejected because users uploading raw iPhone/Android photos often hit 3-4MB files and encounter frustrating upload failures.
  - *Preserving original formats without re-encoding*: Rejected due to security risks (polyglot files, embedded malicious metadata, uncontrolled disk usage).

---

## Decision 3: Storage Strategy for Avatar Media

- **Decision**: Store avatar media in a dedicated content-addressed local directory (`uploads/avatars/<assetId>.webp`) served statically behind an API route, with an abstracted storage interface (`AvatarStorageProvider`) so cloud storage (S3/Cloudflare R2/GCS) can be swapped in without changing business logic.
- **Rationale**:
  - Allows standalone local execution without external cloud credentials.
  - Using random UUIDs (`assetId`) for filenames prevents path traversal vulnerabilities, namespace collisions, and cache poisoning.
- **Alternatives Considered**:
  - *Direct base64 storage in database*: Rejected because base64 increases database size by 33%, degrades query performance, and invalidates browser static asset caching.
  - *Direct cloud-only storage (AWS S3 / GCS)*: Rejected for local dev ergonomics to avoid requiring AWS keys for local testing.

---

## Decision 4: Technology Stack Selection

- **Decision**:
  - **Runtime & Language**: Python 3.12
  - **Framework**: FastAPI (high-performance async ASGI web framework with automatic OpenAPI documentation)
  - **Persistence**: SQLite with SQLAlchemy 2.0 (zero-setup relational database with seamless migration path to PostgreSQL)
  - **Image Processing**: Pillow (`PIL`) for secure image decoding, EXIF stripping, and WebP re-encoding
  - **Testing**: `pytest` and `httpx` (async API client for testing endpoints)
- **Rationale**:
  - Matches the existing Python 3.12 environment on the host system.
  - FastAPI automatically emits the OpenAPI 3.0 contract (`profile-api.yaml`) and provides strict Pydantic validation for all requests.
  - Clean separation of concerns allows building User Story 1 (P1 MVP) in isolation before attaching the avatar upload pipeline (P2).

---

## Conclusion
All `[NEEDS CLARIFICATION]` markers from `spec.md` are resolved. The design is ready to proceed to Phase 1: data modeling, API contract definitions, and quickstart validation.
