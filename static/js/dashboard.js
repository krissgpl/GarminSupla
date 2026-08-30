import {
    ApiError,
    approveWatchPairing,
    getAvailableSuplaItems,
    getUILanguage,
    getWatchItems,
    getWatchStatus,
    resetWatchPairing,
    updateUILanguage,
    updateWatchItems,
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
    },

    pl: {
        never: "Nigdy",
        enabled: "Włączony",
        disabled: "Wyłączony",
        created: "Utworzono",
        lastSeen: "Ostatnia aktywność",
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

function setWatchItemsDirty(dirty) {
    watchItemsDirty = dirty;

    const button =
        document.getElementById(
            "save-watch-items-btn"
        );

    if (button) {
        button.disabled = !dirty;
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

function formatConfirmation(value) {
    return value
        ? "Required"
        : "Not required";
}

function renderWatchItemIcon(icon) {

    if (icon === "sliding_gate") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Sliding gate"
                class="text-body"
            >
                <g
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- posts -->
                    <line x1="6" y1="5" x2="6" y2="35" />
                    <line x1="58" y1="5" x2="58" y2="35" />

                    <!-- rail -->
                    <line x1="2" y1="34" x2="62" y2="34" />

                    <!-- closed sliding leaf -->
                    <rect
                        x="10"
                        y="9"
                        width="44"
                        height="20"
                    />

                    <line x1="21" y1="9" x2="21" y2="29" />
                    <line x1="32" y1="9" x2="32" y2="29" />
                    <line x1="43" y1="9" x2="43" y2="29" />
                </g>
            </svg>
        `;
    }

    if (icon === "double_swing_gate") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Double swing gate"
                class="text-body"
            >
                <g
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- posts -->
                    <line x1="6" y1="5" x2="6" y2="35" />
                    <line x1="58" y1="5" x2="58" y2="35" />

                    <!-- left leaf -->
                    <rect
                        x="10"
                        y="9"
                        width="22"
                        height="20"
                    />

                    <!-- right leaf -->
                    <rect
                        x="32"
                        y="9"
                        width="22"
                        height="20"
                    />
                </g>
            </svg>
        `;
    }

    if (icon === "garage_gate") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Garage gate"
                class="text-body"
            >
                <g
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- garage outline -->
                    <path
                        d="
                            M14 34
                            L14 15
                            L32 5
                            L50 15
                            L50 34
                            Z
                        "
                    />

                    <!-- garage door -->
                    <rect
                        x="19"
                        y="16"
                        width="26"
                        height="18"
                        rx="1"
                    />

                    <!-- sectional panels -->
                    <line x1="19" y1="21" x2="45" y2="21" />
                    <line x1="19" y1="26" x2="45" y2="26" />
                    <line x1="19" y1="31" x2="45" y2="31" />

                    <!-- handle -->
                    <line x1="29" y1="33" x2="35" y2="33" />
                </g>
            </svg>
        `;
    }

    if (icon === "scene") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Scene"
                class="text-body"
            >
                <g
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- clapper top -->
                    <path
                        d="
                            M19 8
                            L45 5
                            L47 11
                            L21 14
                            Z
                        "
                    />

                    <!-- clapper stripes -->
                    <line x1="25" y1="7" x2="29" y2="13" />
                    <line x1="34" y1="6" x2="38" y2="12" />
                    <line x1="43" y1="5" x2="46" y2="10" />

                    <!-- board -->
                    <rect
                        x="19"
                        y="15"
                        width="28"
                        height="19"
                        rx="2"
                    />

                    <!-- play symbol -->
                    <path
                        d="
                            M29 21
                            L38 25
                            L29 29
                            Z
                        "
                    />
                </g>
            </svg>
        `;
    }

    if (icon === "light") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Light"
                class="text-body"
            >
                <g
                    transform="translate(0 3)"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- bulb -->
                    <path
                        d="
                            M24 19
                            C20 16 19 13 19 10
                            C19 3 24 -1 32 -1
                            C40 -1 45 3 45 10
                            C45 13 44 16 40 19
                            C38 21 37 23 37 26
                            L27 26
                            C27 23 26 21 24 19
                        "
                    />

                    <!-- filament -->
                    <path d="M28 13 L32 19 L36 13" />

                    <!-- base -->
                    <line x1="27" y1="29" x2="37" y2="29" />
                    <line x1="28" y1="32" x2="36" y2="32" />
                    <line x1="30" y1="35" x2="34" y2="35" />
                </g>
            </svg>
        `;
    }

    if (icon === "switch") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Switch"
                class="text-body"
            >
                <g
                    transform="translate(0 1)"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- square outer plate -->
                    <rect
                        x="21"
                        y="3"
                        width="22"
                        height="32"
                        rx="3"
                    />

                    <!-- rocker -->
                    <rect
                        x="26"
                        y="8"
                        width="12"
                        height="21"
                        rx="1.5"
                    />

                    <!-- ON mark -->
                    <line
                        x1="32"
                        y1="11"
                        x2="32"
                        y2="16"
                    />

                    <!-- OFF mark -->
                    <circle
                        cx="32"
                        cy="24"
                        r="2"
                    />

                    <!-- screws -->
                    <circle
                        cx="24"
                        cy="6"
                        r="1"
                    />

                    <circle
                        cx="40"
                        cy="32"
                        r="1"
                    />
                </g>
            </svg>
        `;
    }

    if (icon === "roller_shutter") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Roller shutter"
                class="text-body"
            >
                <g
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- frame -->
                    <rect
                        x="18"
                        y="4"
                        width="28"
                        height="31"
                        rx="2"
                    />

                    <!-- top housing -->
                    <rect
                        x="20"
                        y="6"
                        width="24"
                        height="5"
                        rx="1"
                    />

                    <!-- shutter slats -->
                    <line x1="21" y1="14" x2="43" y2="14" />
                    <line x1="21" y1="18" x2="43" y2="18" />
                    <line x1="21" y1="22" x2="43" y2="22" />
                    <line x1="21" y1="26" x2="43" y2="26" />
                    <line x1="21" y1="30" x2="43" y2="30" />

                    <!-- bottom handle -->
                    <line x1="29" y1="32" x2="35" y2="32" />
                </g>
            </svg>
        `;
    }

    if (icon === "awning") {
        return `
            <svg
                width="64"
                height="40"
                viewBox="0 0 64 40"
                role="img"
                aria-label="Awning"
                class="text-body"
            >
                <g
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                >
                    <!-- cassette -->
                    <rect
                        x="18"
                        y="5"
                        width="28"
                        height="6"
                        rx="3"
                    />

                    <!-- canopy -->
                    <path
                        d="
                            M21 11
                            L43 11
                            L48 24
                            L26 24
                            Z
                        "
                    />

                    <!-- front valance -->
                    <path
                        d="
                            M26 24
                            C27 28 30 28 32 25
                            C34 28 37 28 39 25
                            C41 28 44 28 46 25
                            L48 24
                        "
                    />

                    <!-- support arms -->
                    <line
                        x1="22"
                        y1="12"
                        x2="27"
                        y2="24"
                    />

                    <line
                        x1="42"
                        y1="12"
                        x2="47"
                        y2="24"
                    />
                </g>
            </svg>
        `;
    }

    return `
        <i
            class="bi bi-square fs-2 text-muted"
            aria-label="Default icon"
        ></i>
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

                <p class="text-muted mb-0">
                    ${t("noWatchItems")}
                </p>
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

function bindWatchItemActions(items) {

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
                        items
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
                        items
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
                        items
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
            () => showAddFromSupla(items),
        );
    }

    const saveButton =
        document.getElementById(
            "save-watch-items-btn"
        );

    if (saveButton) {
        saveButton.addEventListener(
            "click",
            () => saveWatchItems(items),
        );
    }
}

