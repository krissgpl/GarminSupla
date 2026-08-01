import {
    ApiError,
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
