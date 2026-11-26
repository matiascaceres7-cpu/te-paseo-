"""Capa de dominio: reglas de negocio (matching, cobro, calificación, soporte, publicidad)."""
import math
import random
import uuid
from . import config as C


def _dist(p, x, y):
    return math.hypot(p["x"] - x, p["y"] - y)   # 1 unidad = 1 km


def _limpiar(d):
    """Valida y normaliza lo que llega desde el navegador."""
    num = lambda k, lo, hi, df: min(hi, max(lo, float(d.get(k, df))))
    perros = d.get("perros")
    if not isinstance(perros, list) or not perros:
        perros = [{"nombre": d.get("perro", "Tu perro"), "perfil": d.get("perfil"),
                   "tamano": d.get("tamano")}]
    perros = perros[:5]
    normalizados = []
    for perro in perros:
        if not isinstance(perro, dict):
            perro = {}
        tamano = perro.get("tamano") if perro.get("tamano") in C.TAMANOS else "chico"
        perfil = perro.get("perfil") if perro.get("perfil") in ("docil", "energetico", "experto") else "docil"
        nombre = str(perro.get("nombre", "")).strip()[:40] or "Tu perro"
        normalizados.append({"nombre": nombre, "perfil": perfil, "tamano": tamano})
    tipo_paseador = d.get("tipo_paseador")
    if tipo_paseador not in ("cualquiera", "vip", "nuevo"):
        tipo_paseador = "cualquiera"
    return {"x": num("x", -20, 20, 4), "y": num("y", -20, 20, 4),
            "duracion": int(num("duracion", 30, 60, 30)), "bolsas": int(num("bolsas", 0, 5, 0)),
            "propina": num("propina", 0, 50000, 0), "perros": normalizados,
            "tipo_paseador": tipo_paseador}


class TePaseo:
    def __init__(self, repo):
        self.repo = repo
        self.pagos = {}

    def estado(self):
        vista = ("id", "nombre", "nota", "categoria", "x", "y")   # el usuario no ve datos internos de la plataforma
        return {"paseadores": [{k: p[k] for k in vista} for p in self.repo.paseadores],
                "centro": self.repo.centro}

    def _candidatos(self, x, y, perros, tipo_paseador):
        c = list(self.repo.paseadores)
        if any(perro["perfil"] == "experto" for perro in perros):
            c = [p for p in c if p["nota"] >= C.NOTA_EXPERTO]
        if tipo_paseador != "cualquiera":
            c = [p for p in c if p["categoria"] == tipo_paseador]
        return sorted(c, key=lambda p: _dist(p, x, y) - p["nota"] * 0.3)   # cercanía + calificación

    @staticmethod
    def _cobrar(d):
        cantidad = len(d["perros"])
        base_individual = C.TARIFA_30 * d["duracion"] / 30
        base = base_individual * (1 + 0.6 * (cantidad - 1))
        premium = sum(C.PREMIUM for perro in d["perros"] if perro["perfil"] == "experto")
        tamano = sum(C.TAMANOS[perro["tamano"]] * d["duracion"] / 30 for perro in d["perros"])
        bolsas = d["bolsas"] * C.BOLSA
        sub = base + premium + tamano + bolsas
        recargo_vip = 2000 if d["tipo_paseador"] == "vip" else 0
        sub += recargo_vip
        com = sub * C.COMISION
        return {"base": base, "premium": premium, "cantidad_perros": cantidad,
                "perros": [perro["nombre"] for perro in d["perros"]],
                "extra_tamano": tamano, "costo_bolsas": bolsas, "duracion": d["duracion"], "bolsas": d["bolsas"],
                "propina": d["propina"], "recargo_vip": recargo_vip,
                "total": sub + d["propina"], "comision": com,
                "pago": sub - com + d["propina"]}     # la propina va 100% al paseador

    def solicitar(self, datos):
        d = _limpiar(datos)
        x, y = d["x"], d["y"]
        ofertas, elegido = [], None
        for p in self._candidatos(x, y, d["perros"], d["tipo_paseador"]):
            ok = random.random() < C.PROB_ACEPTAR
            ofertas.append({"nombre": p["nombre"], "nota": p["nota"], "categoria": p["categoria"],
                            "km": round(_dist(p, x, y), 1), "acepto": ok})
            if ok:
                elegido = p
                break
        if not elegido:
            return {"ok": False, "ofertas": ofertas}

        ox, oy = elegido["x"], elegido["y"]
        llegada = [[ox + (x - ox) * i / 10, oy + (y - oy) * i / 10] for i in range(11)]
        ruta, cx, cy = [], x, y
        for _ in range(max(8, d["duracion"] // 3)):
            cx += random.uniform(-.5, .5)
            cy += random.uniform(-.5, .5)
            ruta.append([cx, cy])
        ruta.append([x, y])

        boleta = self._cobrar(d)
        pago_id = uuid.uuid4().hex
        self.pagos[pago_id] = {"paseador": elegido["id"], "boleta": boleta, "confirmado": False}
        elegido.update(x=x, y=y)
        return {"ok": True, "ofertas": ofertas, "paseador": elegido["nombre"], "pid": elegido["id"],
                "categoria": elegido["categoria"], "deposito": elegido["deposito"], "llegada": llegada,
                "ruta": ruta, "boleta": boleta,
                "pago_id": pago_id}

    def confirmar_pago(self, d):
        pago = self.pagos.get(d.get("pago_id"))
        if not pago:
            raise ValueError("pago inválido o inexistente")
        if not pago["confirmado"]:
            paseador = next(p for p in self.repo.paseadores if p["id"] == pago["paseador"])
            boleta = pago["boleta"]
            paseador.update(paseos=paseador["paseos"] + 1,
                            ganancias=paseador["ganancias"] + boleta["pago"])
            self.repo.ingresos += boleta["comision"]
            self.repo.paseos.append({"paseador": paseador["id"], "total": boleta["total"]})
            pago["confirmado"] = True
        return {"ok": True, "total": pago["boleta"]["total"]}

    def ubicacion(self, d):
        """Centra la simulación en la ubicación real del usuario y deja paseadores cerca de él."""
        lat, lng = float(d.get("lat")), float(d.get("lng"))
        if not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError("coordenadas inválidas")
        self.repo.reubicar(lat, lng)
        return self.estado()

    def cotizar(self, d):
        """Precio estimado según duración, perfil del perro, bolsas y propina."""
        return self._cobrar(_limpiar(d))

    def calificar(self, d):
        p = next((p for p in self.repo.paseadores if p["id"] == d.get("pid")), None)
        nota = min(5, max(1, int(d.get("nota", 5))))
        if p:
            p["nota"] = round((p["nota"] * p["n"] + nota) / (p["n"] + 1), 2)
            p["n"] += 1
        return {"ok": bool(p)}

    def incidencia(self, d):
        self.repo.incidencias.append(d.get("detalle", ""))
        return {"ok": True, "ticket": f"INC-{len(self.repo.incidencias):03d}"}

    def clic_ad(self, d):
        self.repo.publicidad += C.CPC
        return {"ok": True}
