#!/usr/bin/env python3
"""Build index.html from the deck: slide 1 in the clear, slides 2+ behind a password gate.
The whole deck is encrypted (AES-256-GCM, PBKDF2-SHA256, 600k iterations) and opened in the browser after the password.
Usage: build.py <deck.html> <password>   (the password is never written to disk)"""
import base64, os, re, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 600_000
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
teaser = teaser.replace('<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex,nofollow">', 1)

salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(hashes.SHA256(), 32, salt, ITER).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, deck.encode(), None)
b64 = lambda b: base64.b64encode(b).decode()
snippet = open("gate-snippet.html", encoding="utf8").read()
for k, v in {"__SALT__": b64(salt), "__IV__": b64(iv), "__ITER__": str(ITER), "__DATA__": b64(ct)}.items():
    snippet = snippet.replace(k, v)
assert teaser.count("</body>") == 1
page = teaser.replace("</body>", snippet + "</body>")
open("index.html", "w", encoding="utf8").write(page)
print("index.html", len(page), "bytes; slides in the clear: 1 of", total)
