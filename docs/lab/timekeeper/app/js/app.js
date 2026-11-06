/* Legal Timekeeper 2.0: interface. */
import { CONFIG } from './config.js';
import * as auth from './auth.js';
import * as sync from './sync.js';
import {
  TYPES, uid, isoDay, addDays, longDay, rangeFor, parseHours, roundHours, fmtHours, parseTimeType,
  knownValues, matchKnown, toCSV, toText, summarize, sum, parseImport, clean, fromLegacy, mergeEntries, reminderICS,
} from './core.js';

const $ = id => document.getElementById(id);
const K = { entries: 'tk.v2.entries', settings: 'tk.v2.settings', ui: 'tk.v2.ui' };

/* ---------------- Storage ---------------- */
const load = (k, d) => { try { const v = JSON.parse(localStorage.getItem(k)); return v ?? d; } catch { return d; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch { toast('This browser blocked saving. Entries will be lost when the tab closes.'); return false; } };

const DEFAULTS = { increment: 0.1, round: 'up', speak: true, listen: true, remind: false, remindTime: '17:30', remindDays: [1, 2, 3, 4, 5] };
let settings = { ...DEFAULTS, ...load(K.settings, {}) };
let all = load(K.entries, []);
const ui = { day: isoDay(), mode: load(K.ui, {}).mode || 'voice', editing: null };

const live = () => all.filter(e => !e.deleted);
function commit(list, { quiet = false } = {}) {
  all = list;
  save(K.entries, all);
  render();
  if (!quiet) scheduleSync();
  if (navigator.storage && navigator.storage.persist && all.length) navigator.storage.persist().catch(() => {});
  if (!quiet) offerSignIn();
}
function offerSignIn() {
  if (!auth.enabled() || auth.account() || !live().length || !$('notice').hidden) return;
  notice('Your entries are saved only on this device. Sign in with Microsoft to back them up to your own OneDrive.', 'Sign in', () => auth.signIn(), 'signin');
}
function upsert(entry) {
  const now = new Date().toISOString();
  const i = all.findIndex(e => e.id === entry.id);
  const next = { ...entry, updatedAt: now };
  if (i < 0) next.createdAt = now;
  const list = all.slice();
  if (i < 0) list.push(next); else list[i] = next;
  commit(list);
  return next;
}
function remove(id) {
  const e = all.find(x => x.id === id);
  if (!e) return;
  upsert({ ...e, deleted: true });
  toast('Entry deleted.', 'Undo', () => upsert({ ...e, deleted: false }));
}

/* ---------------- Small DOM helper (never uses innerHTML for data) ---------------- */
function h(tag, props = {}, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'text') el.textContent = v;
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat()) if (k != null) el.append(k.nodeType ? k : document.createTextNode(k));
  return el;
}

/* ---------------- Toast and notice ---------------- */
let toastTimer;
function toast(text, actionLabel, action) {
  const t = $('toast');
  $('toastText').textContent = text;
  const b = $('toastAction');
  b.hidden = !actionLabel;
  b.textContent = actionLabel || '';
  b.onclick = () => { t.hidden = true; action && action(); };
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, actionLabel ? 7000 : 4000);
}
function notice(text, actionLabel, action, key) {
  if (key && load('tk.v2.dismissed.' + key, false)) return;
  $('noticeText').textContent = text;
  const b = $('noticeAction');
  b.hidden = !actionLabel;
  b.textContent = actionLabel || '';
  b.onclick = () => { $('notice').hidden = true; action && action(); };
  $('noticeDismiss').onclick = () => { $('notice').hidden = true; if (key) save('tk.v2.dismissed.' + key, true); };
  $('notice').hidden = false;
}

