import {
    getUILanguage,
    updateUILanguage,
} from "./api.js";


async function initializeUILanguageSelector() {

    const select =
        document.getElementById(
            "ui-language-select"
        );

    if (!select) {
        return;
    }

    try {

        const settings =
            await getUILanguage();

        let currentLanguage =
            settings.language;

        select.value =
            currentLanguage;

        select.addEventListener(
            "change",
            async () => {

                const nextLanguage =
                    select.value;

                if (
                    nextLanguage
                    === currentLanguage
                ) {
                    return;
                }

                select.disabled = true;

                try {

                    const saved =
                        await updateUILanguage(
                            nextLanguage
                        );

                    currentLanguage =
                        saved.language;

                    window.location.reload();

                } catch (error) {

                    select.value =
                        currentLanguage;

                    select.disabled = false;

                    console.error(
                        "Unable to save UI language:",
                        error,
                    );

                }
            },
        );

    } catch (error) {

        select.disabled = true;

        console.error(
            "Unable to load UI language:",
            error,
        );

    }
}


document.addEventListener(
    "DOMContentLoaded",
    initializeUILanguageSelector,
);


function initializeOAuthCallbackSuggestion() {

    const input =
        document.getElementById("redirect_uri");

    const button =
        document.getElementById(
            "use-current-dashboard-callback"
        );

    const suggestion =
        document.getElementById(
            "callback-suggestion"
        );

    const preview =
        document.getElementById(
            "oauth-callback-preview"
        );

    if (!input || !button) {
        return;
    }

    function updatePreview() {
        if (preview) {
            preview.textContent = input.value.trim();
        }
    }

    input.addEventListener("input", updatePreview);
    updatePreview();

    // Never suggest an HTTP callback.
    if (window.location.protocol !== "https:") {
        return;
    }

    const suggestedUri = new URL(
        "/oauth/callback",
        window.location.origin,
    ).href;

    if (suggestion) {
        suggestion.textContent =
            `${suggestion.dataset.prefix} ${suggestedUri}`;
    }

    button.hidden = false;

    button.addEventListener("click", () => {

        // An explicit click is required. Never
        // overwrite a previously saved callback.
        input.value = suggestedUri;

        updatePreview();
        input.focus();
    });
}

document.addEventListener(
    "DOMContentLoaded",
    initializeOAuthCallbackSuggestion,
);
