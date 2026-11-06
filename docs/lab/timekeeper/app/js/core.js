/* Legal Timekeeper: pure logic (no DOM). Shared by the app and the tests. */

export const TYPES = {
  'billable': 'Billable',
  'non-billable': 'Non-billable',
  'billable-pending': 'Billable, pending',
};

export function uid() {
  const b = new Uint8Array(9);
  crypto.getRandomValues(b);
  return 'e' + Date.now().toString(36) + Array.from(b, x => x.toString(16).padStart(2, '0')).join('').slice(0, 10);
}

/* ---------- Dates (local calendar days as YYYY-MM-DD) ---------- */
export function isoDay(d = new Date()) {
  const p = n => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}
export function parseDay(s) {
  const [y, m, d] = s.split('-').map(Number);
  return new Date(y, m - 1, d);
}
export function addDays(s, n) {
  const d = parseDay(s);
  d.setDate(d.getDate() + n);
  return isoDay(d);
}
export function longDay(s) {
  return parseDay(s).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
}
/** Named ranges for export. Weeks run Monday to Sunday. */
export function rangeFor(name, today = isoDay()) {
  const t = parseDay(today);
  const dow = (t.getDay() + 6) % 7; // Monday = 0
  const monday = addDays(today, -dow);
  const first = isoDay(new Date(t.getFullYear(), t.getMonth(), 1));
  switch (name) {
    case 'today': return [today, today];
    case 'this-week': return [monday, addDays(monday, 6)];
    case 'last-week': return [addDays(monday, -7), addDays(monday, -1)];
    case 'this-month': return [first, isoDay(new Date(t.getFullYear(), t.getMonth() + 1, 0))];
    case 'last-month': return [isoDay(new Date(t.getFullYear(), t.getMonth() - 1, 1)), isoDay(new Date(t.getFullYear(), t.getMonth(), 0))];
    default: return [today, today];
  }
}

/* ---------- Hours ---------- */
const WORDS = {
  zero: 0, a: 1, an: 1, one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9,
  ten: 10, eleven: 11, twelve: 12, fifteen: 15, twenty: 20, thirty: 30, forty: 40, 'forty-five': 45, fifty: 50, sixty: 60, ninety: 90,
};

/**
 * Turn what someone typed or said into hours.
 * Handles "1.5", "1.5 hours", "90 minutes", "an hour and a half", "two point five",
 * "half an hour", "quarter hour", "1h 30m", "1:30", "three tenths", "point three".
 * Returns 0 when nothing usable is found.
 */
export function parseHours(input) {
  if (input == null) return 0;
  let s = String(input).toLowerCase().trim().replace(/,/g, '.');
  if (!s) return 0;
  s = s.replace(/\bforty five\b/g, 'forty-five');

  // 1:30
  let m = s.match(/\b(\d{1,2}):(\d{2})\b/);
  if (m) return +m[1] + +m[2] / 60;

  // 1h 30m / 1 hr 30 min
  m = s.match(/(\d+(?:\.\d+)?)\s*h(?:ou)?rs?\b\s*(?:and\s*)?(\d+)\s*m(?:in(?:ute)?s?)?\b/);
  if (m) return +m[1] + +m[2] / 60;

  // spoken decimals: "two point five", "point three"
  m = s.match(/\b(?:(\w+)\s+)?point\s+(\w+)/);
  if (m) {
    const whole = m[1] == null ? 0 : (WORDS[m[1]] ?? (isFinite(+m[1]) ? +m[1] : NaN));
    const frac = WORDS[m[2]] ?? (isFinite(+m[2]) ? +m[2] : NaN);
    if (!isNaN(whole) && !isNaN(frac)) return +(`${whole}.${frac}`);
  }

  // tenths: "three tenths", "a tenth"
  m = s.match(/\b(\w+)\s+tenths?\b/);
  if (m && (WORDS[m[1]] ?? +m[1]) >= 0) return (WORDS[m[1]] ?? +m[1]) / 10;

  let hours = 0;
  let found = false;
  const num = w => (WORDS[w] !== undefined ? WORDS[w] : (isFinite(+w) ? +w : NaN));

  // "X minutes"
  m = s.match(/(\d+(?:\.\d+)?|[a-z-]+)\s*(?:minutes?|mins?|m)\b/);
  if (m && !isNaN(num(m[1]))) {
    hours += num(m[1]) / 60; found = true;
  }
  // "X hours" or a bare number
  m = s.match(/(\d+(?:\.\d+)?|[a-z-]+)\s*(?:hours?|hrs?|h)\b/);
  if (m && !isNaN(num(m[1]))) { hours += num(m[1]); found = true; }
  else if (!found) {
    m = s.match(/(\d+(?:\.\d+)?)/);
    if (m) { hours += +m[1]; found = true; }
    else {
      const w = s.split(/\s+/).find(x => WORDS[x] !== undefined && x !== 'a' && x !== 'an');
      if (w) { hours += WORDS[w]; found = true; }
    }
  }
  // fractions
  if (/\b(and a half|half an hour|half hour|a half hour)\b/.test(s)) {
    hours += 0.5; found = true;
    if (/^\s*(half an hour|half hour|a half hour)\s*$/.test(s)) hours = 0.5;
  }
  if (/\b(quarter of an hour|quarter hour|a quarter)\b/.test(s)) {
    hours += /three quarters/.test(s) ? 0.75 : 0.25; found = true;
  }
  if (/\bthree quarters of an hour\b/.test(s)) hours = 0.75;
  return found && hours > 0 ? hours : 0;
}

