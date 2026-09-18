WATCH_MODELS_BY_PART_NUMBER: dict[str, str] = {
    "006-B3905-00": "fēnix 7S",
    "006-B3908-00": "fēnix 7S",
    "006-B4374-00": "fēnix 7S Pro",

    "006-B3906-00": "fēnix 7",
    "006-B3909-00": "fēnix 7",
    "006-B4375-00": "fēnix 7 Pro",
    "006-B4595-00": "fēnix 7 Pro Solar (No Wi-Fi)",

    "006-B3907-00": "fēnix 7X",
    "006-B3910-00": "fēnix 7X",
    "006-B4376-00": "fēnix 7X Pro",
    "006-B4596-00": "fēnix 7X Pro (No Wi-Fi)",

    "006-B3287-00": "fēnix 6S",
    "006-B3512-00": "fēnix 6S",
    "006-B3764-00": "fēnix 6S Solar",
    "006-B3768-00": "fēnix 6S Dual Power",

    "006-B3288-00": "fēnix 6S Pro",
    "006-B3513-00": "fēnix 6S Pro",
    "006-B3765-00": "fēnix 6S Pro Solar",
    "006-B3769-00": "fēnix 6S Pro Dual Power",

    "006-B3289-00": "fēnix 6",
    "006-B3514-00": "fēnix 6",
    "006-B3766-00": "fēnix 6 Solar",
    "006-B3770-00": "fēnix 6 Dual Power",

    "006-B3290-00": "fēnix 6 Pro",
    "006-B3515-00": "fēnix 6 Pro",
    "006-B3767-00": "fēnix 6 Pro Solar",
    "006-B3771-00": "fēnix 6 Pro Dual Power",

    "006-B3291-00": "fēnix 6X Pro",
    "006-B3516-00": "fēnix 6X Pro",

    "006-B2700-00": "vívoactive 3",
    "006-B2976-00": "vívoactive 3",
    "006-B3446-00": "vívoactive 3",

    "006-B2988-00": "vívoactive 3 Music",
    "006-B3163-00": "vívoactive 3 Music",

    "006-B3066-00": "vívoactive 3 Music LTE",

    "006-B3225-00": "vívoactive 4",
    "006-B3388-00": "vívoactive 4",

    "006-B3224-00": "vívoactive 4S",
    "006-B3387-00": "vívoactive 4S",

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
    "006-B2544-00": "fēnix 5S",
    "006-B2797-00": "fēnix 5S",
    "006-B2900-00": "fēnix 5S Plus",
    "006-B3134-00": "fēnix 5S Plus",
    "006-B2604-00": "fēnix 5X",
    "006-B2798-00": "fēnix 5X",
    "006-B3111-00": "fēnix 5X Plus",
    "006-B3135-00": "fēnix 5X Plus",
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
