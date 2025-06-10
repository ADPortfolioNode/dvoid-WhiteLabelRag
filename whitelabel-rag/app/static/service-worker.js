/**
 * WhiteLabelRAG Service Worker
 * Provides basic caching for improved performance and offline functionality
 */

// Cache name - update version to force cache refresh
const CACHE_NAME = 'whitelabel-rag-cache-v1';

// Resources to cache
const CACHED_RESOURCES = [
  '/',
  '/static/css/style.css',
  '/static/css/enhancements.css',
  '/static/css/mobile.css',
  '/static/js/app.js',
  '/static/js/ui-enhancer.js',
  '/static/js/mobile-enhancer.js',
  '/static/js/typing-indicator.js',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdn.socket.io/4.7.4/socket.io.min.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap'
];

// Install event - cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching files');
        return cache.addAll(CACHED_RESOURCES);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing old cache');
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

// Fetch event - serve from cache, fall back to network
self.addEventListener('fetch', event => {
  // Skip for socket.io requests which should never be cached
  if (event.request.url.includes('socket.io')) {
    return;
  }
  
  // Skip for API requests
  if (event.request.url.includes('/api/')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached response if found
        if (response) {
          return response;
        }
        
        // Clone the request for fetch and cache
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest)
          .then(response => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone the response for cache and return
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
              
            return response;
          });
      })
      .catch(error => {
        console.log('Service Worker: Fetch failed', error);
        
        // For HTML requests, return the offline page
        if (event.request.headers.get('accept').includes('text/html')) {
          return caches.match('/');
        }
      })
  );
});
