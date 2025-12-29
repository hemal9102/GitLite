let API_BASE;
if (window.location.hostname === '127.0.0.1' && window.location.port === '5500') {
  API_BASE = 'http://127.0.0.1:8080';
} else if (window.location.hostname.includes('github.io')) {
  API_BASE = 'https://gitlite-uicn.onrender.com';
} else {
  API_BASE = window.location.origin || 'http://localhost:8080';
}

// expose for older scripts that expect a global
window.API_BASE = API_BASE;

// compatibility note: do not export as ES module so this file can be
// loaded with a plain <script> tag. Use window.API_BASE from other scripts.
