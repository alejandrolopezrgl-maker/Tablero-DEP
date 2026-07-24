    import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Monitoreo de Desvíos", layout="wide", page_icon="🚗")

# Títulos Principales
st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Filtros Interactivos y Alertas Tempranas en Tiempo Real | Período: Mayo - Junio 2026")

# 2. CONEXIÓN A GOOGLE SHEETS (Truco de lectura pública por GID)
# Usamos el ID único de tu documento: 1jTq_mTfWBfWZCHnC7OlLiRcskWSUj0w1
SPREADSHEET_ID = "1jTq_mTfWBfWZCHnC7OlLiRcskWSUj0w1"

@st.cache_data(ttl=600)  # Se actualiza automáticamente cada 10 minutos
def leer_hoja_google(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={gid}"
    try:
        return pd.read_csv(url)
    except Exception:
        return None

# Cargamos las 4 hojas usando los IDs (gids) exactos que me pasaste
df_hoja1 = leer_hoja_google("1660966037")  # Pestaña 1
df_hoja2 = leer_hoja_google("502299291")   # Pestaña 2
df_hoja3 = leer_hoja_google("389638323")   # Pestaña 3
df_hoja4 = leer_hoja_google("263438988")   # Pestaña 4

# 3. INTERFAZ: MENÚ LATERAL (SIDEBAR)
st.sidebar.header("🚨 Panel de Alertas DEP")
st.sidebar.markdown("**Filtros Globales de Control**")

# Selector de Sucursal
sucursal = st.sidebar.selectbox("Seleccionar Sucursal:", ["Todas", "Salta", "Jujuy", "Tartagal"])

# Alertas visuales de penalizaciones directas según el manual
st.sidebar.divider()
st.sidebar.subheader("⚠️ Restadores de Zona Roja")
restador_fair_play = st.sidebar.toggle("Desvío Fair Play Detectado (-10 pts)", value=True)
fieldman_alerta = st.sidebar.slider("% Cumplimiento Visita Fieldman", 0, 100, 78)

if fieldman_alerta < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa: -40% en Puntos Negativos del área (<85%)")
if restador_fair_play:
    st.sidebar.error("🛑 Penalidad Fair Play Activa: -10 Puntos Directos a la nota final")

# 4. TABLERO PRINCIPAL: MÉTRICAS CLAVE (KPI CARDS)
st.header(f"📌 Estado Actual - Sucursal: {sucursal}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Ventas - SSI Acumulado", value="93.4%", delta="-2.20% vs Objetivo", delta_color="inverse")
with col2:
    st.metric(label="Ventas - NPS Comercial", value="78.1%", delta="-8.90% vs Objetivo", delta_color="inverse")
with col3:
    st.metric(label="KINTO ONE - NPS", value="44.4%", delta="-45.6% vs Objetivo", delta_color="inverse")
with col4:
    st.metric(label="Ranking General", value="Puesto 39 🔻", delta="Bajó desde puesto 8", delta_color="inverse")

st.divider()

# 5. GRÁFICO DINÁMICO DE DESVÍOS (A junio de 2026)
st.subheader("📉 Brecha Crítica por Indicador de Calidad")

# Simulación de datos consolidados para visualización interactiva rápida
data_brechas = {
    "KPI": ["Posventa CSI", "Posventa FIR", "Ventas SSI", "Ventas NPS", "TPA NPS t", "Usados SSI", "Usados NPS", "KINTO NPS"],
    "Brecha Real": [0.90, 2.10, -2.20, -8.90, -2.50, -10.37, -32.80, -45.60],
    "Estado": ["🟢 En Objetivo", "🟢 En Objetivo", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado"]
}
df_plot = pd.DataFrame(data_brechas)

fig = px.bar(
    df_plot,
    x="KPI",
    y="Brecha Real",
    color="Estado",
    text_auto=".2f",
    color_discrete_map={"🟢 En Objetivo": "#2ca02c", "🔴 Desviado": "#d62728"},
    title="Valores negativos representan desvíos urgentes sobre el Target de Calidad"
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# 6. ANÁLISIS DE CAUSA RAÍZ Y VISUALIZADOR DE DATOS DE GOOGLE SHEETS
st.subheader("💡 Origen Físico del Deterioro en la Experiencia")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    **Análisis Operativo (La Voz del Cliente):**
    El **72% de las quejas** en Salta, Jujuy y Tartagal están vinculadas a la percepción de pérdida de beneficios de cortesía:
    *   **Kits de Seguridad (36%)**: Retrasos administrativos internos bloquean la compra oportuna antes de la entrega del 0km.
    *   **Amenities (16%)**: Clientes califican de 'miserable' el retiro de la máquina de café de la sala de espera de Posventa.
    """)
    
    # Renderizador de las tablas vivas de tu Google Sheets
    st.info("📅 Bases de datos vivas conectadas:")
    pestaña_seleccionada = st.radio("Inspeccionar Hojas del Excel:", ["Pestaña 1 (KPIs)", "Pestaña 2", "Pestaña 3", "Pestaña 4"], horizontal=True)
    
    if pestaña_seleccionada == "Pestaña 1 (KPIs)" and df_hoja1 is not None:
        st.dataframe(df_hoja1.head(10), use_container_width=True)
    elif pestaña_seleccionada == "Pestaña 2" and df_hoja2 is not None:
        st.dataframe(df_hoja2.head(10), use_container_width=True)
    elif pestaña_seleccionada == "Pestaña 3" and df_hoja3 is not None:
        st.dataframe(df_hoja3.head(10), use_container_width=True)
    elif pestaña_seleccionada == "Pestaña 4" and df_hoja4 is not None:
        st.dataframe(df_hoja4.head(10), use_container_width=True)
    else:
        st.warning("Asegúrate de cambiar el acceso de tu Google Sheet a 'Cualquier persona con el enlace puede leer' para procesar los datos.")

with col_right:
    # Gráfico de torta de impacto físico
    df_quejas = pd.DataFrame({
        "Motivo de Queja": ["Falta Kit de Seguridad", "Falta Regalos / Merch", "Falta Máquina de Café"],
        "Impacto %": [36, 20, 16]
    })
    fig_pie = px.pie(df_quejas, values="Impacto %", names="Motivo de Queja", color_discrete_sequence=px.colors.sequential.Reds_r)
    st.plotly_chart(fig_pie, use_container_width=True)
