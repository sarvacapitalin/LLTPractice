// sw.js - Service Worker for Offline Practice Resilience
const CACHE_NAME = "ts-llr-practice-v2";
const ASSETS_TO_CACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./css/styles.css",
  "./css/exam-stall.css",
  "./js/app.js",
  "./js/i18n.js",
  "./js/storage-engine.js",
  "./js/coverage-engine.js",
  "./js/exam-engine.js",
  "./js/practice-engine.js",
  "./js/flashcards-engine.js",
  "./js/tricky-twins-engine.js",
  "./js/cheatsheet-engine.js",
  "./js/sync-engine.js",
  "./js/qrcode-generator.js",
  "./js/speech-engine.js",
  "./js/sound-effects.js",
  "./data/i18n/en.json",
  "./data/i18n/te.json",
  "./data/i18n/hi.json",
  "./data/states.json",
  "./data/rto-guide.json",
  "./data/tricky-twins.json",
  "./data/last-minute-cheatsheet.json",
  "./data/questions/telangana/road-signs.json",
  "./data/questions/telangana/rules-of-road.json",
  "./data/questions/telangana/general-principles.json"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS_TO_CACHE).catch(err => {
        console.warn("Some assets failed to cache initially:", err);
      });
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

// Network-first for JSON data; Cache-first with background revalidation for static assets
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  const isDataRequest = url.pathname.endsWith(".json");

  if (isDataRequest) {
    // Network-first strategy for data
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200) {
            const respClone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, respClone));
          }
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first strategy for static shell
    event.respondWith(
      caches.match(event.request).then(cached => {
        return (
          cached ||
          fetch(event.request).then(response => {
            if (response && response.status === 200 && event.request.method === "GET") {
              const respClone = response.clone();
              caches.open(CACHE_NAME).then(cache => {
                cache.put(event.request, respClone);
              });
            }
            return response;
          }).catch(() => cached)
        );
      })
    );
  }
});
