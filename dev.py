import http.server
import os
import socketserver
import sys
from pathlib import Path

# use src as start point
src_dir = Path(__file__).parent / "src"
if src_dir.exists():
    os.chdir(src_dir)
    print(f"[*] Serving from: {src_dir.absolute()}")
else:
    print("[-] src/ dir not found")
    sys.exit(1)

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

try:
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[*] Server running at: http://localhost:{PORT}")
        print(f"[*] Open: http://localhost:{PORT}/")
        print("[-] Press Ctrl+C to stop")
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped")
except OSError as e:
    print(f"[-] Error: {e}")
    print("[-] Try a different port: python dev.py --port 8001")
