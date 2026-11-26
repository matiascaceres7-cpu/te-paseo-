// Te Paseo! - experiencia de reserva y seguimiento para hogares con mascotas.
const $ = id => document.getElementById(id);
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const clp = n => '$' + Math.round(n).toLocaleString('es-CL');
const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));
const api = async (ruta, datos) => {
  const respuesta = await fetch('/api/' + ruta, datos ? { method: 'POST', body: JSON.stringify(datos) } : {});
  const resultado = await respuesta.json();
  if (!respuesta.ok) throw new Error(resultado.error || 'Error al comunicarse con el servidor.');
  return resultado;
};

const STORAGE_KEY = 'tePaseo.historial';
const PREFERENCES_KEY = 'tePaseo.preferencias';
const ACCOUNTS_KEY = 'tePaseo.cuentas';
const CAMPAIGNS_KEY = 'tePaseo.campanas';
const DOG_DEFAULTS = [
  { nombre: 'Toby', tamano: 'mediano', perfil: 'energetico' },
  { nombre: 'Luna', tamano: 'chico', perfil: 'docil' }
];
const DEFAULT_ACCOUNTS = [
  { id: 'matias', nombre: 'Matías Cáceres', email: 'matias@email.cl', perros: DOG_DEFAULTS },
  { id: 'sofia', nombre: 'Sofía Rojas', email: 'sofia@email.cl', perros: [{ nombre: 'Mora', tamano: 'grande', perfil: 'docil' }] }
];
const campaigns = [
  { id: 'pet-feliz', icon: '🦴', name: 'Pet Feliz', offer: '10% de descuento en alimento premium', detail: 'Nutrición rica y equilibrada para acompañar cada aventura.' },
  { id: 'vet-cerca', icon: '🩺', name: 'VetCerca', offer: 'Primera consulta de orientación gratis', detail: 'Resuelve tus dudas con un equipo veterinario cercano.' },
  { id: 'mundo-mascota', icon: '🎾', name: 'Mundo Mascota', offer: '15% en pecheras y juguetes', detail: 'Accesorios seleccionados para paseos más entretenidos.' }
];

let historial = [], cuentas = DEFAULT_ACCOUNTS, cuentaActiva = 'matias', metricasCampana = {};
let errorHistorial = false, centro = [-33.4489, -70.6693], home = { x: 4, y: 4 };
let map, capa, yo, enPaseo = false, primeraLectura = true, watchId = null, quoteVersion = 0;
const preferences = { duracion: '30', bolsas: '0', propina: '0', tipoPaseador: 'cualquiera' };

function cargarLocal(key, fallback) {
  try {
    const saved = JSON.parse(localStorage.getItem(key) || 'null');
    return saved === null ? fallback : saved;
  } catch (error) {
    console.error(`No se pudo leer ${key}.`, error);
    return fallback;
  }
}

historial = cargarLocal(STORAGE_KEY, []);
if (!Array.isArray(historial)) { historial = []; errorHistorial = true; }
const cuentasGuardadas = cargarLocal(ACCOUNTS_KEY, null);
if (Array.isArray(cuentasGuardadas) && cuentasGuardadas.length) cuentas = cuentasGuardadas;
const activaGuardada = cargarLocal('tePaseo.cuentaActiva', 'matias');
if (cuentas.some(cuenta => cuenta.id === activaGuardada)) cuentaActiva = activaGuardada;
metricasCampana = cargarLocal(CAMPAIGNS_KEY, {});
const preferenciasGuardadas = cargarLocal(PREFERENCES_KEY, {});
Object.assign(preferences, preferenciasGuardadas);

