/* Legal Timekeeper: Microsoft sign-in.
   OAuth 2.0 authorization code flow with PKCE, as Microsoft recommends for single-page apps.
   No client secret exists or is needed. Tokens stay in this browser and are sent only to Microsoft. */
import { CONFIG } from './config.js';

const KEY = 'tk.v2.auth';
const PENDING = 'tk.v2.auth.pending';

const b64url = bytes => btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const random = n => { const b = new Uint8Array(n); crypto.getRandomValues(b); return b64url(b); };

function read() { try { return JSON.parse(localStorage.getItem(KEY)) || null; } catch { return null; } }
function write(v) { try { v ? localStorage.setItem(KEY, JSON.stringify(v)) : localStorage.removeItem(KEY); } catch { /* storage blocked */ } }

function claims(idToken) {
  try {
    const p = idToken.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(decodeURIComponent(escape(atob(p))));
  } catch { return {}; }
}

export const enabled = () => !!CONFIG.CLIENT_ID;

export function account() {
  const a = read();
  return a ? { name: a.name, username: a.username, needsReauth: !!a.needsReauth } : null;
}

export async function signIn({ silent = false } = {}) {
  const verifier = random(48);
  const challenge = b64url(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier)));
  const state = random(16);
  sessionStorage.setItem(PENDING, JSON.stringify({ verifier, state, silent }));
  const prior = read();
  const q = new URLSearchParams({
    client_id: CONFIG.CLIENT_ID,
    response_type: 'code',
    redirect_uri: CONFIG.REDIRECT_URI,
    response_mode: 'query',
    scope: CONFIG.SCOPES.join(' '),
    state,
    code_challenge: challenge,
    code_challenge_method: 'S256',
  });
  if (silent) q.set('prompt', 'none');
  else q.set('prompt', 'select_account');
  if (prior && prior.username) q.set('login_hint', prior.username);
  location.assign(`${CONFIG.AUTHORITY}/oauth2/v2.0/authorize?${q}`);
}

async function tokenRequest(params) {
  const res = await fetch(`${CONFIG.AUTHORITY}/oauth2/v2.0/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ client_id: CONFIG.CLIENT_ID, scope: CONFIG.SCOPES.join(' '), ...params }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(data.error_description || data.error || `Sign-in failed (${res.status})`);
    err.code = data.error || 'token_error';
    throw err;
  }
  return data;
}

function store(data, prior = {}) {
  const c = data.id_token ? claims(data.id_token) : {};
  const a = {
    access: data.access_token,
    expires: Date.now() + (Number(data.expires_in) || 3600) * 1000,
    refresh: data.refresh_token || prior.refresh,
    name: c.name || prior.name || '',
    username: c.preferred_username || c.email || prior.username || '',
    oid: c.oid || prior.oid || '',
  };
  write(a);
  return a;
}

/**
 * Call once at start-up. Finishes a sign-in that just came back from Microsoft.
 * Returns { signedIn, error } and cleans the address bar.
 */
export async function handleRedirect() {
  const url = new URL(location.href);
  const code = url.searchParams.get('code');
  const error = url.searchParams.get('error');
  const state = url.searchParams.get('state');
  if (!code && !error) return { signedIn: !!read() };

  let pending = null;
  try { pending = JSON.parse(sessionStorage.getItem(PENDING)); } catch { /* none */ }
  sessionStorage.removeItem(PENDING);
  history.replaceState(null, '', url.pathname + url.hash);

  if (!pending || pending.state !== state) return { signedIn: !!read(), error: 'The sign-in response did not match this browser session. Please try again.' };
  if (error) {
    // A silent attempt that needs interaction is expected; leave the account marked for a manual sign-in.
    const quiet = pending.silent && /interaction_required|login_required|consent_required/.test(error);
    return { signedIn: !!read(), error: quiet ? null : (url.searchParams.get('error_description') || error) };
  }
  try {
    store(await tokenRequest({
      grant_type: 'authorization_code',
      code,
      redirect_uri: CONFIG.REDIRECT_URI,
      code_verifier: pending.verifier,
    }), read() || {});
    return { signedIn: true, justSignedIn: true };
  } catch (e) {
    return { signedIn: !!read(), error: e.message };
  }
}

/** A valid Graph access token, refreshing when needed. Returns null when the user must sign in again. */
export async function token() {
  const a = read();
  if (!a) return null;
  if (a.access && a.expires - Date.now() > 120000) return a.access;
  if (!a.refresh) { write({ ...a, needsReauth: true }); return null; }
  try {
    return store(await tokenRequest({ grant_type: 'refresh_token', refresh_token: a.refresh }), a).access;
  } catch (e) {
    if (e.code === 'invalid_grant' || e.code === 'interaction_required') write({ ...a, access: null, refresh: null, needsReauth: true });
    return null;
  }
}

/** Forget the account on this device. Entries stay on the device and in OneDrive. */
export function signOut() {
  write(null);
}
