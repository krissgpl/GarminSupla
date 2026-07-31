import {
    ApiError,
    getAvailableGates,
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

        const active =
            gate.id === state.selectedGateId
                ? "active"
                : "";

        return `
            <div
                class="list-group-item list-group-item-action gate-item ${active}"
                role="button"
                data-channel-id="${gate.id}"
            >
                <div class="fw-semibold">
                    ${gate.caption}
                </div>

                <small class="text-muted">
                    Relay: ${gate.id}
                    &nbsp;•&nbsp;
                    Sensor: ${gate.sensor_channel_id}
                </small>
            </div>
        `;

    }).join("");

    const html = `
        <div class="list-group">
            ${items}
        </div>
    `;

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

                state.selectedGateId = Number(
                    event.currentTarget.dataset.channelId
                );

                updateContinueButton();

                renderGateList();

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

    button.addEventListener("click", () => {

        console.log(
            "Selected gate:",
            state.selectedGateId,
        );

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
                href="/oauth/start"
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
