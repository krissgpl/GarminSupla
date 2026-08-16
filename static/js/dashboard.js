import {
    ApiError,
    approveWatchPairing,
    getAvailableSuplaItems,
    getWatchItems,
    getWatchStatus,
    updateWatchItems,
} from "./api.js";


function formatDate(value) {

    if (!value) {
        return "Never";
    }

    return new Date(value).toLocaleString();

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

    return `
        <i
            class="bi bi-square fs-2 text-muted"
            aria-label="Default icon"
        ></i>
    `;
}

function getWatchItemIconOptions(selectedIcon) {

    const icons = [
        ["default", "Default"],
        ["sliding_gate", "Sliding gate"],
        ["double_swing_gate", "Double swing gate"],
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
                    Watch items
                </h5>

                <p class="text-muted mb-0">
                    No items configured for the watch.
                </p>
            </div>
        `;
    }

    const rows = items
        .map((item, index) => `
            <div
                class="border rounded-4 p-3 mb-3"
                data-watch-item-index="${index}"
            >

                <div class="d-flex align-items-start">

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
                                Type: ${item.type}
                            </div>
                        </div>

                    </div>

                </div>

                <div class="row g-3 mt-3 pt-3 border-top">

                    <div class="col-12 col-md-6">

                        <label
                            class="form-label small fw-semibold"
                        >
                            Icon
                        </label>

                        <select
                            class="form-select form-select-sm"
                            data-watch-item-icon
                        >
                            ${getWatchItemIconOptions(
                                item.icon
                            )}
                       </select>

                    </div>

                    <div class="col-12 col-md-6">

                        <div class="mb-3">

                            <label
                                class="form-label small fw-semibold d-block"
                            >
                                Visibility
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
                                    Show on watch
                                </label>

                            </div>

                        </div>

                        <div>

                            <label
                                class="form-label small fw-semibold d-block"
                            >
                                Action
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
                                    Require confirmation
                                </label>

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
                Watch items
            </h5>

            ${rows}

            <div class="mt-3">

                <button
                    type="button"
                    class="btn btn-outline-primary"
                    id="add-from-supla-btn"
                >
                    <i class="bi bi-plus-lg me-1"></i>
                    Add from SUPLA
                </button>

                <div
                    id="add-from-supla-content"
                    class="mt-3"
                ></div>

            </div>

            <div class="d-flex align-items-center gap-3 mt-3">

                <button
                    type="button"
                    class="btn btn-primary"
                    id="save-watch-items-btn"
                >
                    <i class="bi bi-check-lg me-1"></i>
                    Save watch configuration
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

                },
            );

        });
}

function bindWatchItemActions(items) {

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
            Loading SUPLA items...
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
                    No additional supported SUPLA
                    items are available.
                </div>
            `;

            return;
        }

        const options =
            availableItems
                .map((item) => `
                    <option value="${item.supla_id}">
                        ${item.name} (${item.type})
                    </option>
                `)
                .join("");

        content.innerHTML = `
            <div class="border rounded-4 p-3">

                <label
                    class="form-label fw-semibold"
                    for="supla-item-select"
                >
                    SUPLA item
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
                        Add
                    </button>

                </div>

                <div class="small text-muted mt-2">
                    Currently supported: gates
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
                Unable to load SUPLA items.
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

    const suplaId =
        Number(select.value);

    const suplaItem =
        availableItems.find(
            (item) =>
                item.supla_id === suplaId
        );

    if (!suplaItem) {
        return;
    }

    const newItem = {
        id: crypto.randomUUID(),
        type: suplaItem.type,
        name: suplaItem.name,
        icon: "default",
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

    status.textContent = "Saving...";
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

        status.textContent = "Saved";
        status.className =
            "small text-success";

    } catch (error) {

        if (error instanceof ApiError) {
            status.textContent =
                error.message;
        } else {
            status.textContent =
                "Unable to save configuration.";
        }

        status.className =
            "small text-danger";

    } finally {
        button.disabled = false;
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
            ? "Enabled"
            : "Disabled";

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
                    Created
                </small>

                <strong>
                    ${formatDate(watch.created_at)}
                </strong>

            </div>

            <div class="col-12 col-md-6 mb-3">

                <small class="text-muted d-block">
                    Last seen
                </small>

                <strong>
                    ${formatDate(watch.last_seen_at)}
                </strong>

            </div>

        </div>

        ${renderWatchItems(items)}

        <div class="border-top pt-3 mt-2">

            <button
                type="button"
                class="btn btn-outline-primary"
                id="replace-watch-btn"
            >
                <i class="bi bi-arrow-repeat me-2"></i>
                Replace Watch
            </button>

            <p class="small text-muted mt-2 mb-0">
                Your current watch will remain active
                until the new watch completes pairing.
            </p>

        </div>
    `;

    document
        .getElementById("replace-watch-btn")
        .addEventListener(
            "click",
            renderPairingForm,
        );

    bindWatchItemEditors();
    bindWatchItemActions(items);

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
}

function showError(message) {

    document.getElementById("watch-content").innerHTML = `
        <div class="alert alert-danger mb-0">
            ${message}
        </div>
    `;

}


document.addEventListener("DOMContentLoaded", async () => {

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
