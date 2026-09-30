"""Tiny static file server for the web clients, with caching disabled.

A plain `python3 -m http.server` lets browsers cache pages, so editing a
file and reloading can still show the old version. This server sends a
"do not cache" header on every response so a reload always gets the
current file.
"""
import http.server


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()


if __name__ == "__main__":
    http.server.test(HandlerClass=NoCacheHandler, port=8080)
