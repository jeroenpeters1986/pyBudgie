"""OpenAI-powered image import for the fixed-layout breeding card."""

import base64
import io
import json
import re
import ssl
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import certifi
from django.conf import settings
from PIL import Image, ImageOps

from budgie_bird.utils import format_ringnumber

SUPPORTED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
_OPENAI_ERROR_TEXT_LIMIT = 1200
_JSON_TEXT_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL | re.IGNORECASE)


class OpenAIImportResult(list):
    """Parsed rows plus safe information that can be shown after an import."""

    def __init__(self, rows=None, diagnostics=None):
        super().__init__(rows or [])
        self.diagnostics = diagnostics or {}


class OpenAIImportError(ValueError):
    """Raised when the OpenAI import cannot be safely performed."""


def validate_image_path(image_path):
    path = Path(image_path)
    if path.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
        raise OpenAIImportError(f"Unsupported image file extension: {path.suffix}")
    if not path.is_file():
        raise OpenAIImportError(f"Image was not found: {image_path}")
    return path


def _card_year(value):
    if value is None:
        raise OpenAIImportError("OpenAI response did not include a card year.")
    year = int(value)
    return 2000 + year if year < 100 else year


def _date_value(value, year):
    match = re.search(
        r"(?P<day>\d{1,2})\s*[/.-]\s*(?P<month>\d{1,2})", str(value or "")
    )
    if not match:
        return None
    try:
        return date(year, int(match.group("month")), int(match.group("day")))
    except ValueError:
        return None


def _date_text(value, year):
    match = re.search(
        r"(?P<day>\d{1,2})\s*[/.-]\s*(?P<month>\d{1,2})", str(value or "")
    )
    if not match:
        return None
    text = f"{match.group('day')}/{match.group('month')}"
    return text if _date_value(text, year) else None


def _parse_gender(value):
    text = str(value or "").strip().lower()
    if text.startswith("p"):
        return "pop"
    if text.startswith("m"):
        return "man"
    return None


def _image_to_data_uri(image_path):
    with Image.open(image_path) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        elif image.mode == "L":
            image = image.convert("RGB")
        max_dimension = int(settings.OPENAI_IMAGE_MAX_DIMENSION or 2000)
        if max_dimension > 0:
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        image.save(buf, format="JPEG", quality=92)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _openai_http_error_detail(error, api_key):
    try:
        body = error.read()
    except (OSError, ValueError):
        return ""

    if isinstance(body, bytes):
        body_text = body.decode("utf-8", errors="replace")
    else:
        body_text = str(body)

    try:
        parsed = json.loads(body_text)
    except (json.JSONDecodeError, TypeError):
        parsed = None

    if isinstance(parsed, dict):
        response_error = parsed.get("error", parsed)
        if isinstance(response_error, dict):
            parts = []
            if response_error.get("message"):
                parts.append(response_error["message"])
            if response_error.get("type"):
                parts.append(f"type={response_error['type']}")
            if response_error.get("code"):
                parts.append(f"code={response_error['code']}")
            if parts:
                body_text = "; ".join(str(part) for part in parts)

    return body_text.replace(api_key, "[redacted]").strip()[:_OPENAI_ERROR_TEXT_LIMIT]


def _extract_json_text(content):
    if isinstance(content, dict):
        return content
    text = str(content or "").strip()
    if not text:
        return {}
    fenced = _JSON_TEXT_RE.search(text)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise OpenAIImportError(
            "OpenAI image import returned invalid JSON content."
        ) from error


