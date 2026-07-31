export class ApiError extends Error {
    constructor(status, body) {
        super(body?.message ?? "Request failed");

        this.name = "ApiError";
        this.status = status;
        this.body = body;
    }
}

async function apiRequest(
    url,
    options = {},
) {

    const response = await fetch(
        url,
        {
            headers: {
                "Content-Type": "application/json",
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