/* ---------------- Rendering ---------------- */
function render() {
  const today = isoDay();
  const list = live().filter(e => e.date === ui.day);
  const isToday = ui.day === today;
  $('dayKicker').textContent = isToday ? 'Today' : (ui.day === addDays(today, -1) ? 'Yesterday' : (ui.day > today ? 'Upcoming' : 'Earlier'));
  $('dayTitle').textContent = longDay(ui.day);
  $('dayPicker').value = ui.day;
  $('todayBtn').hidden = isToday;
  $('forDay').textContent = isToday ? '' : `for ${new Date(ui.day + 'T12:00').toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}`;
  if (!ui.editing) $('fDate').value = ui.day;

  $('tTotal').textContent = fmtHours(sum(list));
  $('tBillable').textContent = fmtHours(sum(list.filter(e => e.type === 'billable')));
  $('tCount').textContent = String(list.length);
  $('empty').hidden = list.length > 0;

  const ul = $('entries');
  ul.replaceChildren(...list.map(e => h('li', { class: 'entry' + (ui.editing === e.id ? ' is-editing' : '') },
    h('div', { class: 'entry-top' },
      h('div', { class: 'entry-who' },
        h('strong', { text: e.client }),
        e.matter ? h('span', { class: 'entry-matter', text: e.matter }) : null),
      h('span', { class: 'entry-hours', text: fmtHours(e.hours) }, h('small', { text: ' hrs' }))),
    h('span', { class: 'badge badge-' + e.type, text: TYPES[e.type] }),
    e.narrative ? h('p', { class: 'entry-text', text: e.narrative }) : null,
    h('div', { class: 'entry-actions' },
      h('button', { type: 'button', class: 'link-btn', onclick: () => startEdit(e.id), 'aria-label': `Edit entry for ${e.client}`, text: 'Edit' }),
      h('button', { type: 'button', class: 'link-btn danger', onclick: () => remove(e.id), 'aria-label': `Delete entry for ${e.client}`, text: 'Delete' })),
  )));

  // Autocomplete lists
  $('clientList').replaceChildren(...knownValues(all, 'client').slice(0, 200).map(v => h('option', { value: v })));
  updateMatterList();
  renderSyncChip();
}

function updateMatterList() {
  const c = $('fClient').value.trim().toLowerCase();
  const matters = knownValues(all, 'matter', c ? e => e.client.toLowerCase() === c : null);
  $('matterList').replaceChildren(...matters.slice(0, 200).map(v => h('option', { value: v })));
}

function setDay(d) { ui.day = d; render(); }

/* ---------------- Mode tabs ---------------- */
function setMode(mode) {
  ui.mode = mode;
  save(K.ui, { mode });
  const voice = mode === 'voice';
  $('tabVoice').setAttribute('aria-selected', String(voice));
  $('tabType').setAttribute('aria-selected', String(!voice));
  $('voicePane').hidden = !voice;
  $('typePane').hidden = voice;
  if (!voice) stopListening();
}

/* ---------------- Typed entry ---------------- */
function incrementLabel() {
  if (!settings.increment) return 'Recorded exactly as entered.';
  const unit = settings.increment === 0.1 ? 'tenth of an hour (6 minutes)' : 'quarter hour';
  return `Rounded ${settings.round === 'up' ? 'up' : 'to the nearest'} ${unit}.`;
}
function updateHoursHelp() {
  const raw = parseHours($('fHours').value);
  const r = roundHours(raw, settings.increment, settings.round);
  $('hoursHelp').textContent = raw ? (Math.abs(r - raw) > 1e-9 ? `Will record ${fmtHours(r)} hrs. ${incrementLabel()}` : `Will record ${fmtHours(r)} hrs.`) : incrementLabel();
}
function formType() { return document.querySelector('#fType input:checked').value; }
function setFormType(t) { document.querySelector(`#fType input[value="${t}"]`).checked = true; }

function clearForm() {
  ui.editing = null;
  $('typePane').reset();
  $('fDate').value = ui.day;
  setFormType('billable');
  $('fSubmit').textContent = 'Add entry';
  $('fDelete').hidden = true;
  $('fClear').textContent = 'Clear';
  $('formError').hidden = true;
  updateHoursHelp();
  render();
}

