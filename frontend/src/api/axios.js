export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8001/api/v1"
).replace(/\/$/, "");
export const API_ORIGIN = API_BASE_URL.replace(/\/api\/v1$/, "");

export async function apiGet(path, params = {}) {
  const url = new URL(`${API_BASE_URL}${path}`);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  }

  let response;
  try {
    response = await fetch(url);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`Cannot connect to the API at ${API_BASE_URL}.`);
    }
    throw error;
  }

  const body = await response.json();
  if (!response.ok) {
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : `The API returned HTTP ${response.status}.`,
    );
  }
  return body;
}

export async function apiGetRoot(path) {
  let response;
  try {
    response = await fetch(`${API_ORIGIN}${path}`);
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`Cannot connect to the API at ${API_ORIGIN}.`);
    }
    throw error;
  }
  const body = await response.json();
  if (!response.ok) {
    throw new Error(
      typeof body.detail === "string"
        ? body.detail
        : `The API returned HTTP ${response.status}.`,
    );
  }
  return body;
}

export async function apiPost(path, payload) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`Cannot connect to the API at ${API_BASE_URL}.`);
    }
    throw error;
  }

  const body = await response.json();
  if (!response.ok) {
    const detail = body.detail;
    const message = Array.isArray(detail)
      ? detail
          .map((item) => `${item.loc.slice(1).join(".")}: ${item.msg}`)
          .join("; ")
      : detail || `The API returned HTTP ${response.status}.`;
    throw new Error(message);
  }
  return body;
}