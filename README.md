# cafebless.com

Password-gated investor deck. `build.py <deck.html> <password>` rebuilds `index.html` from the deck, `gate-snippet.html` and `aes-js.min.js` (aes-js 3.1.2, MIT). The password is not stored in this repo.

The gate uses no WebCrypto, so it works on plain http as well as https. It is casual protection for a landing page, not strong security.
