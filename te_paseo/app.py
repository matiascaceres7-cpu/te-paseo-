"""Te Paseo! — demo web construida para Streamlit Community Cloud."""
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

st.set_page_config(page_title="Te Paseo! | Paseos felices", page_icon="🐕", layout="wide")

# Paleta clara y de alto contraste: texto oscuro sobre superficies claras y
# controles con fondo blanco explícito, incluso si el visitante usa tema oscuro.
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@600;700;800&display=swap');
      :root { --forest:#24553e; --forest-dark:#193e2e; --ink:#20342c; --body:#34443b; --muted:#59685f; --paper:#f5f7f2; --line:#dce5dc; --orange:#b85b25; }
      html, body, [class*="css"], [data-testid="stMarkdownContainer"] { font-family:'DM Sans',sans-serif; }
      .stApp, [data-testid="stAppViewContainer"] { background:radial-gradient(ellipse at 86% 2%,#e6efe3 0,transparent 27rem),var(--paper); color:var(--ink); }
      [data-testid="stHeader"] { background:transparent; }
      .block-container { max-width:1240px; padding:1.8rem 2.2rem 3rem; }
      [data-testid="stSidebar"] { background:linear-gradient(165deg,#193e2e,#24553e 68%,#2d6549); }
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"], [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color:#fff !important; }
      [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color:#e4eee3 !important; }
      [data-testid="stSidebar"] hr { border-color:#ffffff45; }
      [data-testid="stSidebar"] [data-testid="stRadio"] label { padding:.3rem; }
      .brand-lockup { padding:1rem .7rem 1.4rem; border-bottom:1px solid #ffffff45; margin-bottom:1rem; }
      .brand-name { color:#fff; font:800 1.8rem Manrope,sans-serif; letter-spacing:-.06em; }
      .brand-name span { color:#ffc18e; }
      .brand-sub { color:#e4eee3; font-size:.88rem; margin-top:.3rem; }
      .hero-banner { position:relative; overflow:hidden; padding:2.4rem 2.6rem; border-radius:24px; background:linear-gradient(115deg,#193e2e,#2b6548 68%,#4c805a); color:#fff; margin:.2rem 0 1.7rem; box-shadow:0 16px 38px #193e2e24; }
      .hero-banner:after { content:'🐕'; position:absolute; right:5%; bottom:-3rem; font-size:11rem; opacity:.13; transform:rotate(-12deg); }
      .hero-banner .eyebrow { color:#e0efde; font-size:.76rem; font-weight:800; letter-spacing:.13em; text-transform:uppercase; }
      .hero-banner h1 { color:#fff !important; font:800 clamp(2.15rem,4.6vw,3.7rem)/1.04 Manrope,sans-serif; letter-spacing:-.05em; margin:.6rem 0 .7rem; }
      .hero-banner p { color:#f0f5ed !important; max-width:580px; font-size:1rem; margin:0; line-height:1.65; }
      .trust-pills { display:flex; flex-wrap:wrap; gap:.55rem; margin-top:1.1rem; }
      .trust-pill { background:#ffffff20; border:1px solid #ffffff55; border-radius:999px; padding:.4rem .72rem; color:#fff; font-size:.8rem; font-weight:650; }
      h1,h2,h3,h4,h5 { color:var(--ink) !important; font-family:Manrope,'DM Sans',sans-serif; letter-spacing:-.025em; }
      p, li, [data-testid="stMarkdownContainer"] { color:var(--body); }
      .section-kicker { color:var(--forest); font-size:.75rem; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }
      .section-lead { color:var(--muted) !important; margin-top:-.35rem; margin-bottom:1rem; }
      [data-testid="stVerticalBlockBorderWrapper"] { border:1px solid var(--line); border-radius:17px; background:#fff; box-shadow:0 9px 26px #263b2b0b; }
      [data-testid="stExpander"] { border:1px solid var(--line); border-radius:14px; background:#fff; }
      [data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color:var(--forest) !important; font-weight:700; }
      [data-testid="stWidgetLabel"] p, label { color:#263a30 !important; font-weight:650; }
      [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input, [data-testid="stTextArea"] textarea,
      [data-testid="stSelectbox"] [role="combobox"] { color:#20342c !important; background:#fff !important; border:1px solid #b9c9bc !important; border-radius:10px !important; }
      [data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder { color:#69776d !important; opacity:1; }
      [data-testid="stNumberInput"] button { color:#20342c !important; background:#f2f6f1 !important; }
      [data-testid="stMetric"] { background:#fff; border:1px solid var(--line); padding:1rem; border-radius:15px; }
      [data-testid="stMetricLabel"] { color:#45564b !important; }
      [data-testid="stMetricValue"] { color:var(--forest) !important; font-family:Manrope,sans-serif; }
      div.stButton > button { border-radius:10px; font-weight:700; color:#20342c; border-color:#9bac9f; }
      div.stButton > button[kind="primary"] { background:var(--forest); border-color:var(--forest); color:#fff; min-height:3rem; box-shadow:0 6px 14px #24553e25; }
      div.stButton > button[kind="primary"]:hover { background:var(--forest-dark); border-color:var(--forest-dark); color:#fff; }
      div.stButton > button:focus { outline:3px solid #edaa73; outline-offset:2px; }
      [data-testid="stAlert"] { border-radius:12px; }
      [data-testid="stCaptionContainer"] p, .demo-note { color:#59685f !important; }
      .price-label { color:#59685f; font-size:.84rem; font-weight:700; letter-spacing:.06em; }
      .price { color:var(--forest); font:800 2.4rem Manrope,sans-serif; letter-spacing:-.04em; margin:.2rem 0; }
      .status-chip { display:inline-block; background:#e6f1e6; color:#204d35; padding:.38rem .7rem; border-radius:999px; font-size:.78rem; font-weight:800; }
      .feature-icon { font-size:1.7rem; }
      footer { color:#526158; text-align:center; padding-top:2.4rem; font-size:.84rem; }
      @media(max-width:700px) { .block-container{padding:1.1rem .9rem 2rem}.hero-banner{padding:1.7rem 1.25rem;border-radius:18px}.hero-banner:after{right:-2rem;font-size:7rem}.hero-banner p{max-width:85%} }
    </style>
    """,
    unsafe_allow_html=True,
)

SIZES = {"chico": "Pequeño", "mediano": "Mediano", "grande": "Grande"}
PROFILES = {"docil": "Tranquilo y dócil", "energetico": "Activo y energético", "experto": "Manejo experto"}


def servicio_actual() -> TePaseo:
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
    for i in range(5):
        dog = dog_defaults[i] if i < len(dog_defaults) else {"nombre": "", "tamano": "chico", "perfil": "docil"}
        st.session_state.setdefault(f"dog_name_{i}", dog["nombre"])
        # Compatibilidad con estado viejo: antes estos valores podían guardarse
        # como etiqueta visible (p. ej. "Mediano") en lugar de código interno.
        old_size = st.session_state.get(f"dog_size_{i}", dog["tamano"])
        size_aliases = {"Pequeño": "chico", "Mediano": "mediano", "Grande": "grande"}
        st.session_state[f"dog_size_{i}"] = size_aliases.get(old_size, old_size if old_size in SIZES else dog["tamano"])
        old_profile = st.session_state.get(f"dog_profile_{i}", dog["perfil"])
        profile_aliases = {value: key for key, value in PROFILES.items()}
        st.session_state[f"dog_profile_{i}"] = profile_aliases.get(old_profile, old_profile if old_profile in PROFILES else dog["perfil"])


def clp(value: float) -> str:
    return f"${round(value):,}".replace(",", ".")


def a_coordenadas(lat: float, lng: float, x: float, y: float) -> tuple[float, float]:
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
            for i in range(count):
                with st.expander(f"🐾  Compañero {i + 1}", expanded=True):
                    name_col, size_col, profile_col = st.columns([1.15, 0.9, 1.35])
                    with name_col:
                        name = st.text_input("Nombre", key=f"dog_name_{i}", max_chars=40, placeholder="Ej. Toby")
                    with size_col:
                        size_options = list(SIZES)
                        raw_size = st.session_state.get(f"dog_size_{i}", "chico")
                        # Si hubo un estado de widget antiguo o corrupto, sanea a
                        # un tamaño permitido antes de calcular el índice.
                        size_value = raw_size if raw_size in size_options else "chico"
                        size_index = size_options.index(size_value)
                        size_value = st.selectbox(
                            "Tamaño", size_options, index=size_index,
                            format_func=lambda value: SIZES[value], key=f"dog_size_select_{i}",
                        )
                        st.session_state[f"dog_size_{i}"] = size_value
                    with profile_col:
                        profile_options = list(PROFILES)
                        raw_profile = st.session_state.get(f"dog_profile_{i}", "docil")
                        profile_value = raw_profile if raw_profile in profile_options else "docil"
                        profile_value = st.selectbox(
                            "Personalidad", profile_options, index=profile_options.index(profile_value),
                            format_func=lambda value: PROFILES[value], key=f"dog_profile_select_{i}",
                        )
                        st.session_state[f"dog_profile_{i}"] = profile_value
                    dogs.append({"nombre": name.strip(), "tamano": size_value, "perfil": profile_value})
            st.markdown("##### ⚙️ Detalles del paseo")
            st.selectbox("Duración", [30, 45, 60], format_func=lambda value: f"{value} minutos", key="duration")
            walker_labels = {
                "Mejor coincidencia disponible": "cualquiera",
                "Paseador VIP · mejor calificación": "vip",
                "Darle una oportunidad a alguien nuevo": "nuevo",
            }
            walker_label = st.selectbox("Preferencia de paseador", list(walker_labels), key="walker_label")
            bags_col, tip_col = st.columns(2)
            with bags_col:
                st.number_input("Bolsas extra · $1.500 c/u", min_value=0, max_value=5, step=1, key="bags")
            with tip_col:
                st.number_input("Propina opcional (CLP)", min_value=0, max_value=50000, step=500, key="tip")

    quote = service.cotizar({
        "perros": dogs, "duracion": int(st.session_state.duration),
        "tipo_paseador": walker_labels[walker_label], "bolsas": int(st.session_state.bags),
        "propina": int(st.session_state.tip),
    })
    st.session_state.last_quote = quote
    with summary_col:
        st.markdown('<div class="section-kicker">02 · Tu estimación</div><h2>Resumen del paseo</h2><p class="section-lead">Transparente y sin sorpresas.</p>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f'<span class="status-chip">✦ {quote["duracion"]} MIN · {quote["cantidad_perros"]} PERRO(S)</span>', unsafe_allow_html=True)
            st.write("")
            st.write(f"**Tarifa base** · {clp(quote['base'])}")
            for key, label in [("extra_tamano", "Recargo por tamaño"), ("premium", "Manejo experto"), ("costo_bolsas", "Bolsas extra"), ("recargo_vip", "Servicio VIP"), ("propina", "Propina")]:
                if quote[key]:
                    st.write(f"**{label}** · {clp(quote[key])}")
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
                        "tipo_paseador": walker_labels[walker_label], "bolsas": int(st.session_state.bags),
                        "propina": int(st.session_state.tip),
                    })
                    st.session_state.last_result = result
                    st.session_state.last_dogs = dogs
                    st.session_state.payment_done = False
                    st.session_state.rating_done = False
                    st.session_state.incident_ticket = None
                    if result["ok"]:
                        st.session_state.history.insert(0, {
                            "perros": ", ".join(d["nombre"] for d in dogs),
                            "paseador": result["paseador"], "total": result["boleta"]["total"],
                        })
                    st.rerun()
        st.markdown('<p class="demo-note">🔒 Tus datos no se comparten entre visitantes. Ubicación, paseadores y pago son simulados.</p>', unsafe_allow_html=True)

    result = st.session_state.last_result
    if result:
        st.markdown("---")
        st.markdown('<div class="section-kicker">03 · Actualización</div><h2>Resultado de tu solicitud</h2>', unsafe_allow_html=True)
        offers = result.get("ofertas", [])
        if offers:
            offer_cols = st.columns(min(3, len(offers)))
            for i, offer in enumerate(offers):
                with offer_cols[i % len(offer_cols)]:
                    with st.container(border=True):
                        st.markdown(f"### {'✅' if offer['acepto'] else '⌛'} {offer['nombre']}")
                        st.write(f"{'Aceptó tu paseo' if offer['acepto'] else 'No está disponible'} · ★ {offer['nota']}")
                        st.caption(f"A {offer['km']} km · {offer['categoria'].upper()}")
        if result["ok"]:
            st.success(f"¡{result['paseador']} aceptó! Este es un paseo simulado; no se ha enviado una reserva real.")
            with st.expander("Ver recibo y acciones", expanded=True):
                st.write(f"**Manada:** {', '.join(d['nombre'] for d in st.session_state.last_dogs)}")
                st.write(f"**Total estimado:** {clp(result['boleta']['total'])}")
                if st.button("💳 Confirmar pago simulado", disabled=st.session_state.payment_done):
                    service.confirmar_pago({"pago_id": result["pago_id"]})
                    st.session_state.payment_done = True
                    st.rerun()
                if st.session_state.payment_done:
                    st.success("Pago simulado confirmado; no se realizó ningún cargo.")
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
        st.subheader(f"🐾 Paseo de {', '.join(d['nombre'] for d in st.session_state.last_dogs)}")
        c1, c2, c3 = st.columns(3)
        c1.metric("Paseador", result["paseador"])
        c2.metric("Categoría", result["categoria"].upper())
        c3.metric("Estado", "Pago simulado" if st.session_state.payment_done else "En proceso")
        st.info("La llegada y la ruta se simulan; no hay GPS en tiempo real.")
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
            left.markdown(f"### 🐕 {item['perros']} · con {item['paseador']}")
            right.markdown(f"<div class='price'>{clp(item['total'])}</div>", unsafe_allow_html=True)
    if st.button("Limpiar historial de esta sesión"):
        st.session_state.history = []
        st.rerun()
    st.caption("El historial vive solo en esta sesión; no se comparte entre visitantes.")


def render_cuenta() -> None:
    st.markdown('<div class="section-kicker">♙ Tu espacio personal</div>', unsafe_allow_html=True)
    st.title("Mi cuenta")
    st.caption("Perfil de demostración: no se requiere iniciar sesión y los datos no se guardan en una base compartida.")
    profile_col, pack_col = st.columns(2, gap="large")
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
                    st.markdown(f"**🐾 {dog['nombre']}** · {SIZES.get(dog['tamano'], 'Pequeño')} · {PROFILES.get(dog['perfil'], 'Tranquilo y dócil')}")
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
        page = st.radio("EXPLORA", ["Reservar", "Seguimiento", "Historial", "Mi cuenta", "Promociones"])
        st.divider()
        st.markdown("**🐾 Hecho para la manada**")
        st.caption("Prototipo web público. Los pedidos, mapas y pagos de esta versión son simulados.")
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
