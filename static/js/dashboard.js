import {
    ApiError,
    approveWatchPairing,
    copyWatchItemsById,
    deleteWatchById,
    getAvailableSuplaItems,
    getUILanguage,
    getUITheme,
    getWatchItemsById,
    getWatchStatuses,
    startWatchRePair,
    updateUILanguage,
    updateUITheme,
    updateWatchApplicationLanguageById,
    updateWatchItemsById,
    updateWatchNameById,
} from "./api.js";

const uiLanguage =
    document.documentElement.lang === "pl"
        ? "pl"
        : "en";

const uiText = {
    en: {
        never: "Never",
        enabled: "Enabled",
        disabled: "Disabled",
        created: "Created",
        lastSeen: "Last seen",
        deviceModel: "Model",
        deviceId: "Device ID",
        partNumber: "Part number",
        firmwareVersion: "Firmware",
        connectIqVersion: "Connect IQ",
        garminSuplaVersion: "GarminSupla",
        systemLanguage: "System language",
        applicationLanguage: "Application language",
        automaticLanguage: "Auto",
        unableToSaveWatchLanguage:
            "Unable to save watch application language.",
        notAvailable: "Not available",
        polish: "Polish",
        english: "English",
        renameWatch: "Rename",
        watchName: "Watch name",
        save: "Save",
        invalidWatchName:
            "Enter a watch name up to 50 characters.",
        unableToRenameWatch:
            "Unable to rename Garmin watch.",
        watchItems: "Watch items",
        noWatchItems: "No items configured for the watch.",
        type: "Type",
        icon: "Icon",
        visibility: "Visibility",
        showOnWatch: "Show on watch",
        action: "Action",
        requireConfirmation: "Require confirmation",
        moveUp: "Move up",
        moveDown: "Move down",
        remove: "Remove",
        addFromSupla: "Add from SUPLA",
        saveWatchConfiguration: "Save watch configuration",
        garageGate: "Garage gate",
        slidingGate: "Sliding gate",
        doubleSwingGate: "Double swing gate",
        light: "Light",
        switch: "Switch",
        scene: "Scene",
        rollerShutter: "Roller shutter",
        awning: "Awning",
        defaultIcon: "Default",
        typeGate: "Gate",
        typeScene: "Scene",
        typeLight: "Light",
        typeSwitch: "Switch",
        typeRollerShutter: "Roller shutter",
        typeAwning: "Awning",
        loadingSuplaItems: "Loading SUPLA items...",
        noAdditionalSuplaItems: "No additional supported SUPLA items are available.",
        gates: "Gates",
        scenes: "Scenes",
        otherDevices: "Other devices",
        suplaItem: "SUPLA item",
        add: "Add",
        unableToLoadSuplaItems: "Unable to load SUPLA items.",
        saving: "Saving...",
        saved: "Saved",
        unableToSaveConfiguration: "Unable to save configuration.",
        noWatchConfigured: "No Garmin watch has been configured yet.",
        configureWatch: "Configure Watch",
        replaceWatch: "Replace Watch",
        rePairCurrentWatch: "Re-pair current watch",
        deleteWatch: "Delete watch",
        deleteWatchConfirmation:
            "Delete this watch?\n\nIts configuration will be permanently removed and its token will stop working.",
        unableToDeleteWatch:
            "Unable to delete Garmin watch.",
        watchReplacementInfo:
            "Replace Watch keeps the current watch active until the new watch completes pairing. Re-pair invalidates the current watch token immediately.",
        pairGarminWatch: "Pair Garmin Watch",
        pairingInstructions:
            "Enter the 6-digit code displayed by GarminSupla on your watch.",
        pairingCode: "Pairing code",
        pairWatch: "Pair Watch",
        pairingApproved: "Pairing approved",
        completePairingOnWatch:
            "Complete the pairing process on your Garmin watch.",
        cancel: "Cancel",
        rePairConfirmation:
            "Re-pair the current watch?\n\nThe current watch token will be invalidated. The watch will need to pair again.",
        unableToResetWatchPairing:
            "Unable to reset watch pairing.",
        invalidPairingCode:
            "Enter a valid 6-digit pairing code.",
        pairingCodeNotFound:
            "Pairing code not found or expired.",
        unableToPairWatch:
            "Unable to pair Garmin watch.",
        unableToLoadWatchConfiguration:
            "Unable to load Garmin watch configuration.",
        selectWatch: "Select watch",
        addWatch: "Add watch",
        copyWatchItems: "Copy Watch items",
        copyWatchItemsFrom: "Copy Watch items from",
        copyWatchItemsConfirmation:
            "Replace the current Watch items with items from the selected watch?",
        unableToCopyWatchItems:
            "Unable to copy Watch items.",
        copyWatchConfiguration:
            "Copy configuration from",
        emptyWatchConfiguration:
            "Start with empty configuration",
        details: "Details",
        hideDetails: "Hide details",
    },

    pl: {
        never: "Nigdy",
        enabled: "Włączony",
        disabled: "Wyłączony",
        created: "Utworzono",
        lastSeen: "Ostatnia aktywność",
        deviceModel: "Model",
        deviceId: "Device ID",
        partNumber: "Numer części",
        firmwareVersion: "Firmware",
        connectIqVersion: "Connect IQ",
        garminSuplaVersion: "GarminSupla",
        systemLanguage: "Język systemowy",
        applicationLanguage: "Język aplikacji",
        automaticLanguage: "Automatyczny",
        unableToSaveWatchLanguage:
            "Nie można zapisać języka aplikacji zegarka.",
        notAvailable: "Brak danych",
        polish: "Polski",
        english: "Angielski",
        renameWatch: "Zmień nazwę",
        watchName: "Nazwa zegarka",
        save: "Zapisz",
        invalidWatchName:
            "Wpisz nazwę zegarka o długości do 50 znaków.",
        unableToRenameWatch:
            "Nie można zmienić nazwy zegarka Garmin.",
        watchItems: "Elementy zegarka",
        noWatchItems: "Brak skonfigurowanych elementów zegarka.",
        type: "Typ",
        icon: "Ikona",
        visibility: "Widoczność",
        showOnWatch: "Pokaż na zegarku",
        action: "Akcja",
        requireConfirmation: "Wymagaj potwierdzenia",
        moveUp: "Przenieś wyżej",
        moveDown: "Przenieś niżej",
        remove: "Usuń",
        addFromSupla: "Dodaj z SUPLA",
        saveWatchConfiguration: "Zapisz konfigurację zegarka",
        garageGate: "Brama garażowa",
        slidingGate: "Brama przesuwna",
        doubleSwingGate: "Brama dwuskrzydłowa",
        light: "Światło",
        switch: "Przełącznik",
        scene: "Scena",
        rollerShutter: "Roleta",
        awning: "Markiza",
        defaultIcon: "Domyślna",
        typeGate: "Brama",
        typeScene: "Scena",
        typeLight: "Światło",
        typeSwitch: "Przełącznik",
        typeRollerShutter: "Roleta",
        typeAwning: "Markiza",
        loadingSuplaItems: "Ładowanie elementów SUPLA...",
        noAdditionalSuplaItems: "Brak dodatkowych obsługiwanych elementów SUPLA.",
        gates: "Bramy",
        scenes: "Sceny",
        otherDevices: "Inne urządzenia",
        suplaItem: "Element SUPLA",
        add: "Dodaj",
        unableToLoadSuplaItems: "Nie można załadować elementów SUPLA.",
        saving: "Zapisywanie...",
        saved: "Zapisano",
        unableToSaveConfiguration: "Nie można zapisać konfiguracji.",
        noWatchConfigured: "Nie skonfigurowano jeszcze zegarka Garmin.",
        configureWatch: "Skonfiguruj zegarek",
        replaceWatch: "Zmień zegarek",
        rePairCurrentWatch: "Sparuj ponownie zegarek",
        deleteWatch: "Usuń zegarek",
        deleteWatchConfirmation:
            "Usunąć ten zegarek?\n\nJego konfiguracja zostanie trwale usunięta, a token przestanie działać.",
        unableToDeleteWatch:
            "Nie można usunąć zegarka Garmin.",
        watchReplacementInfo:
            "Zmiana zegarka pozostawia obecny zegarek aktywny do czasu zakończenia parowania nowego. Ponowne parowanie natychmiast unieważnia token obecnego zegarka.",
        pairGarminWatch: "Sparuj zegarek Garmin",
        pairingInstructions:
            "Wpisz 6-cyfrowy kod wyświetlany przez GarminSupla na zegarku.",
        pairingCode: "Kod parowania",
        pairWatch: "Sparuj zegarek",
        pairingApproved: "Parowanie zatwierdzone",
        completePairingOnWatch:
            "Dokończ proces parowania na zegarku Garmin.",
        cancel: "Anuluj",
        rePairConfirmation:
            "Sparować ponownie obecny zegarek?\n\nToken obecnego zegarka zostanie unieważniony. Zegarek będzie wymagał ponownego sparowania.",
        unableToResetWatchPairing:
            "Nie można zresetować parowania zegarka.",
        invalidPairingCode:
            "Wpisz prawidłowy 6-cyfrowy kod parowania.",
        pairingCodeNotFound:
            "Nie znaleziono kodu parowania lub kod wygasł.",
        unableToPairWatch:
            "Nie można sparować zegarka Garmin.",
        unableToLoadWatchConfiguration:
            "Nie można załadować konfiguracji zegarka Garmin.",
        selectWatch: "Wybierz zegarek",
        addWatch: "Dodaj zegarek",
        copyWatchItems: "Kopiuj elementy zegarka",
        copyWatchItemsFrom: "Kopiuj elementy zegarka z",
        copyWatchItemsConfirmation:
            "Zastąpić elementy bieżącego zegarka elementami z wybranego zegarka?",
        unableToCopyWatchItems:
            "Nie można skopiować elementów zegarka.",
        copyWatchConfiguration:
            "Skopiuj konfigurację z",
        emptyWatchConfiguration:
            "Zacznij z pustą konfiguracją",
        details: "Szczegóły",
        hideDetails: "Ukryj szczegóły",
    },
};

