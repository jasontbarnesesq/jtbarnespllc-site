/* Legal Timekeeper: OneDrive sync.
   One file, timekeeper-data.json, in the app's private folder of the signed-in user's own OneDrive
   (inside OneDrive > Apps, named after the Microsoft app registration). The app can see only that folder. The firm never receives the data. */
import { CONFIG } from './config.js';
import * as auth from './auth.js';
import { mergeEntries, sameEntries } from './core.js';

const META = 'tk.v2.sync';
const ITEM = () => `${CONFIG.GRAPH}/me/drive/special/approot:/${CONFIG.SYNC_FILE}`;

export function meta() { try { return JSON.parse(localStorage.getItem(META)) || {}; } catch { return {}; } }
function setMeta(m) { try { localStorage.setItem(META, JSON.stringify({ ...meta(), ...m })); } catch { /* ignore */ } }
export function clearMeta() { try { localStorage.removeItem(META); } catch { /* ignore */ } }

class SyncError extends Error {
  constructor(msg, kind) { super(msg); this.kind = kind; }
}

async function graph(path, tok, init = {}) {
  let res;
  try {
    res = await fetch(path, { ...init, headers: { Authorization: `Bearer ${tok}`, ...(init.headers || {}) } });
  } catch {
    throw new SyncError('Offline. Changes are saved on this device and will sync later.', 'offline');
  }
  return res;
}

async function readRemote(tok) {
  const res = await graph(ITEM(), tok);
  if (res.status === 404) return { entries: [], etag: null };
  if (res.status === 401) throw new SyncError('Your Microsoft sign-in has expired.', 'auth');
  if (res.status === 403) throw new SyncError('OneDrive is not available for this account. Ask your administrator, or use a personal Microsoft account.', 'drive');
  if (!res.ok) throw new SyncError(`OneDrive did not respond (${res.status}).`, 'server');
  const item = await res.json();
  const dl = item['@microsoft.graph.downloadUrl'];
  let body;
  try {
    body = await (dl ? fetch(dl, { cache: 'no-store' }) : graph(ITEM() + ':/content', tok)).then(r => r.json());
  } catch {
    throw new SyncError('The OneDrive copy could not be read.', 'server');
  }
  const entries = Array.isArray(body) ? body : (body && body.entries) || [];
  return { entries, etag: item.eTag };
}

async function writeRemote(tok, entries, etag) {
  const body = JSON.stringify({ app: 'Legal Timekeeper', publisher: 'J.T. Barnes & Associates, PLLC', format: 2, savedAt: new Date().toISOString(), entries });
  const headers = { 'Content-Type': 'application/json' };
  if (etag) headers['If-Match'] = etag;
  const res = await graph(ITEM() + ':/content', tok, { method: 'PUT', headers, body });
  if (res.status === 412 || res.status === 409) return { conflict: true };
  if (res.status === 401) throw new SyncError('Your Microsoft sign-in has expired.', 'auth');
  if (res.status === 507) throw new SyncError('Your OneDrive is full.', 'drive');
  if (!res.ok) throw new SyncError(`OneDrive did not save the update (${res.status}).`, 'server');
  const item = await res.json().catch(() => ({}));
  return { etag: item.eTag || null };
}

let running = null;

/**
 * Two-way sync. getLocal() returns the device's entries; setLocal(list) replaces them.
 * Resolves to { status: 'synced' | 'signed-out' | 'reauth' | 'error', message, at }.
 */
export function syncNow(getLocal, setLocal) {
  if (running) return running;
  running = (async () => {
    if (!auth.enabled() || !auth.account()) return { status: 'signed-out' };
    const tok = await auth.token();
    if (!tok) return { status: 'reauth', message: 'Sign in again to keep syncing.' };
    try {
      for (let attempt = 0; attempt < 4; attempt++) {
        const remote = await readRemote(tok);
        const local = getLocal();
        const merged = mergeEntries(local, remote.entries);
        if (!sameEntries(merged, local)) setLocal(merged);
        if (sameEntries(merged, remote.entries) && remote.etag) {
          const at = new Date().toISOString();
          setMeta({ etag: remote.etag, at });
          return { status: 'synced', at };
        }
        const w = await writeRemote(tok, merged, remote.etag);
        if (w.conflict) continue; // another device saved first: read again and merge
        const at = new Date().toISOString();
        setMeta({ etag: w.etag, at });
        return { status: 'synced', at };
      }
      return { status: 'error', message: 'Another device kept saving at the same moment. Will retry.' };
    } catch (e) {
      if (e.kind === 'auth') return { status: 'reauth', message: e.message };
      return { status: 'error', message: e.message, kind: e.kind };
    }
  })().finally(() => { running = null; });
  return running;
}
