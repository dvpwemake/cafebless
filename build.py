#!/usr/bin/env python3
"""Build index.html from the deck: slide 1 in the clear, slides 2+ behind a password gate.
The whole deck is encrypted (AES-256-CTR, key = SHA-256 repeated ITER times over salt+password) and opened in the browser
after the password; the encrypted deck is a separate file, deck.enc, fetched only after a password is typed. It uses no WebCrypto, so it works on plain http:// too. Casual protection for a landing page, not strong security.
Usage: build.py <deck.html> <password>   (the password is never written to disk)"""
import base64, os, re, sys
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ITER = 100_000
MAGIC = b"CAFEBLESS-DECK-1"
src, pw = sys.argv[1], sys.argv[2]
deck = open(src, encoding="utf8").read()

old = '<p class="lead">&#9993;&nbsp; pr@hshub.com</p>'
new = '<p class="lead">&#9993;&nbsp; <a href="mailto:pr@hshub.com" style="color:inherit;text-decoration:underline">pr@hshub.com</a></p>'
assert deck.count(old) == 1, "email line not found exactly once"
deck = deck.replace(old, new)

# Public page: the deck with only slide 1, the no-script slide controls removed, the counter still reading "n / total".
sections = re.findall(r'<section class="slide">.*?</section>', deck, re.S)
total = len(sections)
assert total > 1
teaser = deck
for s in sections[1:]:
    assert teaser.count(s) == 1
    teaser = teaser.replace(s, "")
teaser = re.sub(r'<input type="radio" name="pg" class="pg" id="p(?:[2-9]|1\d)">', "", teaser)
teaser = re.sub(r'<label class="tap [^"]*" for="p\d+"></label>', "", teaser)
cnt = "c.textContent=(i+1)+' / '+s.length"
assert teaser.count(cnt) == 1
teaser = teaser.replace(cnt, f"c.textContent=(i+1)+' / {total}'")
# Link-preview (Open Graph / Twitter) tags, so a shared link shows the cover image.
from html import escape
SITE = "https://cafebless.com"
# Owner 2026-10-23: the share preview shows only this text. No description tags.
OG_TITLE = "Tina's New Salon BP"
OG_ALT = OG_TITLE
og = "".join([
    '<meta name="robots" content="noindex,nofollow">',
    '<meta property="og:type" content="website">',
    f'<meta property="og:url" content="{SITE}/">',
    f'<meta property="og:title" content="{escape(OG_TITLE)}">',
    f'<meta property="og:image" content="{SITE}/og-image.jpg">',
    '<meta property="og:image:type" content="image/jpeg">',
    '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
    f'<meta property="og:image:alt" content="{escape(OG_ALT)}">',
    '<meta name="twitter:card" content="summary_large_image">',
    f'<meta name="twitter:title" content="{escape(OG_TITLE)}">',
    f'<meta name="twitter:image" content="{SITE}/og-image.jpg">',
])
assert teaser.count('<meta charset="utf-8">') == 1
teaser = teaser.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + og, 1)
old_title = "<title>Nail Salon Investor Deck</title>"
assert teaser.count(old_title) == 1
teaser = teaser.replace(old_title, "<title>" + OG_TITLE + "</title>", 1)

salt, iv = os.urandom(16), os.urandom(16)
p = pw.encode()
key = hashlib.sha256(salt + p).digest()
for _ in range(ITER):
    key = hashlib.sha256(key + p + salt).digest()
enc = Cipher(algorithms.AES(key), modes.CTR(iv)).encryptor()
ct = enc.update(MAGIC + deck.encode()) + enc.finalize()
b64 = lambda b: base64.b64encode(b).decode()
snippet = open("gate-snippet.html", encoding="utf8").read()
snippet = snippet.replace("__AESJS__", open("aes-js.min.js", encoding="utf8").read().replace("</script", "<\\/script"))
tag = hashlib.sha256(ct).hexdigest()[:10]
open("deck.enc", "w", encoding="ascii").write(b64(ct))
for k, v in {"__SALT__": b64(salt), "__IV__": b64(iv), "__ITER__": str(ITER), "__DATAURL__": "deck.enc?v=" + tag}.items():
    snippet = snippet.replace(k, v)
assert teaser.count("</body>") == 1
page = teaser.replace("</body>", snippet + "</body>")
open("index.html", "w", encoding="utf8").write(page)
print("index.html", len(page), "bytes (must stay small: link-preview engines abort on huge pages); deck.enc", len(b64(ct)), "bytes; slides in the clear: 1 of", total)