function t(key) {
    return uiText[uiLanguage][key]
        ?? uiText.en[key]
        ?? key;
}

function formatItemType(type) {

    const typeKeys = {
        gate: "typeGate",
        scene: "typeScene",
        light: "typeLight",
        switch: "typeSwitch",
        roller_shutter: "typeRollerShutter",
        awning: "typeAwning",
    };

    const key = typeKeys[type];

    if (!key) {
        return type;
    }

    return t(key);
}

function getDefaultWatchItemIcon(type) {

    const defaultIcons = {
        gate: "garage_gate",
        scene: "scene",
        light: "light",
        switch: "switch",
        roller_shutter: "roller_shutter",
        awning: "awning",
    };

    return defaultIcons[type]
        ?? "default";
}

let watchItemsDirty = false;
let selectedWatchId = null;

function setWatchSelectorCardsDisabled(
    disabled
) {

    document
        .querySelectorAll(
            "[data-watch-selector-card]"
        )
        .forEach((button) => {
            button.disabled = disabled;
        });
}

function setWatchItemsDirty(dirty) {
    watchItemsDirty = dirty;

    const button =
        document.getElementById(
            "save-watch-items-btn"
        );

    if (button) {
        button.disabled = !dirty;
    }

    setWatchSelectorCardsDisabled(
        dirty
    );

    const addWatchButton =
        document.getElementById(
            "add-watch-btn"
        );

    if (addWatchButton) {
        addWatchButton.disabled = dirty;
    }

    const copyWatchItemsButton =
        document.getElementById(
            "copy-watch-items-btn"
        );

    if (copyWatchItemsButton) {
        copyWatchItemsButton.disabled =
            dirty;
    }

    const copyWatchItemsSource =
        document.getElementById(
            "copy-watch-items-source"
        );

    if (copyWatchItemsSource) {
        copyWatchItemsSource.disabled =
            dirty;
    }

    const confirmCopyWatchItemsButton =
        document.getElementById(
            "confirm-copy-watch-items-btn"
        );

    if (confirmCopyWatchItemsButton) {
        confirmCopyWatchItemsButton.disabled =
            dirty;
    }

    const deleteWatchButton =
        document.getElementById(
            "delete-watch-btn"
        );

    if (deleteWatchButton) {
        deleteWatchButton.disabled = dirty;
    }

    const replaceWatchButton =
        document.getElementById(
            "replace-watch-btn"
        );

    if (replaceWatchButton) {
        replaceWatchButton.disabled = dirty;
    }

    const rePairWatchButton =
        document.getElementById(
            "reset-watch-pairing-btn"
        );

    if (rePairWatchButton) {
        rePairWatchButton.disabled = dirty;
    }

}

function formatDate(value) {

    if (!value) {
        return t("never");
    }

    return new Date(value).toLocaleString(
        uiLanguage
    );

}

function formatMetadataValue(value) {

    if (
        value === null
        || value === undefined
        || value === ""
    ) {
        return t("notAvailable");
    }

    return value;
}

function formatSystemLanguage(value) {

    if (
        !value
        || value === "unknown"
    ) {
        return t("notAvailable");
    }

    if (value === "pol") {
        return t("polish");
    }

    if (value === "eng") {
        return t("english");
    }

    return value.toUpperCase();
}

function renderWatchItemIcon(icon) {

    const watchIcons = {
        garage_gate: [
            "garage_gate_closed.png",
            t("garageGate"),
        ],
        sliding_gate: [
            "sliding_gate_closed.png",
            t("slidingGate"),
        ],
        double_swing_gate: [
            "double_swing_gate_closed.png",
            t("doubleSwingGate"),
        ],
        light: [
            "light_off.png",
            t("light"),
        ],
        switch: [
            "switch_off.png",
            t("switch"),
        ],
        roller_shutter: [
            "roller_shutter_closed.png",
            t("rollerShutter"),
        ],
        awning: [
            "awning_closed.png",
            t("awning"),
        ],
        scene: [
            "scene.png",
            t("scene"),
        ],
    };

    const iconConfig =
        watchIcons[icon];

    if (!iconConfig) {
        return `
            <i
                class="bi bi-square fs-2 text-muted"
                aria-label="${t("defaultIcon")}"
            ></i>
        `;
    }

    const [filename, label] =
        iconConfig;

    return `
        <img
            src="/watch-icons/${filename}"
            alt="${label}"
            style="
                max-width: 64px;
                max-height: 40px;
                object-fit: contain;
            "
        >
    `;
}

function getWatchItemIconOptions(
    itemType,
    selectedIcon,
) {

    const iconsByType = {
        gate: [
            ["garage_gate", t("garageGate")],
            ["sliding_gate", t("slidingGate")],
            ["double_swing_gate", t("doubleSwingGate")],
        ],

        light: [
            ["light", t("light")],
        ],

        switch: [
            ["switch", t("switch")],
        ],

        scene: [
            ["scene", t("scene")],
        ],

        roller_shutter: [
            ["roller_shutter", t("rollerShutter")],
        ],

        awning: [
            ["awning", t("awning")],
        ],
    };

    const icons =
        iconsByType[itemType]
        ?? [
            ["default", t("defaultIcon")],
        ];

    return icons
        .map(([value, label]) => `
            <option
                value="${value}"
                ${
                    value === selectedIcon
                        ? "selected"
                        : ""
                }
            >
                ${label}
            </option>
        `)
        .join("");
}

