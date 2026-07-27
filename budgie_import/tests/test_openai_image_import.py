import io
import json
import base64
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import Mock, patch
from urllib.error import HTTPError

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from budgie_bird.models import Bird
from budgie_import.admin import ImportFileAdmin
from budgie_import.models import ImportFile
from budgie_import.services.import_from_file import import_from_file
from budgie_import.services.read_image_with_ai import (
    OpenAIImportError,
    _openai_chat_completion,
    _image_to_data_uri,
    read_image,
    validate_image_path,
)
from budgie_user.models import BudgieUser


def _write_temp_image(suffix=".jpg"):
    handle = NamedTemporaryFile(suffix=suffix, delete=False)
    image = Image.new("RGB", (800, 600), color=(255, 255, 255))
    image.save(handle, format="JPEG")
    handle.close()
    return Path(handle.name)


class OpenAIImageImportTest(TestCase):
    def setUp(self):
        self.user = BudgieUser.objects.create_user(
            username="openai-user", breeding_reg_nr="OPAI"
        )

    def test_validate_image_path_rejects_wrong_extension(self):
        with self.assertRaisesMessage(
            OpenAIImportError,
            "Unsupported image file extension: .gif",
        ):
            validate_image_path("card.gif")

    @override_settings(OPENAI_IMAGE_MAX_DIMENSION=2000)
    def test_image_to_data_uri_downscales_large_images(self):
        image_path = _write_temp_image()
        self.addCleanup(image_path.unlink, missing_ok=True)
        with Image.open(image_path) as image:
            image = image.resize((4000, 3000))
            image.save(image_path, format="JPEG")

        data_uri = _image_to_data_uri(image_path)
        raw = base64.b64decode(data_uri.split(",", 1)[1])
        with Image.open(io.BytesIO(raw)) as resized:
            self.assertLessEqual(max(resized.size), 2000)
            self.assertEqual(resized.size, (2000, 1500))

    def test_parse_openai_image_maps_json_to_import_rows(self):
        image_path = _write_temp_image()
        self.addCleanup(image_path.unlink, missing_ok=True)

        def client(*args):
            return {
                "model": "gpt-4.1-mini",
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "card_year": 26,
                                    "parents": {
                                        "vader": "ALOG-109-2024",
                                        "moeder": "STJJ-026-2024",
                                    },
                                    "rows": [
                                        {
                                            "row_number": 1,
                                            "hatched": "06/10 k10",
                                            "ring_number": "001",
                                            "gender": "P",
                                            "color": "C6m   HB",
                                        }
                                    ],
                                }
                            )
                        }
                    }
                ],
            }

        result = read_image(str(image_path), "PROFILE-001", client=client)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ringnummer"], "PROFILE-001-001-2026")
        self.assertEqual(result[0]["geslacht"], "pop")
        self.assertEqual(result[0]["geboren"], "06-10-2026")
        self.assertEqual(result[0]["kleur"], "C6m HB")
        self.assertEqual(result[0]["vader"], "ALOG-109-2024")
        self.assertEqual(result[0]["moeder"], "STJJ-026-2024")
        self.assertEqual(result.diagnostics["parser_source"], "openai")

    @override_settings(OPENAI_API_KEY="")
    def test_openai_chat_completion_requires_api_key(self):
        image_path = _write_temp_image()
        self.addCleanup(image_path.unlink, missing_ok=True)
        with self.assertRaisesMessage(OpenAIImportError, "requires OPENAI_API_KEY"):
            _openai_chat_completion(image_path, "gpt-4.1-mini")

    @override_settings(OPENAI_API_KEY="test-key")
    @patch("budgie_import.services.read_image_with_ai.urlopen")
    def test_openai_http_error_includes_details(self, urlopen):
        image_path = _write_temp_image()
        self.addCleanup(image_path.unlink, missing_ok=True)
        error_body = {
            "error": {
                "message": "insufficient_quota",
                "type": "invalid_request_error",
                "code": "insufficient_quota",
            }
        }
        error = HTTPError(
            "https://api.openai.com/v1/chat/completions",
            429,
            "Too Many Requests",
            {},
            Mock(read=Mock(return_value=json.dumps(error_body).encode())),
        )
        urlopen.side_effect = error

        with self.assertRaises(OpenAIImportError) as raised:
            _openai_chat_completion(image_path, "gpt-4.1-mini")

        self.assertIn("HTTP 429", str(raised.exception))
        self.assertIn("insufficient_quota", str(raised.exception))
        self.assertNotIn("test-key", str(raised.exception))

    @patch("budgie_import.services.read_image_with_ai.read_image")
    def test_image_import_uses_existing_bird_import_logic(self, parse_image):
        image_path = _write_temp_image()
        self.addCleanup(image_path.unlink, missing_ok=True)
        parse_image.return_value = [
            {
                "ringnummer": "PROFILE-001-001-2026",
                "geboren": "06-10-2026",
                "geslacht": "pop",
                "kleur": "C6m HB",
                "notes": "C6m HB",
            }
        ]

        import_from_file(str(image_path), self.user)

        bird = Bird.objects.get(user=self.user)
        self.assertEqual(bird.gender, Bird.Gender.FEMALE)
        self.assertEqual(bird.notes, "C6m HB")

    @patch(
        "budgie_import.admin.budgie_import.services.import_from_file.import_from_file"
    )
    def test_admin_report_contains_image_diagnostics(self, import_file):
        import_file.return_value = Mock(
            summary=Mock(return_value="Imported 1 bird(s): PROFILE-001-001-2026."),
            diagnostics_text=Mock(
                return_value='Image diagnostics:\n{"parser_source":"openai"}'
            ),
        )

        imported_file = ImportFile.objects.create(
            user=self.user,
            import_file=SimpleUploadedFile("card.jpg", b"not-used"),
        )
        request = Mock(user=self.user)

        ImportFileAdmin(ImportFile, Mock()).save_model(
            request, imported_file, Mock(), False
        )

        imported_file.refresh_from_db()
        self.assertIn("Image diagnostics", imported_file.notes)
