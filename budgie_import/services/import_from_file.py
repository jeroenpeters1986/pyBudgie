from collections.abc import Mapping
from dataclasses import dataclass, field
import json
from datetime import datetime

import budgie_import.services.read_csv
import budgie_import.services.read_xlsx
import budgie_import.services.read_zooeasy
import budgie_import.services.read_image_with_ai
from budgie_bird.models import Bird, Breeder, ColorProperty


@dataclass
class ImportRowResult:
    """The outcome of importing one source row."""

    imported: bool
    ring_number: str = None
    created: bool = False
    skipped_reason: str = None
    warnings: list = field(default_factory=list)

    def __bool__(self):
        return self.imported


@dataclass
class ImportResult:
    """The outcome of importing all rows from one file."""

    imported_ring_numbers: list = field(default_factory=list)
    created_ring_numbers: list = field(default_factory=list)
    updated_ring_numbers: list = field(default_factory=list)
    skipped_rows: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    diagnostics: dict = field(default_factory=dict)

    @property
    def created_or_updated_ring_numbers(self):
        return self.created_ring_numbers + self.updated_ring_numbers

    @property
    def imported(self):
        return self.imported_ring_numbers

    def __getitem__(self, key):
        return {
            "imported": self.imported_ring_numbers,
            "imported_ring_numbers": self.imported_ring_numbers,
            "created_ring_numbers": self.created_ring_numbers,
            "updated_ring_numbers": self.updated_ring_numbers,
            "created_or_updated": self.created_or_updated_ring_numbers,
            "created_or_updated_ring_numbers": self.created_or_updated_ring_numbers,
            "skipped": self.skipped_rows,
            "skipped_rows": self.skipped_rows,
            "warnings": self.warnings,
            "diagnostics": self.diagnostics,
        }[key]

    def diagnostics_text(self, limit=12000):
        if not self.diagnostics:
            return ""
        text = json.dumps(self.diagnostics, ensure_ascii=False, indent=2)
        return f"Image diagnostics:\n{text[:limit]}"

    def summary(self):
        parts = [
            f"Imported {len(self.imported_ring_numbers)} bird(s): "
            f"{', '.join(self.imported_ring_numbers) or 'none'}."
        ]
        if self.created_ring_numbers:
            parts.append(f"Created: {', '.join(self.created_ring_numbers)}.")
        if self.updated_ring_numbers:
            parts.append(f"Updated: {', '.join(self.updated_ring_numbers)}.")
        if self.skipped_rows:
            skipped = "; ".join(
                f"row {row['row_number']} ({row['reason']})"
                for row in self.skipped_rows
            )
            parts.append(f"Skipped {len(self.skipped_rows)} row(s): {skipped}.")
        if self.warnings:
            parts.append(f"Warnings: {'; '.join(self.warnings)}.")
        return " ".join(parts)


def import_from_file(file_path, user):
    file_type = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    image_result = None

    if file_type == "xlsx":
        bird_import_rows = budgie_import.services.read_xlsx.read_xlsx(
            file_path, header=True
        )
    elif file_type == "csv":
        bird_import_rows = budgie_import.services.read_csv.read_csv(
            file_path, header=True
        )
    elif file_type == "zoo":
        bird_import_rows = budgie_import.services.read_zooeasy.read_zooeasy(file_path)
    elif f".{file_type}" in budgie_import.services.read_image_with_ai.SUPPORTED_IMAGE_EXTENSIONS:
        image_result = budgie_import.services.read_image_with_ai.read_image(
            file_path, user.breeding_reg_nr
        )
        bird_import_rows = image_result
    else:
        raise ValueError("No valid .xlsx, .csv, .zoo, .jpg, .jpeg, or .png file found.")

    result = ImportResult()
    if hasattr(image_result, "diagnostics"):
        result.diagnostics = image_result.diagnostics
    for row_number, import_bird in enumerate(bird_import_rows, start=1):
        row_result = import_or_update_bird(import_bird, user)
        if not row_result:
            result.skipped_rows.append(
                {
                    "row_number": row_number,
                    "ring_number": row_result.ring_number,
                    "reason": row_result.skipped_reason,
                }
            )
            continue

        result.imported_ring_numbers.append(row_result.ring_number)
        if row_result.created:
            result.created_ring_numbers.append(row_result.ring_number)
        else:
            result.updated_ring_numbers.append(row_result.ring_number)
        result.warnings.extend(row_result.warnings)

    return result


