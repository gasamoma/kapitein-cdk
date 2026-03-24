# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-03-21

### Added

- **`CognitoWebPortalConstruct`** — Cognito User Pool with email sign-in, hosted UI domain, user groups, and customizable invite emails
- **`AuthorizedApiConstruct`** — REST API Gateway with Cognito authorizer, CORS, and helper methods for adding authorized endpoints
- **`WebAppConstruct`** — S3 + CloudFront static web hosting with OAC, SPA routing, config injection, and optional build support
- **`S3VectorBucket`** — S3 Vector bucket with multi-index support for vector search
- **`S3VectorIndex`** — Standalone vector index for attaching to existing buckets
- **`create_vector_permissions`** — IAM policy helper for S3 Vector operations
