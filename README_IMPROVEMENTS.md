# Data-Dharma improvement checkpoints

## What changed

- [x] Checkpoint 0: Audited the existing Flask/SQLite prototype and retained its current routes, tables, templates, and AI model.
- [x] Checkpoint 1: Added Fernet encryption for newly uploaded files and a one-time startup migration that encrypts legacy document files. Files are decrypted only after the existing route authorization checks pass.
- [x] Checkpoint 2: Added document source, document date, relationship to owner, date of birth, insurance nominee, and creation timestamp fields. Existing rows are preserved with nullable fields.
- [x] Checkpoint 3: Added vault reminders for missing source/date/relationship and applicable DOB/nominee information. Document age is shown in days based on the entered document date or upload date.
- [ ] Checkpoint 4: Complete manual browser testing on Windows with the existing local environment.

## Run on Windows

1. Extract the ZIP into a folder.
2. Open Command Prompt in the `Data-Dharama` folder.
3. Activate your existing environment if it works: `venv\\Scripts\\activate`
4. Install missing dependencies if needed: `python -m pip install -r requirements.txt`
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000` and sign in with your existing test account.
7. Open Data Vault and upload a harmless demo file. Verify it opens for its owner and the vault shows missing-information reminders.
8. Test organization View Only/Download only with test accounts and approved access.

## Encryption key warning

On first startup, the app creates `instance/document_encryption.key`. Keep this file private and back it up securely. Do not commit it or send it separately. If it is lost or changed, encrypted documents cannot be decrypted. The `.gitignore` now excludes `instance/`.

The current encryption is a prototype improvement, not a security certification. For production, use a managed key store, CSRF protection, stronger secret management, HTTPS, and security review. Only use synthetic documents for demos.

## Preserved components

- Existing local database files are excluded from Git. Schema changes happen at startup using additive `ALTER TABLE` migrations.
- Existing route names and AI model file are retained.
- `train_ai.py` is not modified and the model is not retrained.
