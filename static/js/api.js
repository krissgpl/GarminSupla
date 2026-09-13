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

export async function getUILanguage() {

    return apiRequest(
        "/api/v1/setup/ui/language",
    );

}

export async function updateUILanguage(language) {

    return apiRequest(
        "/api/v1/setup/ui/language",
        {
            method: "PUT",
            body: JSON.stringify({
                language: language,
            }),
        },
    );

}

export async function getUITheme() {

    return apiRequest(
        "/api/v1/setup/ui/theme",
    );

}

export async function updateUITheme(theme) {

    return apiRequest(
        "/api/v1/setup/ui/theme",
        {
            method: "PUT",
            body: JSON.stringify({
                theme: theme,
            }),
        },
    );

}

export async function getWatchStatus() {

    return apiRequest(
        "/api/v1/setup/watch",
    );

}

export async function getWatchStatuses() {

    return apiRequest(
        "/api/v1/setup/watches",
    );

}

export async function getWatchStatusById(
    watchId,
) {

    return apiRequest(
        `/api/v1/setup/watches/${encodeURIComponent(watchId)}`,
    );

}

export async function updateWatchName(name) {

    return apiRequest(
        "/api/v1/setup/watch",
        {
            method: "PATCH",
            body: JSON.stringify({
                name: name,
            }),
        },
    );

}

export async function updateWatchNameById(
    watchId,
    name,
) {

    return apiRequest(
        `/api/v1/setup/watches/${encodeURIComponent(watchId)}`,
        {
            method: "PATCH",
            body: JSON.stringify({
                name: name,
            }),
        },
    );

}

export async function updateWatchApplicationLanguageById(
    watchId,
    language,
) {

    return apiRequest(
        `/api/v1/setup/watches/${encodeURIComponent(watchId)}/language`,
        {
            method: "PUT",
            body: JSON.stringify({
                language: language,
            }),
        },
    );

}

export async function getWatchItems() {

    return apiRequest(
        "/api/v1/setup/watch/items",
    );

}

export async function getWatchItemsById(
    watchId,
) {

    return apiRequest(
        `/api/v1/setup/watches/${encodeURIComponent(watchId)}/items`,
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

export async function updateWatchItemsById(
    watchId,
    items,
) {

    return apiRequest(
        `/api/v1/setup/watches/${encodeURIComponent(watchId)}/items`,
        {
            method: "PUT",
            body: JSON.stringify({
                items: items,
            }),
        },
    );

}

export async function deleteWatchById(
    watchId,
) {

    return apiRequest(
        `/api/v1/setup/watches/${encodeURIComponent(watchId)}`,
        {
            method: "DELETE",
        },
    );

}

export async function startWatchRePair(
    watchId,
) {

    return apiRequest(
        `/api/v1/setup/watches/${encodeURIComponent(watchId)}/re-pair`,
        {
            method: "POST",
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

export async function approveWatchPairing(
    code,
    watchId = null,
    copyFromWatchId = null,
) {

    const payload = {
        code: code,
    };

    if (watchId !== null) {
        payload.watch_id = watchId;

    } else if (copyFromWatchId !== null) {
        payload.copy_from_watch_id =
            copyFromWatchId;
    }

    return apiRequest(
        "/api/v1/setup/watch/pair",
        {
            method: "POST",
            body: JSON.stringify(
                payload
            ),
        },
    );

}

export async function getAvailableSuplaItems() {

    return apiRequest(
        "/api/v1/setup/supla/items",
    );

}
