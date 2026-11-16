# Quickstart Validation Guide: User Profile & Avatar System

**Feature**: `001-user-profile` | **Date**: 2026-11-16

This guide provides runnable scenarios to validate that the User Profile and Avatar feature functions end-to-end according to the specification and contracts.

---

## Prerequisites

- Python 3.11+ (Python 3.12 detected)
- Project dependencies installed: `fastapi`, `uvicorn`, `sqlalchemy`, `pillow`, `pydantic`, `pytest`, `httpx`

---

## 1. Setup & Starting the Service

1. Navigate to the project root:
   ```bash
   cd C:/Users/Welcome/.gemini/antigravity/scratch/user-profile-app
   ```
2. Start the local development server:
   ```bash
   uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

---

## 2. Validation Scenarios

### Scenario 1: Retrieve and Update Profile (User Story 1 - P1 MVP)
Verify that an authenticated user can fetch their profile and update their bio and display name.

**Step 1: Fetch Profile**
```bash
curl -X GET "http://127.0.0.1:8000/api/profile/me" \
  -H "Authorization: Bearer mock-test-token"
```
*Expected*: Status `200 OK`. `bio` is empty or existing string, `avatarUrl` points to default placeholder SVG.

**Step 2: Update Bio**
```bash
curl -X PUT "http://127.0.0.1:8000/api/profile/me" \
  -H "Authorization: Bearer mock-test-token" \
  -H "Content-Type: application/json" \
  -d '{
    "displayName": "Alex Developer",
    "bio": "Building autonomous AI agents and open-source software with Spec-Driven Development."
  }'
```
*Expected*: Status `200 OK`. Response returns updated `displayName` and `bio`.

**Step 3: Verify Character Limit Validation**
Attempt to submit a bio exceeding 500 characters.
*Expected*: Status `400 Bad Request` or `422 Unprocessable Entity` with validation error indicating max length 500.

---

### Scenario 2: Avatar Upload, Preview & Removal (User Story 2 - P2)
Verify avatar upload processing, format conversion, and deletion.

**Step 1: Upload Valid Avatar Image**
```bash
curl -X POST "http://127.0.0.1:8000/api/profile/me/avatar" \
  -H "Authorization: Bearer mock-test-token" \
  -F "file=@avatar_sample.png"
```
*Expected*: Status `200 OK`. Response contains `assetId`, `avatarUrl` pointing to `/media/avatars/<assetId>.webp`, and dimensions `width: 256`, `height: 256`.

**Step 2: Verify Image Serving**
```bash
curl -I "http://127.0.0.1:8000/media/avatars/<assetId>.webp"
```
*Expected*: Status `200 OK`, `Content-Type: image/webp`.

**Step 3: Reject Oversized or Invalid File**
Attempt to upload a 6MB file or a `.txt` file.
*Expected*: Status `400 Bad Request` with message indicating invalid MIME type or file size exceeding 5MB limit.

**Step 4: Remove Avatar**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/profile/me/avatar" \
  -H "Authorization: Bearer mock-test-token"
```
*Expected*: Status `200 OK`. `avatarUrl` reverts back to default placeholder.

---

### Scenario 3: Public Profile View (User Story 3 - P3)
Verify that anonymous or distinct users can view another member's profile in a read-only state.

```bash
curl -X GET "http://127.0.0.1:8000/api/profile/alex_dev"
```
*Expected*: Status `200 OK`. Returns public fields (`username`, `displayName`, `bio`, `avatarUrl`) without private fields or edit permissions.

---

## 3. Automated Test Suite Execution

Run all contract, integration, and unit tests:
```bash
pytest tests/ -v
```