function renderWatchItems(items) {

    if (!items.length) {
        return `
            <div
                class="border-top pt-3 mt-3"
                id="watch-items-section"
            >
                <h5 class="mb-2">
                    ${t("watchItems")}
                </h5>

                <p class="text-muted mb-3">
                    ${t("noWatchItems")}
                </p>

                <button
                    type="button"
                    class="btn btn-outline-primary"
                    id="add-from-supla-btn"
                >
                    <i class="bi bi-plus-lg me-1"></i>
                    ${t("addFromSupla")}
                </button>

                <div
                    id="add-from-supla-content"
                    class="mt-3"
                ></div>
            </div>
        `;
    }

    const rows = items
        .map((item, index) => `
            <div class="col-12 col-xl-6 col-xxl-4">

                <div
                    class="border rounded-4 p-3 h-100"
                    data-watch-item-index="${index}"
                >

                    <div class="d-flex flex-column flex-md-row align-items-stretch align-items-md-start justify-content-between gap-3">

                        <div class="d-flex align-items-center gap-3">

                            <div
                                class="d-flex align-items-center justify-content-center flex-shrink-0"
                                style="width: 72px; height: 48px;"
                                data-watch-item-icon-preview
                            >
                                ${renderWatchItemIcon(item.icon)}
                            </div>

                            <div>
                                <strong>
                                    ${item.name}
                                </strong>

                                <div class="small text-muted mt-1">
                                    ${t("type")}: ${formatItemType(item.type)}
                                </div>
                            </div>

                        </div>

                        <div class="d-flex gap-2 justify-content-end flex-shrink-0">

                            <button
                                type="button"
                                class="btn btn-outline-secondary btn-sm px-2"
                                data-watch-item-up="${index}"
                                ${index === 0 ? "disabled" : ""}
                                title="${t("moveUp")}"
                                aria-label="${t("moveUp")}"
                            >
                                <i class="bi bi-arrow-up"></i>
                            </button>

                            <button
                                type="button"
                                class="btn btn-outline-secondary btn-sm px-2"
                                data-watch-item-down="${index}"
                                ${
                                    index === items.length - 1
                                        ? "disabled"
                                        : ""
                                }
                                title="${t("moveDown")}"
                                aria-label="${t("moveDown")}"
                            >
                                <i class="bi bi-arrow-down"></i>
                            </button>

                            <button
                                type="button"
                                class="btn btn-outline-danger btn-sm px-2"
                                data-watch-item-remove="${index}"
                                title="${t("remove")}"
                                aria-label="${t("remove")}"
                            >
                                <i class="bi bi-trash"></i>
                            </button>

                        </div>

                    </div>

                    <div class="row g-3 mt-3 pt-3 border-top">

                        <div class="col-12 col-md-6">

                            <label
                                class="form-label small fw-semibold"
                            >
                                ${t("icon")}
                            </label>

                            <select
                                class="form-select form-select-sm"
                                data-watch-item-icon
                            >
                                ${getWatchItemIconOptions(
                                    item.type,
                                    item.icon
                                )}
                           </select>

                        </div>

                        <div class="col-12 col-md-6">

                            <div class="mb-3">

                                <label
                                    class="form-label small fw-semibold d-block"
                                >
                                    ${t("visibility")}
                                </label>

                                <div class="form-check form-switch">

                                    <input
                                        class="form-check-input"
                                        type="checkbox"
                                        role="switch"
                                        data-watch-item-enabled
                                        ${
                                            item.enabled
                                                ? "checked"
                                                : ""
                                        }
                                    >

                                    <label class="form-check-label small">
                                        ${t("showOnWatch")}
                                    </label>

                                </div>

                            </div>

                            <div>

                                <label
                                    class="form-label small fw-semibold d-block"
                                >
                                    ${t("action")}
                                </label>

                                <div class="form-check form-switch">

                                    <input
                                        class="form-check-input"
                                        type="checkbox"
                                        role="switch"
                                        data-watch-item-confirmation
                                        ${
                                            item.confirmation_required
                                                ? "checked"
                                                : ""
                                        }
                                    >

                                    <label class="form-check-label small">
                                        ${t("requireConfirmation")}
                                    </label>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>

            </div>
        `)
        .join("");

    return `
        <div
            class="border-top pt-3 mt-3"
            id="watch-items-section"
        >
            <h5 class="mb-3">
                ${t("watchItems")}
            </h5>

            <div class="row g-3">
                ${rows}
            </div>

            <div class="mt-3">

                <button
                    type="button"
                    class="btn btn-outline-primary"
                    id="add-from-supla-btn"
                >
                    <i class="bi bi-plus-lg me-1"></i>
                    ${t("addFromSupla")}
                </button>

                <div
                    id="add-from-supla-content"
                    class="mt-3"
                ></div>

            </div>

            <div class="d-flex align-items-center gap-3 mt-3">

                <button
                    type="button"
                    class="btn ${
                        watchItemsDirty
                            ? "btn-primary"
                            : "btn-secondary"
                    }"
                    id="save-watch-items-btn"
                    ${watchItemsDirty ? "" : "disabled"}
                >
                    <i class="bi bi-check-lg me-1"></i>
                    ${t("saveWatchConfiguration")}
                </button>

                <span
                    id="watch-items-save-status"
                    class="small"
                ></span>

            </div>
        </div>

    `;
}

function bindWatchItemEditors() {

    document
        .querySelectorAll(
            "[data-watch-item-index]"
        )
        .forEach((row) => {

            const iconSelect =
                row.querySelector(
                    "[data-watch-item-icon]"
                );

            const enabledToggle =
                row.querySelector(
                    "[data-watch-item-enabled]"
                );

            const confirmationToggle =
                row.querySelector(
                    "[data-watch-item-confirmation]"
                );

            enabledToggle.addEventListener(
                "change",
                () => setWatchItemsDirty(true),
            );

            confirmationToggle.addEventListener(
                "change",
                () => setWatchItemsDirty(true),
            );

            const iconPreview =
                row.querySelector(
                    "[data-watch-item-icon-preview]"
                );

            iconSelect.addEventListener(
                "change",
                () => {

                    iconPreview.innerHTML =
                        renderWatchItemIcon(
                            iconSelect.value
                        );
                    setWatchItemsDirty(true);

                },
            );

        });
}

function bindWatchItemActions(
    items,
    watchId,
) {

    document
        .querySelectorAll(
            "[data-watch-item-up]"
        )
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    const index = Number(
                        button.dataset.watchItemUp
                    );

                    if (
                        !Number.isInteger(index)
                        || index <= 0
                        || index >= items.length
                    ) {
                        return;
                    }

                    [
                        items[index - 1],
                        items[index],
                    ] = [
                        items[index],
                        items[index - 1],
                    ];

                    items.forEach(
                        (item, itemIndex) => {
                            item.order = itemIndex;
                        }
                    );

                    setWatchItemsDirty(true);

                    renderWatchItemsInPlace(
                        items,
                        watchId,
                    );
                },
            );

        });

    document
        .querySelectorAll(
            "[data-watch-item-down]"
        )
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    const index = Number(
                        button.dataset.watchItemDown
                    );

                    if (
                        !Number.isInteger(index)
                        || index < 0
                        || index >= items.length - 1
                    ) {
                        return;
                    }

                    [
                        items[index],
                        items[index + 1],
                    ] = [
                        items[index + 1],
                        items[index],
                    ];

                    items.forEach(
                        (item, itemIndex) => {
                            item.order = itemIndex;
                        }
                    );

                    setWatchItemsDirty(true);

                    renderWatchItemsInPlace(
                        items,
                        watchId,
                    );
                },
            );

        });

    document
        .querySelectorAll(
            "[data-watch-item-remove]"
        )
        .forEach((button) => {

            button.addEventListener(
                "click",
                () => {

                    const index = Number(
                        button.dataset.watchItemRemove
                    );

                    if (
                        !Number.isInteger(index)
                        || index < 0
                        || index >= items.length
                    ) {
                        return;
                    }

                    items.splice(
                        index,
                        1
                    );

                    items.forEach(
                        (item, itemIndex) => {
                            item.order = itemIndex;
                        }
                    );

                    setWatchItemsDirty(true);

                    renderWatchItemsInPlace(
                        items,
                        watchId,
                    );
                },
            );

        });

    const addButton =
        document.getElementById(
            "add-from-supla-btn"
        );

    if (addButton) {
        addButton.addEventListener(
            "click",
            () => showAddFromSupla(
                items,
                watchId,
            ),
        );
    }

    const saveButton =
        document.getElementById(
            "save-watch-items-btn"
        );

    if (saveButton) {
        saveButton.addEventListener(
            "click",
            () => saveWatchItems(
                items,
                watchId,
            ),
        );
    }
}