function startEdit(id) {
  const e = all.find(x => x.id === id);
  if (!e) return;
  setMode('type');
  ui.editing = id;
  $('fClient').value = e.client;
  $('fMatter').value = e.matter;
  setFormType(e.type);
  $('fHours').value = fmtHours(e.hours);
  $('fDate').value = e.date;
  $('fNarrative').value = e.narrative;
  $('fSubmit').textContent = 'Save changes';
  $('fClear').textContent = 'Cancel';
  $('fDelete').hidden = false;
  updateHoursHelp();
  render();
  $('log').scrollIntoView({ behavior: 'smooth', block: 'start' });
  $('fClient').focus({ preventScroll: true });
}

function submitForm(ev) {
  ev.preventDefault();
  const client = $('fClient').value.trim();
  const raw = parseHours($('fHours').value);
  const err = !client ? 'Enter a client.' : !raw ? 'Enter the time, for example 1.5 or 90 min.' : !$('fDate').value ? 'Choose a date.' : '';
  if (err) { $('formError').textContent = err; $('formError').hidden = false; return; }
  const base = ui.editing ? all.find(x => x.id === ui.editing) : { id: uid() };
  const entry = clean({
    ...base,
    client, matter: $('fMatter').value.trim(), type: formType(), narrative: $('fNarrative').value.trim(),
    hours: roundHours(raw, settings.increment, settings.round), date: $('fDate').value, deleted: false,
  });
  delete entry.deleted;
  const wasEditing = !!ui.editing;
  upsert(entry);
  if (entry.date !== ui.day) ui.day = entry.date;
  clearForm();
  toast(wasEditing ? 'Changes saved.' : `Added ${fmtHours(entry.hours)} hrs for ${entry.client}.`);
  $('fClient').focus();
}

/* ---------------- Voice conversation ---------------- */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let rec = null, listening = false, convo = null, keepListening = false;
const STEPS = ['client', 'matter', 'type', 'narrative', 'hours'];

function say(text, role = 'bot', { silent = false } = {}) {
  const li = h('li', { class: 'msg msg-' + role }, h('span', { text }));
  const chat = $('chat');
  chat.append(li);
  chat.scrollTop = chat.scrollHeight;
  if (silent) return false;
  if (role === 'bot' && settings.speak && 'speechSynthesis' in window) {
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.05;
    u.onend = () => { if (keepListening && convo && settings.listen) startListening(); };
    speechSynthesis.speak(u);
    return true;
  }
  if (role === 'bot' && keepListening && convo && settings.listen) setTimeout(startListening, 350);
  return false;
}

function question(step) {
  const c = convo.entry;
  switch (step) {
    case 'client': return 'Who was the work for?';
    case 'matter': {
      const recent = knownValues(all, 'matter', e => e.client.toLowerCase() === c.client.toLowerCase()).slice(0, 3);
      return recent.length ? `Which matter for ${c.client}? Recent ones: ${recent.join('; ')}.` : `Which matter for ${c.client}? Say "none" to skip.`;
    }
    case 'type': return 'Billable, non-billable, or pending?';
    case 'narrative': return 'Describe the work, as it should read on the bill.';
    case 'hours': return 'How much time? For example, "one point two" or "ninety minutes".';
  }
}

function ask() { say(question(STEPS[convo.step])); }

function startConversation(first) {
  convo = { step: 0, entry: {} };
  if (first) handleAnswer(first); else ask();
}