/**
 * Round hours to a billing increment.
 * increment: 0.1, 0.25, or 0 (no rounding). mode: 'up' or 'nearest'.
 * Any positive time is at least one increment.
 */
export function roundHours(h, increment = 0.1, mode = 'up') {
  if (!(h > 0)) return 0;
  if (!increment) return Math.round(h * 100) / 100;
  const units = h / increment;
  let n = mode === 'nearest' ? Math.round(units) : Math.ceil(units - 1e-9);
  if (n < 1) n = 1;
  return Math.round(n * increment * 100) / 100;
}

export function fmtHours(h) {
  return (Math.round(h * 100) / 100).toFixed(h * 10 % 1 ? 2 : 1);
}

export function parseTimeType(input) {
  const s = String(input || '').toLowerCase();
  if (/pending/.test(s)) return 'billable-pending';
  if (/\b(non|not|no)[\s-]?bill/.test(s) || /\bnon\b/.test(s) || /unbillable/.test(s)) return 'non-billable';
  if (/billable|bill it|billed|yes/.test(s)) return 'billable';
  return null;
}

/* ---------- Autocomplete ---------- */
/** Most-used first, then most recent. */
export function knownValues(entries, field, where = null) {
  const stats = new Map();
  for (const e of entries) {
    if (e.deleted || !e[field]) continue;
    if (where && !where(e)) continue;
    const k = e[field].trim();
    const key = k.toLowerCase();
    const cur = stats.get(key) || { value: k, n: 0, last: '' };
    cur.n++;
    if ((e.updatedAt || '') > cur.last) { cur.last = e.updatedAt || ''; cur.value = k; }
    stats.set(key, cur);
  }
  return [...stats.values()].sort((a, b) => b.n - a.n || (b.last > a.last ? 1 : -1)).map(x => x.value);
}

/** Match a spoken name to a known one: exact, then prefix, then contains, then all words present. */
export function matchKnown(input, known) {
  const s = String(input || '').toLowerCase().replace(/[^\w\s&]/g, ' ').replace(/\s+/g, ' ').trim();
  if (!s) return null;
  const norm = v => v.toLowerCase().replace(/[^\w\s&]/g, ' ').replace(/\s+/g, ' ').trim();
  return known.find(k => norm(k) === s)
    || known.find(k => norm(k).startsWith(s))
    || known.find(k => s.length >= 4 && norm(k).includes(s))
    || known.find(k => { const w = s.split(' '); return w.length > 1 && w.every(x => norm(k).includes(x)); })
    || null;
}

