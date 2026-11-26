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
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
      :root { --forest:#24553e; --forest-dark:#193e2e; --mint:#e8f1e8; --ink:#20342c; --muted:#758078; --paper:#f6f7f1; --line:#e4e9e1; --orange:#e88a52; }
      html, body, [class*="css"], [data-testid="stMarkdownContainer"] { font-family:'DM Sans',sans-serif; }
      .stApp, [data-testid="stAppViewContainer"] { background:radial-gradient(ellipse at 86% 2%, #e7efe4 0, transparent 26rem),var(--paper); color:var(--ink); }
      [data-testid="stHeader"] { background:transparent; }
      .block-container { max-width:1240px; padding:2rem 2.4rem 3.2rem; }
      [data-testid="stSidebar"] { background:linear-gradient(165deg,#193e2e 0%,#24553e 62%,#2d6549 100%); border-right:0; }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"], [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color:#f4f8f2; }
      [data-testid="stSidebar"] hr { border-color:#ffffff30; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.28rem .3rem; }
      .brand-lockup { padding:1.2rem .8rem 1.5rem; border-bottom:1px solid #ffffff30; margin-bottom:1rem; }
      .brand-lockup .brand-name { font:800 1.8rem Manrope,sans-serif; letter-spacing:-.06em; color:white; }
      .brand-lockup .brand-name span { color:#f5b27c; }
      .brand-lockup .brand-sub { color:#d5e5d7; font-size:.88rem; margin-top:.3rem; }
      .hero-banner { position:relative; overflow:hidden; padding:2.5rem 2.7rem; border-radius:26px; background:linear-gradient(115deg,#193e2e 0%,#2b6548 64%,#4c805a 100%); color:#fff; margin:.2rem 0 1.7rem; box-shadow:0 18px 45px #193e2e24; }
      .hero-banner:after { content:'🐕'; position:absolute; right:5%; bottom:-3.2rem; font-size:12rem; opacity:.12; transform:rotate(-12deg); }
      .hero-banner .eyebrow { color:#cfe6cf; font-size:.75rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; }
      .hero-banner h1 { color:#fff; font:800 clamp(2.2rem,4.7vw,3.8rem)/1.02 Manrope,sans-serif; letter-spacing:-.055em; margin:.65rem 0 .7rem; }
      .hero-banner p { color:#e4eee3; max-width:570px; font-size:1.02rem; margin:0; line-height:1.65; }
      .trust-pills { display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1.2rem; }
      .trust-pill { background:#ffffff19; border:1px solid #ffffff35; border-radius:999px; padding:.42rem .75rem; color:#f4f8f2; font-size:.8rem; font-weight:600; }
      h1,h2,h3 { color:var(--ink); font-family:Manrope,'DM Sans',sans-serif; letter-spacing:-.035em; }
      h2 { margin-top:.3rem; }
      .section-kicker { color:var(--forest); font-size:.74rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; }
      .section-lead { color:var(--muted); margin-top:-.35rem; margin-bottom:1rem; }
      [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--line); border-radius:18px; background:#ffffffd9; box-shadow:0 10px 30px #263b2b0a; }
      [data-testid="stExpander"] { border:1px solid var(--line); border-radius:15px; background:#fff; }
      [data-testid="stExpander"] summary { color:var(--forest); font-weight:700; }
      [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea,
      [data-testid="stSelectbox"] [role="combobox"] { border-radius:11px; }
      [data-testid="stWidgetLabel"] p { color:#42534a; font-weight:650; }
      [data-testid="stMetric"] { background:linear-gradient(145deg,#f3f8f1,#fff); border:1px solid #e4ece1; padding:1rem 1.1rem; border-radius:16px; }
      [data-testid="stMetricLabel"] { color:#718076; }
      [data-testid="stMetricValue"] { color:var(--forest); font-family:Manrope,sans-serif; }
      div.stButton > button { border-radius:11px; font-weight:700; transition:all .18s ease; }
      div.stButton > button[kind="primary"] { background:var(--forest); border-color:var(--forest); color:#fff; min-height:3rem; box-shadow:0 7px 16px #24553e24; }
      div.stButton > button[kind="primary"]:hover { background:var(--forest-dark); border-color:var(--forest-dark); transform:translateY(-1px); }
      [data-testid="stAlert"] { border-radius:13px; }
      [data-testid="stDataFrame"] { border-radius:14px; overflow:hidden; }
      .price-label { color:var(--muted); font-size:.88rem; }
      .price { color:var(--forest); font:800 2.45rem Manrope,sans-serif; letter-spacing:-.05em; margin:.25rem 0; }
      .demo-note { color:#718076; font-size:.82rem; line-height:1.5; }
      .status-chip { display:inline-block; background:#e9f4e9; color:#28573e; padding:.35rem .7rem; border-radius:999px; font-size:.78rem; font-weight:750; }
      .feature-card { min-height:155px; padding:1.15rem; border-radius:16px; border:1px solid var(--line); background:linear-gradient(145deg,#fff,#f8faf6); }
      .feature-icon { font-size:1.65rem; }
      footer { color:#89928a; text-align:center; padding-top:2.5rem; font-size:.84rem; }
      @media(max-width:700px) { .block-container{padding:1.2rem 1rem 2rem}.hero-banner{padding:1.8rem 1.35rem;border-radius:20px}.hero-banner:after{right:-2rem;font-size:8rem}.hero-banner p{max-width:85%} }
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
        "dogs_count": 2, "duration": 30, "bags": 0, "tip": 0,
        "owner_name": "", "owner_email": "", "history": [], "last_result": None,
        "last_quote": None, "last_dogs": [], "payment_done": False,
        "rating_done": False, "incident_ticket": None, "campaign_clicks": 0,
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
    st.markdown(
        '<section class="hero-banner"><div class="eyebrow">🐾 Paseos felices, perros felices</div>'
        '<h1>Un poco de aire fresco<br>les hace bien.</h1>'
        '<p>Cuéntanos sobre tu manada. Encontramos a la persona ideal para su próxima aventura.</p>'
        '<div class="trust-pills"><span class="trust-pill">✓ Paseadores verificados</span>'
        '<span class="trust-pill">⌖ Seguimiento de demostración</span><span class="trust-pill">♥ Hecho para su bienestar</span></div></section>',
        unsafe_allow_html=True,
    )
    form_col, summary_col = st.columns([1.25, 0.75], gap="large")
    with form_col:
        st.markdown('<div class="section-kicker">01 · Tu manada</div><h2>Arma su paseo</h2><p class="section-lead">Personaliza la aventura para cada integrante.</p>', unsafe_allow_html=True)
        with st.container(border=True):
            count = int(st.number_input("¿Cuántos perros salen?", min_value=1, max_value=5, step=1, key="dogs_count"))
            dogs = []
            sizes = {"Pequeño": "chico", "Mediano": "mediano", "Grande": "grande"}
            profiles = {"Tranquilo y dócil": "docil", "Activo y energético": "energetico", "Manejo experto": "experto"}
            for index in range(count):
                with st.expander(f"🐾  Compañero {index + 1}", expanded=True):
                    name_col, size_col, profile_col = st.columns([1.15, 0.9, 1.35])
                    with name_col:
                        name = st.text_input("Nombre", key=f"dog_name_{index}", max_chars=40, placeholder="Ej. Toby")
                    with size_col:
                        size_values = list(sizes.values())
                        selected_size = st.session_state[f"dog_size_{index}"]
                        size_label = st.selectbox("Tamaño", list(sizes), key=f"dog_size_label_{index}", index=size_values.index(selected_size))
                        st.session_state[f"dog_size_{index}"] = sizes[size_label]
                    with profile_col:
                        profile_values = list(profiles.values())
                        selected_profile = st.session_state[f"dog_profile_{index}"]
                        profile_label = st.selectbox("Personalidad", list(profiles), key=f"dog_profile_label_{index}", index=profile_values.index(selected_profile))
                        st.session_state[f"dog_profile_{index}"] = profiles[profile_label]
                    dogs.append({"nombre": name.strip(), "tamano": sizes[size_label], "perfil": profiles[profile_label]})

            st.markdown("##### ⚙️ Detalles del paseo")
            st.selectbox("Duración", [30, 45, 60], format_func=lambda value: f"{value} minutos", key="duration")
            walker_labels = {
                "Mejor coincidencia disponible": "cualquiera",
                "Paseador VIP · mejor calificación": "vip",
                "Darle una oportunidad a alguien nuevo": "nuevo",
            }
            label = st.selectbox("Preferencia de paseador", list(walker_labels), key="walker_label")
            bags_col, tip_col = st.columns(2)
            with bags_col:
                st.number_input("Bolsas extra · $1.500 c/u", min_value=0, max_value=5, step=1, key="bags")
            with tip_col:
                st.number_input("Propina opcional (CLP)", min_value=0, max_value=50000, step=500, key="tip")

    quote = service.cotizar({
        "perros": dogs,
        "duracion": int(st.session_state.duration),
        "tipo_paseador": walker_labels[label],
        "bolsas": int(st.session_state.bags),
        "propina": int(st.session_state.tip),
    })
    st.session_state.last_quote = quote
    with summary_col:
        st.markdown('<div class="section-kicker">02 · Tu estimación</div><h2>Resumen del paseo</h2><p class="section-lead">Transparente y sin sorpresas.</p>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f'<span class="status-chip">✦ {quote["duracion"]} MIN · {quote["cantidad_perros"]} PERRO(S)</span>', unsafe_allow_html=True)
            st.write("")
            st.write(f"**Tarifa base** · {clp(quote['base'])}")
            if quote["extra_tamano"]:
                st.write(f"**Recargo por tamaño** · {clp(quote['extra_tamano'])}")
            if quote["premium"]:
                st.write(f"**Manejo experto** · {clp(quote['premium'])}")
            if quote["costo_bolsas"]:
                st.write(f"**Bolsas extra** · {clp(quote['costo_bolsas'])}")
            if quote["recargo_vip"]:
                st.write(f"**Servicio VIP** · {clp(quote['recargo_vip'])}")
            if quote["propina"]:
                st.write(f"**Propina** · {clp(quote['propina'])}")
            st.divider()
            st.markdown('<div class="price-label">TOTAL ESTIMADO</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price">{clp(quote["total"])}</div>', unsafe_allow_html=True)
            st.caption("Precio de demostración · no se realizará ningún cobro real.")
            if st.button(f"🐕  Solicitar paseo · {clp(quote['total'])}", type="primary", use_container_width=True):
                if any(not dog["nombre"] for dog in dogs):
                    st.error("Escribe el nombre de cada perro para continuar.")
                else:
                    result = service.solicitar({
                        "x": 4, "y": 4, "perros": dogs, "duracion": int(st.session_state.duration),
                        "tipo_paseador": walker_labels[label], "bolsas": int(st.session_state.bags),
                        "propina": int(st.session_state.tip),
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
        st.markdown('<p class="demo-note">🔒 Tus datos no se comparten entre visitantes. La ubicación, los paseadores y el pago son simulados.</p>', unsafe_allow_html=True)

    result = st.session_state.last_result
    if result:
        st.markdown("---")
        st.markdown('<div class="section-kicker">03 · Actualización</div><h2>Resultado de tu solicitud</h2>', unsafe_allow_html=True)
        offer_cols = st.columns(max(1, min(3, len(result.get("ofertas", [])))))
        for index, offer in enumerate(result.get("ofertas", [])):
            with offer_cols[index % len(offer_cols)]:
                with st.container(border=True):
                    st.markdown(f"### {'✅' if offer['acepto'] else '⌛'} {offer['nombre']}")
                    st.write(f"{'Aceptó tu paseo' if offer['acepto'] else 'No está disponible'} · ★ {offer['nota']}")
                    st.caption(f"A {offer['km']} km · {offer['categoria'].upper()}")
        if result["ok"]:
            st.success(f"¡{result['paseador']} aceptó! Este es un paseo simulado; no se ha enviado una reserva real.")
            with st.expander("Ver recibo y acciones", expanded=True):
                st.write(f"**Manada:** {', '.join(dog['nombre'] for dog in st.session_state.last_dogs)}")
                st.write(f"**Total estimado:** {clp(result['boleta']['total'])}")
                action1, action2 = st.columns(2)
                with action1:
                    if st.button("💳 Confirmar pago simulado", disabled=st.session_state.payment_done, use_container_width=True):
                        service.confirmar_pago({"pago_id": result["pago_id"]})
                        st.session_state.payment_done = True
                        st.rerun()
                with action2:
                    if st.session_state.payment_done:
                        st.success("Pago simulado · sin cargo")
                st.divider()
                if not st.session_state.rating_done:
                    rating = st.slider("¿Cómo estuvo la experiencia?", 1, 5, 5, key="rating")
                    if st.button("⭐ Enviar calificación"):
                        service.calificar({"pid": result["pid"], "nota": rating})
                        st.session_state.rating_done = True
                        st.rerun()
                else:
                    st.success("¡Gracias por tu calificación!")
                detail = st.text_area("¿Necesitas reportar una incidencia?", key="incident_detail")
                if st.session_state.incident_ticket:
                    st.success(f"Reporte registrado: {st.session_state.incident_ticket}")
                elif st.button("Enviar reporte"):
                    ticket = service.incidencia({"detalle": detail or "Reporte desde la aplicación"})
                    st.session_state.incident_ticket = ticket["ticket"]
                    st.rerun()
        else:
            st.warning("No encontramos a un paseador disponible. Prueba con otra preferencia.")


def render_seguimiento(service: TePaseo) -> None:
    st.markdown('<div class="section-kicker">⌖ Tu paseo, paso a paso</div>', unsafe_allow_html=True)
    st.title("Seguimiento del paseo")
    result = st.session_state.last_result
    if result and result.get("ok"):
        st.subheader(f"🐾 Paseo de {', '.join(dog['nombre'] for dog in st.session_state.last_dogs)}")
        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Paseador", result["paseador"])
        metric2.metric("Categoría", result["categoria"].upper())
        metric3.metric("Estado", "Pago simulado" if st.session_state.payment_done else "En proceso")
        st.info("La llegada y la ruta se simulan para esta demostración; no hay GPS en tiempo real.")
        mostrar_mapa(service, result)
    else:
        st.info("Todavía no tienes un paseo. Ve a **Reservar** para solicitar uno de demostración.")
        mostrar_mapa(service)


def render_historial() -> None:
    st.markdown('<div class="section-kicker">◷ Recuerdos de la manada</div>', unsafe_allow_html=True)
    st.title("Paseos anteriores")
    if not st.session_state.history:
        with st.container(border=True):
            st.markdown("### 🐾 La próxima aventura empieza aquí")
            st.write("Cuando solicites un paseo, aparecerá en este historial.")
        return
    st.caption("Tus paseos de esta sesión")
    for item in st.session_state.history:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.markdown(f"### 🐕 {item['perros']} <span class='muted'>con {item['paseador']}</span>", unsafe_allow_html=True)
            right.markdown(f"<div class='price'>{clp(item['total'])}</div>", unsafe_allow_html=True)
    if st.button("Limpiar historial de esta sesión"):
        st.session_state.history = []
        st.rerun()
    st.caption("El historial se mantiene solo en esta sesión y no se comparte entre visitantes.")


def render_cuenta() -> None:
    st.markdown('<div class="section-kicker">♙ Tu espacio personal</div>', unsafe_allow_html=True)
    st.title("Mi cuenta")
    st.caption("Perfil de demostración. No se requiere iniciar sesión y los datos no se almacenan en una base compartida.")
    profile_col, pack_col = st.columns([1, 1], gap="large")
    with profile_col:
        with st.container(border=True):
            st.subheader("👋 Perfil del hogar")
            with st.form("account_form"):
                st.text_input("Nombre", key="owner_name")
                st.text_input("Correo electrónico", key="owner_email")
                saved = st.form_submit_button("Guardar perfil", type="primary", use_container_width=True)
            if saved:
                st.success("Perfil guardado durante esta sesión.")
    with pack_col:
        with st.container(border=True):
            st.subheader("🐶 La manada")
            dogs = st.session_state.get("last_dogs", [])
            if dogs:
                for dog in dogs:
                    st.markdown(f"**🐾 {dog['nombre']}** · {dog['tamano']} · {dog['perfil']}")
            else:
                st.info("Tus perros aparecerán aquí después de una solicitud de paseo.")


def render_promociones(service: TePaseo) -> None:
    st.markdown('<div class="section-kicker">✦ Beneficios para la manada</div>', unsafe_allow_html=True)
    st.title("Un mimo extra para ellos")
    st.caption("Promociones simuladas. No se realizan compras ni cargos.")
    campaigns = [
        ("🦴", "Pet Feliz", "10% de descuento en alimento premium", "Nutrición rica y equilibrada para cada aventura."),
        ("🩺", "VetCerca", "Primera consulta de orientación gratis", "Resuelve tus dudas con un equipo veterinario cercano."),
        ("🎾", "Mundo Mascota", "15% en pecheras y juguetes", "Accesorios seleccionados para paseos entretenidos."),
    ]
    cols = st.columns(3, gap="medium")
    for col, (icon, name, offer, detail) in zip(cols, campaigns):
        with col:
            with st.container(border=True):
                st.markdown(f"<div class='feature-icon'>{icon}</div>", unsafe_allow_html=True)
                st.subheader(name)
                st.write(detail)
                st.success(offer)
                if st.button("Ver beneficio", key=f"campaign_{name}", use_container_width=True):
                    service.clic_ad({})
                    st.session_state.campaign_clicks += 1
                    st.toast("Beneficio activado (demostración)")
    st.caption(f"Interacciones durante esta sesión: {st.session_state.campaign_clicks}")


def main() -> None:
    inicializar_estado()
    service = servicio_actual()
    with st.sidebar:
        st.markdown('<div class="brand-lockup"><div class="brand-name">🐕 te paseo<span>!</span></div><div class="brand-sub">Una aventura para cada patita</div></div>', unsafe_allow_html=True)
        page = st.radio("EXPLORA", ["Reservar", "Seguimiento", "Historial", "Mi cuenta", "Promociones"], label_visibility="visible")
        st.divider()
        st.markdown("**🐾 Hecho para la manada**")
        st.caption("Prototipo web público. Los pedidos, mapas y pagos de esta versión son simulados.")
        st.markdown("<br><span style='color:#cfe6cf;font-size:.78rem'>● Servicio de demostración</span>", unsafe_allow_html=True)
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
    st.markdown("<footer>© Te Paseo! &nbsp;·&nbsp; Hecho para que cada paseo termine con una cola feliz. ♥</footer>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
