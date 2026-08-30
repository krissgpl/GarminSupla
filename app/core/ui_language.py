from fastapi import Request


def resolve_ui_language(
    request: Request,
    language_setting: str,
) -> str:
    if language_setting == "pl":
        return "pl"

    if language_setting == "en":
        return "en"

    accept_language = request.headers.get(
        "accept-language",
        "",
    )

    preferred_language = (
        accept_language
        .split(",", 1)[0]
        .split(";", 1)[0]
        .strip()
        .lower()
    )

    if (
        preferred_language == "pl"
        or preferred_language.startswith("pl-")
    ):
        return "pl"

    return "en"
