/**
 * frontend/src/services/api.js
 * ----------------------------
 * Typed fetch helpers for the Yatra backend API.
 * Base URL is read from VITE_API_BASE_URL (set in frontend/.env).
 */

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Internal helper — throws a readable error on non-2xx responses.
 */
async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const msg = body?.detail || body?.message || `HTTP ${res.status}`;
    throw new Error(msg);
  }

  return res.json();
}

// ---------------------------------------------------------------------------
// Walkthrough endpoints
// ---------------------------------------------------------------------------

/**
 * Start (or return cached) a walkthrough for a given place + era.
 * @param {string} place
 * @param {string} era
 * @param {string|null} token  Firebase ID token (optional)
 */
export async function startWalkthrough(place, era, token = null) {
  return request('/api/walkthrough/start', {
    method: 'POST',
    token,
    body: JSON.stringify({ place, era }),
  });
}

/**
 * Fetch the full walkthrough document by its ID (no auth required).
 * @param {string} walkthroughId
 */
export async function getWalkthroughById(walkthroughId) {
  return request(`/api/walkthrough/${walkthroughId}`);
}

/**
 * Fetch the authenticated user's walkthrough history (summary cards only).
 * @param {string} token  Firebase ID token
 */
export async function getMyWalkthroughs(token) {
  return request('/api/walkthrough/mine', { token });
}

/**
 * Claim a system-generated walkthrough to the current user's account.
 * @param {string} walkthroughId
 * @param {string} token
 */
export async function saveWalkthrough(walkthroughId, token) {
  return request(`/api/walkthrough/${walkthroughId}/save`, {
    method: 'POST',
    token,
  });
}

/**
 * Generate a shareable public slug for a user-owned walkthrough.
 * @param {string} walkthroughId
 * @param {string} token
 * @returns {{ share_slug: string }}
 */
export async function shareWalkthrough(walkthroughId, token) {
  return request(`/api/walkthrough/${walkthroughId}/share`, {
    method: 'POST',
    token,
  });
}

/**
 * Fetch a publicly shared walkthrough by its slug (no auth required).
 * @param {string} slug
 */
export async function getSharedWalkthrough(slug) {
  return request(`/api/walkthrough/shared/${slug}`);
}