async function showAddFromSupla(
    items,
    watchId,
) {

    const button =
        document.getElementById(
            "add-from-supla-btn"
        );

    const content =
        document.getElementById(
            "add-from-supla-content"
        );

    if (!button || !content) {
        return;
    }

    button.disabled = true;

    content.innerHTML = `
        <div class="text-muted small">
            ${t("loadingSuplaItems")}
        </div>
    `;

    try {

        const suplaItems =
            await getAvailableSuplaItems();

        const usedSuplaItems =
            new Set(
                items.map(
                    (item) =>
                        `${item.type}:${item.supla_id}`
                )
            );

        const availableItems =
            suplaItems.filter(
                (item) =>
                    !usedSuplaItems.has(
                        `${item.type}:${item.supla_id}`
                    )
            );

        if (!availableItems.length) {

            content.innerHTML = `
                <div class="alert alert-info mb-0">
                    ${t("noAdditionalSuplaItems")}
                </div>
            `;

            return;
        }

        const groups = [
            {
                label: t("gates"),
                items: availableItems.filter(
                    (item) => item.type === "gate"
                ),
            },
            {
                label: t("scenes"),
                items: availableItems.filter(
                    (item) => item.type === "scene"
                ),
            },
            {
                label: t("otherDevices"),
                items: availableItems.filter(
                    (item) =>
                        item.type !== "gate"
                        && item.type !== "scene"
                ),
            },
        ];

        const options =
            groups
                .filter(
                    (group) => group.items.length
                )
                .map((group) => `
                    <optgroup label="${group.label}">
                        ${
                            group.items
                                .map((item) => `
                                    <option
                                        value="${item.type}:${item.supla_id}"
                                    >
                                        ${item.name} (${formatItemType(item.type)})
                                    </option>
                                `)
                                .join("")
                        }
                    </optgroup>
                `)
                .join("");

        content.innerHTML = `
            <div class="border rounded-4 p-3">

                <label
                    class="form-label fw-semibold"
                    for="supla-item-select"
                >
                    ${t("suplaItem")}
                </label>

                <div class="d-flex gap-2">

                    <select
                        class="form-select"
                        id="supla-item-select"
                    >
                        ${options}
                    </select>

                    <button
                        type="button"
                        class="btn btn-primary"
                        id="confirm-add-supla-item-btn"
                    >
                        ${t("add")}
                    </button>

                </div>

            </div>
        `;

        document
            .getElementById(
                "confirm-add-supla-item-btn"
            )
            .addEventListener(
                "click",
                () => addSuplaItemLocally(
                    items,
                    availableItems,
                    watchId,
                ),
            );

    } catch (error) {

        content.innerHTML = `
            <div class="alert alert-danger mb-0">
                ${t("unableToLoadSuplaItems")}
            </div>
        `;

    } finally {
        button.disabled = false;
    }
}

function addSuplaItemLocally(
    items,
    availableItems,
    watchId,
) {

    const select =
        document.getElementById(
            "supla-item-select"
        );

    if (!select) {
        return;
    }

    const [
        itemType,
        suplaIdValue,
    ] = select.value.split(":");

    const suplaId =
        Number(suplaIdValue);

    const suplaItem =
        availableItems.find(
            (item) =>
                item.type === itemType
                && item.supla_id === suplaId
        );

    if (!suplaItem) {
        return;
    }

    const newItem = {
        id: crypto.randomUUID(),
        type: suplaItem.type,
        name: suplaItem.name,
        icon: getDefaultWatchItemIcon(
            suplaItem.type
        ),
        supla_id: suplaItem.supla_id,
        order: items.length,
        confirmation_required: true,
        status_enabled:
            suplaItem.sensor_channel_id !== null,
        sensor_channel_id:
            suplaItem.sensor_channel_id,
        enabled: true,
    };

    items.push(newItem);

    setWatchItemsDirty(true);

    renderWatchItemsInPlace(
        items,
        watchId,
    );
}

function renderWatchItemsInPlace(
    items,
    watchId,
) {

    const current =
        document.getElementById(
            "watch-items-section"
        );

    if (!current) {
        return;
    }

    const wrapper =
        document.createElement("div");

    wrapper.innerHTML =
        renderWatchItems(items);

    const replacement =
        wrapper.firstElementChild;

    current.replaceWith(
        replacement
    );

    bindWatchItemEditors();
    bindWatchItemActions(
        items,
        watchId,
    );
}

async function saveWatchItems(
    items,
    watchId,
) {

    const button =
        document.getElementById(
            "save-watch-items-btn"
        );

    const status =
        document.getElementById(
            "watch-items-save-status"
        );

    if (!button || !status) {
        return;
    }

    const rows = [
        ...document.querySelectorAll(
            "[data-watch-item-index]"
        ),
    ];

    const updatedItems = rows.map((row) => {

        const index = Number(
            row.dataset.watchItemIndex
        );

        const original = items[index];

        const icon =
            row.querySelector(
                "[data-watch-item-icon]"
            ).value;

        const enabled =
            row.querySelector(
                "[data-watch-item-enabled]"
            ).checked;

        const confirmationRequired =
            row.querySelector(
                "[data-watch-item-confirmation]"
            ).checked;

        return {
            ...original,
            icon: icon,
            enabled: enabled,
            confirmation_required:
                confirmationRequired,
        };
    });

    button.disabled = true;

    status.textContent = t("saving");
    status.className =
        "small text-muted";

    try {

        const savedItems =
            await updateWatchItemsById(
                watchId,
                updatedItems,
            );

        items.splice(
            0,
            items.length,
            ...savedItems
        );

        setWatchItemsDirty(false);

        status.textContent = t("saved");
        status.className =
            "small text-success";

    } catch (error) {

        console.error(
            "Unable to save watch configuration:",
            error,
        );

        status.textContent =
            t("unableToSaveConfiguration");

        status.className =
            "small text-danger";

    } finally {
        button.disabled = !watchItemsDirty;
    }
}

