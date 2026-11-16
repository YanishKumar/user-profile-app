# Tasks: User Profile Page with Avatar Upload and Bio

**Feature Branch**: `001-user-profile`  
**Input**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md), [contracts/profile-api.yaml](contracts/profile-api.yaml)

## Phase 1: Setup & Foundational Infrastructure
- [x] T001: Configure project skeleton with directories (`src/models`, `src/schemas`, `src/services`, `src/api`, `tests/unit`, `tests/integration`, `tests/contract`).
- [x] T002: Implement SQLite database setup and session manager in [src/models/base.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/models/base.py).
- [x] T003: [P] Implement mock authentication and database dependency provider in [src/api/dependencies.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/api/dependencies.py).

---

## Phase 2: User Story 1 (P1 MVP) - View and Edit Bio & Profile Info
- [x] T004: [US1] Define SQLAlchemy database model for `UserProfile` in [src/models/profile.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/models/profile.py).
- [x] T005: [US1] [P] Define Pydantic request/response schemas (`ProfileResponse`, `ProfileUpdateRequest`) in [src/schemas/profile.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/schemas/profile.py).
- [x] T006: [US1] Implement `ProfileService` with bio length validation (max 500 chars) and sanitization in [src/services/profile_service.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/services/profile_service.py).
- [x] T007: [US1] Implement routes `GET /api/profile/me` and `PATCH /api/profile/me` in [src/api/routes.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/api/routes.py).
- [x] T008: [US1] Bootstrap FastAPI app and router in [src/main.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/main.py).
- [x] T009: [US1] Write unit tests for bio sanitization in [tests/unit/test_sanitization.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/tests/unit/test_sanitization.py).
- [x] T010: [US1] Write integration tests for profile view and update flow in [tests/integration/test_profile_flow.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/tests/integration/test_profile_flow.py).

**Checkpoint US1**: Profile view and edit bio fully operational, tested with >80% coverage. [PASSED - 19/19 tests green]

---

## Phase 3: User Story 2 (P2) - Avatar Image Upload and Preview
- [ ] T011: [US2] Define SQLAlchemy database model for `AvatarAsset` in [src/models/avatar.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/models/avatar.py).
- [ ] T012: [US2] [P] Define Pydantic schemas for avatar upload response in [src/schemas/avatar.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/schemas/avatar.py).
- [ ] T013: [US2] Implement `ImageService` with Pillow to strip EXIF, resize to 256x256, and re-encode to WebP in [src/services/image_service.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/services/image_service.py).
- [ ] T014: [US2] Implement routes `POST /api/profile/me/avatar` and `DELETE /api/profile/me/avatar` in [src/api/routes.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/api/routes.py).
- [ ] T015: [US2] Mount static avatar file serving in [src/main.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/main.py).
- [ ] T016: [US2] Write unit tests for image transformation and format rejection in [tests/unit/test_image_processing.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/tests/unit/test_image_processing.py).
- [ ] T017: [US2] Write integration tests for avatar upload, preview, and removal in [tests/integration/test_avatar_upload.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/tests/integration/test_avatar_upload.py).

**Checkpoint US2**: Avatar upload, validation, WebP processing, and avatar deletion verified.

---

## Phase 4: User Story 3 (P3) - Public Read-Only Profile View
- [ ] T018: [US3] Implement `GET /api/profile/{username}` public read-only endpoint in [src/api/routes.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/src/api/routes.py).
- [ ] T019: [US3] Write integration tests verifying public view exposes only public fields in [tests/integration/test_public_profile.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/tests/integration/test_public_profile.py).
- [ ] T020: [US3] Contract verification test against [specs/001-user-profile/contracts/profile-api.yaml](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/specs/001-user-profile/contracts/profile-api.yaml) in [tests/contract/test_profile_contract.py](file:///C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app/tests/contract/test_profile_contract.py).

**Checkpoint US3**: Complete user profile system end-to-end verified.
