# Data-Dharma

**Privacy-First AI-Powered Personal Data Vault & Digital Identity Platform**

Data-Dharma is an academic project focused on secure personal document storage, controlled document sharing, and AI-assisted risk analysis.

## Key Features
- Personal document vault for uploading and managing documents.
- Role-based access for document owners and organizations.
- Access request approval, rejection, and revocation.
- Fernet encryption for uploaded documents at rest.
- Document metadata and reminders for missing information.
- AI-assisted risk classification using a Random Forest model.
- Activity tracking and document access controls.

## Technology Stack
- Python and Flask
- SQLite
- HTML, CSS, and JavaScript
- Scikit-learn
- Cryptography (Fernet)

## Run Locally on Windows
1. Clone or download this repository.
2. Open Command Prompt in the project folder.
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `venv\Scripts\activate`
5. Install dependencies: `python -m pip install -r requirements.txt`
6. Start the application: `python app.py`
7. Open `http://127.0.0.1:5000` in your browser.

## Run Tests
`python -m unittest discover -s tests -v`

## Important Security Notes
- The SQLite database, uploaded documents, and encryption keys are local files and are not included in this repository.
- Keep `instance/document_encryption.key` backed up securely. Losing this key can make encrypted documents unrecoverable.
- Never commit secret keys, real personal documents, database files, or private credentials.
- Use synthetic documents for demonstrations and testing.

## Project Status
Data-Dharma is an academic prototype. Its encryption and AI-assisted risk classification features are not production-certified and require further testing and security review before real-world deployment.