/* ---------- Merge (sync) ---------- */
/** Last write wins per entry id; on a tie a deletion wins. Returns a new array sorted by date then creation. */
export function mergeEntries(a = [], b = []) {
  const out = new Map();
  for (const e of [...a, ...b]) {
    if (!e || !e.id) continue;
    const cur = out.get(e.id);
    if (!cur) { out.set(e.id, e); continue; }
    const ta = cur.updatedAt || '', tb = e.updatedAt || '';
    if (tb > ta || (tb === ta && e.deleted && !cur.deleted)) out.set(e.id, e);
  }
  return [...out.values()].sort((x, y) => (x.date + (x.createdAt || '')).localeCompare(y.date + (y.createdAt || '')));
}

export function sameEntries(a, b) {
  if (a.length !== b.length) return false;
  const m = new Map(a.map(e => [e.id, e.updatedAt + (e.deleted ? 'd' : '')]));
  return b.every(e => m.get(e.id) === e.updatedAt + (e.deleted ? 'd' : ''));
}

/* ---------- Export ---------- */
const csvCell = v => {
  let s = v == null ? '' : String(v);
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; // keep spreadsheet formulas from running
  return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
};

export function toCSV(entries) {
  const rows = [['Date', 'Client', 'Matter', 'Time Type', 'Hours', 'Narrative']];
  for (const e of entries) rows.push([e.date, e.client, e.matter, TYPES[e.type] || e.type, fmtHours(e.hours), e.narrative]);
  return '﻿' + rows.map(r => r.map(csvCell).join(',')).join('\r\n') + '\r\n';
}

export function toText(entries, from, to) {
  const title = from === to ? longDay(from) : `${longDay(from)} to ${longDay(to)}`;
  const lines = [`TIME ENTRIES: ${title}`, '='.repeat(64), ''];
  const byDay = groupBy(entries, e => e.date);
  for (const [day, list] of byDay) {
    if (from !== to) lines.push(longDay(day).toUpperCase(), '-'.repeat(40));
    for (const e of list) {
      lines.push(`${e.client} | ${e.matter}`, `${TYPES[e.type] || e.type} | ${fmtHours(e.hours)} hrs`, e.narrative, '');
    }
    if (from !== to) lines.push(`Day total: ${fmtHours(sum(list))} hrs`, '');
  }
  lines.push('='.repeat(64));
  const billable = entries.filter(e => e.type === 'billable');
  lines.push(`Total: ${fmtHours(sum(entries))} hrs (billable ${fmtHours(sum(billable))} hrs)`);
  return lines.join('\n') + '\n';
}

export function summarize(entries) {
  const byClient = new Map();
  for (const e of entries) {
    const c = byClient.get(e.client) || { client: e.client, billable: 0, other: 0 };
    if (e.type === 'billable') c.billable += e.hours; else c.other += e.hours;
    byClient.set(e.client, c);
  }
  return [...byClient.values()].sort((a, b) => (b.billable + b.other) - (a.billable + a.other));
}

export const sum = list => list.reduce((t, e) => t + (e.hours || 0), 0);
export function groupBy(list, key) {
  const m = new Map();
  for (const x of list) { const k = key(x); if (!m.has(k)) m.set(k, []); m.get(k).push(x); }
  return m;
}

/* ---------- Import ---------- */
function parseCSVRows(text) {
  const rows = []; let row = [], cell = '', q = false;
  text = text.replace(/^﻿/, '');
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; }
      else cell += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && text[i + 1] === '\n') i++;
      row.push(cell); rows.push(row); row = []; cell = '';
    } else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows.filter(r => r.some(x => x.trim()));
}

function typeFromLabel(s) {
  const t = parseTimeType(s);
  return t || 'billable';
}

/** Old app entry {id, date, clientName, clientMatter, timeType, narrative, totalTime} to new shape. */
export function fromLegacy(o, now = new Date().toISOString()) {
  const when = o.date ? new Date(o.date) : new Date();
  return {
    id: 'legacy-' + (o.id ?? uid()),
    date: isoDay(isNaN(when) ? new Date() : when),
    client: String(o.clientName || '').trim() || 'Unassigned',
    matter: String(o.clientMatter || '').trim(),
    type: TYPES[o.timeType] ? o.timeType : typeFromLabel(o.timeType),
    narrative: String(o.narrative || '').trim(),
    hours: Math.round((parseFloat(o.totalTime) || 0) * 100) / 100,
    createdAt: isNaN(when) ? now : when.toISOString(),
    updatedAt: now,
  };
}

