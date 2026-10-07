"""Preview the site's HTML content and shared Jekyll layout without installing Jekyll.

Run: python tools/preview_site.py
Then open http://127.0.0.1:8000. Edits appear after refreshing the browser.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import io

ROOT = Path(__file__).resolve().parents[1]


class PreviewHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        route = self.path.split("?", 1)[0]
        if route in ("/", "/index.html"):
            source = ROOT / "index.md"
        else:
            source = Path(self.translate_path(self.path))
        if source.is_file() and source.suffix in (".html", ".md"):
            text = source.read_text(encoding="utf-8")
            if text.startswith("---\n"):
                _, metadata, body = text.split("---", 2)
                fields = dict(line.split(":", 1) for line in metadata.splitlines() if ":" in line)
                if fields.get("layout", "").strip() == "default":
                    layout = (ROOT / "_layouts/default.html").read_text(encoding="utf-8")
                    rendered = layout.replace("{{ page.title }}", fields["title"].strip()).replace("{{ content }}", body.strip())
                    payload = rendered.encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.send_header("Content-Length", str(len(payload)))
                    self.send_header("Cache-Control", "no-cache")
                    self.end_headers()
                    return io.BytesIO(payload)
        return super().send_head()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(PreviewHandler, directory=str(ROOT)))
    print(f"Local preview: http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