function handleAnswer(text) {
  const t = text.trim();
  if (!t) return;
  say(t, 'me');
  const low = t.toLowerCase().replace(/[.!?]$/, '');
  if (/^(start over|cancel|reset|never ?mind)$/.test(low)) {
    convo = null; keepListening = false;
    say('Okay, cleared. Tap the microphone when you are ready.');
    return;
  }
  if (!convo) { convo = { step: 0, entry: {} }; }
  if (/^(go back|back|undo)$/.test(low)) {
    convo.step = Math.max(0, convo.step - 1);
    ask(); return;
  }
  const step = STEPS[convo.step];
  const c = convo.entry;
  switch (step) {
    case 'client': {
      const m = matchKnown(t, knownValues(all, 'client'));
      c.client = m || capitalize(t);
      break;
    }
    case 'matter': {
      if (/^(none|no matter|skip|general|n\/a)$/.test(low)) c.matter = '';
      else c.matter = matchKnown(t, knownValues(all, 'matter', e => e.client.toLowerCase() === c.client.toLowerCase())) || capitalize(t);
      break;
    }
    case 'type': {
      const ty = /^(skip|default)$/.test(low) ? 'billable' : parseTimeType(t);
      if (!ty) { say('Sorry, was that billable, non-billable, or pending?'); return; }
      c.type = ty; break;
    }
    case 'narrative': c.narrative = capitalize(t).replace(/([^.!?])$/, '$1.'); break;
    case 'hours': {
      const raw = parseHours(t);
      if (!raw) { say('I did not catch a time. Try "one point five hours" or "forty-five minutes".'); return; }
      c.hours = roundHours(raw, settings.increment, settings.round);
      const saved = upsert(clean({ id: uid(), date: ui.day, ...c }));
      const note = Math.abs(c.hours - raw) > 1e-9 ? ` (${fmtHours(raw)} rounded to your increment)` : '';
      const when = ui.day === isoDay() ? '' : ` on ${longDay(ui.day)}`;
      convo = null; keepListening = false;
      say(`Saved ${fmtHours(saved.hours)} hours${note} for ${saved.client}${when}. Tap the microphone for another entry.`);
      lastSaved(saved.id);
      return;
    }
  }
  convo.step++;
  ask();
}

function lastSaved(id) {
  const li = h('li', { class: 'msg msg-tools' },
    h('button', { type: 'button', class: 'link-btn', text: 'Edit this entry', onclick: () => startEdit(id) }),
    h('button', { type: 'button', class: 'link-btn danger', text: 'Undo', onclick: () => remove(id) }));
  $('chat').append(li);
  $('chat').scrollTop = $('chat').scrollHeight;
}

const capitalize = s => s.charAt(0).toUpperCase() + s.slice(1);

function setMic(on, status) {
  listening = on;
  $('micBtn').classList.toggle('on', on);
  $('micBtn').setAttribute('aria-pressed', String(on));
  $('micLabel').textContent = on ? 'Stop listening' : 'Start speaking';
  if (status) $('micStatus').textContent = status;
}

function startListening() {
  if (!SR) return;
  if (listening) return;
  if ('speechSynthesis' in window) speechSynthesis.cancel();
  rec = new SR();
  rec.lang = navigator.language || 'en-US';
  rec.interimResults = true;
  rec.maxAlternatives = 1;
  rec.continuous = false;
  let final = '';
  rec.onresult = ev => {
    let interim = '';
    for (let i = ev.resultIndex; i < ev.results.length; i++) {
      const r = ev.results[i];
      if (r.isFinal) final += r[0].transcript; else interim += r[0].transcript;
    }
    $('replyInput').value = (final + interim).trim();
  };
  rec.onerror = ev => {
    const msg = ev.error === 'not-allowed' || ev.error === 'service-not-allowed'
      ? 'Microphone access is blocked. Allow it in your browser settings, or type your answers.'
      : ev.error === 'no-speech' ? 'I did not hear anything. Tap the microphone to try again.' : 'Voice input stopped. Tap the microphone to try again.';
    keepListening = false;
    setMic(false, msg);
  };
  rec.onend = () => {
    setMic(false, convo ? 'Tap the microphone to answer, or type below.' : 'Tap the microphone and say who the work was for.');
    const said = final.trim();
    if (said) {
      $('replyInput').value = '';
      if (!convo) startConversation(said); else handleAnswer(said);
    }
  };
  try {
    rec.start();
    keepListening = true;
    setMic(true, 'Listening...');
  } catch {
    setMic(false, 'Tap the microphone to start.');
  }
}
function stopListening() {
  keepListening = false;
  if (rec && listening) { try { rec.stop(); } catch { /* already stopped */ } }
}

