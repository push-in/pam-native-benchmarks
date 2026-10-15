#!/usr/bin/env python3
"""Deterministic asset server for the framework suite.

Generates (once) and serves the fixtures declared in SCENARIOS.md on
https://127.0.0.1:8099 (TLS, test CA in tls/) and counts every byte it sends, so the harness can measure
network usage per app run:

  GET /__stats          -> {"bytes": n, "requests": n} (not counted)
  POST /__reset          -> zero the counters
"""
from __future__ import annotations

import hashlib
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / ".assets"
WORDS = (ROOT / "words.txt").read_text().split()
PORT = int(os.environ.get("BENCH_PORT", "8099"))

lock = threading.Lock()
stats = {"bytes": 0, "requests": 0, "not_modified": 0}


def lcg(seed: int):
    x = seed
    while True:
        x = (x * 1103515245 + 12345) % 2**31
        yield x


def generate() -> None:
    (ASSETS / "img").mkdir(parents=True, exist_ok=True)
    from PIL import Image, ImageDraw

    for i in range(500):
        p = ASSETS / "img" / f"{i}.jpg"
        if p.exists():
            continue
        g = lcg(1000 + i)
        img = Image.new("RGB", (480, 480), (next(g) % 256, next(g) % 256, next(g) % 256))
        d = ImageDraw.Draw(img)
        for _ in range(40):
            x0, y0 = next(g) % 480, next(g) % 480
            d.ellipse((x0, y0, x0 + next(g) % 160, y0 + next(g) % 160),
                      fill=(next(g) % 256, next(g) % 256, next(g) % 256))
        d.text((20, 20), str(i), fill=(255, 255, 255))
        img.save(p, "JPEG", quality=82)

    video = ASSETS / "video.mp4"
    if not video.exists():
        subprocess.run([
            "ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi",
            "-i", "testsrc2=size=1280x720:rate=30:duration=20",
            "-c:v", "libx264", "-profile:v", "main", "-pix_fmt", "yuv420p",
            "-b:v", "2M", "-movflags", "+faststart", str(video),
        ], check=True)

    feed = ASSETS / "feed.json"
    if not feed.exists():
        g = lcg(42)
        posts = []
        for k in range(50):
            words = [WORDS[next(g) % 64] for _ in range(24)]
            posts.append({
                "id": k + 1,
                "title": f"Post {k + 1}",
                "body": " ".join(words).capitalize() + ".",
                "image": f"https://127.0.0.1:{PORT}/img/{k}.jpg",
                "likes": (k * 13) % 97,
            })
        feed.write_text(json.dumps({"posts": posts}, separators=(",", ":")))

    compute = ASSETS / "compute.json"
    if not compute.exists():
        g = lcg(7)
        rows = []
        for i in range(20000):
            rows.append({
                "id": i,
                "name": f"{WORDS[next(g) % 64]} {WORDS[next(g) % 64]}",
                "email": f"user{i}@example.com",
                "active": i % 3 == 0,
                "score": (next(g) % 100000) / 100,
                "tags": [WORDS[next(g) % 64] for _ in range(4)],
                "address": {"city": WORDS[next(g) % 64].capitalize(), "zip": f"{next(g) % 99999:05d}",
                            "street": " ".join(WORDS[next(g) % 64] for _ in range(3))},
                "bio": " ".join(WORDS[next(g) % 64] for _ in range(12)),
            })
        compute.write_text(json.dumps(rows, separators=(",", ":")))


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    def _send(self, code: int, body: bytes, ctype: str, headers: dict | None = None, count: bool = True):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        if count:
            with lock:
                stats["bytes"] += len(body)
                stats["requests"] += 1

    def do_POST(self):
        if self.path == "/__reset":
            with lock:
                for k in stats:
                    stats[k] = 0
            return self._send(200, b"{}", "application/json", count=False)
        self._send(404, b"", "text/plain")

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/__stats":
            with lock:
                body = json.dumps(stats).encode()
            return self._send(200, body, "application/json", count=False)
        target = (ASSETS / path.lstrip("/")).resolve()
        if not str(target).startswith(str(ASSETS)) or not target.is_file():
            return self._send(404, b"not found", "text/plain")
        data = target.read_bytes()
        etag = '"' + hashlib.sha1(data).hexdigest()[:16] + '"'
        ctype = {".jpg": "image/jpeg", ".mp4": "video/mp4", ".json": "application/json"}.get(target.suffix, "application/octet-stream")
        cache = "no-cache" if target.suffix == ".json" else "public, max-age=31536000, immutable"
        headers = {"ETag": etag, "Cache-Control": cache, "Accept-Ranges": "bytes"}
        if self.headers.get("If-None-Match") == etag:
            with lock:
                stats["not_modified"] += 1
            return self._send(304, b"", ctype, headers)
        rng = self.headers.get("Range")
        if rng and rng.startswith("bytes="):
            start_s, _, end_s = rng[6:].partition("-")
            start = int(start_s or 0)
            end = int(end_s) if end_s else len(data) - 1
            end = min(end, len(data) - 1)
            headers["Content-Range"] = f"bytes {start}-{end}/{len(data)}"
            return self._send(206, data[start:end + 1], ctype, headers)
        self._send(200, data, ctype, headers)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


if __name__ == "__main__":
    generate()
    if len(sys.argv) > 1 and sys.argv[1] == "--generate-only":
        sys.exit(0)
    import ssl
    httpd = Server(("127.0.0.1", PORT), Handler)
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(ROOT / "tls" / "server.pem", ROOT / "tls" / "server.key")
    httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
    httpd.serve_forever()