const cuentaActual = () => cuentas.find(cuenta => cuenta.id === cuentaActiva) || cuentas[0];
const K = 111, cosL = () => Math.cos(centro[0] * Math.PI / 180);
const toLL = (x, y) => [centro[0] - (y - 4) / K, centro[1] + (x - 4) / (K * cosL())];
const fromLL = ll => ({ x: +((ll.lng - centro[1]) * K * cosL() + 4).toFixed(2), y: +((centro[0] - ll.lat) * K + 4).toFixed(2) });
const icono = (text, cls = '') => L.divIcon({ html: `<div class="pin ${cls}">${text}</div>`, className: '', iconSize: [30, 30], iconAnchor: [15, 15] });
const pin = (text, x, y, cls = '') => L.marker(toLL(x, y), { icon: icono(text, cls) }).addTo(capa);
const perrosActuales = () => Array.from($('dogsList').querySelectorAll('.dog-card')).map(card => ({
  nombre: card.querySelector('[data-dog="nombre"]').value.trim(),
  tamano: card.querySelector('[data-dog="tamano"]').value,
  perfil: card.querySelector('[data-dog="perfil"]').value
}));

function guardarCuentas() {
  localStorage.setItem(ACCOUNTS_KEY, JSON.stringify(cuentas));
}

function guardarPreferencias() {
  preferences.duracion = $('dur').value;
  preferences.bolsas = $('bolsas').value;
  preferences.propina = $('propina').value;
  preferences.tipoPaseador = $('tipoPaseador').value;
  localStorage.setItem(PREFERENCES_KEY, JSON.stringify(preferences));
  const cuenta = cuentaActual();
  cuenta.perros = perrosActuales();
  guardarCuentas();
}

function crearPerro(perro = {}, index = 0) {
  const card = document.createElement('div');
  card.className = 'dog-card';
  card.innerHTML = `<div class="dog-card-top"><span>🐾 Compañero ${index + 1}</span>${index ? '<button class="remove-dog" type="button">Quitar</button>' : ''}</div>
    <div class="dog-fields">
      <label>Nombre<input data-dog="nombre" maxlength="40" placeholder="Ej. Toby" value="${escapeHTML(perro.nombre || '')}"></label>
      <label>Tamaño<select data-dog="tamano">
        <option value="chico">Pequeño</option><option value="mediano">Mediano</option><option value="grande">Grande</option>
      </select></label>
      <label>Personalidad<select data-dog="perfil">
        <option value="docil">Tranquilo y dócil</option><option value="energetico">Activo y energético</option><option value="experto">Manejo experto</option>
      </select></label>
    </div>`;
  card.querySelector('[data-dog="tamano"]').value = perro.tamano || 'chico';
  card.querySelector('[data-dog="perfil"]').value = perro.perfil || 'docil';
  const remove = card.querySelector('.remove-dog');
  if (remove) remove.addEventListener('click', () => {
    card.remove();
    renumerarPerros();
    guardarPreferencias();
    cotizar();
  });
  return card;
}

function renumerarPerros() {
  $('dogsList').querySelectorAll('.dog-card').forEach((card, index) => {
    card.querySelector('.dog-card-top > span').textContent = `🐾 Compañero ${index + 1}`;
    const remove = card.querySelector('.remove-dog');
    if (index === 0 && remove) remove.remove();
    if (index > 0 && !remove) {
      const button = document.createElement('button');
      button.className = 'remove-dog';
      button.type = 'button';
      button.textContent = 'Quitar';
      button.addEventListener('click', () => {
        card.remove();
        renumerarPerros();
        guardarPreferencias();
        cotizar();
      });
      card.querySelector('.dog-card-top').append(button);
    }
  });
}

function renderPerros(perros) {
  $('dogsList').replaceChildren();
  const lista = Array.isArray(perros) && perros.length ? perros.slice(0, 5) : [{ nombre: '', tamano: 'chico', perfil: 'docil' }];
  lista.forEach((perro, index) => $('dogsList').append(crearPerro(perro, index)));
}

function pintar(estado) {
  capa.clearLayers();
  estado.paseadores.forEach(paseador => {
    const nivel = paseador.categoria === 'vip' ? 'VIP' : 'Nuevo';
    pin('🚶', paseador.x, paseador.y, 'w').bindTooltip(`${paseador.nombre} · ${nivel} · ★${paseador.nota}`);
  });
}

