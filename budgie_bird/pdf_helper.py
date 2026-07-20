import ssl

from io import BytesIO
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from django.conf import settings
from django.utils.translation import gettext as _
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfgen import canvas


CARD_WIDTH = 165
CARD_HEIGHT = 94
CARD_HEIGHT_WITH_NOTES = 132
COLUMN_GAP = 38
ROW_GAP = 24
PAGE_MARGIN = 36
TITLE_HEIGHT = 40


def _build_tree(bird, ancestors=None):
    ancestors = set() if ancestors is None else ancestors
    if bird.pk in ancestors:
        return {"bird": bird, "children": []}

    next_ancestors = ancestors | {bird.pk}
    children = []
    for parent in (bird.father, bird.mother):
        if parent:
            children.append(_build_tree(parent, next_ancestors))
    return {"bird": bird, "children": children}


def _position_tree(tree):
    leaves = []
    nodes = []

    def position(node, depth):
        node["depth"] = depth
        nodes.append(node)
        if not node["children"]:
            node["row"] = len(leaves)
            leaves.append(node)
            return node["row"]

        child_rows = [position(child, depth + 1) for child in node["children"]]
        node["row"] = sum(child_rows) / len(child_rows)
        return node["row"]

    position(tree, 0)
    return nodes, len(leaves)


def _draw_wrapped_text(pdf, text, x, y, width, font="Helvetica", size=8, leading=10):
    pdf.setFillColor(colors.HexColor("#222222"))
    pdf.setFont(font, size)
    for line in simpleSplit(str(text), font, size, width):
        pdf.drawString(x, y, line)
        y -= leading
    return y


def _draw_bird_photo(pdf, bird, left, bottom, card_height):
    if not bird.photo or not bird.photo.name:
        return False

    max_size = min(52, card_height - 16)
    photo_url = bird.photo.url
    parsed_url = urlparse(photo_url)

    try:
        if parsed_url.scheme in ("http", "https"):
            urlopen_options = {"timeout": 10}
            if settings.DEBUG:
                urlopen_options["context"] = ssl._create_unverified_context()
            photo_file = urlopen(photo_url, **urlopen_options)
        else:
            photo_file = bird.photo.storage.open(bird.photo.name, "rb")
    except HTTPError as exc:
        if exc.code == 404:
            return False
        raise
    except (URLError, OSError):
        return False

    with photo_file:
        image = ImageReader(photo_file)
        image_width, image_height = image.getSize()
        scale = min(max_size / image_width, max_size / image_height)
        width = image_width * scale
        height = image_height * scale
        pdf.drawImage(
            image,
            left + CARD_WIDTH - width - 8,
            bottom + card_height - height - 8,
            width=width,
            height=height,
            preserveAspectRatio=True,
            mask="auto",
        )
    return True


def _draw_bird_card(pdf, node, left, bottom, card_height, include_notes):
    bird = node["bird"]
    gender_colors = {
        "male": colors.HexColor("#1976d2"),
        "female": colors.HexColor("#d81b60"),
    }
    border_color = gender_colors.get(bird.gender, colors.HexColor("#616161"))

    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(border_color)
    pdf.setLineWidth(2)
    pdf.roundRect(left, bottom, CARD_WIDTH, card_height, 6, fill=1, stroke=1)

    text_x = left + 8
    has_photo = _draw_bird_photo(pdf, bird, left, bottom, card_height)
    text_width = CARD_WIDTH - 74 if has_photo else CARD_WIDTH - 16
    text_y = bottom + card_height - 16
    text_y = _draw_wrapped_text(
        pdf, bird.ring_number, text_x, text_y, text_width, "Helvetica-Bold", 10, 12
    )
    text_y -= 2
    text_y = _draw_wrapped_text(
        pdf, bird.get_gender_display(), text_x, text_y, text_width, size=8
    )
    text_y = _draw_wrapped_text(
        pdf, bird.descriptive_color() or "-", text_x, text_y, text_width, size=8
    )

    dates = []
    if bird.date_of_birth:
        dates.append("{}: {}".format(_("Born"), bird.date_of_birth))
    if bird.date_of_death:
        dates.append("{}: {}".format(_("Died"), bird.date_of_death))
    for date in dates:
        text_y = _draw_wrapped_text(pdf, date, text_x, text_y, text_width, size=8)

    if include_notes and bird.notes:
        text_y -= 2
        pdf.setStrokeColor(colors.HexColor("#dddddd"))
        pdf.line(text_x, text_y + 3, left + CARD_WIDTH - 8, text_y + 3)
        _draw_wrapped_text(
            pdf,
            "{}: {}".format(_("Notes"), bird.notes),
            text_x,
            text_y - 7,
            text_width,
            size=8,
        )


def _draw_tree_page(pdf, bird, include_notes):
    tree = _build_tree(bird)
    nodes, leaf_count = _position_tree(tree)
    max_depth = max(node["depth"] for node in nodes)
    note_lines = 0
    if include_notes:
        for node in nodes:
            note_lines = max(
                note_lines,
                len(
                    simpleSplit(
                        "{}: {}".format(_("Notes"), node["bird"].notes),
                        "Helvetica",
                        8,
                        CARD_WIDTH - 16,
                    )
                ),
            )
    card_height = (
        CARD_HEIGHT_WITH_NOTES + max(0, note_lines - 3) * 10
        if include_notes
        else CARD_HEIGHT
    )
    width = max(
        landscape(A3)[0],
        2 * PAGE_MARGIN + (max_depth + 1) * CARD_WIDTH + max_depth * COLUMN_GAP,
    )
    height = max(
        landscape(A3)[1],
        PAGE_MARGIN + TITLE_HEIGHT + leaf_count * (card_height + ROW_GAP) + PAGE_MARGIN,
    )
    pdf.setPageSize((width, height))

    pdf.setFillColor(colors.HexColor("#222222"))
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(
        PAGE_MARGIN,
        height - PAGE_MARGIN,
        "{}: {}".format(_("Family tree"), bird.ring_number),
    )
    if include_notes:
        pdf.setFont("Helvetica", 9)
        pdf.drawRightString(
            width - PAGE_MARGIN, height - PAGE_MARGIN, _("Including bird notes")
        )

    top = height - PAGE_MARGIN - TITLE_HEIGHT
    for node in nodes:
        x = PAGE_MARGIN + node["depth"] * (CARD_WIDTH + COLUMN_GAP)
        center_y = top - node["row"] * (card_height + ROW_GAP)
        bottom = center_y - card_height / 2
        node["left"] = x
        node["bottom"] = bottom
        node["center_y"] = center_y

    pdf.setStrokeColor(colors.HexColor("#999999"))
    pdf.setLineWidth(1)
    for node in nodes:
        for child in node["children"]:
            parent_right = node["left"] + CARD_WIDTH
            child_left = child["left"]
            midpoint = parent_right + (child_left - parent_right) / 2
            pdf.line(parent_right, node["center_y"], midpoint, node["center_y"])
            pdf.line(midpoint, node["center_y"], midpoint, child["center_y"])
            pdf.line(midpoint, child["center_y"], child_left, child["center_y"])

    for node in nodes:
        _draw_bird_card(
            pdf, node, node["left"], node["bottom"], card_height, include_notes
        )


def render_bird_tree_pdf(birds, include_notes=False):
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=landscape(A3))
    pdf.setTitle(_("Bird family tree"))
    pdf.setPageCompression(0)

    for bird in birds:
        _draw_tree_page(pdf, bird, include_notes)
        pdf.showPage()

    pdf.save()
    return output.getvalue()
