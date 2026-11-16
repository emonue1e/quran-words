const CACHE_NAME = 'quran-hifz-v12';
const ASSETS = [
  './manifest.json',
  './juz30_data.json',
  './words_data.json'
];

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.map((k) => {
        if (k !== CACHE_NAME) return caches.delete(k);
      })
    ))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);

  // Network-First for HTML/page navigation so user always gets the latest UI code
  if (e.request.mode === 'navigate' || e.request.destination === 'document' || url.pathname.endsWith('.html') || url.pathname.endsWith('/')) {
    e.respondWith(
      fetch(e.request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
          }
          return response;
        })
        .catch(() => caches.match(e.request) || caches.match('./index.html'))
    );
    return;
  }

  // Cache-First for static assets with background network update
  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(e.request, clone));
        }
        return response;
      });
    })
  );
});