/**
 * Read an exported file: this app's JSON backup, this app's CSV, or the old app's CSV
 * (which has no date column; the date comes from the file name or falls back to today).
 */
export function parseImport(text, filename = '', now = new Date().toISOString()) {
  const t = text.trim();
  if (t.startsWith('{') || t.startsWith('[')) {
    const data = JSON.parse(t);
    const list = Array.isArray(data) ? data : (data.entries || []);
    return list.map(e => (e.clientName !== undefined ? fromLegacy(e, now) : clean(e, now))).filter(Boolean);
  }
  const rows = parseCSVRows(text);
  if (!rows.length) return [];
  const head = rows[0].map(h => h.trim().toLowerCase());
  const col = names => head.findIndex(h => names.includes(h));
  const iDate = col(['date']), iClient = col(['client', 'client name']), iMatter = col(['matter', 'client matter']);
  const iType = col(['time type', 'type']), iHours = col(['hours', 'total time (hrs)', 'total time']), iNarr = col(['narrative', 'description']);
  if (iClient < 0 || iHours < 0) throw new Error('This file does not look like a Timekeeper export.');
  const fileDay = (filename.match(/(\d{4}-\d{2}-\d{2})/) || [])[1] || isoDay();
  return rows.slice(1).map((r, n) => clean({
    id: 'import-' + hash(filename + '|' + r.join('|') + '|' + n),
    date: iDate >= 0 && /^\d{4}-\d{2}-\d{2}$/.test((r[iDate] || '').trim()) ? r[iDate].trim() : fileDay,
    client: r[iClient], matter: iMatter >= 0 ? r[iMatter] : '', type: iType >= 0 ? typeFromLabel(r[iType]) : 'billable',
    hours: parseFloat(r[iHours]), narrative: iNarr >= 0 ? r[iNarr] : '',
    createdAt: now, updatedAt: now,
  }, now)).filter(Boolean);
}

export function clean(e, now = new Date().toISOString()) {
  if (!e || typeof e !== 'object') return null;
  const hours = Math.round((parseFloat(e.hours) || 0) * 100) / 100;
  const date = /^\d{4}-\d{2}-\d{2}$/.test(e.date || '') ? e.date : isoDay();
  const out = {
    id: String(e.id || uid()),
    date,
    client: String(e.client || '').trim().slice(0, 200),
    matter: String(e.matter || '').trim().slice(0, 200),
    type: TYPES[e.type] ? e.type : 'billable',
    narrative: String(e.narrative || '').trim().slice(0, 5000),
    hours,
    createdAt: e.createdAt || now,
    updatedAt: e.updatedAt || now,
  };
  if (e.deleted) out.deleted = true;
  if (!out.deleted && (!out.client || !(hours > 0))) return null;
  return out;
}

function hash(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(36);
}

/* ---------- Calendar reminder (.ics) ---------- */
export function reminderICS(time = '17:30', days = [1, 2, 3, 4, 5], url = '') {
  const map = ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA'];
  const [hh, mm] = time.split(':');
  const start = new Date(); start.setHours(+hh, +mm, 0, 0);
  const p = n => String(n).padStart(2, '0');
  const local = d => `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}T${p(d.getHours())}${p(d.getMinutes())}00`;
  const end = new Date(start.getTime() + 10 * 60000);
  const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+/, '');
  return [
    'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//J.T. Barnes & Associates PLLC//Legal Timekeeper//EN', 'CALSCALE:GREGORIAN',
    'BEGIN:VEVENT', `UID:timekeeper-reminder-${Date.now()}@jtbarnespllc.com`, `DTSTAMP:${stamp}`,
    `DTSTART:${local(start)}`, `DTEND:${local(end)}`,
    `RRULE:FREQ=WEEKLY;BYDAY=${days.map(d => map[d]).join(',')}`,
    'SUMMARY:Log today\'s time', `DESCRIPTION:Open the Legal Timekeeper: ${url}`, url ? `URL:${url}` : null,
    'BEGIN:VALARM', 'ACTION:DISPLAY', 'DESCRIPTION:Log today\'s time', 'TRIGGER:PT0M', 'END:VALARM',
    'END:VEVENT', 'END:VCALENDAR',
  ].filter(Boolean).join('\r\n') + '\r\n';
}
