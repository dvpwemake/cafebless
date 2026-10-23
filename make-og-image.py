#!/usr/bin/env python3
"""Make og-image.jpg (1200x630, the link-preview image) from a screenshot of the cover slide.
Usage: make-og-image.py <screenshot.png>   Needs Pillow. Keeps the top-left, drops the nav bar at the bottom."""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
h = round(im.height * 0.883)            # drops the slide's bottom bar (about 12% of the height)
w = round(h * 1200 / 630)
im.crop((0, 0, min(w, im.width), h)).resize((1200, 630), Image.LANCZOS).save("og-image.jpg", "JPEG", quality=82, optimize=True, progressive=True)
