"""Capa de datos: repositorio en memoria. Se puede reemplazar por SQLite/PostgreSQL
sin tocar la capa de servicios."""
import random
from . import config as C

PASEADORES = [("Camila Rojas", 4.9), ("Matías Soto", 4.6), ("Javiera Pinto", 4.8),
              ("Diego Muñoz", 4.4), ("Valentina Díaz", 4.7), ("Felipe Araya", 4.5)]


class Repositorio:
    def __init__(self):
        self.centro = C.CENTRO
        self.paseos, self.incidencias = [], []
        self.ingresos = 0.0      # comisiones (solo visible para la plataforma)
        self.publicidad = 0.0    # ingresos B2B
        self.paseadores = [
            {"id": i, "nombre": n, "nota": nota, "n": 84 if nota >= 4.8 else 7,
             "categoria": "vip" if nota >= 4.8 else "nuevo", "paseos": 0, "ganancias": 0,
             "deposito": C.DEPOSITO_KIT, "certificado": True, "x": 4, "y": 4}
            for i, (n, nota) in enumerate(PASEADORES, 1)
        ]
        self.reubicar(*C.CENTRO)

    def reubicar(self, lat, lng):
        """Centra la simulación en la ubicación real del usuario (grilla de 8x8 km, centro en 4,4)."""
        self.centro = (lat, lng)
        for p in self.paseadores:
            p["x"], p["y"] = round(random.uniform(1, 7), 1), round(random.uniform(1, 7), 1)
