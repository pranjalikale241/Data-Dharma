# Data-Dharma Checkpoint Log

## Checkpoint 0 — Baseline audit — COMPLETE
- Inspected the current Flask app, templates, SQLite schema/data, uploaded files, and existing risk model.
- Preserved the current database, routes, and `risk_model.pkl`.

## Checkpoint 1 — Document encryption at rest — IMPLEMENTED; UNIT TESTS PASS
- New uploads are encrypted using Fernet before being written to disk.
- Existing referenced uploads are encrypted in place on startup using a temporary file + atomic replace.
- Authorized file access decrypts in memory only after the current owner/organization permission checks.
- Legacy unencrypted file reading remains supported during migration.
- Key is stored in `instance/document_encryption.key`; `.gitignore` excludes `instance/`.
- Test result: encryption round-trip, legacy migration, and idempotent repeat migration passed in an isolated test copy.

## Checkpoint 2 — Document metadata — IMPLEMENTED; SCHEMA TEST PASS
- Added nullable fields for source, document date, relationship, date of birth, nominee, and creation timestamp.
- Schema uses additive `ALTER TABLE` migrations; existing rows are retained.
- Test result: required columns were present after migration in an isolated database copy.

## Checkpoint 3 — Missing-field reminders — IMPLEMENTED; TEMPLATE PARSE PASS
- Vault upload form accepts the new metadata.
- Vault list shows source, document date, age in days, relationship, and reminders for missing details.
- DOB/nominee reminders are conditional by document category and labelled as applicable, not mandatory legal requirements.
- Test result: Jinja template parsed successfully.

## Checkpoint 4 — Regression/manual browser testing — PARTIAL (historical)
- `python -m py_compile app.py train_ai.py`: PASS.
- Database migration, encryption round-trip, legacy-file migration and idempotency: PASS in isolated test copy.
- Vault Jinja syntax: PASS.
- Full Flask browser/client test could not be run in this runtime because Flask/Werkzeug are not installed here and package installation/network access is unavailable.
- The existing model was preserved and not retrained. Loading it under scikit-learn 1.8 produced a version warning because it was persisted under 1.7.2; `requirements.txt` pins 1.7.2 to match the saved model.
- Later upload-route regression tests are recorded in Checkpoints 6 and 7.

## Before a real demo
1. Install dependencies from `requirements.txt` in the Windows project environment.
2. Run the app and test login, upload, owner open, organization View Only, organization Download, revoked access, and expired access.
3. Back up `instance/document_encryption.key` securely. Loss of the key makes encrypted files unreadable.
4. Use synthetic test documents only. This remains a student prototype, not production-certified secure storage.

## Checkpoint 5 — PNG upload filename validation — IMPLEMENTED
- The upload form uses the expected `document_file` field, multipart encoding, and allowed extensions. The filename check now normalizes the client-supplied name before checking its extension.
- `allowed_file` now rejects blank/non-string names and checks the extension on Werkzeug's sanitized filename, case-insensitively. The route strips surrounding whitespace before deriving the persisted original filename; routes, database, encryption, permissions, and risk model are unchanged.
- The cause of the original rejection has not been reproduced; the earlier raw-filename explanation was a hypothesis, not a confirmed finding.

## Checkpoint 6 — Isolated Flask upload regression tests — PASS
- Added `tests/test_vault_upload.py`, which uses a temporary database, upload folder, and encryption key; it does not modify the project's database or uploaded files.
- Flask test-client uploads passed for `.png`, uppercase `.PNG`, a trailing-space filename, and a Windows-style `C:\\fakepath\\...` filename. Each response redirected successfully, and the saved bytes were verified encrypted and decryptable.
- A `.exe` upload returned HTTP 400 as expected.
- Test command: `python -m unittest discover -s tests -v` (run from the project folder with its virtual environment active).
- The tests prove the current route accepts these PNG filename forms. If a browser still displays the rejection, restart the server from this exact project folder and check the server console; the rejected client filename has not yet been captured.

## Checkpoint 7 — WebP uploads — IMPLEMENTED; TESTS PASS
- The provided CEP assets include `.webp` images, which the prior allow-list did not accept. Added `.webp` to server validation and the file input's accepted extensions and helper text; existing formats remain supported.
- The upload regression test now covers standard and uppercase `.webp` filenames and verifies encrypted storage. The unsupported `.exe` rejection test remains in place.

## Checkpoint 8 — Approved document link — FIXED; TESTS PASS
- The owner and organization Access Requests views used `req[9]` as a filename, but `SELECT *` supplied the owner's numeric ID in that position. This generated links such as `/uploads/3`, which could not match `documents.file_path`.
- Replaced those positional `SELECT *` queries with explicit joins that supply the document's stored `file_path` at the template's expected position and the owner's username for the organization view. Existing `/uploads/<filename>` route and access checks are unchanged.
- Added a regression test that checks the approved-request page emits the stored filename and successfully opens the document through the existing route. The test suite now passes all three tests.
