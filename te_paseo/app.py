"""Te Paseo! - punto de entrada.  Ejecutar:  python app.py   (solo librería estándar)"""
import webbrowser
from backend import config as C
from backend.datos import Repositorio
from backend.servicios import TePaseo
from backend.servidor import crear_servidor

if __name__ == "__main__":
    url = f"http://{C.HOST}:{C.PORT}"
    servidor = crear_servidor(TePaseo(Repositorio()))
    print(f"Te Paseo! corriendo en {url}  (Ctrl+C para detener)")
    webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
