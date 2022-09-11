from datetime import datetime

import budgie_import.services.read_csv
import budgie_import.services.read_xlsx
from budgie_bird.models import Bird, Breeder, ColorProperty


def import_from_file(file_path, user):
    file_type = file_path.split(".")[-1]

    if file_type == "xlsx":
        bird_import_rows = budgie_import.services.read_xlsx.read_xlsx(
            file_path, header=True
        )
    elif file_type == "csv":
        bird_import_rows = budgie_import.services.read_csv.read_csv(
            file_path, header=True
        )
    else:
        raise Exception("No valid .xlsx or .csv found")

    for import_bird in bird_import_rows:
        import_or_update_bird(import_bird, user)

    return True


def import_or_update_bird(bird_data, user):
    if "ringnummer" not in bird_data:
        return False

    bird = Bird.objects.get_or_create(user=user, ring_number=bird_data["ringnummer"])[0]

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
            # TODO: pass this as a note or something
            print("ERROR: ", error)
            pass

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
                breeding_reg_nr=bird_data["ringnummer"].split("-")[0],
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

    bird.save()

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
