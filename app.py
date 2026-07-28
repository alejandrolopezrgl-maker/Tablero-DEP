import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado a Junio 2026 | Sincronizado con Reporte Oficial de TASA (Puesto 24 Cerrado)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL (SIDEBAR): SIMULADOR DE PENALIDADES DE CAMPO
st.sidebar.header("🚨 Zona de Control DEP")

default_fair_play = False
default_movilidad = False
default_fieldman = 85

if st.session_state.reestablecer:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts)", value=default_fair_play, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5 pts)", value=default_movilidad, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, default_fieldman, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts)", value=default_fair_play)
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5 pts)", value=default_movilidad)
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, default_fieldman)

puntos_a_restar_global = 0
castigo_posventa_fieldman = 0

st.sidebar.divider()
if visitas_fieldman < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa (-10.8% en el área).")
    castigo_posventa_fieldman = 10.8
else:
    st.sidebar.success("🟢 Posventa a salvo de penalidad (≥85%).")

if penalidad_fair_play: puntos_a_restar_global += 10

if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. VALORES PORCENTUALES REALES FIJOS DE LA PLANILLA TOYOTA (COLUMNA LUX)
base_ventas = 55.7 if not penalidad_movilidad else (55.7 - 5.0)
base_posventa = 91.7 - castigo_posventa_fieldman

df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [base_ventas, 49.0, base_posventa, 72.8, 35.8, 75.8, 73.0, 25.0, 67.6],
    "Estado": ["🔴 Crítico", "🔴 Crítico", "🟢 Excelente" if base_posventa >= 80 else "🟡 En Alerta", "🟢 Excelente", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

# CÁLCULO DIRECTO DEL SCORE EN BASE A LAS PONDERACIONES OFICIALES
score_global_final = (
    (base_ventas * 0.22) + 
    (49.0 * 0.05) + 
    (base_posventa * 0.27) + 
    (72.8 * 0.09) + 
    (35.8 * 0.06) + 
    (75.8 * 0.06) + 
    (73.0 * 0.04) + 
    (25.0 * 0.01) + 
    (67.6 * 0.20)
) - puntos_a_restar_global

st.subheader("📉 Cumplimiento Real por Área Evaluada (Foto Oficial Consolidada)")
filtros = st.multiselect("🔍 Filtrar áreas específicas:", options=df_areas["Área"].unique(), default=[])
areas_activas = filtros if filtros else list(df_areas["Área"].unique())
df_plot_areas = df_areas[df_areas["Área"].isin(areas_activas)]

if score_global_final >= 61.9 and not penalidad_movilidad and castigo_posventa_fieldman == 0 and puntos_a_restar_global == 0:
    label_ranking = "Puesto 24 🏆"
    categoria_dinamica = "Categoría C"
elif score_global_final < 60.0:
    label_ranking = "Puesto 39 🔻"
    categoria_dinamica = "Categoría D / E ⚠️"
else:
    label_ranking = "Puesto 28 🟡"
    categoria_dinamica = "Categoría C"

# 4. CUADRO DE MANDO PRINCIPAL
st.header("📌 Resumen Ejecutivo de Desvíos Autolux")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
with col2: st.metric("Ranking General Red", label_ranking, delta="Puesto 4 en TPA 🏆")
with col3: st.metric("Pilar Posventa Real", f"{base_posventa:.1f}%")
with col4: st.metric("Estatus de Categoría", categoria_dinamica)

st.divider()
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 En Alerta": "#ff7f0e", "🔴 Crítico": "#d62728"}), use_container_width=True)

st.divider()
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
col_left, col_right = st.columns(2)
with col_left:
    df_quejas = pd.DataFrame({"Motivo de la Queja": ["Falta de Kit de Seguridad", "Falta de Presentes / Merch", "Falta de Máquina de Café"], "Impacto %": [36.0, 20.0, 16.0]})
    st.plotly_chart(px.pie(df_quejas, values="Impacto %", names="Motivo de la Queja", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)
with col_right:
    st.markdown("""
    *   **Área Ventas (55.7%)**: Acciones de mitigación con kits de seguridad en Tartagal y Jujuy contuvieron las encuestas.
    *   **Focos Críticos Reales**: Ventas Especiales (49.0%) y KINTO (35.8%) penalizados por demoras de unidades corporativas.
    """)

st.subheader("📋 Plan de Acción Comercial")
plan_data = {
    "Sucursal": ["Salta - Jujuy - Tartagal", "Salta - Jujuy", "Salta - Jujuy - Tartagal"],
    "Sector": ["Comercial", "USI", "Posventa"],
    "Problema Detected": ["Unidades sin obsequio", "Falta stock y presupuesto", "Retiro de máquina de café"],
    "Causa Raíz": ["Demoras administrativas", "Ausencia de presupuesto fijo", "Optimización de costos errónea"],
    "Acción Obligatoria": ["Consultar kits alternativos", "Implementar propuesta de presupuesto fijo", "Restaurar máquina de café"],
    "Responsable": ["Asesores UCT", "Gerencia Comercial", "Responsable Posventa"],
    "Estatus Actual": ["En Proceso", "Pendiente", "Restablecido"]
}
st.dataframe(pd.DataFrame(plan_data), use_container_width=True)

st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP)")
st.markdown("### 📊 Resumen por Grandes Grupos Ponderados")
st.dataframe(df_areas[["Área", "Cumplimiento %", "Estado"]], use_container_width=True)
