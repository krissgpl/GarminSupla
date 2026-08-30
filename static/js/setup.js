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
