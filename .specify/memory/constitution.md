# Project Constitution: User Profile Application

## Core Mission & Architecture
- Intent-Driven: High quality, user-friendly profile management.
- Modularity: Separation of UI representation, business validation, and data persistence.
- Security & Privacy: Never leak private user information; sanitize all user-supplied text and uploads.

## Quality & Governance Gates
- G-001: All specs must have prioritized user stories (P1 MVP minimum).
- G-002: Ambiguities must be flagged with [NEEDS CLARIFICATION] before architectural lock-in.
- G-003: Every user story must be independently verifiable and testable.
- G-004: All file uploads must be validated against allowed MIME types and file size boundaries.
