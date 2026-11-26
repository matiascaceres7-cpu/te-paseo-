# Te Paseo!

Aplicación web de demostración construida con Streamlit. Incluye cotización de paseos, solicitud de paseador, mapa de ejemplo, historial de sesión, cuenta, promociones y acciones de pago/calificación simuladas.

> **Importante:** es un prototipo. No integra pagos reales, geolocalización GPS real, autenticación ni una base de datos compartida. Los datos se mantienen por sesión y pueden perderse al reiniciar la aplicación.

## Ejecutar localmente

Desde la raíz del repositorio:

```bash
pip install -r te_paseo/requirements.txt
streamlit run te_paseo/app.py
```

También puedes entrar a `te_paseo/` y ejecutar `streamlit run app.py`.

## Desplegar en Streamlit Community Cloud

1. Conecta el repositorio público `matiascaceres7-cpu/te-paseo-` en Streamlit Community Cloud.
2. Selecciona la rama que contiene estos cambios (actualmente `streamlit-web`) o integra esa rama en `main`.
3. Configura **Main file path** como `te_paseo/app.py`.
4. Streamlit instalará las dependencias de `te_paseo/requirements.txt`. Si la configuración de tu despliegue no detecta ese archivo, coloca una copia de `requirements.txt` en la raíz del repositorio.
5. Pulsa **Deploy** o reinicia la aplicación para que reconstruya el entorno.

El archivo `app.py` ya no inicia un servidor HTTP propio; Streamlit gestiona el servidor web y el puerto, evitando el `OSError` del `HTTPServer` que ocurría en Streamlit Cloud.