function log(mensaje, clase = '') {
  const fila = document.createElement('div');
  fila.className = clase;
  fila.innerHTML = mensaje;
  $('log').prepend(fila);
}

function mostrar(vista) {
  const vistas = { pedido: 'vistaPedido', seguimiento: 'vistaSeguimiento', historial: 'vistaHistorial', cuenta: 'vistaCuenta', marketing: 'vistaMarketing' };
  Object.entries(vistas).forEach(([nombre, id]) => { $(id).hidden = nombre !== vista; });
  document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.toggle('active', tab.dataset.view === vista));
  if (vista === 'seguimiento' && map) {
    setTimeout(() => { map.invalidateSize(); map.setView(yo.getLatLng(), 13); }, 40);
    $('nuevo').hidden = enPaseo || !$('boleta').innerHTML;
  }
  if (vista === 'historial') cargarHistorial();
  if (vista === 'cuenta') cargarCuenta();
}

function usarUbicacion(lat, lng) {
  home = fromLL({ lat, lng });
  yo.setLatLng([lat, lng]);
}

function geolocalizar() {
  const fallo = mensaje => {
    $('btn').disabled = false;
    $('gpsTexto').textContent = `⚠ ${mensaje} Usaremos una ubicación de ejemplo.`;
  };
  if (!navigator.geolocation) return fallo('Tu navegador no soporta geolocalización.');
  watchId = navigator.geolocation.watchPosition(async pos => {
    const { latitude: lat, longitude: lng, accuracy } = pos.coords;
    if (primeraLectura) {
      try {
        const estado = await api('ubicacion', { lat, lng });
        centro = estado.centro;
        map.setView([lat, lng], 14);
        pintar(estado);
        primeraLectura = false;
        if (!enPaseo) $('btn').disabled = false;
      } catch (error) {
        fallo(`No pudimos actualizar la ubicación: ${error.message}`);
        return;
      }
    }
    usarUbicacion(lat, lng);
    $('gpsTexto').textContent = `📡 Ubicación en tiempo real activa (±${Math.round(accuracy)} m)`;
  }, error => {
    if (primeraLectura) fallo(error.code === 1 ? 'Permiso de ubicación denegado.' : 'No pudimos obtener tu ubicación.');
  }, { enableHighAccuracy: true, maximumAge: 2000, timeout: 15000 });
}

function cargarHistorial() {
  const ownerId = cuentaActual().id;
  const items = historial.filter(item => !item.ownerId || item.ownerId === ownerId);
  const lista = $('historialLista');
  lista.replaceChildren();
  $('historialOwner').textContent = cuentaActual().nombre;
  $('historialVacio').hidden = items.length > 0;
  $('limpiarHistorial').hidden = items.length === 0 || errorHistorial;
  items.slice(0, 30).forEach(item => {
    const fila = document.createElement('div');
    fila.className = 'history-item';
    const detalle = document.createElement('span');
    const nombre = document.createElement('strong');
    nombre.textContent = `${(item.perros || [item.perro || 'Tu perro']).join(', ')} con ${item.paseador}`;
    const fecha = document.createElement('small');
    fecha.textContent = new Date(item.fecha).toLocaleString('es-CL', { dateStyle: 'medium', timeStyle: 'short' });
    detalle.append(nombre, fecha);
    const total = document.createElement('strong');
    total.textContent = clp(item.total);
    fila.append(detalle, total);
    lista.append(fila);
  });
}

