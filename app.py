import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado a Junio 2026 | Sincronizado con Reporte Oficial (Puesto 24)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# BARRA LATERAL
st.sidebar.header("🚨 Zona Roja: Penalidades Directas")
if st.session_state.reestablecer:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=False, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=False, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, 78, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=False)
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=False)
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, 78)

puntos_a_restar_global = 0
if visitas_fieldman < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa")
if penalidad_fair_play:
    puntos_a_restar_global += 10
if penalidad_movilidad:
    puntos_a_restar_global += 5

if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

# DATOS BASE (TPA CORREGIDO A 72.8%)
df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [40.7, 0.0, 90.5, 72.8, 35.8, 75.8, 75.0, 25.0, 44.2],
    "Estado": ["🔴 Crítico", "🔴 Crítico (Nota 0)", "🟢 Excelente", "🟡 Desviado", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

filtros = st.multiselect("🔍 Filtrar áreas:", options=df_areas["Área"].unique(), default=[])
areas_activas = filtros if filtros else list(df_areas["Área"].unique())
df_plot_areas = df_areas[df_areas["Área"].isin(areas_activas)]
posventa_incluida = "Posventa" in areas_activas

score_global_calculado = 62.00 - puntos_a_restar_global if posventa_incluida else df_plot_areas["Cumplimiento %"].mean() - puntos_a_restar_global

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Cumplimiento General DEP", value=f"{score_global_calculado:.1f}%")
with col2: st.metric(label="Ranking General Oficial", value="Puesto 24 🏆" if posventa_incluida else "Puesto 39 🔻")
with col3: st.metric(label="Pilar Posventa (Líder)", value="90.5%" if posventa_incluida else "Excluido 🚫")
with col4: st.metric(label="Estatus de Categoría", value="Categoría C" if score_global_calculado < 80 else "Categoría B")

st.divider()
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f"), use_container_width=True)
st.divider()

# QUEJAS Y PLAN
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(px.pie(pd.DataFrame({"Motivo": ["Kit Seguridad", "Merch", "Café"], "Impacto": [36, 20, 16]}), values="Impacto", names="Motivo"), use_container_width=True)
with col_right:
    st.markdown("**Análisis de la Mejora:** Ventas subió. Focos críticos: Kinto y Especiales.")

st.divider()
st.subheader("📋 Plan de Acción Comercial")
plan_data = {"Sucursal": ["Salta - Jujuy"], "Sector": ["Comercial"], "Problema Detected": ["Unidades sin obsequio"], "Causa Raíz": ["Demoras administrativas"], "Acción Correctiva Obligatoria": ["Consultar kits alternativos"], "Responsable": ["Asesores UCT"], "Estatus Actual": ["En Proceso"]}
st.dataframe(pd.DataFrame(plan_data), use_container_width=True)
st.divider()
# 8. CONSOLIDADO POR CATEGORÍAS Y SIMULADOR EMT
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")
pestaña = st.radio("Selecciona pestaña:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.markdown("### Resumen consolidado por grupos")
    st.dataframe(df_areas, use_container_width=True)
else:
    st.markdown("### 📋 Simulador Oficial EMT - TOYOTA (Target Septiembre)")
    
    base_emt_data = {
        "Capítulo": ["A - Estructura Central", "B - Servicio al Cliente", "C - Kinto", "D - Club Toyota", "E - Toyota Plan de Ahorro", "F - Toyota Financial Services", "G - Usados", "H - Convencional", "I - Servicios Conectados"],
        "Puntos Máximos":,
        "Puntos Obtenidos (Simulados)": [100, 100, 100, 100, 100, 100, 100, 100, 100]
    }
    
    df_base_emt = pd.DataFrame(base_emt_data)
    df_editado_emt = st.data_editor(df_base_emt, disabled=["Capítulo", "Puntos Máximos"], use_container_width=True)
    
    suma_maxima = df_editado_emt["Puntos Máximos"].sum()
    suma_obtenida = df_editado_emt["Puntos Obtenidos (Simulados)"].sum()
    porcentaje_emt_final = (suma_obtenida / suma_maxima) * 100
    
    st.markdown("#### 🎯 Resultado Consolidado de la Simulación")
    if porcentaje_emt_final == 100.0:
        st.success(f"🏆 **Perfecto:** {suma_obtenida:.0f}/{suma_maxima:.0f} Puntos — **{porcentaje_emt_final:.1f}%**")
    elif porcentaje_emt_final >= 90.0:
        st.info(f"🟢 **Conforme:** {suma_obtenida:.0f}/{suma_maxima:.0f} Puntos — **{porcentaje_emt_final:.1f}%**")
    elif porcentaje_emt_final >= 75.0:
        st.warning(f"🟡 **Alerta:** {suma_obtenida:.0f}/{suma_maxima:.0f} Puntos — **{porcentaje_emt_final:.1f}%**")
    else:
        st.error(f"🔴 **Crítico:** {suma_obtenida:.0f}/{suma_maxima:.0f} Puntos — **{porcentaje_emt_final:.1f}%**")
