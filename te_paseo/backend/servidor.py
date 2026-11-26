"""Capa de API: expone los servicios por HTTP/JSON y sirve el frontend."""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from . import config as C

FRONT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
MIME = {".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript"}


def crear_servidor(servicio):
    rutas = {"/api/solicitar": servicio.solicitar, "/api/confirmar_pago": servicio.confirmar_pago,
             "/api/calificar": servicio.calificar,
             "/api/incidencia": servicio.incidencia, "/api/clic_ad": servicio.clic_ad,
             "/api/ubicacion": servicio.ubicacion,
             "/api/cotizar": servicio.cotizar}

    class Handler(BaseHTTPRequestHandler):
        def _enviar(self, codigo, tipo, datos):
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.end_headers()
            self.wfile.write(datos)

        def _json(self, obj, codigo=200):
            self._enviar(codigo, "application/json", json.dumps(obj).encode())

        def do_GET(self):
            if self.path == "/api/estado":
                return self._json(servicio.estado())
            ruta = "index.html" if self.path in ("", "/") else self.path.lstrip("/")
            archivo = os.path.normpath(os.path.join(FRONT, ruta))
            if not archivo.startswith(FRONT) or not os.path.isfile(archivo):
                return self._enviar(404, "text/plain", b"No encontrado")
            with open(archivo, "rb") as f:
                self._enviar(200, MIME.get(os.path.splitext(archivo)[1], "application/octet-stream"), f.read())

        def do_POST(self):
            if self.path not in rutas:
                return self._json({"error": "ruta inexistente"}, 404)
            try:
                datos = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or "{}")
                self._json(rutas[self.path](datos))
            except (ValueError, TypeError) as e:
                self._json({"error": str(e)}, 400)

        def log_message(self, *args):
            pass

    return HTTPServer((C.HOST, C.PORT), Handler)