function cargarCuenta() {
  $('accountSelect').replaceChildren();
  cuentas.forEach(cuenta => {
    const option = document.createElement('option');
    option.value = cuenta.id;
    option.textContent = cuenta.nombre;
    $('accountSelect').append(option);
  });
  $('accountSelect').value = cuentaActiva;
  const cuenta = cuentaActual();
  $('ownerName').value = cuenta.nombre;
  $('ownerEmail').value = cuenta.email || '';
  $('accountDogsCount').textContent = `${(cuenta.perros || []).length} compañero${(cuenta.perros || []).length === 1 ? '' : 's'} registrado${(cuenta.perros || []).length === 1 ? '' : 's'}`;
  const lista = $('accountDogs');
  lista.replaceChildren();
  (cuenta.perros || []).forEach(perro => {
    const fila = document.createElement('div');
    fila.className = 'account-dog';
    const detalle = document.createElement('span');
    const nombre = document.createElement('strong');
    nombre.textContent = perro.nombre;
    const info = document.createElement('small');
    info.textContent = `${{ chico: 'Pequeño', mediano: 'Mediano', grande: 'Grande' }[perro.tamano] || 'Pequeño'} · ${{ docil: 'Tranquilo', energetico: 'Energético', experto: 'Manejo experto' }[perro.perfil] || 'Tranquilo'}`;
    detalle.append(nombre, info);
    const icon = document.createElement('span');
    icon.textContent = '🐕';
    fila.append(detalle, icon);
    lista.append(fila);
  });
  $('accountAvatar').textContent = cuenta.nombre.charAt(0).toUpperCase();
  $('accountSwitchName').textContent = cuenta.nombre.split(' ')[0];
}

function fin() {
  enPaseo = false;
  $('btn').disabled = false;
  $('nuevo').hidden = false;
}

async function cotizar() {
  const version = ++quoteVersion;
  const perros = perrosActuales();
  try {
    const boleta = await api('cotizar', {
      perros, duracion: +$('dur').value, tipo_paseador: $('tipoPaseador').value,
      bolsas: +$('bolsas').value, propina: +$('propina').value
    });
    if (version !== quoteVersion) return;
    $('precio').innerHTML = `<div class="row"><span>Paseo de ${boleta.duracion} min · ${boleta.cantidad_perros} perro${boleta.cantidad_perros === 1 ? '' : 's'}</span><span>${clp(boleta.base)}</span></div>` +
      (boleta.cantidad_perros > 1 ? `<div class="row"><span>Tarifa compartida para ${boleta.cantidad_perros} perros</span><span>Descuento aplicado</span></div>` : '') +
      (boleta.costo_bolsas ? `<div class="row"><span>Bolsas extra (${boleta.bolsas})</span><span>${clp(boleta.costo_bolsas)}</span></div>` : '') +
      (boleta.extra_tamano ? `<div class="row"><span>Recargo por tamaño</span><span>${clp(boleta.extra_tamano)}</span></div>` : '') +
      (boleta.premium ? `<div class="row"><span>Manejo experto</span><span>${clp(boleta.premium)}</span></div>` : '') +
      (boleta.recargo_vip ? `<div class="row"><span>Servicio paseador VIP</span><span>${clp(boleta.recargo_vip)}</span></div>` : '') +
      (boleta.propina ? `<div class="row"><span>Propina</span><span>${clp(boleta.propina)}</span></div>` : '') +
      `<div class="row tot"><span>Precio estimado</span><b>${clp(boleta.total)}</b></div>`;
    $('btn').textContent = `Pedir paseador · ${clp(boleta.total)}`;
  } catch (error) {
    $('errorPedido').textContent = `No se pudo calcular el precio: ${error.message}`;
    $('errorPedido').hidden = false;
  }
}

