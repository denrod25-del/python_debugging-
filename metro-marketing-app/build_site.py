#!/usr/bin/env python3
"""Inline data.json into template.html -> dist/index.html (self-contained)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "data.json")) as fh:
    payload = json.dumps(json.load(fh), separators=(",", ":"))
# Keep the inline <script> safe regardless of content.
payload = payload.replace("<", "\\u003c")

with open(os.path.join(HERE, "template.html")) as fh:
    html = fh.read()

out = html.replace("/*__DATA__*/", payload)
os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
dest = os.path.join(HERE, "dist", "index.html")
with open(dest, "w") as fh:
    fh.write(out)
print(f"dist/index.html written ({os.path.getsize(dest)//1024} KB)")
