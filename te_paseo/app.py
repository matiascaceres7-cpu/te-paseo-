"""Te Paseo! — aplicación web para Streamlit Community Cloud.

Ejecutar desde la raíz del repositorio:
    streamlit run te_paseo/app.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Permite ejecutar este archivo tanto desde la raíz del repositorio como desde
# te_paseo/, que es el directorio recomendado al desplegar en Streamlit Cloud.
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from backend.datos import Repositorio  # noqa: E402
from backend.servicios import TePaseo  # noqa: E402

st.set_page_config(
    page_title="Te Paseo! | Paseos felices",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
      .stApp { background: radial-gradient(ellipse at 10% 5%, #e8efe2 0, transparent 30rem), #f7f8f3; }
      html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
      .block-container { max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem; }
      [data-testid="stSidebar"] { background: #fff; border-right: 1px solid #e8ebe4; }
      .hero { padding: 1.3rem 0 1.8rem; }
      .eyebrow { color: #376b4f; font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
      .hero h1 { color: #20342c; font-size: clamp(2.2rem, 5vw, 3.7rem); line-height: 1.04; letter-spacing: -.05em; margin: .55rem 0; }
      .hero p, .muted { color: #748078; }
      .card { background: white; border: 1px solid #e8ebe4; border-radius: 18px; padding: 1.15rem 1.25rem; box-shadow: 0 12px 36px #263b2b0d; margin-bottom: 1rem; }
      .price { color: #376b4f; font-size: 1.8rem; font-weight: 800; }
      .dog-title { color: #376b4f; font-weight: 700; }
      .small-note { color: #748078; font-size: .86rem; }
      div.stButton > button[kind="primary"] { background: #376b4f; border-color: #376b4f; border-radius: 10px; font-weight: 700; }
      div.stButton > button[kind="primary"]:hover { background: #28573e; border-color: #28573e; }
      footer { color: #89928a; text-align: center; padding-top: 2rem; font-size: .85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def servicio_actual() -> TePaseo:
    """Cada visitante obtiene su propia instancia; no se comparten pagos ni datos."""
    if "te_paseo_service" not in st.session_state:
        st.session_state.te_paseo_service = TePaseo(Repositorio())
    return st.session_state.te_paseo_service


def inicializar_estado() -> None:
    defaults = {
        "dogs_count": 2,
        "duration": 30,
        "walker_type": "cualquiera",
        "bags": 0,
        "tip": 0,
        "owner_name": "",
        "owner_email": "",
        "history": [],
        "last_result": None,
        "last_quote": None,
        "last_dogs": [],
        "payment_done": False,
        "rating_done": False,
        "incident_ticket": None,
        "campaign_clicks": 0,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    dog_defaults = [
        {"nombre": "Toby", "tamano": "mediano", "perfil": "energetico"},
        {"nombre": "Luna", "tamano": "chico", "perfil": "docil"},
    ]
    for index in range(5):
        dog = dog_defaults[index] if index < len(dog_defaults) else {"nombre": "", "tamano": "chico", "perfil": "docil"}
        st.session_state.setdefault(f"dog_name_{index}", dog["nombre"])
        st.session_state.setdefault(f"dog_size_{index}", dog["tamano"])
        st.session_state.setdefault(f"dog_profile_{index}", dog["perfil"])


def clp(value: float) -> str:
    return f"${round(value):,}".replace(",", ".")


def perros_del_formulario() -> list[dict[str, str]]:
    dogs = []
    for index in range(st.session_state.dogs_count):
        dogs.append({
            "nombre": st.session_state.get(f"dog_name_{index}", "").strip(),
            "tamano": st.session_state.get(f"dog_size_{index}", "chico"),
            "perfil": st.session_state.get(f"dog_profile_{index}", "docil"),
        })
    return dogs


def a_coordenadas(lat: float, lng: float, x: float, y: float) -> tuple[float, float]:
    """Convierte la grilla de simulación (km) a coordenadas para el mapa."""
    cos_lat = math.cos(math.radians(lat))
    return lat - (y - 4) / 111, lng + (x - 4) / (111 * max(cos_lat, 0.01))


def mostrar_mapa(service: TePaseo, result: dict | None = None) -> None:
    state = service.estado()
    lat, lng = state["centro"]
    points = [{"lat": lat, "lon": lng, "tipo": "📍 Tu ubicación"}]
    for walker in state["paseadores"]:
        wlat, wlng = a_coordenadas(lat, lng, walker["x"], walker["y"])
        points.append({"lat": wlat, "lon": wlng, "tipo": f"🚶 {walker['nombre']}"})
    if result and result.get("ok") and result.get("llegada"):
        x, y = result["llegada"][0]
        wlat, wlng = a_coordenadas(lat, lng, x, y)
        points.append({"lat": wlat, "lon": wlng, "tipo": f"🚶 {result['paseador']} · en camino"})
    st.map(pd.DataFrame(points), latitude="lat", longitude="lon", size=30, color="#376b4f", zoom=12)
    st.caption("Mapa de demostración centrado en Santiago. Los paseadores y recorridos son simulados.")


def render_reserva(service: TePaseo) -> None:
    st.markdown('<div class="hero"><div class="eyebrow">🐾 Un paseo a su medida</div><h1>Un poco de aire fresco<br>les hace bien.</h1><p>Cuéntanos sobre tu manada. Encontramos a la persona ideal para su próxima aventura.</p></div>', unsafe_allow_html=True)
    form_col, summary_col = st.columns([1.2, 0.8], gap="large")
    with form_col:
        st.markdown('<div class="card"><span class="dog-title">🐶 ¿Quiénes salen hoy?</span><p class="small-note">Puedes reservar para hasta cinco perros.</p></div>', unsafe_allow_html=True)
        count = st.number_input("Cantidad de perros", min_value=1, max_value=5, step=1, key="dogs_count")
        dogs = []
        sizes = {"Pequeño": "chico", "Mediano": "mediano", "Grande": "grande"}
        profiles = {"Tranquilo y dócil": "docil", "Activo y energético": "energetico", "Manejo experto": "experto"}
        for index in range(int(count)):
            with st.expander(f"🐾 Compañero {index + 1}", expanded=True):
                name_col, size_col, profile_col = st.columns([1.2, 1, 1.3])
                with name_col:
                    name = st.text_input("Nombre", key=f"dog_name_{index}", max_chars=40, placeholder="Ej. Toby")
                with size_col:
                    size_label = st.selectbox("Tamaño", list(sizes), key=f"dog_size_{index}", index=list(sizes.values()).index(st.session_state[f"dog_size_{index}"]))
                with profile_col:
                    profile_label = st.selectbox("Personalidad", list(profiles), key=f"dog_profile_{index}", index=list(profiles.values()).index(st.session_state[f"dog_profile_{index}"]))
                dogs.append({"nombre": name.strip(), "tamano": sizes[size_label], "perfil": profiles[profile_label]})
        st.selectbox("Duración del paseo", [30, 45, 60], format_func=lambda value: f"{value} minutos", key="duration")
        walker_labels = {
            "Mejor coincidencia disponible": "cualquiera",
            "Paseador VIP · mejor calificación": "vip",
            "Darle una oportunidad a alguien nuevo": "nuevo",
        }
        label = st.selectbox("Preferencia de paseador", list(walker_labels), key="walker_label")
        st.session_state.walker_type = walker_labels[label]
        bag_col, tip_col = st.columns(2)
        with bag_col:
            st.number_input("Bolsas extra · $1.500 c/u", min_value=0, max_value=5, step=1, key="bags")
        with tip_col:
            st.number_input("Propina opcional (CLP)", min_value=0, max_value=50000, step=500, key="tip")

    quote = service.cotizar({
        "perros": dogs,
        "duracion": int(st.session_state.duration),
        "tipo_paseador": st.session_state.walker_type,
        "bolsas": int(st.session_state.bags),
        "propina": int(st.session_state.tip),
    })
    st.session_state.last_quote = quote
    with summary_col:
        st.markdown("### 💚 Resumen estimado")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f"Paseo de {quote['duracion']} min · {quote['cantidad_perros']} perro(s)")
        st.write(f"Tarifa base: **{clp(quote['base'])}**")
        if quote["extra_tamano"]:
            st.write(f"Recargo por tamaño: **{clp(quote['extra_tamano'])}**")
        if quote["premium"]:
            st.write(f"Manejo experto: **{clp(quote['premium'])}**")
        if quote["costo_bolsas"]:
            st.write(f"Bolsas extra: **{clp(quote['costo_bolsas'])}**")
        if quote["recargo_vip"]:
            st.write(f"Servicio VIP: **{clp(quote['recargo_vip'])}**")
        if quote["propina"]:
            st.write(f"Propina: **{clp(quote['propina'])}**")
        st.markdown(f'<div class="price">{clp(quote["total"])}</div><span class="small-note">Precio de demostración · no se realizará ningún cobro real.</span></div>', unsafe_allow_html=True)
        st.info("La ubicación, los paseadores y el pago de esta versión son simulados.")
        if st.button(f"🐕 Solicitar paseo · {clp(quote['total'])}", type="primary", use_container_width=True):
            missing = [dog for dog in dogs if not dog["nombre"]]
            if missing:
                st.error("Escribe el nombre de cada perro para continuar.")
            else:
                result = service.solicitar({
                    "x": 4, "y": 4, "perros": dogs,
                    "duracion": int(st.session_state.duration),
                    "tipo_paseador": st.session_state.walker_type,
                    "bolsas": int(st.session_state.bags), "propina": int(st.session_state.tip),
                })
                st.session_state.last_result = result
                st.session_state.last_dogs = dogs
                st.session_state.payment_done = False
                st.session_state.rating_done = False
                st.session_state.incident_ticket = None
                if result["ok"]:
                    st.session_state.history.insert(0, {
                        "perros": ", ".join(dog["nombre"] for dog in dogs),
                        "paseador": result["paseador"], "total": result["boleta"]["total"],
                    })
                st.rerun()

    result = st.session_state.last_result
    if result:
        st.divider()
        st.subheader("Resultado de la solicitud")
        for offer in result.get("ofertas", []):
            badge = "✅ Aceptó" if offer["acepto"] else "⏳ No disponible"
            st.write(f"{badge} · **{offer['nombre']}** · ★ {offer['nota']} · {offer['km']} km")
        if result["ok"]:
            st.success(f"¡{result['paseador']} aceptó! Este es un paseo simulado; no se ha enviado una reserva real.")
            with st.expander("Ver resumen y acciones"):
                st.write(f"Perros: {', '.join(dog['nombre'] for dog in st.session_state.last_dogs)}")
                st.write(f"Total estimado: **{clp(result['boleta']['total'])}**")
                if st.button("Confirmar pago simulado", disabled=st.session_state.payment_done):
                    service.confirmar_pago({"pago_id": result["pago_id"]})
                    st.session_state.payment_done = True
                    st.rerun()
                if st.session_state.payment_done:
                    st.success("Pago simulado confirmado. No se realizó ningún cargo.")
                if not st.session_state.rating_done:
                    rating = st.slider("Califica el servicio", 1, 5, 5, key="rating")
                    if st.button("Enviar calificación"):
                        service.calificar({"pid": result["pid"], "nota": rating})
                        st.session_state.rating_done = True
                        st.rerun()
                else:
                    st.success("¡Gracias por tu calificación!")
                detail = st.text_area("¿Quieres reportar una incidencia?", key="incident_detail")
                if st.session_state.incident_ticket:
                    st.success(f"Reporte registrado: {st.session_state.incident_ticket}")
                elif st.button("Enviar reporte"):
                    ticket = service.incidencia({"detalle": detail or "Reporte desde la aplicación"})
                    st.session_state.incident_ticket = ticket["ticket"]
                    st.rerun()
        else:
            st.warning("No encontramos a un paseador disponible. Prueba con otra preferencia.")


def render_seguimiento(service: TePaseo) -> None:
    st.title("⌖ Seguimiento del paseo")
    result = st.session_state.last_result
    if result and result.get("ok"):
        st.subheader(f"Paseo de {', '.join(dog['nombre'] for dog in st.session_state.last_dogs)}")
        st.success(f"Paseador asignado: {result['paseador']} · categoría {result['categoria']}")
        st.write("La llegada y la ruta se simulan para esta demostración; no hay GPS en tiempo real.")
        st.write(f"Estado: {'Pago simulado confirmado' if st.session_state.payment_done else 'Esperando confirmación del pago simulado'}")
        mostrar_mapa(service, result)
    else:
        st.info("Todavía no tienes un paseo. Ve a **Reservar** para solicitar uno de demostración.")
        mostrar_mapa(service)


def render_historial() -> None:
    st.title("◷ Paseos anteriores")
    if not st.session_state.history:
        st.info("La próxima aventura empieza aquí. Cuando solicites un paseo, aparecerá en este historial.")
        return
    for item in st.session_state.history:
        left, right = st.columns([4, 1])
        left.markdown(f"**{item['perros']}** con {item['paseador']}")
        right.markdown(f"**{clp(item['total'])}**")
        st.divider()
    if st.button("Limpiar historial de esta sesión"):
        st.session_state.history = []
        st.rerun()
    st.caption("El historial se mantiene en esta sesión del navegador y no se comparte entre visitantes.")


def render_cuenta() -> None:
    st.title("♙ Mi cuenta")
    st.caption("Perfil de demostración. No se requiere iniciar sesión y los datos no se almacenan en una base compartida.")
    with st.form("account_form"):
        st.text_input("Nombre", key="owner_name")
        st.text_input("Correo electrónico", key="owner_email")
        saved = st.form_submit_button("Guardar perfil")
    if saved:
        st.success("Perfil guardado durante esta sesión.")
    dogs = st.session_state.get("last_dogs", [])
    st.subheader("🐾 Tu manada")
    if dogs:
        for dog in dogs:
            st.write(f"**{dog['nombre']}** · {dog['tamano']} · {dog['perfil']}")
    else:
        st.info("Tus perros aparecerán aquí después de una solicitud de paseo.")


def render_promociones(service: TePaseo) -> None:
    st.title("✦ Beneficios para la manada")
    st.caption("Promociones simuladas. No se realizan compras ni cargos.")
    campaigns = [
        ("🦴", "Pet Feliz", "10% de descuento en alimento premium", "Nutrición rica y equilibrada para cada aventura."),
        ("🩺", "VetCerca", "Primera consulta de orientación gratis", "Resuelve tus dudas con un equipo veterinario cercano."),
        ("🎾", "Mundo Mascota", "15% en pecheras y juguetes", "Accesorios seleccionados para paseos entretenidos."),
    ]
    cols = st.columns(3)
    for col, (icon, name, offer, detail) in zip(cols, campaigns):
        with col:
            st.markdown(f"### {icon} {name}")
            st.write(detail)
            st.success(offer)
            if st.button("Ver beneficio", key=f"campaign_{name}"):
                service.clic_ad({})
                st.session_state.campaign_clicks += 1
                st.toast("Beneficio activado (demostración)")
    st.caption(f"Interacciones durante esta sesión: {st.session_state.campaign_clicks}")


def main() -> None:
    inicializar_estado()
    service = servicio_actual()
    with st.sidebar:
        st.markdown("# 🐕 te paseo!")
        st.caption("Paseos felices, perros felices.")
        page = st.radio("Navegación", ["Reservar", "Seguimiento", "Historial", "Mi cuenta", "Promociones"], label_visibility="collapsed")
        st.divider()
        st.caption("Prototipo web público · Los pedidos, mapas y pagos son simulados.")
    if page == "Reservar":
        render_reserva(service)
    elif page == "Seguimiento":
        render_seguimiento(service)
    elif page == "Historial":
        render_historial()
    elif page == "Mi cuenta":
        render_cuenta()
    else:
        render_promociones(service)
    st.markdown("<footer>© Te Paseo! · Hecho para que cada paseo termine con una cola feliz. ♥</footer>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
