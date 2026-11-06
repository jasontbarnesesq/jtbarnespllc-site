/* Legal Timekeeper service worker.
   Network first for the app's own files, so updates arrive on the next visit; the cached copy is used only offline.
   Microsoft sign-in and OneDrive requests are never cached. */
const CACHE = 'timekeeper-2.0.0';
const SHELL = [
  './', './index.html', './app.css', './manifest.webmanifest',
  './js/app.js', './js/core.js', './js/auth.js', './js/sync.js', './js/config.js',
  './icons/icon-192.png', './icons/favicon-32.png',
  '/assets/img/barnes-logo-white.png',
  '/assets/fonts/dm-sans-latin-400-normal.woff2', '/assets/fonts/dm-sans-latin-500-normal.woff2', '/assets/fonts/dm-sans-latin-600-normal.woff2',
  '/assets/fonts/playfair-display-latin-400-normal.woff2', '/assets/fonts/playfair-display-latin-400-italic.woff2',
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k.startsWith('timekeeper-') && k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  e.respondWith((async () => {
    try {
      const res = await fetch(req, { cache: 'no-cache' });
      if (res.ok && res.type === 'basic') {
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req.mode === 'navigate' ? './' : req, copy));
      }
      return res;
    } catch {
      const hit = await caches.match(req.mode === 'navigate' ? './' : req, { ignoreSearch: req.mode === 'navigate' });
      return hit || Response.error();
    }
  })());
});