async function pedirPaseo() {
  const perros = perrosActuales();
  const sinNombre = perros.find(perro => !perro.nombre);
  if (sinNombre) {
    $('errorPedido').textContent = 'Escribe el nombre de cada perro para continuar.';
    $('errorPedido').hidden = false;
    $('dogsList').querySelector('[data-dog="nombre"]:placeholder-shown')?.focus();
    return;
  }
  $('errorPedido').hidden = true;
  guardarPreferencias();
  enPaseo = true;
  $('btn').disabled = true;
  $('boleta').style.display = 'none';
  $('boleta').innerHTML = '';
  $('nuevo').hidden = true;
  $('log').replaceChildren();
  $('paseoTitulo').textContent = `Paseo de ${perros.map(perro => perro.nombre).join(' y ')}`;
  mostrar('seguimiento');
  const destino = { ...home };
  log('📍 Usando tu ubicación actual. Buscando paseadores certificados cerca de ti...');
  let resultado;
  try {
    resultado = await api('solicitar', {
      ...destino, perros, tipo_paseador: $('tipoPaseador').value,
      duracion: +$('dur').value, bolsas: +$('bolsas').value, propina: +$('propina').value
    });
  } catch (error) {
    mostrar('pedido');
    $('errorPedido').textContent = `No se pudo pedir el paseo: ${error.message}`;
    $('errorPedido').hidden = false;
    fin();
    return;
  }

  for (const oferta of resultado.ofertas) {
    await sleep(650);
    const categoria = oferta.categoria === 'vip' ? 'VIP' : 'nuevo';
    log(oferta.acepto
      ? `✔ <b>${escapeHTML(oferta.nombre)}</b> · ${categoria} · ★${oferta.nota}, a ${oferta.km} km aceptó`
      : `✘ ${escapeHTML(oferta.nombre)} · ${categoria} · ★${oferta.nota} no está disponible`, oferta.acepto ? 'ok' : 'no');
  }
  if (!resultado.ok) {
    log('No encontramos un paseador disponible para esta selección. Puedes probar con otro tipo de paseador.', 'no');
    fin();
    return;
  }

  pintar(await api('estado'));
  const marcador = L.marker(toLL(...resultado.llegada[0]), { icon: icono('🚶‍♂️') }).addTo(capa);
  const nivel = resultado.categoria === 'vip' ? 'VIP' : 'nuevo';
  log(`✅ <b>${escapeHTML(resultado.paseador)}</b> es paseador ${nivel}. Kit VIP entregado (depósito en garantía ${clp(resultado.deposito)}).`);
  log(`${escapeHTML(resultado.paseador)} va hacia tu ubicación...`);
  for (const [x, y] of resultado.llegada) { marcador.setLatLng(toLL(x, y)); await sleep(180); }
  log(`🔔 ${escapeHTML(resultado.paseador)} llegó para recoger a ${perros.map(perro => escapeHTML(perro.nombre)).join(', ')}`);
  marcador.setIcon(icono('🐕'));
  log(`🐾 Paseo en curso con ${perros.length} perro${perros.length === 1 ? '' : 's'} (GPS en tiempo real)`);
  const huella = L.polyline([], { color: '#f97316', weight: 4 }).addTo(capa);
  for (const [x, y] of resultado.ruta) { marcador.setLatLng(toLL(x, y)); huella.addLatLng(toLL(x, y)); await sleep(220); }
  log('🏠 Paseo finalizado. ¡La manada ya está en casa!', 'ok');
  historial.unshift({ perros: perros.map(perro => perro.nombre), paseador: resultado.paseador,
    total: resultado.boleta.total, fecha: new Date().toISOString(), ownerId: cuentaActual().id });
  historial = historial.slice(0, 100);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(historial));
  cargarHistorial();
  mostrarBoleta(resultado);
  fin();
}

