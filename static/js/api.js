export class ApiError extends Error {
    constructor(status, body) {
        super(body?.message ?? "Request failed");

        this.name = "ApiError";
        this.status = status;
        this.body = body;
    }
}

function getCookie(name) {
    const prefix = `${encodeURIComponent(name)}=`;

    for (const part of document.cookie.split(";")) {
        const cookie = part.trim();

        if (cookie.startsWith(prefix)) {
            return decodeURIComponent(
                cookie.substring(prefix.length),
            );
        }
    }

    return null;
}

async function apiRequest(
    url,
    options = {},
) {

    const csrfToken = getCookie(
        "garminsupla_csrf",
    );

    const response = await fetch(
        url,
        {
            headers: {
                "Content-Type": "application/json",
                ...(csrfToken
                    ? {"X-CSRF-Token": csrfToken}
                    : {}),
                ...(options.headers ?? {}),
            },
            ...options,
        },
    );

    let body = null;

    try {
        body = await response.json();
    } catch {
        // ignore non-JSON responses
    }

    if (!response.ok) {
        throw new ApiError(
            response.status,
            body,
        );
    }

    return body;
}

export async function getSetupStatus() {

    return apiRequest(
        "/api/v1/setup",
    );

}

export async function getWatchStatus() {

    return apiRequest(
        "/api/v1/setup/watch",
    );

}

export async function getWatchItems() {

    return apiRequest(
        "/api/v1/setup/watch/items",
    );

}

export async function updateWatchItems(items) {

    return apiRequest(
        "/api/v1/setup/watch/items",
        {
            method: "PUT",
            body: JSON.stringify({
                items: items,
            }),
        },
    );

}

export async function getAvailableGates() {
    return apiRequest("/api/v1/setup/gates");
}

export async function selectGate(channelId) {

    return apiRequest(
        "/api/v1/setup/gate",
        {
            method: "POST",
            body: JSON.stringify({
                channel_id: channelId,
            }),
        },
    );

}

export async function approveWatchPairing(code) {

    return apiRequest(
        "/api/v1/setup/watch/pair",
        {
            method: "POST",
            body: JSON.stringify({
                code: code,
            }),
        },
    );

}

export async function getAvailableSuplaItems() {

    return apiRequest(
        "/api/v1/setup/supla/items",
    );

}

export async function resetWatchPairing() {

    return apiRequest(
        "/api/v1/setup/watch/reset",
        {
            method: "POST",
        },
    );

}
