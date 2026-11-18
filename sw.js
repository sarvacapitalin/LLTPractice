// sw.js - Service Worker SELF-DESTRUCT
// The SW was causing stale JS module caching (exam-engine.js, coverage-engine.js etc.
// loaded from old cache while app.js was fresh). Disabling SW entirely for reliability.
// This SW immediately unregisters itself and wipes all caches on install + activate.

self.addEventListener("install", event => {
  console.log("[SW v5-unregister] install: will unregister on activate");
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => {
      return Promise.all(keys.map(k => {
        console.log("[SW v5-unregister] deleting cache:", k);
        return caches.delete(k);
      }));
    }).then(() => {
      console.log("[SW v5-unregister] all caches cleared, unregistering SW");
      return self.registration.unregister();
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Pass all fetches through to network (no caching)
self.addEventListener("fetch", event => {
  event.respondWith(fetch(event.request));
});