def import_or_update_bird(bird_data, user):
    if not isinstance(bird_data, Mapping):
        return ImportRowResult(
            imported=False,
            skipped_reason="row is not a mapping",
        )

    ring_number = bird_data.get("ringnummer")
    if not isinstance(ring_number, str) or not ring_number.strip():
        return ImportRowResult(
            imported=False,
            ring_number=ring_number,
            skipped_reason="missing ring number",
        )
    ring_number = ring_number.strip()

    bird, created = Bird.objects.get_or_create(user=user, ring_number=ring_number)
    warnings = []

    # Mother
    if "moeder" in bird_data:
        bird.mother = Bird.objects.get_or_create(
            user=user,
            ring_number=bird_data["moeder"],
            defaults={"gender": Bird.Gender.FEMALE},
        )[0]

    # Father
    if "vader" in bird_data:
        bird.father = Bird.objects.get_or_create(
            user=user, ring_number=bird_data["vader"]
        )[0]

    # Gender
    if "geslacht" in bird_data:
        if bird_data["geslacht"].lower() == "pop":
            bird.gender = Bird.Gender.FEMALE
        if bird_data["geslacht"].lower() == "man":
            bird.gender = Bird.Gender.MALE

    # Birth date
    if "geboren" in bird_data:
        try:
            bird.date_of_birth = datetime.strptime(
                bird_data["geboren"], "%d-%m-%Y"
            ).date()
        except ValueError as error:
            warnings.append(f"invalid birth date ({error})")

    # Breeder
    if "kweker" in bird_data:
        if "onbekend" not in bird_data["kweker"].lower():
            try:
                last_name = bird_data["kweker"].split(",")[0]
                first_name = bird_data["kweker"].split(",")[1].strip()
            except IndexError:
                last_name = bird_data["kweker"]
                first_name = ""

            bird.breeder = Breeder.objects.get_or_create(
                user=user,
                breeding_reg_nr=ring_number.split("-")[0],
                defaults={
                    "last_name": last_name,
                    "first_name": first_name,
                },
            )[0]

    # Is the bird currently owned?
    if "in bezit" in bird_data and bird_data["in bezit"].lower() == "ja":
        bird.is_owned = True

    # Owner
    if "eigenaar" in bird_data:
        possible_owners = Breeder.objects.filter(
            user=user, last_name__icontains=bird_data["eigenaar"].split(",")[0]
        )

        if possible_owners.count() > 1:
            possible_owners.filter(
                first_name__icontains=bird_data["eigenaar"].split(",")[1]
            )

        if possible_owners.count() == 1:
            bird.owner = possible_owners[0]

    if "notes" in bird_data:
        bird.notes = bird_data["notes"]

    # All sorts of colors and properties
    if "kleur" in bird_data:
        # Primary color
        for color in Bird.Color.choices:
            if color[1].lower() in bird_data["kleur"].lower():
                bird.color = color[0]
                break

        # Color properties
        matched_color_props = []
        for color_prop in ColorProperty.objects.filter(user=user).order_by("rank"):
            if color_prop.color_name.lower() in bird_data["kleur"].lower():
                matched_color_props.append(color_prop)

        for matched_color_prop in matched_color_props:
            bird.color_property.add(matched_color_prop)

    bird.save()

    return ImportRowResult(
        imported=True,
        ring_number=ring_number,
        created=created,
        warnings=warnings,
    )
