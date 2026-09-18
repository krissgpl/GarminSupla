WATCH_MODELS_BY_PART_NUMBER: dict[str, str] = {
    "006-B4315-00": "Forerunner 965",
    "006-B4426-00": "vívoactive 5",
    "006-B4532-00": "fēnix 8 Solar (47mm)",
    "006-B4533-00": "fēnix 8 Solar (51mm)",
    "006-B4534-00": "fēnix 8 AMOLED (43mm)",
    "006-B4536-00": "fēnix 8 AMOLED (47mm/51mm)",
    "006-B4565-00": "Forerunner 970",
    "006-B4625-00": "vívoactive 6",
    "006-B4631-00": "fēnix 8 Pro",
    "006-B4666-00": "fēnix E",
}


def resolve_watch_model(
    part_number: str | None,
) -> str | None:
    """Resolve Garmin watch model from its Connect IQ part number."""

    if part_number is None:
        return None

    normalized = (
        part_number
        .strip()
        .upper()
    )

    if not normalized:
        return None

    return WATCH_MODELS_BY_PART_NUMBER.get(
        normalized
    )
