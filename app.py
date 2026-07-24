import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="DEP Autolux - Control de Desvíos", layout="wide", page_icon="📊")

st.title("🚗 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Período de Evaluación: Mayo - Junio 2026 | Enfoque: Núcleo Estratégico")

# --- DATA GENERATION (Simulación de las hojas actuales según PDF) ---
@st.cache_data
def load_data():
    # Tabla resumen de indicadores a Junio
    indicadores_data = {
        "Área": ["Posventa", "Posventa", "Ventas", "Ventas", "TPA", "Usados", "Usados", "KINTO ONE"],
        "KPI": ["CSI", "FIR", "SSI", "NPS", "NPS t", "SSI", "NPS", "NPS"],
        "Actual Acumulado": [94.70, 98.60, 93.40, 78.10, 82.50, 84.13, 56.25, 44.40],
        "Objetivo Target": [93.80, 96.50, 95.60, 87.00, 85.00, 94.50, 89.00, 90.00],
        "Peso Pilar %": [27.0, 27.0, 22.0, 22.0, 9.0, 6.0, 6.0, 6.0]
    }
    df = pd.DataFrame(indicadores_data)
    df["Brecha"] = df["Actual Acumulado"] - df["Objetivo Target"]
    df["Estado"] = df["Brecha"].apply(lambda x: "🟢 En Objetivo" if x >= 0 else "🔴 Desviado")
    return df

df_kpis = load_data()

# --- SIDEBAR: ALERTAS CRÍTICAS (Restadores Directos) ---
st.sidebar.header("🚨 Zona Roja: Penalidades Directas")
fair_play = st.sidebar.toggle("Ventas fuera de zona / Sobreprecios (-10 pts)", value=True)
fieldman_compromisos = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 78) # Caso real Salta 7/9 (78%)

# Lógica de penalización en Sidebar
st.sidebar.divider()
st.sidebar.subheader("Estatus de Filtros")
if fieldman_compromisos < 85:
    st.sidebar.error("⚠️ Penalidad Posventa Activa: -40% en Puntos Negativos del área (<85%)")
if fair_play:
    st.sidebar.error("🛑 Penalidad Fair Play Activa: -10 Puntos Directos a la nota final")

# --- MAIN DASHBOARD INTERFACE ---

# 1. KPIs principales de control rápido
st.header("📌 Alertas de Desvío Crítico")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="VT - SSI Acumulado", value="93.4%", delta="-2.20% vs Target", delta_color="inverse")
with col2:
    st.metric(label="VT - NPS Comercial", value="78.1%", delta="-8.90% vs Target", delta_color="inverse")
with col3:
    st.metric(label="KINTO ONE - NPS", value="44.4%", delta="-45.6% vs Target", delta_color="inverse")
with col4:
    st.metric(label="Puesto Actual Ranking", value="39 🔻", delta="Bajó del puesto 8 en Abril", delta_color="inverse")

st.divider()

# 2. Vista General de la Tabla de Desvíos
st.subheader("📊 Grilla de Indicadores y Brechas a Junio")
st.dataframe(
    df_kpis.style.map(
        lambda v: 'background-color: #ffcccc;' if "🔴" in str(v) else ('background-color: #ccffcc;' if "🟢" in str(v) else ''),
        subset=["Estado"]
    ),
    use_container_width=True
)

# 3. Gráfico de Brechas
st.subheader("📉 Magnitud de los Desvíos por Indicador")
fig = px.bar(
    df_kpis, 
    x="KPI", 
    y="Brecha", 
    color="Estado",
    text_auto=".2f",
    color_discrete_map={"🟢 En Objetivo": "#2ca02c", "🔴 Desviado": "#d62728"},
    title="Brecha Real vs Meta (Valores negativos indican desvío)"
)
st.plotly_chart(fig, use_container_width=True)

# 4. Plan de Acción y Causa Raíz Física (Datos del PDF)
st.divider()
st.subheader("💡 Análisis de Causa Raíz (¿Por qué caímos al Puesto 39?)")
col_pie, col_txt = st.columns([1, 1])

with col_pie:
    quejas_data = {
        "Factor de Queja": ["Falta de Kit de Seguridad", "Falta de Regalos / Merch", "Falta de Máquina de Café"],
        "Porcentaje": [36, 20, 16]
    }
    df_quejas = pd.DataFrame(quejas_data)
    fig_pie = px.pie(df_quejas, values="Porcentaje", names="Factor de Queja", color_discrete_sequence=px.colors.sequential.Reds_r)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_txt:
    st.markdown("""
    **Análisis Operativo:**
    El **72% de las quejas** se concentran en factores físicos de las sucursales (Salta, Jujuy, Tartagal) y no en fallas del vehículo.
    
    *   **Kit de Seguridad (36%)**: El circuito administrativo demora la compra anticipada. Los asesores entregan unidades vacías.
    *   **Máquina de Café (16%)**: Los clientes de posventa perciben una "actitud miserable" por el retiro del beneficio en sala de espera.
    
    👉 **Acción Comercial Urgente:** El Gerente Comercial debe implementar un presupuesto fijo y validar proveedores alternativos de kits para el 100% de las entregas.
    """)
