async function apiGet(url) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return await response.json();
}

export async function getAvailableGates() {
    return apiGet("/api/v1/setup/gates");
}
