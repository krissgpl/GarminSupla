import {
    ApiError,
    getAvailableGates,
    selectGate,
} from "./api.js";

const state = {
    gates: [],
    selectedGateId: null,
};

function setContent(html) {
    document.getElementById("gate-content").innerHTML = html;
}

function renderGateList() {

    const gates = state.gates;

    if (!gates.length) {
        setContent(`
            <div class="alert alert-info text-center">
                No gate channels were found in your SUPLA account.
            </div>
        `);
        return;
    }

    const items = gates.map(gate => {

    const isSelected =
        gate.id === state.selectedGateId;

    const active =
        isSelected
            ? "border-primary shadow"
            : "";

    const selected =
        isSelected
            ? ""
            : "d-none";

        return `
            <div
                class="card gate-card mb-3 border-2 ${active} gate-item"
                role="button"
                data-channel-id="${gate.id}"
            >

                <div class="card-body">

                    <div class="d-flex justify-content-between align-items-start">

                        <h5 class="fw-semibold mb-0">

                            <i class="bi bi-door-open me-2"></i>

                            ${gate.caption}

                        </h5>

                        <i
                            class="bi bi-check-circle-fill text-primary ${selected}"
                        ></i>

                    </div>

                    <div class="row mt-4">

                        <div class="col-6">

                            <small class="text-muted d-block">
                                Relay ID
                            </small>

                            <strong>${gate.id}</strong>

                        </div>

                        <div class="col-6">

                            <small class="text-muted d-block">
                                Sensor ID
                            </small>

                            <strong>${gate.sensor_channel_id}</strong>

                        </div>

                    </div>

                    <div class="d-flex align-items-center mt-4">

                        <i
                            class="bi bi-circle-fill text-secondary me-2"
                        ></i>

                        <div>

                            <small class="text-muted d-block">
                                Status
                            </small>

                            <strong>
                                Unknown
                            </strong>

                        </div>

                    </div>

            </div>
        `;

    }).join("");

    const html = items;

    setContent(html);

    bindGateEvents();

}

function bindGateEvents() {

    document
        .querySelectorAll(".gate-item")
        .forEach(item => {

            item.addEventListener("click", (event) => {

                state.selectedGateId = Number(
                    event.currentTarget.dataset.channelId
                );

                renderGateList();

                updateContinueButton();

            });

        });

}

function updateContinueButton() {

    const button =
        document.getElementById("continue-btn");

    button.disabled =
        state.selectedGateId === null;

}

function bindContinueButton() {

    const button =
        document.getElementById("continue-btn");

    button.addEventListener("click", async () => {

        if (state.selectedGateId === null) {
            return;
        }

        button.disabled = true;

        const originalContent = button.innerHTML;

        button.innerHTML = `
            <span
                class="spinner-border spinner-border-sm me-2"
                aria-hidden="true"
            ></span>
            Saving...
        `;

        try {

            await selectGate(
                state.selectedGateId,
            );

            window.location.href = "/summary";

        } catch (error) {

            button.innerHTML = originalContent;

            updateContinueButton();

            if (
                error instanceof ApiError &&
                error.status === 401 &&
                error.body?.error === "oauth_expired"
            ) {
                showOAuthExpired();
                return;
            }

            showGenericError(
                error.message,
            );

        }

    });

}

function showOAuthExpired() {
     setContent(`
        <div class="alert alert-warning text-center">

            <h5 class="mb-3">
                 Authorization expired
            </h5>

            <p class="mb-4">
                GarminSupla must be authorized again before
                available gates can be loaded.
            </p>

            <a
                href="/oauth/login"
                class="btn btn-primary"
            >
                Authorize again
            </a>

        </div>
    `);
}

function showGenericError(message) {
    setContent(`
        <div class="alert alert-danger">

            <h5>Unexpected error</h5>

            <p>${message}</p>
 
        </div>
    `);
}

document.addEventListener("DOMContentLoaded", async () => {

    try {
        state.gates = await getAvailableGates();

        renderGateList();

        updateContinueButton();

        bindContinueButton();

    } catch (error) {

        if (
            error instanceof ApiError &&
            error.status === 401 &&
            error.body?.error === "oauth_expired"
        ) {
            showOAuthExpired();
            return;
        }

        showGenericError(error.message);
    }

});