function bindWatchNameEditor(watch) {

    const nameElement =
        document.getElementById(
            "watch-name"
        );

    const renameButton =
        document.getElementById(
            "rename-watch-btn"
        );

    const form =
        document.getElementById(
            "rename-watch-form"
        );

    const input =
        document.getElementById(
            "watch-name-input"
        );

    const saveButton =
        document.getElementById(
            "save-watch-name-btn"
        );

    const cancelButton =
        document.getElementById(
            "cancel-watch-name-btn"
        );

    const errorBox =
        document.getElementById(
            "watch-name-error"
        );

    if (
        !nameElement
        || !renameButton
        || !form
        || !input
        || !saveButton
        || !cancelButton
        || !errorBox
    ) {
        return;
    }

    nameElement.textContent =
        watch.name ?? "";

    input.value =
        watch.name ?? "";

    renameButton.addEventListener(
        "click",
        () => {

            input.value =
                watch.name ?? "";

            errorBox.textContent = "";
            errorBox.classList.add(
                "d-none"
            );

            form.classList.remove(
                "d-none"
            );

            renameButton.classList.add(
                "d-none"
            );

            input.focus();
            input.select();
        },
    );

    cancelButton.addEventListener(
        "click",
        () => {

            input.value =
                watch.name ?? "";

            errorBox.textContent = "";
            errorBox.classList.add(
                "d-none"
            );

            form.classList.add(
                "d-none"
            );

            renameButton.classList.remove(
                "d-none"
            );
        },
    );

    form.addEventListener(
        "submit",
        async (event) => {

            event.preventDefault();

            const name =
                input.value.trim();

            errorBox.textContent = "";
            errorBox.classList.add(
                "d-none"
            );

            if (
                !name
                || name.length > 50
            ) {
                errorBox.textContent =
                    t("invalidWatchName");

                errorBox.classList.remove(
                    "d-none"
                );

                return;
            }

            saveButton.disabled = true;
            cancelButton.disabled = true;
            input.disabled = true;

            try {

                const updatedWatch =
                    await updateWatchNameById(
                        watch.id,
                        name,
                    );

                watch.name =
                    updatedWatch.name;

                updateWatchSelectorCard(
                    watch
                );

                nameElement.textContent =
                    updatedWatch.name;

                input.value =
                    updatedWatch.name;

                form.classList.add(
                    "d-none"
                );

                renameButton.classList.remove(
                    "d-none"
                );

            } catch (error) {

                console.error(
                    "Unable to rename Garmin watch:",
                    error,
                );

                errorBox.textContent =
                    error instanceof ApiError
                    && error.status === 422
                        ? t("invalidWatchName")
                        : t("unableToRenameWatch");

                errorBox.classList.remove(
                    "d-none"
                );

            } finally {

                saveButton.disabled = false;
                cancelButton.disabled = false;
                input.disabled = false;
            }
        },
    );
}

function bindWatchApplicationLanguage(watch) {

    const select =
        document.getElementById(
            "watch-application-language-select"
        );

    const status =
        document.getElementById(
            "watch-application-language-status"
        );

    if (!select || !status || !watch.id) {
        return;
    }

    let currentLanguage =
        watch.application_language
        ?? "auto";

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

            status.textContent =
                t("saving");

            status.className =
                "small text-muted mt-1";

            try {

                const updatedWatch =
                    await updateWatchApplicationLanguageById(
                        watch.id,
                        nextLanguage,
                    );

                currentLanguage =
                    updatedWatch.application_language
                    ?? "auto";

                watch.application_language =
                    currentLanguage;

                select.value =
                    currentLanguage;

                status.textContent =
                    t("saved");

                status.className =
                    "small text-success mt-1";

            } catch (error) {

                console.error(
                    "Unable to save watch application language:",
                    error,
                );

                select.value =
                    currentLanguage;

                status.textContent =
                    t("unableToSaveWatchLanguage");

                status.className =
                    "small text-danger mt-1";

            } finally {

                select.disabled = false;
            }
        },
    );
}

function bindWatchDetailsToggle() {

    const button =
        document.getElementById(
            "watch-details-toggle"
        );

    const details =
        document.getElementById(
            "watch-details"
        );

    if (!button || !details) {
        return;
    }

    button.addEventListener(
        "click",
        () => {

            const isHidden =
                details.classList.contains(
                    "d-none"
                );

            details.classList.toggle(
                "d-none",
                !isHidden,
            );

            button.setAttribute(
                "aria-expanded",
                isHidden
                    ? "true"
                    : "false",
            );

            const label =
                button.querySelector(
                    "[data-watch-details-label]"
                );

            if (label) {
                label.textContent =
                    isHidden
                        ? t("hideDetails")
                        : t("details");
            }
        },
    );
}

function renderWatch(
    watch,
    items = [],
) {

    const content =
        document.getElementById("watch-content");

    if (!watch.configured) {

        content.innerHTML = `
            <div class="text-center py-3">

                <i class="bi bi-smartwatch fs-1 text-muted"></i>

                <p class="mt-3 mb-3 text-muted">
                    ${t("noWatchConfigured")}
                </p>

                <button
                    type="button"
                    class="btn btn-primary"
                    id="configure-watch-btn"
                >
                    <i class="bi bi-plus-circle me-2"></i>
                    ${t("configureWatch")}
                </button>

            </div>
        `;

        document
            .getElementById("configure-watch-btn")
            .addEventListener(
                "click",
                renderPairingForm,
            );

        return;
    }

    const statusClass =
        watch.enabled
            ? "text-bg-success"
            : "text-bg-secondary";

    const statusText =
        watch.enabled
            ? t("enabled")
            : t("disabled");

    content.innerHTML = `
        <div>

            <div
                class="
                    d-flex
                    flex-wrap
                    align-items-center
                    gap-2
                "
            >
                <h4 class="mb-0">
                    <span id="watch-name"></span>
                </h4>

                <button
                    type="button"
                    class="btn btn-sm btn-outline-secondary"
                    id="rename-watch-btn"
                >
                    <i class="bi bi-pencil me-1"></i>
                    ${t("renameWatch")}
                </button>
            </div>

            <div class="mt-2">
                <span class="badge ${statusClass}">
                    ${statusText}
                </span>
            </div>

            <form
                id="rename-watch-form"
                class="d-none mt-3"
                style="max-width: 520px;"
            >
                <label
                    for="watch-name-input"
                    class="form-label fw-semibold"
                >
                    ${t("watchName")}
                </label>

                <div
                    class="
                        d-flex
                        flex-column
                        flex-sm-row
                        gap-2
                    "
                >
                    <input
                        type="text"
                        class="form-control"
                        id="watch-name-input"
                        maxlength="50"
                    >

                    <button
                        type="submit"
                        class="btn btn-primary"
                        id="save-watch-name-btn"
                    >
                        ${t("save")}
                    </button>

                    <button
                        type="button"
                        class="btn btn-outline-secondary"
                        id="cancel-watch-name-btn"
                    >
                        ${t("cancel")}
                    </button>
                </div>

                <div
                    id="watch-name-error"
                    class="small text-danger mt-2 d-none"
                ></div>
            </form>

        </div>

        <div class="row g-3 mt-3 align-items-end">

            <div class="col-12 col-md-6 col-xl-4">
                <label
                    for="watch-application-language-select"
                    class="small text-muted d-block mb-1"
                >
                    ${t("applicationLanguage")}
                </label>

                <select
                    class="form-select form-select-sm"
                    id="watch-application-language-select"
                    style="max-width: 220px;"
                >
                    <option value="auto">
                        ${t("automaticLanguage")}
                    </option>

                    <option value="pl">
                        ${t("polish")}
                    </option>

                    <option value="en">
                        ${t("english")}
                    </option>
                </select>

                <div
                    id="watch-application-language-status"
                    class="small mt-1"
                ></div>
            </div>

            <div class="col-12 col-md-auto">
                <button
                    type="button"
                    class="btn btn-outline-secondary"
                    id="watch-details-toggle"
                    aria-expanded="false"
                    aria-controls="watch-details"
                >
                    <i class="bi bi-info-circle me-1"></i>
                    <span data-watch-details-label>
                        ${t("details")}
                    </span>
                </button>
            </div>

        </div>

        <div
            id="watch-details"
            class="d-none border rounded-4 p-3 mt-3"
        >
            <div class="row g-3">

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("deviceModel")}
                    </small>

                    <strong>
                        ${formatMetadataValue(
                            watch.device_model
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("partNumber")}
                    </small>

                    <strong>
                        ${formatMetadataValue(
                            watch.part_number
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("deviceId")}
                    </small>

                    <strong class="text-break">
                        ${formatMetadataValue(
                            watch.device_id
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("firmwareVersion")}
                    </small>

                    <strong>
                        ${formatMetadataValue(
                            watch.firmware_version
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("connectIqVersion")}
                    </small>

                    <strong>
                        ${formatMetadataValue(
                            watch.connect_iq_version
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("garminSuplaVersion")}
                    </small>

                    <strong>
                        ${formatMetadataValue(
                            watch.app_version
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("systemLanguage")}
                    </small>

                    <strong>
                        ${formatSystemLanguage(
                            watch.system_language
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("created")}
                    </small>

                    <strong>
                        ${formatDate(
                            watch.created_at
                        )}
                    </strong>
                </div>

                <div class="col-12 col-md-6 col-xl-4">
                    <small class="text-muted d-block">
                        ${t("lastSeen")}
                    </small>

                    <strong>
                        ${formatDate(
                            watch.last_seen_at
                        )}
                    </strong>
                </div>

            </div>
        </div>

        ${renderWatchItems(items)}

        <div class="border-top pt-3 mt-2">

            <div class="d-flex flex-wrap gap-2">

                <button
                    type="button"
                    class="btn btn-outline-primary"
                    id="replace-watch-btn"
                    ${watchItemsDirty ? "disabled" : ""}
                >
                    <i class="bi bi-arrow-repeat me-2"></i>
                    ${t("replaceWatch")}
                </button>

                <button
                    type="button"
                    class="btn btn-outline-danger"
                    id="reset-watch-pairing-btn"
                    ${watchItemsDirty ? "disabled" : ""}
                >
                    <i class="bi bi-link-45deg me-2"></i>
                    ${t("rePairCurrentWatch")}
                </button>

                <button
                    type="button"
                    class="btn btn-outline-danger"
                    id="delete-watch-btn"
                    ${watchItemsDirty ? "disabled" : ""}
                >
                    <i class="bi bi-trash me-2"></i>
                    ${t("deleteWatch")}
                </button>

            </div>

            <p class="small text-muted mt-2 mb-0">
                ${t("watchReplacementInfo")}
            </p>

        </div>
    `;

    document
        .getElementById("replace-watch-btn")
        .addEventListener(
            "click",
            () => renderPairingForm(
                true,
                watch.id,
            ),
        );

    document
        .getElementById("reset-watch-pairing-btn")
        .addEventListener(
            "click",
            () => handleWatchRePair(
                watch.id
            ),
        );

    document
        .getElementById("delete-watch-btn")
        .addEventListener(
            "click",
            () => handleWatchDelete(
                watch.id
            ),
        );

    bindWatchNameEditor(watch);
    bindWatchApplicationLanguage(watch);
    bindWatchDetailsToggle();
    bindWatchItemEditors();
    bindWatchItemActions(
        items,
        watch.id,
    );

}