/* ---------------- Export ---------------- */
function exportRange() {
  const r = document.querySelector('#rangeChoice input:checked').value;
  $('customRange').hidden = r !== 'custom';
  let from, to;
  if (r === 'custom') { from = $('xFrom').value || ui.day; to = $('xTo').value || from; if (to < from) [from, to] = [to, from]; }
  else [from, to] = rangeFor(r, isoDay());
  const list = live().filter(e => e.date >= from && e.date <= to);
  return { from, to, list };
}
function renderExport() {
  const { from, to, list } = exportRange();
  const box = $('xSummary');
  const label = from === to ? longDay(from) : `${longDay(from)} to ${longDay(to)}`;
  if (!list.length) { box.replaceChildren(h('p', { class: 'muted', text: `No entries for ${label}.` })); toggleExportButtons(false); return; }
  const rows = summarize(list);
  box.replaceChildren(
    h('p', { class: 'summary-head' }, h('strong', { text: `${fmtHours(sum(list))} hrs` }), ` across ${list.length} ${list.length === 1 ? 'entry' : 'entries'}, ${label}`),
    h('table', {},
      h('thead', {}, h('tr', {}, h('th', { scope: 'col', text: 'Client' }), h('th', { scope: 'col', class: 'num', text: 'Billable' }), h('th', { scope: 'col', class: 'num', text: 'Other' }))),
      h('tbody', {}, rows.map(r => h('tr', {}, h('td', { text: r.client }), h('td', { class: 'num', text: fmtHours(r.billable) }), h('td', { class: 'num', text: fmtHours(r.other) }))))));
  toggleExportButtons(true);
}
function toggleExportButtons(on) { for (const id of ['xCopy', 'xText', 'xCsv']) $(id).disabled = !on; }
function download(name, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = h('a', { href: url, download: name });
  document.body.append(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}
const fileStem = (from, to) => `timekeeper_${from}${from === to ? '' : '_to_' + to}`;

/* ---------------- Settings ---------------- */
function fillSettings() {
  $('sIncrement').value = `${settings.increment}:${settings.increment ? settings.round : 'none'}`;
  $('sSpeak').checked = settings.speak;
  $('sListen').checked = settings.listen;
  $('sRemind').checked = settings.remind;
  $('sRemindTime').value = settings.remindTime;
  for (const cb of document.querySelectorAll('#sDays input')) cb.checked = settings.remindDays.includes(+cb.value);
  $('voiceSupport').textContent = SR ? '' : 'This browser does not offer voice input. Use Type, or open the Timekeeper in Chrome, Edge, or Safari.';
  $('aboutText').textContent = `Legal Timekeeper ${CONFIG.VERSION}. Built by J.T. Barnes & Associates, PLLC.`;
  renderAccount();
}
function saveSettings() {
  const [inc, round] = $('sIncrement').value.split(':');
  settings = {
    ...settings,
    increment: +inc, round: round === 'none' ? 'up' : round,
    speak: $('sSpeak').checked, listen: $('sListen').checked,
    remind: $('sRemind').checked, remindTime: $('sRemindTime').value || '17:30',
    remindDays: [...document.querySelectorAll('#sDays input:checked')].map(cb => +cb.value),
  };
  save(K.settings, settings);
  updateHoursHelp();
}

/* ---------------- Reminders ---------------- */
async function onRemindToggle() {
  if ($('sRemind').checked && 'Notification' in window && Notification.permission !== 'granted') {
    const p = await Notification.requestPermission().catch(() => 'denied');
    if (p !== 'granted') { $('sRemind').checked = false; toast('Notifications are blocked in this browser. Use "Add reminder to my calendar" instead.'); }
  }
  if ($('sRemind').checked && !('Notification' in window)) { $('sRemind').checked = false; toast('This browser cannot show reminders. Use "Add reminder to my calendar" instead.'); }
  saveSettings();
}
function checkReminder() {
  if (!settings.remind || !('Notification' in window) || Notification.permission !== 'granted') return;
  const now = new Date();
  if (!settings.remindDays.includes(now.getDay())) return;
  const [hh, mm] = settings.remindTime.split(':').map(Number);
  const due = new Date(now); due.setHours(hh, mm, 0, 0);
  const today = isoDay(now);
  if (now >= due && now - due < 3 * 3600e3 && load('tk.v2.reminded', '') !== today) {
    save('tk.v2.reminded', today);
    const logged = sum(live().filter(e => e.date === today));
    const n = new Notification('Log today\'s time', { body: logged ? `${fmtHours(logged)} hrs logged so far today.` : 'Nothing logged yet today.', icon: 'icons/icon-192.png', tag: 'timekeeper-reminder' });
    n.onclick = () => { window.focus(); n.close(); };
  }
}

/* ---------------- Sync ---------------- */
let syncTimer, syncState = { status: 'local' };
function scheduleSync(delay = 2000) {
  if (!auth.enabled() || !auth.account()) return;
  clearTimeout(syncTimer);
  syncTimer = setTimeout(runSync, delay);
}
async function runSync() {
  if (!auth.enabled() || !auth.account()) { syncState = { status: 'local' }; renderSyncChip(); return; }
  syncState = { ...syncState, status: 'syncing' };
  renderSyncChip();
  const r = await sync.syncNow(() => all, list => commit(list, { quiet: true }));
  syncState = r;
  renderSyncChip();
  renderAccount();
  return r;
}
function renderSyncChip() {
  const chip = $('syncChip');
  const acct = auth.account();
  chip.hidden = !auth.enabled();
  let text = 'On this device', cls = 'local';
  if (acct) {
    if (acct.needsReauth || syncState.status === 'reauth') { text = 'Sign in to sync'; cls = 'warn'; }
    else if (syncState.status === 'syncing') { text = 'Syncing'; cls = 'busy'; }
    else if (syncState.status === 'error') { text = syncState.kind === 'offline' ? 'Offline' : 'Sync paused'; cls = 'warn'; }
    else if (syncState.status === 'synced') { text = 'Synced ' + new Date(syncState.at).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' }); cls = 'ok'; }
    else { const m = sync.meta(); text = m.at ? 'Synced ' + new Date(m.at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : 'Signed in'; cls = 'ok'; }
  }
  chip.className = 'sync-chip ' + cls;
  $('syncText').textContent = text;
  chip.title = syncState.message || '';
  $('footSync').textContent = acct ? ' and in your OneDrive (in the Apps folder)' : '';
}
function renderAccount() {
  const acct = auth.account();
  const on = auth.enabled();
  $('setAccount').hidden = !on;
  if (!on) return;
  $('signInBtn').hidden = !!acct && !acct.needsReauth && syncState.status !== 'reauth';
  $('signInBtn').lastChild.textContent = acct ? ' Sign in again' : ' Sign in with Microsoft';
  $('syncBtn').hidden = !acct;
  $('signOutBtn').hidden = !acct;
  const m = sync.meta();
  $('acctText').textContent = acct
    ? `Signed in as ${acct.name || acct.username}${acct.username && acct.name ? ` (${acct.username})` : ''}. Entries sync to a private app folder in your OneDrive, inside the Apps folder.${m.at ? ` Last synced ${new Date(m.at).toLocaleString()}.` : ''}${syncState.message ? ' ' + syncState.message : ''}`
    : 'Entries are saved only on this device. Sign in with a personal or work Microsoft account to back them up to your own OneDrive and use them on your other devices. The firm never receives your entries.';
}

/* ---------------- Import ---------------- */
function mergeIn(list, source) {
  if (!list.length) { toast(`No entries found in ${source}.`); return; }
  const before = new Set(live().map(e => e.id));
  commit(mergeEntries(all, list));
  const added = list.filter(e => !before.has(e.id) && !e.deleted).length;
  toast(added ? `Imported ${added} ${added === 1 ? 'entry' : 'entries'} from ${source}.` : `Everything in ${source} was already here.`);
}

/** The old app at jasontbarnes.com opens this page and hands over the entries saved in that browser. */
function listenForLegacy() {
  if (!window.opener || location.hash !== '#import-legacy') return;
  history.replaceState(null, '', location.pathname);
  const onMsg = ev => {
    if (!CONFIG.LEGACY_ORIGINS.includes(ev.origin)) return;
    const d = ev.data || {};
    if (d.type !== 'tk-legacy-entries' || !Array.isArray(d.entries)) return;
    window.removeEventListener('message', onMsg);
    const now = new Date().toISOString();
    mergeIn(d.entries.map(o => fromLegacy(o, now)).map(e => clean(e, now)).filter(Boolean), 'the original Timekeeper');
    try { ev.source.postMessage({ type: 'tk-legacy-received' }, ev.origin); } catch { /* opener closed */ }
  };
  window.addEventListener('message', onMsg);
  for (const o of CONFIG.LEGACY_ORIGINS) { try { window.opener.postMessage({ type: 'tk-ready' }, o); } catch { /* not that origin */ } }
}

/* ---------------- Wire up ---------------- */
function bind() {
  $('tabVoice').onclick = () => setMode('voice');
  $('tabType').onclick = () => setMode('type');
  for (const tab of [$('tabVoice'), $('tabType')]) tab.addEventListener('keydown', ev => {
    if (ev.key === 'ArrowRight' || ev.key === 'ArrowLeft') { const other = tab === $('tabVoice') ? $('tabType') : $('tabVoice'); other.click(); other.focus(); }
  });

  $('micBtn').onclick = () => {
    if (!SR) { toast('Voice input is not available in this browser. Type your answers instead.'); $('replyInput').focus(); return; }
    if (listening) stopListening(); else startListening();
  };
  $('replyForm').onsubmit = ev => {
    ev.preventDefault();
    const v = $('replyInput').value.trim();
    if (!v) return;
    $('replyInput').value = '';
    stopListening();
    if (!convo) startConversation(v); else handleAnswer(v);
  };

  $('typePane').addEventListener('submit', submitForm);
  $('fClear').onclick = clearForm;
  $('fDelete').onclick = () => { const id = ui.editing; clearForm(); remove(id); };
  $('fHours').addEventListener('input', updateHoursHelp);
  $('fClient').addEventListener('input', updateMatterList);

  $('prevDay').onclick = () => setDay(addDays(ui.day, -1));
  $('nextDay').onclick = () => setDay(addDays(ui.day, 1));
  $('todayBtn').onclick = () => setDay(isoDay());
  $('dayPicker').addEventListener('change', ev => ev.target.value && setDay(ev.target.value));

  $('openExport').onclick = () => { $('xFrom').value = $('xFrom').value || ui.day; $('xTo').value = $('xTo').value || ui.day; renderExport(); $('exportDlg').showModal(); };
  $('exportDlg').addEventListener('change', renderExport);
  $('xCsv').onclick = () => { const { from, to, list } = exportRange(); download(fileStem(from, to) + '.csv', toCSV(list), 'text/csv;charset=utf-8'); };
  $('xText').onclick = () => { const { from, to, list } = exportRange(); download(fileStem(from, to) + '.txt', toText(list, from, to), 'text/plain;charset=utf-8'); };
  $('xCopy').onclick = async () => {
    const { from, to, list } = exportRange();
    try { await navigator.clipboard.writeText(toText(list, from, to)); toast('Copied to the clipboard.'); }
    catch { toast('Copying is blocked here. Use Download text instead.'); }
  };

  $('openSettings').onclick = () => { fillSettings(); $('settingsDlg').showModal(); };
  for (const id of ['sIncrement', 'sSpeak', 'sListen', 'sRemindTime']) $(id).addEventListener('change', saveSettings);
  $('sDays').addEventListener('change', saveSettings);
  $('sRemind').addEventListener('change', onRemindToggle);
  $('icsBtn').onclick = () => download('timekeeper-reminder.ics', reminderICS(settings.remindTime, settings.remindDays, CONFIG.REDIRECT_URI), 'text/calendar');

  $('signInBtn').onclick = () => auth.signIn();
  $('syncBtn').onclick = async () => { const r = await runSync(); toast(r && r.status === 'synced' ? 'Synced with OneDrive.' : (r && r.message) || 'Could not sync.'); };
  $('signOutBtn').onclick = () => {
    auth.signOut(); sync.clearMeta(); syncState = { status: 'local' };
    renderSyncChip(); renderAccount();
    toast('Signed out on this device. Your entries remain here and in your OneDrive.');
  };
  $('syncChip').onclick = () => { fillSettings(); $('settingsDlg').showModal(); };

  $('backupBtn').onclick = () => download(`timekeeper-backup_${isoDay()}.json`, JSON.stringify({ app: 'Legal Timekeeper', format: 2, savedAt: new Date().toISOString(), entries: all }, null, 1), 'application/json');
  $('importFile').addEventListener('change', async ev => {
    const f = ev.target.files[0];
    ev.target.value = '';
    if (!f) return;
    try { mergeIn(parseImport(await f.text(), f.name), f.name); }
    catch (e) { toast(e.message || 'That file could not be read.'); }
  });
  $('wipeBtn').onclick = () => {
    const n = live().length;
    if (!n) { toast('There are no entries to delete.'); return; }
    if (!confirm(`Delete all ${n} entries? ${auth.account() ? 'This also removes them from your OneDrive copy. ' : ''}Download a backup first if you may need them.`)) return;
    const now = new Date().toISOString();
    commit(all.map(e => (e.deleted ? e : { ...e, deleted: true, updatedAt: now })));
    toast('All entries deleted.');
  };

  for (const d of [$('exportDlg'), $('settingsDlg')]) d.addEventListener('click', ev => { if (ev.target === d) d.close(); });

  window.addEventListener('storage', ev => {
    if (ev.key === K.entries) { all = load(K.entries, []); render(); }
    if (ev.key === K.settings) { settings = { ...DEFAULTS, ...load(K.settings, {}) }; }
  });
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      if (ui.day < isoDay() && !ui.editing && load('tk.v2.lastDay', '') !== isoDay()) { save('tk.v2.lastDay', isoDay()); setDay(isoDay()); }
      scheduleSync(300); checkReminder();
    }
  });
  window.addEventListener('online', () => scheduleSync(300));
}

