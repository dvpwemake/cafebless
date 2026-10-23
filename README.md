# cafebless.com

Password-gated investor deck. `build.py <deck.html> <password>` rebuilds `index.html` from the deck, `gate-snippet.html` and `aes-js.min.js` (aes-js 3.1.2, MIT). The password is not stored in this repo.

The gate uses no WebCrypto, so it works on plain http as well as https. It is casual protection for a landing page, not strong security.

The encrypted deck is a separate file, `deck.enc`, fetched only after a password is typed. Keep `index.html` small (about 250 KB): Apple's link-preview engine (Messages) aborts on a 4.5 MB page with 'Frame load interrupted', and the shared link then shows no preview. Test after any change: build a tiny Swift tool around `LPMetadataProvider` and run it on the page.
