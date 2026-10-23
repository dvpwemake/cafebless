#!/usr/bin/env python3
"""Build index.html: the deck encrypted (AES-256-GCM, PBKDF2-SHA256) behind a password gate.
Usage: build.py <deck.html> <password>   (the password is never written to disk)"""
import base64, os, sys
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

salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(hashes.SHA256(), 32, salt, ITER).derive(pw.encode())
ct = AESGCM(key).encrypt(iv, deck.encode(), None)
b64 = lambda b: base64.b64encode(b).decode()

page = open("gate.template.html", encoding="utf8").read()
for k, v in {"__SALT__": b64(salt), "__IV__": b64(iv), "__ITER__": str(ITER), "__DATA__": b64(ct)}.items():
    page = page.replace(k, v)
open("index.html", "w", encoding="utf8").write(page)
print("index.html", len(page), "bytes")
