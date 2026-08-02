import {
    ApiError,
    approveWatchPairing,
    getWatchStatus,
} from "./api.js";


function formatDate(value) {

    if (!value) {
        return "Never";
    }

    return new Date(value).toLocaleString();

}


function renderWatch(watch) {

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

        const watch =
            await getWatchStatus();

        renderWatch(watch);

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
