import {
    ApiError,
    getSetupStatus,
} from "./api.js";


function setContent(html) {
    document.getElementById("summary-content").innerHTML = html;
}


function renderSummary(setup) {

    const gate = setup.selected_gate;

    if (!gate) {
        setContent(`
            <div class="alert alert-warning text-center">

                <h5 class="mb-3">
                    No gate selected
                </h5>

                <p class="mb-4">
                    Select a gate before completing the setup.
                </p>

                <a
                    href="/select-gate"
                    class="btn btn-primary"
                >
                    <i class="bi bi-arrow-left me-2"></i>
                    Select Gate
                </a>

            </div>
        `);

        return;
    }

    setContent(`
        <div class="summary-section">

            <div class="mb-4">

                <small class="text-muted d-block mb-1">
                    <i class="bi bi-cloud me-1"></i>
                    SUPLA Server
                </small>

                <div class="fw-semibold">
                    ${setup.server}
                </div>

            </div>

            <div class="mb-4">

                <small class="text-muted d-block mb-1">
                    <i class="bi bi-shield-check me-1"></i>
                    Authorization
                </small>

                <div class="fw-semibold text-success">
                    <i class="bi bi-circle-fill me-2 small"></i>
                    Authorized
                </div>

            </div>

            <hr>

            <div class="mt-4">

                <small class="text-muted d-block mb-1">
                    Selected Gate
                </small>

                <h5 class="mb-4">
                    <i class="bi bi-door-open me-2"></i>
                    ${gate.caption}
                </h5>

                <div class="row">

                    <div class="col-6">

                        <small class="text-muted d-block">
                            Relay ID
                        </small>

                        <strong>
                            ${gate.id}
                        </strong>

                    </div>

                    <div class="col-6">

                        <small class="text-muted d-block">
                            Sensor ID
                        </small>

                        <strong>
                            ${gate.sensor_channel_id}
                        </strong>

                    </div>

                </div>

            </div>

        </div>
    `);
}

function updateFinishButton(setup) {

    const button =
        document.getElementById("finish-btn");

    button.disabled =
        !setup.setup_completed;

}

function showGenericError(message) {

    setContent(`
        <div class="alert alert-danger">

            <h5>
                Unable to load configuration
            </h5>

            <p class="mb-0">
                ${message}
            </p>

        </div>
    `);

}

function bindFinishButton() {

    const button =
        document.getElementById("finish-btn");

    button.addEventListener("click", () => {

        window.location.href = "/";

    });

}

document.addEventListener("DOMContentLoaded", async () => {

    try {

        const setup =
            await getSetupStatus();

        renderSummary(setup);

        updateFinishButton(setup);

        bindFinishButton();

    } catch (error) {

        if (error instanceof ApiError) {
            showGenericError(error.message);
            return;
        }

        showGenericError(
            "An unexpected error occurred.",
        );

    }

});
