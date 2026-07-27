import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado a Junio 2026 | Sincronizado con Reporte Oficial (Puesto 24)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL
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
    st.sidebar.error("❌ Penalidad Posventa Activa (<85%).")
if penalidad_fair_play:
    puntos_a_restar_global += 10
if penalidad_movilidad:
    puntos_a_restar_global += 5

if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. DATOS GENERALES (TPA CORREGIDO AL 72.8%)
df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [40.7, 0.0, 90.5, 72.8, 35.8, 75.8, 75.0, 25.0, 44.2],
    "Estado": ["🔴 Crítico", "🔴 Crítico", "🟢 Excelente", "🟡 Desviado", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

filtros = st.multiselect("🔍 Filtrar áreas:", options=df_areas["Área"].unique(), default=[])
areas_activas = filtros if filtros else list(df_areas["Área"].unique())
df_plot_areas = df_areas[df_areas["Área"].isin(areas_activas)]
posventa_incluida = "Posventa" in areas_activas

score_global = 62.00 - puntos_a_restar_global if posventa_incluida else df_plot_areas["Cumplimiento %"].mean() - puntos_a_restar_global

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Cumplimiento DEP", f"{score_global:.1f}%")
with col2: st.metric("Ranking Oficial", "Puesto 24 🏆" if posventa_incluida else "Puesto 39 🔻")
with col3: st.metric("Pilar Posventa", "90.5%" if posventa_incluida else "Excluido 🚫")
with col4: st.metric("Categoría", "Categoría C" if score_global < 80 else "Categoría B")

st.divider()
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 Desviado": "#ff7f0e", "🟡 En Alerta": "#bcbd22", "🔴 Crítico": "#d62728"}), use_container_width=True)

# 4. MATRICES DE ACCIÓN Y QUEJAS
st.divider()
c_left, c_right = st.columns(2)
with c_left:
    st.plotly_chart(px.pie(pd.DataFrame({"Motivo": ["Kit Seguridad", "Merch", "Café"], "Impacto": [36.0, 20.0, 16.0]}), values="Impacto", names="Motivo", title="Quejas"), use_container_width=True)
with c_right:
    st.markdown("**Mejora:** Ventas subió a 40.7%. **Focos críticos:** Kinto y Especiales.")

st.dataframe(pd.DataFrame({"Sucursal": ["Salta-Jujuy"], "Sector": ["Comercial"], "Problema": ["Falta de obsequios"], "Acción": ["Kits alternativos"], "Estatus": ["En Proceso"]}), use_container_width=True)

# 5. SIMULADOR EMT (900 PUNTOS BASE - REPARADO CON LISTAS EXPLICITAS)
st.divider()
st.subheader("📋 Simulador Oficial EMT - TOYOTA (Target Septiembre)")

base_emt_data = {
    "Capítulo": ["A - Estructura Central", "B - Servicio al Cliente", "C - Kinto", "D - Club Toyota", "E - Toyota Plan de Ahorro", "F - Toyota Financial Services", "G - Usados", "H - Convencional", "I - Servicios Conectados"],
    "Puntos Máximos":,
    "Puntos Obtenidos (Simulados)": [100, 100, 100, 100, 100, 100, 100, 100, 100]
}

df_editado_emt = st.data_editor(pd.DataFrame(base_emt_data), disabled=["Capítulo", "Puntos Máximos"], use_container_width=True)

suma_max = df_editado_emt["Puntos Máximos"].sum()
suma_obt = df_editado_emt["Puntos Obtenidos (Simulados)"].sum()
pct_emt = (suma_obt / suma_max) * 100

st.markdown("#### 🎯 Resultado Consolidado de la Simulación")
if pct_emt == 100.0:
    st.success(f"🏆 Perfecto: {suma_obt:.0f}/{suma_max:.0f} Puntos ({pct_emt:.1f}%)")
elif pct_emt >= 90.0:
    st.info(f"🟢 Conforme: {suma_obt:.0f}/{suma_max:.0f} Puntos ({pct_emt:.1f}%)")
elif pct_emt >= 75.0:
    st.warning(f"🟡 Alerta: {suma_obt:.0f}/{suma_max:.0f} Puntos ({pct_emt:.1f}%)")
else:
    st.error(f"🔴 Crítico: {suma_obt:.0f}/{suma_max:.0f} Puntos ({pct_emt:.1f}%)")
