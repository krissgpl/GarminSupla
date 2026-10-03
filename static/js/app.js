(() => {
    const systemDarkTheme =
        window.matchMedia(
            "(prefers-color-scheme: dark)"
        );

    function resolveUITheme(theme) {
        if (theme === "dark") {
            return "dark";
        }

        if (theme === "light") {
            return "light";
        }

        return systemDarkTheme.matches
            ? "dark"
            : "light";
    }

    function applyUITheme(theme) {
        document.documentElement.setAttribute(
            "data-bs-theme",
            resolveUITheme(theme)
        );
    }

    async function initializeUITheme() {
        let currentTheme =
            document.documentElement.dataset.uiTheme;

        try {
            if (
                currentTheme !== "auto"
                && currentTheme !== "light"
                && currentTheme !== "dark"
            ) {
                const response = await fetch(
                    "/api/v1/setup/ui/theme",
                    {
                        headers: {
                            "Accept": "application/json",
                        },
                    }
                );

                if (!response.ok) {
                    throw new Error(
                        "Unable to load UI theme."
                    );
                }

                const settings =
                    await response.json();

                currentTheme =
                    settings.theme;
            }

            applyUITheme(
                currentTheme
            );

            systemDarkTheme.addEventListener(
                "change",
                () => {
                    if (currentTheme === "auto") {
                        applyUITheme(
                            currentTheme
                        );
                    }
                }
            );

        } catch (error) {
            console.error(
                "Unable to load UI theme:",
                error
            );
        }
    }

    function initializeRecoveryCodeCopy() {
        const copyButton =
            document.getElementById(
                "copy-recovery-codes"
            );

        if (!copyButton) {
            return;
        }

        const label =
            document.getElementById(
                "copy-recovery-codes-label"
            );

        const recoveryCodes = Array.from(
            document.querySelectorAll(
                "#recovery-codes .recovery-code"
            )
        );

        const codesText = recoveryCodes
            .map(
                (element) =>
                    element.textContent.trim()
            )
            .filter(Boolean)
            .join("\n");

        if (!codesText) {
            copyButton.disabled = true;
            return;
        }

        const originalLabel =
            copyButton.dataset.copyLabel;

        const copiedLabel =
            copyButton.dataset.copiedLabel;

        const failedLabel =
            copyButton.dataset.copyFailedLabel;

        const setTemporaryLabel = (text) => {
            if (!label) {
                return;
            }

            label.textContent = text;

            window.setTimeout(
                () => {
                    label.textContent =
                        originalLabel;
                },
                2000
            );
        };

        const fallbackCopy = (text) => {
            const textarea =
                document.createElement(
                    "textarea"
                );

            textarea.value = text;

            textarea.style.position =
                "fixed";

            textarea.style.left =
                "-9999px";

            textarea.style.top =
                "0";

            textarea.style.opacity =
                "0";

            document.body.appendChild(
                textarea
            );

            textarea.focus();
            textarea.select();

            textarea.setSelectionRange(
                0,
                textarea.value.length
            );

            const copied =
                document.execCommand(
                    "copy"
                );

            textarea.remove();

            if (!copied) {
                throw new Error(
                    "Clipboard copy failed."
                );
            }
        };

        const copyCodes = async () => {
            if (
                window.isSecureContext
                && navigator.clipboard
                && navigator.clipboard.writeText
            ) {
                try {
                    await navigator.clipboard.writeText(
                        codesText
                    );

                    return;

                } catch {
                    // Fall back to the legacy clipboard API.
                }
            }

            fallbackCopy(
                codesText
            );
        };

        copyButton.addEventListener(
            "click",
            async () => {
                try {
                    await copyCodes();

                    setTemporaryLabel(
                        copiedLabel
                    );

                } catch {
                    setTemporaryLabel(
                        failedLabel
                    );
                }
            }
        );
    }

    initializeUITheme();
    initializeRecoveryCodeCopy();
})();