def _openai_chat_completion(image_path, model):
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise OpenAIImportError("OpenAI import requires OPENAI_API_KEY.")

    data_uri = _image_to_data_uri(image_path)
    payload = {
        "model": model or settings.OPENAI_IMAGE_MODEL,
        "temperature": 0,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    "You extract breeding-card data from one photo and return only JSON. "
                    "Do not translate characters. Keep Latin text as seen. "
                    "Use this schema: "
                    '{"card_year": 26, "parents": {"vader": "...", "moeder": "..."}, '
                    '"rows": [{"row_number": 1, "hatched": "DD/MM", "ring_number": "001", '
                    '"gender": "P", "color": "text"}]}'
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Read the breeding card in the attached image. "
                            "Return strict JSON only. "
                            "The third table column contains a hatch date in DD/MM format only; "
                            "ignore extra OCR tokens like k10 or similar noise. "
                            "The left side of the fourth column contains a numeric ring number. "
                            "The right side of the fourth column contains gender, "
                            "P for pop and M for man. "
                            "Keep the color text as a normal space-separated string and "
                            "do not merge words."
                            "The parent ring numbers are usually shaped like XXXX-XXX-YYYY; "
                            "normalize them to that form. "
                            "Only include rows that contain both a hatch date and a ring number."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": data_uri},
                    },
                ],
            },
        ],
    }
    request = Request(
        settings.OPENAI_API_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    try:
        with urlopen(request, timeout=60, context=ssl_context) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = _openai_http_error_detail(error, api_key)
        suffix = f": {detail}" if detail else ""
        raise OpenAIImportError(
            f"OpenAI image import request failed with HTTP {error.code}{suffix}."
        ) from error
    except URLError as error:
        raise OpenAIImportError(
            f"OpenAI image import request failed: {error.reason}"
        ) from error
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OpenAIImportError(
            "OpenAI image import returned an unreadable response."
        ) from error

    return result


def _parse_response_json(result):
    if not isinstance(result, dict):
        raise OpenAIImportError("OpenAI response must be a JSON object.")

    choices = result.get("choices") or []
    if not choices:
        raise OpenAIImportError("OpenAI image import returned no choices.")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if not content:
        raise OpenAIImportError("OpenAI image import returned no message content.")

    return _extract_json_text(content)


def _parse_import_rows(payload, breeder_number):
    breeder_number = str(breeder_number or "").strip()
    if not breeder_number:
        raise OpenAIImportError(
            "The logged-in user has no breeding registration number."
        )

    card_year = _card_year(payload.get("card_year"))
    parents_data = payload.get("parents") or {}
    parents = {
        "vader": format_ringnumber(parents_data.get("vader")),
        "moeder": format_ringnumber(parents_data.get("moeder")),
    }

    rows = []
    diagnostics_rows = []
    for row in payload.get("rows") or []:
        row_number = row.get("row_number")
        hatched_text = _date_text(row.get("hatched"), card_year)
        hatched = _date_value(hatched_text, card_year)
        ring_serial_number = str(int(row.get("ring_number"))).zfill(3)
        gender = _parse_gender(row.get("gender"))
        color = " ".join(str(row.get("color") or "").split())
        diagnostics_rows.append(
            {
                "row_number": row_number,
                "hatched": hatched_text or row.get("hatched"),
                "ring_serial_number": ring_serial_number,
                "gender": row.get("gender"),
                "color": color,
            }
        )
        if not hatched or not ring_serial_number or not gender:
            continue
        imported = {
            "ringnummer": f"{breeder_number}-{ring_serial_number}-{card_year}",
            "geboren": hatched.strftime("%d-%m-%Y"),
            "geslacht": gender,
            "kleur": color,
            "notes": color,
        }
        if parents["vader"]:
            imported["vader"] = parents["vader"]
        if parents["moeder"]:
            imported["moeder"] = parents["moeder"]
        rows.append(imported)

    diagnostics = {
        "parser_source": "openai",
        "model": payload.get("model"),
        "card_year": card_year,
        "parents": parents,
        "rows": diagnostics_rows,
        "imported_ring_numbers": [row["ringnummer"] for row in rows],
        "raw_response": payload,
    }
    return OpenAIImportResult(rows=rows, diagnostics=diagnostics)


def read_image(image_path, breeder_number, model=None, client=None):
    path = validate_image_path(image_path)
    result = (
        client(path, breeder_number, model)
        if client
        else _openai_chat_completion(path, model)
    )
    payload = _parse_response_json(result)
    payload["model"] = (result.get("model") if isinstance(result, dict) else None) or (
        model or settings.OPENAI_IMAGE_MODEL
    )
    return _parse_import_rows(payload, breeder_number)