async function handleWatchDelete(
    watchId,
) {

    const confirmed = window.confirm(
        t("deleteWatchConfirmation")
    );

    if (!confirmed) {
        return;
    }

    const button =
        document.getElementById(
            "delete-watch-btn"
        );

    if (button) {
        button.disabled = true;
    }

    try {

        await deleteWatchById(
            watchId
        );

        window.location.reload();

    } catch (error) {

        console.error(
            "Unable to delete Garmin watch:",
            error,
        );

        if (button) {
            button.disabled = false;
        }

        showError(
            t("unableToDeleteWatch")
        );
    }
}

async function handleWatchRePair(
    watchId,
) {

    const confirmed = window.confirm(
        t("rePairConfirmation")
    );

    if (!confirmed) {
        return;
    }

    const button =
        document.getElementById(
            "reset-watch-pairing-btn"
        );

    if (button) {
        button.disabled = true;
    }

    try {

        await startWatchRePair(
            watchId
        );

        setWatchItemsDirty(false);

        const selectorContainer =
            document.getElementById(
                "watch-selector-container"
            );

        if (selectorContainer) {
            selectorContainer.classList.add(
                "d-none"
            );
        }

        renderPairingForm(
            false,
            watchId,
        );

    } catch (error) {

        console.error(
            "Unable to start watch re-pairing:",
            error,
        );

        showError(
            t("unableToResetWatchPairing")
        );

    }
}

function renderPairingForm(
    allowCancel = true,
    targetWatchId = null,
    copySourceWatches = [],
) {

    const content =
        document.getElementById("watch-content");

    content.innerHTML = `
        <div class="mx-auto" style="max-width: 420px;">

            <div class="text-center mb-4">
                <i class="bi bi-smartwatch fs-1 text-primary"></i>

                <h4 class="mt-3 mb-2">
                    ${t("pairGarminWatch")}
                </h4>

                <p class="text-muted mb-0">
                    ${t("pairingInstructions")}
                </p>
            </div>

            <form id="pair-watch-form">

                <div class="mb-3">
                    <label
                        for="pairing-code"
                        class="form-label fw-semibold"
                    >
                        ${t("pairingCode")}
                    </label>

                    <input
                        type="text"
                        class="form-control form-control-lg text-center"
                        id="pairing-code"
                        inputmode="numeric"
                        autocomplete="one-time-code"
                        maxlength="6"
                        pattern="[0-9]{6}"
                        placeholder="000000"
                        required
                        autofocus
                    >
                </div>

                ${
                    targetWatchId === null
                    && copySourceWatches.length
                        ? `
                            <div class="mb-3">
                                <label
                                    for="copy-watch-config"
                                    class="form-label fw-semibold"
                                >
                                    ${t(
                                        "copyWatchConfiguration"
                                    )}
                                </label>

                                <select
                                    class="form-select"
                                    id="copy-watch-config"
                                >
                                    <option value="">
                                        ${t(
                                            "emptyWatchConfiguration"
                                        )}
                                    </option>
                                </select>
                            </div>
                        `
                        : ""
                }

                <div
                    id="pairing-error"
                    class="alert alert-danger d-none"
                ></div>

                <div class="d-grid gap-2">
                    <button
                        type="submit"
                        class="btn btn-primary btn-lg"
                        id="pair-watch-btn"
                    >
                        <i class="bi bi-link-45deg me-2"></i>
                        ${t("pairWatch")}
                    </button>

                    ${allowCancel ? `
                        <button
                            type="button"
                            class="btn btn-outline-secondary"
                            id="cancel-pairing-btn"
                        >
                            ${t("cancel")}
                        </button>
                    ` : ""}
                </div>

            </form>

        </div>
    `;

    const form =
        document.getElementById(
            "pair-watch-form"
        );

    form.dataset.watchId =
        targetWatchId ?? "";

    const copySelector =
        document.getElementById(
            "copy-watch-config"
        );

    if (copySelector) {
        for (
            const watch
            of copySourceWatches
        ) {
            const option =
                document.createElement(
                    "option"
                );

            option.value = watch.id;

            option.textContent =
                getWatchSelectorLabel(
                    watch
                );

            copySelector.append(
                option
            );
        }
    }

    form.addEventListener(
        "submit",
        handlePairingSubmit,
    );

    const cancelButton =
        document.getElementById(
            "cancel-pairing-btn"
        );

    if (cancelButton) {
        cancelButton.addEventListener(
            "click",
            () => window.location.reload(),
        );
    }
}

