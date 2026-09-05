WATCH_MODELS_BY_PART_NUMBER: dict[str, str] = {
    "006-B4631-00": "fēnix 8 Pro",
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
