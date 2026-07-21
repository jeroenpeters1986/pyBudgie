from pathlib import Path

from budgie_import.services.read_zooeasy import read_zooeasy


def test_read_zooeasy_maps_known_fields(tmp_path):
    xml_content = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
    <zooeasy type=\"ExportDier\" versie=\"11.03\" taal=\"2\" dier=\"24-5815-150\">
      <Dier>
        <Registratienummer>24-5815-150</Registratienummer>
        <Geboortedatum>22-09-2023</Geboortedatum>
        <Overlijdingsdatum>07-07-2024</Overlijdingsdatum>
        <Geslacht>1</Geslacht>
        <RegistratienummerVader>22-AL09-052</RegistratienummerVader>
        <RegistratienummerMoeder>21-5815-204</RegistratienummerMoeder>
        <Ras>Grasparkiet</Ras>
        <Kleur>lutino</Kleur>
      </Dier>
    </zooeasy>
    """

    zoo_file = tmp_path / "birds.zoo"
    zoo_file.write_text(xml_content, encoding="utf-8")

    rows = read_zooeasy(zoo_file)

    assert rows == [
        {
            "ringnummer": "24-5815-150",
            "geboren": "22-09-2023",
            "overleden": "07-07-2024",
            "geslacht": "1",
            "vader": "22-AL09-052",
            "moeder": "21-5815-204",
            "kleur": "lutino",
            "ras": "Grasparkiet",
        }
    ]