async function handlePairingSubmit(event) {

    event.preventDefault();

    const targetWatchId =
        event.currentTarget.dataset.watchId
        || null;

    const copySelector =
        document.getElementById(
            "copy-watch-config"
        );

    const copyFromWatchId =
        targetWatchId === null
        && copySelector
        && copySelector.value
            ? copySelector.value
            : null;

    const input =
        document.getElementById("pairing-code");

    const button =
        document.getElementById("pair-watch-btn");

    const errorBox =
        document.getElementById("pairing-error");

    const code = input.value.trim();

    errorBox.classList.add("d-none");

    if (!/^\d{6}$/.test(code)) {
        errorBox.textContent =
            t("invalidPairingCode");

        errorBox.classList.remove("d-none");
        return;
    }

    button.disabled = true;

    try {

        const existingWatches =
            await getWatchStatuses();

        const existingWatchIds =
            new Set(
                existingWatches
                    .map(
                        (watch) => watch.id
                    )
                    .filter(Boolean)
            );

        const targetWatch =
            targetWatchId === null
                ? null
                : existingWatches.find(
                    (watch) =>
                        watch.id
                        === targetWatchId
                );

        const targetLastSeenAt =
            targetWatch?.last_seen_at
            ?? null;

        const targetCredentialRevision =
            targetWatch?.credential_revision
            ?? null;

        await approveWatchPairing(
            code,
            targetWatchId,
            copyFromWatchId,
        );

        renderPairingApproved(
            existingWatchIds,
            targetWatchId,
            targetLastSeenAt,
            targetCredentialRevision,
        );

    } catch (error) {

        if (error instanceof ApiError) {

            if (error.status === 404) {
                errorBox.textContent =
                    t("pairingCodeNotFound");
            } else {
                errorBox.textContent =
                    t("unableToPairWatch");
            }

        } else {
            errorBox.textContent =
                t("unableToPairWatch");
        }

        errorBox.classList.remove("d-none");
        button.disabled = false;
    }
}

function renderPairingApproved(
    existingWatchIds,
    targetWatchId = null,
    targetLastSeenAt = null,
    targetCredentialRevision = null,
) {

    const content =
        document.getElementById("watch-content");

    content.innerHTML = `
        <div class="text-center py-3">

            <i
                class="bi bi-check-circle-fill
                       fs-1 text-success"
            ></i>

            <h4 class="mt-3">
                ${t("pairingApproved")}
            </h4>

            <p class="text-muted mb-0">
                ${t("completePairingOnWatch")}
            </p>

        </div>
    `;

    waitForWatchPairingCompletion(
        existingWatchIds,
        targetWatchId,
        targetLastSeenAt,
        targetCredentialRevision,
    );
}

async function waitForWatchPairingCompletion(
    existingWatchIds,
    targetWatchId = null,
    targetLastSeenAt = null,
    targetCredentialRevision = null,
) {

    const maxAttempts = 30;
    const delayMs = 2000;

    for (
        let attempt = 0;
        attempt < maxAttempts;
        attempt += 1
    ) {

        await new Promise(
            (resolve) =>
                setTimeout(
                    resolve,
                    delayMs,
                ),
        );

        try {

            const watches =
                await getWatchStatuses();

            const watch =
                targetWatchId === null
                    ? watches.find(
                        (candidate) =>
                            candidate.configured
                            && candidate.id
                            && !existingWatchIds.has(
                                candidate.id
                            )
                    )
                    : watches.find(
                        (candidate) =>
                            candidate.configured
                            && candidate.id
                                === targetWatchId
                            && candidate.credential_revision
                                > targetCredentialRevision
                            && candidate.last_seen_at
                            && candidate.last_seen_at
                                !== targetLastSeenAt
                    );

            if (!watch) {
                continue;
            }

            await selectWatch(
                watch
            );

            renderWatchSelector(
                watches
            );

            return;

        } catch (error) {

            console.error(
                "Unable to check pairing status:",
                error,
            );

        }
    }
}

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
    const resolvedTheme =
        resolveUITheme(theme);

    document.documentElement.setAttribute(
        "data-bs-theme",
        resolvedTheme,
    );

}

async function initializeUIThemeSelector() {

    const select =
        document.getElementById(
            "ui-theme-select"
        );

    if (!select) {
        return;
    }

    try {

        const settings =
            await getUITheme();

        let currentTheme =
            settings.theme;

        select.value =
            currentTheme;

        applyUITheme(
            currentTheme
        );

        select.addEventListener(
            "change",
            async () => {

                const nextTheme =
                    select.value;

                if (
                    nextTheme
                    === currentTheme
                ) {
                    return;
                }

                select.disabled = true;

                try {

                    const saved =
                        await updateUITheme(
                            nextTheme
                        );

                    currentTheme =
                        saved.theme;

                    applyUITheme(
                        currentTheme
                    );

                    select.disabled = false;

                } catch (error) {

                    select.value =
                        currentTheme;

                    select.disabled = false;

                    console.error(
                        "Unable to save UI theme:",
                        error,
                    );

                }
            },
        );

        systemDarkTheme.addEventListener(
            "change",
            () => {
                if (currentTheme === "auto") {
                    applyUITheme(
                        currentTheme
                    );
                }
            },
        );

    } catch (error) {

        select.disabled = true;

        console.error(
            "Unable to load UI theme:",
            error,
        );

    }
}

function showError(message) {

    document.getElementById("watch-content").innerHTML = `
        <div class="alert alert-danger mb-0">
            ${message}
        </div>
    `;

}

function getWatchSelectorLabel(watch) {

    const name =
        watch.name
        ?? watch.device_model
        ?? watch.id;

    if (
        watch.device_model
        && watch.device_model !== name
    ) {
        return `${name} — ${watch.device_model}`;
    }

    return name;
}


function updateWatchSelectorCard(watch) {

    if (!watch.id) {
        return;
    }

    const card = [
        ...document.querySelectorAll(
            "[data-watch-selector-card]"
        ),
    ].find(
        (candidate) =>
            candidate.dataset.watchId
            === watch.id
    );

    if (!card) {
        return;
    }

    const label =
        card.querySelector(
            "[data-watch-selector-label]"
        );

    if (label) {
        label.textContent =
            getWatchSelectorLabel(watch);
    }
}


