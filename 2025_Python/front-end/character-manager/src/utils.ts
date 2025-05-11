const API_BASE_URL = "http://localhost:8000";

export async function apiFetch(path: string, options?: RequestInit) {
    const response = await fetch(`${API_BASE_URL}${path}`, options)
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
    }
    return response.json()
}