async function start() {
  bind();
  setMode(SR ? ui.mode : 'type');
  if (!SR) { $('micStatus').textContent = 'Voice input is not available in this browser. Type your answers below, or use Type.'; }
  clearForm();
  render();
  say('Tap the microphone and tell me who the work was for. I will ask for the matter, the time type, a narrative, and the time.', 'bot', { silent: true });

  const r = auth.enabled() ? await auth.handleRedirect() : { signedIn: false };
  if (r.error) toast('Microsoft sign-in did not finish: ' + r.error);
  renderSyncChip();
  if (r.justSignedIn) {
    const s = await runSync();
    toast(s && s.status === 'synced' ? 'Signed in. Your entries are synced with OneDrive.' : 'Signed in. ' + ((s && s.message) || ''));
  } else if (auth.account()) {
    scheduleSync(200);
  } else {
    offerSignIn();
  }

  listenForLegacy();
  setInterval(checkReminder, 30000);
  checkReminder();
  setInterval(() => { if (document.visibilityState === 'visible') scheduleSync(0); }, 5 * 60000);

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js').then(reg => {
      reg.addEventListener('updatefound', () => {
        const nw = reg.installing;
        nw && nw.addEventListener('statechange', () => {
          if (nw.state === 'installed' && navigator.serviceWorker.controller) toast('An update is ready.', 'Reload', () => location.reload());
        });
      });
    }).catch(() => {});
  }
}

start();