async function showAddFromSupla(items) {

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

    renderWatchItemsInPlace(items);
}

function renderWatchItemsInPlace(items) {

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
    bindWatchItemActions(items);
}

async function saveWatchItems(items) {

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
            await updateWatchItems(
                updatedItems
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

        if (error instanceof ApiError) {
            status.textContent =
                error.message;
        } else {
            status.textContent =
                t("unableToSaveConfiguration");
        }

        status.className =
            "small text-danger";

    } finally {
        button.disabled = !watchItemsDirty;
    }
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
                    No Garmin watch has been configured yet.
                </p>

                <button
                    type="button"
                    class="btn btn-primary"
                    id="configure-watch-btn"
                >
                    <i class="bi bi-plus-circle me-2"></i>
                    Configure Watch
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
        <div class="d-flex justify-content-between align-items-start">

            <div>
                <h4 class="mb-2">
                    <i class="bi bi-smartwatch me-2"></i>
                    ${watch.name}
                </h4>

                <span class="badge ${statusClass}">
                    ${statusText}
                </span>
            </div>

        </div>

        <div class="row mt-4">

            <div class="col-12 col-md-6 mb-3">

                <small class="text-muted d-block">
                    ${t("created")}
                </small>

                <strong>
                    ${formatDate(watch.created_at)}
                </strong>

            </div>

            <div class="col-12 col-md-6 mb-3">

                <small class="text-muted d-block">
                    ${t("lastSeen")}
                </small>

                <strong>
                    ${formatDate(watch.last_seen_at)}
                </strong>

            </div>

        </div>

        ${renderWatchItems(items)}

        <div class="border-top pt-3 mt-2">

            <div class="d-flex flex-wrap gap-2">

                <button
                    type="button"
                    class="btn btn-outline-primary"
                    id="replace-watch-btn"
                >
                    <i class="bi bi-arrow-repeat me-2"></i>
                    Replace Watch
                </button>

                <button
                    type="button"
                    class="btn btn-outline-danger"
                    id="reset-watch-pairing-btn"
                >
                    <i class="bi bi-link-45deg me-2"></i>
                    Re-pair current watch
                </button>

            </div>

            <p class="small text-muted mt-2 mb-0">
                Replace Watch keeps the current watch active
                until the new watch completes pairing.
                Re-pair invalidates the current watch token immediately.
            </p>

        </div>
    `;

    document
        .getElementById("replace-watch-btn")
        .addEventListener(
            "click",
            renderPairingForm,
        );

    document
        .getElementById("reset-watch-pairing-btn")
        .addEventListener(
            "click",
            handleWatchRePair,
        );

    bindWatchItemEditors();
    bindWatchItemActions(items);

}

async function handleWatchRePair() {

    const confirmed = window.confirm(
        "Re-pair the current watch?\n\n"
        + "The current watch token will be invalidated. "
        + "The watch will need to pair again."
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

        await resetWatchPairing();

        renderPairingForm();

    } catch (error) {

        if (error instanceof ApiError) {
            showError(error.message);
        } else {
            showError(
                "Unable to reset watch pairing."
            );
        }

    }
}

function renderPairingForm() {

    const content =
        document.getElementById("watch-content");

    content.innerHTML = `
        <div class="mx-auto" style="max-width: 420px;">

            <div class="text-center mb-4">
                <i class="bi bi-smartwatch fs-1 text-primary"></i>

                <h4 class="mt-3 mb-2">
                    Pair Garmin Watch
                </h4>

                <p class="text-muted mb-0">
                    Enter the 6-digit code displayed
                    by GarminSupla on your watch.
                </p>
            </div>

            <form id="pair-watch-form">

                <div class="mb-3">
                    <label
                        for="pairing-code"
                        class="form-label fw-semibold"
                    >
                        Pairing code
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

                <div
                    id="pairing-error"
                    class="alert alert-danger d-none"
                ></div>

                <div class="d-grid">
                    <button
                        type="submit"
                        class="btn btn-primary btn-lg"
                        id="pair-watch-btn"
                    >
                        <i class="bi bi-link-45deg me-2"></i>
                        Pair Watch
                    </button>
                </div>

            </form>

        </div>
    `;

    document
        .getElementById("pair-watch-form")
        .addEventListener(
            "submit",
            handlePairingSubmit,
        );
}

async function handlePairingSubmit(event) {

    event.preventDefault();

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
            "Enter a valid 6-digit pairing code.";

        errorBox.classList.remove("d-none");
        return;
    }

    button.disabled = true;

    try {

        await approveWatchPairing(code);

        renderPairingApproved();

    } catch (error) {

        if (error instanceof ApiError) {

            if (error.status === 404) {
                errorBox.textContent =
                    "Pairing code not found or expired.";
            } else {
                errorBox.textContent =
                    error.message;
            }

        } else {
            errorBox.textContent =
                "Unable to pair Garmin watch.";
        }

        errorBox.classList.remove("d-none");
        button.disabled = false;
    }
}

function renderPairingApproved() {

    const content =
        document.getElementById("watch-content");

    content.innerHTML = `
        <div class="text-center py-3">

            <i
                class="bi bi-check-circle-fill
                       fs-1 text-success"
            ></i>

            <h4 class="mt-3">
                Pairing approved
            </h4>

            <p class="text-muted mb-0">
                Complete the pairing process
                on your Garmin watch.
            </p>

        </div>
    `;

    waitForWatchPairingCompletion();
}

async function waitForWatchPairingCompletion() {

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

            const watch =
                await getWatchStatus();

            if (!watch.configured) {
                continue;
            }

            const items =
                await getWatchItems();

            renderWatch(
                watch,
                items,
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

function showError(message) {

    document.getElementById("watch-content").innerHTML = `
        <div class="alert alert-danger mb-0">
            ${message}
        </div>
    `;

}


document.addEventListener("DOMContentLoaded", async () => {

    initializeUILanguageSelector();

    try {

        const [
            watch,
            items,
        ] = await Promise.all([
            getWatchStatus(),
            getWatchItems(),
        ]);

        renderWatch(
            watch,
            items,
        );

    } catch (error) {

        if (error instanceof ApiError) {
            showError(error.message);
            return;
        }

        showError(
            "Unable to load Garmin watch configuration."
        );

    }

});
