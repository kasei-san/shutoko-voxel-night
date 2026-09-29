# 録画モード（index.html?pv&rec）用のローカルサーバー。
# リポジトリ直下を配信しつつ、POST /save?name=xxx で受け取ったファイルを out/ に保存する。
# 動画（.webm）を受け取ったら終了するので、終了をもって録画完了とみなせる。
#
#   python tools/rec_server.py [port]   # 既定 8766
import os
import sys
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out')
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8766


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != '/save':
            self.send_error(404)
            return
        name = os.path.basename(parse_qs(u.query).get('name', ['upload.bin'])[0])
        n = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(n)
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, name), 'wb') as f:
            f.write(data)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
        print(f'saved {name} {len(data)} bytes', flush=True)
        if name.endswith('.webm'):
            threading.Thread(target=self.server.shutdown).start()

    def log_message(self, *a):
        pass


print(f'serving {ROOT} on http://localhost:{PORT}/', flush=True)
ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