function showCopyWatchItemsForm(watches) {

    const container =
        document.getElementById(
            "watch-selector-container"
        );

    if (!container || watchItemsDirty) {
        return;
    }

    const targetWatch =
        watches.find(
            (watch) =>
                watch.id === selectedWatchId
        );

    if (!targetWatch) {
        return;
    }

    const sourceWatches =
        watches.filter(
            (watch) =>
                watch.configured
                && watch.id
                && watch.id !== targetWatch.id
        );

    if (!sourceWatches.length) {
        return;
    }

    const existingForm =
        document.getElementById(
            "copy-watch-items-form"
        );

    if (existingForm) {
        return;
    }

    const addWatchButton =
        document.getElementById(
            "add-watch-btn"
        );

    const copyWatchItemsButton =
        document.getElementById(
            "copy-watch-items-btn"
        );

    setWatchSelectorCardsDisabled(
        true
    );

    if (addWatchButton) {
        addWatchButton.disabled = true;
    }

    if (copyWatchItemsButton) {
        copyWatchItemsButton.disabled = true;
    }

    const form =
        document.createElement("div");

    form.id =
        "copy-watch-items-form";

    form.className =
        "border rounded-3 p-3 mt-2";

    const label =
        document.createElement("label");

    label.className =
        "form-label fw-semibold";

    label.htmlFor =
        "copy-watch-items-source";

    label.textContent =
        t("copyWatchItemsFrom");

    const controls =
        document.createElement("div");

    controls.className =
        "d-flex flex-column flex-sm-row gap-2";

    const sourceSelect =
        document.createElement("select");

    sourceSelect.id =
        "copy-watch-items-source";

    sourceSelect.className =
        "form-select";

    for (const watch of sourceWatches) {

        const option =
            document.createElement(
                "option"
            );

        option.value =
            watch.id;

        option.textContent =
            getWatchSelectorLabel(
                watch
            );

        sourceSelect.append(
            option
        );
    }

    const confirmButton =
        document.createElement(
            "button"
        );

    confirmButton.type =
        "button";

    confirmButton.id =
        "confirm-copy-watch-items-btn";

    confirmButton.className =
        "btn btn-primary flex-shrink-0";

    confirmButton.textContent =
        t("copyWatchItems");

    const cancelButton =
        document.createElement(
            "button"
        );

    cancelButton.type =
        "button";

    cancelButton.className =
        "btn btn-outline-secondary flex-shrink-0";

    cancelButton.textContent =
        t("cancel");

    const errorBox =
        document.createElement("div");

    errorBox.className =
        "small text-danger mt-2 d-none";

    controls.append(
        sourceSelect,
        confirmButton,
        cancelButton,
    );

    form.append(
        label,
        controls,
        errorBox,
    );

    container.append(
        form
    );

    const restoreSelectorControls = () => {

        setWatchSelectorCardsDisabled(
            watchItemsDirty
        );

        if (addWatchButton) {
            addWatchButton.disabled =
                watchItemsDirty;
        }

        if (copyWatchItemsButton) {
            copyWatchItemsButton.disabled =
                watchItemsDirty;
        }
    };

    cancelButton.addEventListener(
        "click",
        () => {

            form.remove();

            restoreSelectorControls();
        },
    );

    confirmButton.addEventListener(
        "click",
        async () => {

            const sourceWatch =
                sourceWatches.find(
                    (watch) =>
                        watch.id
                        === sourceSelect.value
                );

            if (!sourceWatch) {
                return;
            }

            const confirmed =
                window.confirm(
                    `${t(
                        "copyWatchItemsConfirmation"
                    )}\n\n`
                    + `${getWatchSelectorLabel(
                        sourceWatch
                    )} → `
                    + `${getWatchSelectorLabel(
                        targetWatch
                    )}`
                );

            if (!confirmed) {
                return;
            }

            sourceSelect.disabled = true;
            confirmButton.disabled = true;
            cancelButton.disabled = true;

            errorBox.classList.add(
                "d-none"
            );

            try {

                const copiedItems =
                    await copyWatchItemsById(
                        targetWatch.id,
                        sourceWatch.id,
                    );

                form.remove();

                setWatchItemsDirty(false);

                renderWatch(
                    targetWatch,
                    copiedItems,
                );

                restoreSelectorControls();

            } catch (error) {

                console.error(
                    "Unable to copy Watch items:",
                    error,
                );

                errorBox.textContent =
                    t(
                        "unableToCopyWatchItems"
                    );

                errorBox.classList.remove(
                    "d-none"
                );

                sourceSelect.disabled =
                    watchItemsDirty;

                confirmButton.disabled =
                    watchItemsDirty;

                cancelButton.disabled =
                    false;
            }
        },
    );
}


function renderWatchSelector(watches) {

    const container =
        document.getElementById(
            "watch-selector-container"
        );

    if (!container) {
        return;
    }

    container.replaceChildren();

    const selectableWatches =
        watches.filter(
            (watch) =>
                watch.configured
                && watch.id
        );

    if (!selectableWatches.length) {
        container.classList.add(
            "d-none"
        );

        return;
    }

    const label =
        document.createElement("div");

    label.className =
        "form-label fw-semibold";

    label.textContent =
        t("selectWatch");

    const cards =
        document.createElement("div");

    cards.id =
        "watch-selector-cards";

    cards.className =
        "row g-2";

    for (const watch of selectableWatches) {

        const isSelected =
            watch.id === selectedWatchId;

        const column =
            document.createElement(
                "div"
            );

        column.className =
            "col-12 col-md-6 col-xl-4";

        const card =
            document.createElement(
                "button"
            );

        card.type =
            "button";

        card.dataset.watchSelectorCard =
            "";

        card.dataset.watchId =
            watch.id;

        card.className = [
            "btn",
            "w-100",
            "h-100",
            "text-start",
            "p-3",
            isSelected
                ? "btn-primary"
                : "btn-outline-secondary",
        ].join(" ");

        card.disabled =
            watchItemsDirty;

        card.setAttribute(
            "aria-pressed",
            isSelected
                ? "true"
                : "false",
        );

        const layout =
            document.createElement(
                "div"
            );

        layout.className =
            "d-flex align-items-center gap-3";

        const icon =
            document.createElement("i");

        icon.className =
            "bi bi-smartwatch fs-4 flex-shrink-0";

        const text =
            document.createElement(
                "div"
            );

        text.className =
            "min-w-0";

        const watchLabel =
            document.createElement(
                "div"
            );

        watchLabel.dataset.watchSelectorLabel =
            "";

        watchLabel.className =
            "fw-semibold text-break";

        watchLabel.textContent =
            getWatchSelectorLabel(
                watch
            );

        const status =
            document.createElement(
                "div"
            );

        status.className =
            "small opacity-75 mt-1";

        status.textContent =
            watch.enabled
                ? t("enabled")
                : t("disabled");

        text.append(
            watchLabel,
            status,
        );

        layout.append(
            icon,
            text,
        );

        card.append(
            layout
        );

        card.addEventListener(
            "click",
            async () => {

                if (
                    watchItemsDirty
                    || watch.id
                        === selectedWatchId
                ) {
                    return;
                }

                setWatchSelectorCardsDisabled(
                    true
                );

                try {

                    await selectWatch(
                        watch
                    );

                    renderWatchSelector(
                        watches
                    );

                } catch (error) {

                    console.error(
                        "Unable to select Garmin watch:",
                        error,
                    );

                    showError(
                        t(
                            "unableToLoadWatchConfiguration"
                        )
                    );

                } finally {

                    setWatchSelectorCardsDisabled(
                        watchItemsDirty
                    );
                }
            },
        );

        column.append(
            card
        );

        cards.append(
            column
        );
    }

    const controls =
        document.createElement(
            "div"
        );

    controls.className =
        "d-flex flex-column flex-sm-row gap-2 mt-3";

    const addButton =
        document.createElement(
            "button"
        );

    addButton.type =
        "button";

    addButton.id =
        "add-watch-btn";

    addButton.className =
        "btn btn-outline-primary flex-shrink-0";

    addButton.innerHTML = `
        <i class="bi bi-plus-circle me-1"></i>
        ${t("addWatch")}
    `;

    addButton.disabled =
        watchItemsDirty;

    addButton.addEventListener(
        "click",
        () => renderPairingForm(
            true,
            null,
            selectableWatches,
        ),
    );

    controls.append(
        addButton
    );

    if (selectableWatches.length > 1) {

        const copyButton =
            document.createElement(
                "button"
            );

        copyButton.type =
            "button";

        copyButton.id =
            "copy-watch-items-btn";

        copyButton.className =
            "btn btn-outline-secondary flex-shrink-0";

        copyButton.innerHTML = `
            <i class="bi bi-copy me-1"></i>
            ${t("copyWatchItems")}
        `;

        copyButton.disabled =
            watchItemsDirty;

        copyButton.addEventListener(
            "click",
            () => showCopyWatchItemsForm(
                selectableWatches
            ),
        );

        controls.append(
            copyButton
        );
    }

    container.append(
        label,
        cards,
        controls,
    );

    container.classList.remove(
        "d-none"
    );
}


async function selectWatch(watch) {

    const nextWatchId =
        watch.configured
            ? watch.id
            : null;

    const items =
        nextWatchId !== null
            ? await getWatchItemsById(
                nextWatchId
            )
            : [];

    selectedWatchId =
        nextWatchId;

    setWatchItemsDirty(false);

    renderWatch(
        watch,
        items,
    );
}


document.addEventListener("DOMContentLoaded", async () => {

    initializeUILanguageSelector();
    initializeUIThemeSelector();

    try {

        const watches =
            await getWatchStatuses();

        const watch =
            watches.length
                ? watches[watches.length - 1]
                : {
                    configured: false,
                };

        await selectWatch(
            watch
        );

        renderWatchSelector(
            watches
        );

    } catch (error) {

        console.error(
            "Unable to load watch configuration:",
            error,
        );

        showError(
            t("unableToLoadWatchConfiguration")
        );

    }

});
