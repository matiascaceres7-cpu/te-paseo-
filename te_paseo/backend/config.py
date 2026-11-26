"""Parámetros del negocio (Business Model Canvas) y del servidor."""
HOST, PORT = "127.0.0.1", 8000
CENTRO = (-33.4489, -70.6693)      # centro del mapa (Santiago). Cámbialo a tu ciudad.

COMISION = 0.20                    # % retenido por Te Paseo (Fuentes de Ingresos)
TARIFA_30 = 6000                   # CLP por 30 minutos
BOLSA = 1500                       # microtransacción: bolsa extra
PREMIUM = 2000                     # recargo por perros que requieren manejo experimentado
DEPOSITO_KIT = 20000               # depósito en garantía del Kit VIP
CPC = 300                          # comisión de afiliación por clic en publicidad B2B
PROB_ACEPTAR = 0.75                # probabilidad de que un paseador acepte
NOTA_EXPERTO = 4.7                 # nota mínima para perros de manejo experimentado
TAMANOS = {"chico": 0, "mediano": 500, "grande": 1000}   # recargo por cada 30 min según tamaño del perro
