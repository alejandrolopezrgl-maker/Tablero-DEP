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

st.dataframe(pd.DataFrame({"Sucursal": ["Salta-Jujuy-Tartagal", "Salta-Jujuy", "Salta-Jujuy-Tartagal"], "Sector": ["Comercial", "USI", "Posventa"], "Problema": ["Falta obsequio", "Falta stock", "Retiro café"], "Acción": ["Kits alternativos", "Presupuesto fijo", "Restaurar café"], "Responsable": ["Asesores UCT", "Gerencia Com.", "Resp. Posventa"], "Estatus": ["En Proceso", "Pendiente", "Restablecido"]}), use_container_width=True)

# 5. CONSOLIDADO POR PESTAÑAS Y SIMULADOR EMT COMPACTADO
st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")

pestaña = st.radio("Selecciona pestaña:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.markdown("### 📊 Resumen por Grandes Grupos")
    st.dataframe(df_areas, use_container_width=True)
else:
    st.markdown("### 🎯 Módulo de Preparación EMT")
    c_a, c_b, c_c = st.columns(3)
    with c_a: sim_est = st.selectbox("Área A - Estructura Central:", ["🟢 Conforme", "🔴 Alerta"], index=0)
    with c_b: sim_ser = st.selectbox("Área B - Servicio al Cliente:", ["🟢 Conforme", "🔴 Alerta"], index=0)
    with c_c: sim_kin = st.selectbox("Área C - KINTO:", ["🟢 Conforme", "🔴 Alerta"], index=0)
    c_d, c_e, c_f = st.columns(3)
    with c_d: sim_clb = st.selectbox("Área D - Club Toyota:", ["🟢 Conforme", "🔴 Alerta"], index=0)
    with c_e: sim_tpa = st.selectbox("Área E - Toyota Plan (TPA):", ["🟢 Conforme", "🔴 Alerta"], index=0)
    with c_f: sim_tfs = st.selectbox("Área F - Financial (TCFA):", ["🟢 Conforme", "🔴 Alerta"], index=0)
    c_g, c_h, c_i = st.columns(3)
    with c_g: sim_usd = st.selectbox("Área G - Usados:", ["🟢 Conforme", "🔴 Alerta"], index=0)
    with c_h: sim_dig = st.selectbox("Área H - Convencional (Ventas):", ["🟢 Conforme", "🔴 Alerta"], index=0)
    with c_i: sim_con = st.selectbox("Área I - Servicios Conectados:", ["🟢 Conforme", "🔴 Alerta"], index=0)

    p_list = [100 if "🟢" in s else 0 for s in [sim_est, sim_ser, sim_kin, sim_clb, sim_tpa, sim_tfs, sim_usd, sim_dig, sim_con]]
    tot_sim = sum(p_list)
    pct_emt = (tot_sim / 900) * 100

    df_emt = pd.DataFrame({
        "Macro-Capítulo EMT": ["A-Estructura", "B-Servicio", "C-Kinto", "D-Club", "E-TPA", "F-TFS", "G-Usados", "H-Convencional", "I-Conectados"],
        "Puntaje Maximo": [100] * 9,
        "Puntaje Simulado": p_list,
        "Estado": ["🟢 Conforme" if x > 0 else "🔴 Alerta" for x in p_list]
    })

    st.metric(label="🏆 NOTA CONSOLIDADA DE AUDITORÍA EMT SIMULADA", value=f"{tot_sim} / 900 Puntos", delta=f"{pct_emt:.1f}% Cumplimiento")
    st.dataframe(df_emt, use_container_width=True)
