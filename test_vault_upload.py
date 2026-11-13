import contextlib
import io
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import app as project


class VaultUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(
            prefix="datadharma-upload-",
            dir=Path(__file__).resolve().parents[1],
        )
        self.root = Path(self.temp_dir.name)
        self.previous_database = project.DATABASE
        self.previous_key_path = project.ENCRYPTION_KEY_PATH
        self.previous_upload_folder = project.app.config["UPLOAD_FOLDER"]
        self.previous_testing = project.app.config.get("TESTING")

        project.DATABASE = str(self.root / "test.db")
        project.ENCRYPTION_KEY_PATH = str(self.root / "instance" / "test.key")
        project.app.config.update(
            TESTING=True,
            UPLOAD_FOLDER=str(self.root / "uploads"),
        )
        Path(project.ENCRYPTION_KEY_PATH).parent.mkdir(parents=True)
        Path(project.app.config["UPLOAD_FOLDER"]).mkdir()

        project.init_db()
        with contextlib.closing(sqlite3.connect(project.DATABASE)) as connection:
            connection.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("upload-test-owner", "unused", "owner"),
            )
            self.owner_id = connection.execute(
                "SELECT id FROM users WHERE username = ?",
                ("upload-test-owner",),
            ).fetchone()[0]
            connection.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("upload-test-organization", "unused", "organization"),
            )
            self.organization_id = connection.execute(
                "SELECT id FROM users WHERE username = ?",
                ("upload-test-organization",),
            ).fetchone()[0]
            connection.commit()

        self.client = project.app.test_client()
        with self.client.session_transaction() as session:
            session["user_id"] = self.owner_id
            session["role"] = "owner"
            session["username"] = "upload-test-owner"

    def tearDown(self):
        project.DATABASE = self.previous_database
        project.ENCRYPTION_KEY_PATH = self.previous_key_path
        project.app.config["UPLOAD_FOLDER"] = self.previous_upload_folder
        if self.previous_testing is None:
            project.app.config.pop("TESTING", None)
        else:
            project.app.config["TESTING"] = self.previous_testing
        self.temp_dir.cleanup()

    def test_png_and_webp_filenames_upload_and_remain_encrypted(self):
        filenames = (
            "sample.png",
            "SAMPLE.PNG",
            "sample.png ",
            r"C:\fakepath\sample.png",
            "sample.webp",
            "SAMPLE.WEBP",
        )
        for filename in filenames:
            with self.subTest(filename=filename):
                response = self.client.post(
                    "/vault",
                    data={
                        "document_name": "Upload test",
                        "document_type": "Personal",
                        "document_file": (
                            io.BytesIO(b"test PNG bytes"),
                            filename,
                        ),
                    },
                    content_type="multipart/form-data",
                )
                self.assertEqual(response.status_code, 302)

                with contextlib.closing(sqlite3.connect(project.DATABASE)) as connection:
                    stored_name = connection.execute(
                        "SELECT file_path FROM documents ORDER BY id DESC LIMIT 1"
                    ).fetchone()[0]

                stored_bytes = (
                    Path(project.app.config["UPLOAD_FOLDER"]) / stored_name
                ).read_bytes()
                self.assertTrue(stored_bytes.startswith(project.ENCRYPTED_PREFIX))
                self.assertEqual(
                    project.decrypt_document(stored_bytes), b"test PNG bytes"
                )

    def test_disallowed_extension_is_rejected(self):
        response = self.client.post(
            "/vault",
            data={
                "document_name": "Rejected test",
                "document_type": "Personal",
                "document_file": (io.BytesIO(b"test bytes"), "sample.exe"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Invalid file type", response.data)

    def test_approved_request_link_uses_stored_filename(self):
        upload = self.client.post(
            "/vault",
            data={
                "document_name": "Shared test",
                "document_type": "Personal",
                "document_file": (io.BytesIO(b"shared test bytes"), "shared.webp"),
            },
            content_type="multipart/form-data",
        )
        self.assertEqual(upload.status_code, 302)

        with contextlib.closing(sqlite3.connect(project.DATABASE)) as connection:
            document_id, stored_name = connection.execute(
                "SELECT id, file_path FROM documents ORDER BY id DESC LIMIT 1"
            ).fetchone()
            connection.execute(
                """INSERT INTO access_requests (
                    organization, document, purpose, permission, duration, status,
                    approved_at, expires_at, owner_id, organization_id, document_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "upload-test-organization",
                    "Shared test",
                    "Regression test",
                    "View Only",
                    "1 day",
                    "Approved",
                    datetime.now().isoformat(timespec="seconds"),
                    (datetime.now() + timedelta(days=1)).isoformat(timespec="seconds"),
                    self.owner_id,
                    self.organization_id,
                    document_id,
                ),
            )
            connection.commit()

        with self.client.session_transaction() as session:
            session["user_id"] = self.organization_id
            session["role"] = "organization"
            session["username"] = "upload-test-organization"

        page = self.client.get("/access-requests")
        self.assertEqual(page.status_code, 200)
        expected_link = f'href="/uploads/{stored_name}"'.encode()
        self.assertIn(expected_link, page.data)
        self.assertNotIn(f'href="/uploads/{self.owner_id}"'.encode(), page.data)

        opened = self.client.get(f"/uploads/{stored_name}")
        self.assertEqual(opened.status_code, 200)
        self.assertEqual(opened.data, b"shared test bytes")


if __name__ == "__main__":
    unittest.main()