function mostrarBoleta(resultado) {
  const boleta = resultado.boleta;
  const detallePerros = boleta.perros.map(escapeHTML).join(', ');
  $('boleta').innerHTML = `<h3>Resumen de tu paseo</h3>
    <div class="row"><span>Compañeros</span><span>${detallePerros}</span></div>
    <div class="row"><span>Duración</span><span>${boleta.duracion} min</span></div>
    <div class="row"><span>Tarifa de grupo (${boleta.cantidad_perros} perros)</span><span>${clp(boleta.base)}</span></div>
    <div class="row"><span>Bolsas extra</span><span>${boleta.bolsas} · ${clp(boleta.costo_bolsas)}</span></div>
    ${boleta.extra_tamano ? `<div class="row"><span>Recargo por tamaño</span><span>${clp(boleta.extra_tamano)}</span></div>` : ''}
    ${boleta.premium ? `<div class="row"><span>Manejo experto</span><span>${clp(boleta.premium)}</span></div>` : ''}
    ${boleta.recargo_vip ? `<div class="row"><span>Servicio paseador VIP</span><span>${clp(boleta.recargo_vip)}</span></div>` : ''}
    <div class="row"><span>Propina</span><span>${clp(boleta.propina)}</span></div>
    <div class="row tot"><span>Total</span><span>${clp(boleta.total)}</span></div>
    <p class="payment-status" id="estadoPago" aria-live="polite">Pago simulado: no se realizará un cargo real.</p>
    <button class="go" id="pagar">Confirmar pago · ${clp(boleta.total)}</button>
    <h3>Califica a ${escapeHTML(resultado.paseador)}</h3>
    <div class="stars" role="group" aria-label="Calificación del paseo">${[1, 2, 3, 4, 5].map(n => `<button type="button" data-n="${n}" aria-label="${n} estrellas">★</button>`).join('')}</div>
    <button class="go" id="inc">⚠ Reportar incidencia</button>`;
  $('boleta').style.display = 'block';
  $('pagar').onclick = async () => {
    const boton = $('pagar'), estado = $('estadoPago');
    boton.disabled = true;
    estado.textContent = 'Confirmando pago...';
    try {
      await api('confirmar_pago', { pago_id: resultado.pago_id });
      estado.textContent = `¡Pago confirmado! ${clp(boleta.total)} (simulado).`;
      boton.remove();
      log(`💳 Pago confirmado: ${clp(boleta.total)} (simulado).`, 'ok');
    } catch (error) {
      estado.textContent = `No se pudo confirmar el pago: ${error.message}`;
      boton.disabled = false;
    }
  };
  $('boleta').querySelectorAll('.stars button').forEach(button => button.onclick = async () => {
    button.disabled = true;
    try {
      await api('calificar', { pid: resultado.pid, nota: +button.dataset.n });
      $('boleta').querySelector('.stars').textContent = `¡Gracias! Calificaste con ${button.dataset.n} ★`;
      pintar(await api('estado'));
    } catch (error) {
      button.disabled = false;
      $('estadoPago').textContent = `No se pudo guardar la calificación: ${error.message}`;
    }
  });
  $('inc').onclick = async () => {
    const button = $('inc');
    button.disabled = true;
    try {
      const ticket = await api('incidencia', { detalle: `Reporte del hogar ${cuentaActual().id}` });
      button.outerHTML = `<div class="hint">Reporte enviado al soporte In-App. Ticket ${escapeHTML(ticket.ticket)}</div>`;
    } catch (error) {
      button.disabled = false;
      $('estadoPago').textContent = `No se pudo enviar el reporte: ${error.message}`;
    }
  };
}

function renderCampaigns() {
  $('campaigns').replaceChildren();
  campaigns.forEach(campana => {
    const card = document.createElement('article');
    card.className = 'campaign-card';
    const count = Number(metricasCampana[campana.id] || 0);
    card.innerHTML = `<div class="campaign-art" aria-hidden="true">${campana.icon}</div>
      <div class="campaign-content"><span class="campaign-label">Marca asociada</span><h2>${escapeHTML(campana.name)}</h2>
      <p>${escapeHTML(campana.detail)}</p><span class="campaign-terms">${escapeHTML(campana.offer)}</span>
      <button type="button" data-campaign="${campana.id}">${count ? 'Beneficio activado ✓' : 'Ver beneficio'}</button></div>`;
    const button = card.querySelector('button');
    button.disabled = count > 0;
    button.addEventListener('click', async () => {
      button.disabled = true;
      try {
        await api('clic_ad', {});
        metricasCampana[campana.id] = count + 1;
        localStorage.setItem(CAMPAIGNS_KEY, JSON.stringify(metricasCampana));
        button.textContent = 'Beneficio activado ✓';
        $('campaignCount').textContent = `${Object.values(metricasCampana).reduce((sum, value) => sum + Number(value), 0)} interacciones`;
      } catch (error) {
        button.disabled = false;
        button.textContent = `Error: ${error.message}`;
      }
    });
    $('campaigns').append(card);
  });
  $('campaignCount').textContent = `${Object.values(metricasCampana).reduce((sum, value) => sum + Number(value), 0)} interacciones`;
}

async function iniciar() {
  const estado = await api('estado');
  centro = estado.centro;
  map = L.map('map').setView(toLL(4, 4), 14);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map);
  capa = L.layerGroup().addTo(map);
  yo = L.marker(toLL(4, 4), { icon: icono('📍'), zIndexOffset: 1000 }).addTo(map).bindTooltip('Tú');
  pintar(estado);
  const cuenta = cuentaActual();
  renderPerros(cuenta.perros);
  $('dur').value = preferences.duracion;
  $('bolsas').value = preferences.bolsas;
  $('propina').value = preferences.propina;
  $('tipoPaseador').value = preferences.tipoPaseador;

  document.querySelectorAll('[data-view]').forEach(control => control.addEventListener('click', () => {
    const vista = control.dataset.view;
    mostrar(vista);
    if (vista === 'pedido') cotizar();
  }));
  $('accountSwitch').addEventListener('click', () => mostrar('cuenta'));
  $('accountSelect').addEventListener('change', () => {
    cuentaActiva = $('accountSelect').value;
    localStorage.setItem('tePaseo.cuentaActiva', JSON.stringify(cuentaActiva));
    const nueva = cuentaActual();
    renderPerros(nueva.perros);
    cargarCuenta();
    cargarHistorial();
    guardarPreferencias();
    cotizar();
  });
  $('saveAccount').addEventListener('click', () => {
    const nombre = $('ownerName').value.trim();
    const email = $('ownerEmail').value.trim();
    if (!nombre || !email || !$('ownerEmail').checkValidity()) {
      $('accountMessage').textContent = 'Ingresa un nombre y un correo electrónico válido.';
      $('accountMessage').hidden = false;
      return;
    }
    cuentaActual().nombre = nombre;
    cuentaActual().email = email;
    guardarCuentas();
    cargarCuenta();
    cargarHistorial();
    $('accountMessage').textContent = 'Cambios guardados en este dispositivo.';
    $('accountMessage').hidden = false;
  });
  $('addDog').addEventListener('click', () => {
    const perros = perrosActuales();
    if (perros.length >= 5) {
      $('errorPedido').textContent = 'Puedes agregar hasta 5 perros por paseo.';
      $('errorPedido').hidden = false;
      return;
    }
    $('dogsList').append(crearPerro({}, perros.length));
    guardarPreferencias();
    cotizar();
  });
  $('dogsList').addEventListener('input', () => {
    $('errorPedido').hidden = true;
    guardarPreferencias();
    cotizar();
  });
  $('dogsList').addEventListener('change', () => { guardarPreferencias(); cotizar(); });
  ['dur', 'tipoPaseador'].forEach(id => $(id).addEventListener('change', () => { guardarPreferencias(); cotizar(); }));
  ['bolsas', 'propina'].forEach(id => $(id).addEventListener('input', () => { guardarPreferencias(); cotizar(); }));
  $('btn').addEventListener('click', pedirPaseo);
  $('nuevo').addEventListener('click', () => {
    $('log').replaceChildren();
    $('boleta').style.display = 'none';
    $('boleta').innerHTML = '';
    mostrar('pedido');
    cotizar();
  });
  $('reintentarGps').addEventListener('click', () => {
    if (watchId !== null) navigator.geolocation.clearWatch(watchId);
    primeraLectura = true;
    $('gpsTexto').textContent = 'Buscando tu ubicación...';
    geolocalizar();
  });
  $('limpiarHistorial').addEventListener('click', () => {
    if (!confirm('¿Quieres borrar el historial de paseos de esta cuenta en este dispositivo?')) return;
    historial = historial.filter(item => !item.ownerId || item.ownerId !== cuentaActual().id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(historial));
    cargarHistorial();
  });
  renderCampaigns();
  cargarCuenta();
  cargarHistorial();
  cotizar();
  geolocalizar();
}

iniciar().catch(error => {
  console.error('No se pudo iniciar Te Paseo.', error);
  $('btn').disabled = true;
  $('gpsTexto').textContent = `No se pudo cargar la aplicación: ${error.message}`;
});
