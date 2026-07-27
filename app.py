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
    st.sidebar.error("❌ Penalidad Posventa Activa: Cumplimiento <85% genera castigo automático en Puntos Negativos del área.")
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
    "Estado": ["🔴 Crítico", "🔴 Crítico (Nota 0)", "🟢 Excelente", "🟡 Desviado", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

filtros = st.multiselect("🔍 Filtrar áreas específicas para enfocar el análisis:", options=df_areas["Área"].unique(), default=[])
areas_activas = filtros if filtros else list(df_areas["Área"].unique())
df_plot_areas = df_areas[df_areas["Área"].isin(areas_activas)]
posventa_incluida = "Posventa" in areas_activas

score_global = 62.00 - puntos_a_restar_global if posventa_incluida else df_plot_areas["Cumplimiento %"].mean() - puntos_a_restar_global

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Cumplimiento General DEP", f"{score_global:.1f}%", delta=f"-{puntos_a_restar_global}% Penalidad" if puntos_a_restar_global > 0 else "Subió +0.8%")
with col2: st.metric("Ranking General Oficial", "Puesto 24 🏆" if posventa_incluida else "Puesto 39 🔻", delta="Escaló desde el Puesto 26" if posventa_incluida else "Retroceso crítico en simulación")
with col3: st.metric("Pilar Posventa (Líder)", "90.5%" if posventa_incluida else "Excluido 🚫", delta="Desempeño destacado en red" if posventa_incluida else "Se quitó el pilar de apoyo")
with col4: st.metric("Estatus de Categoría", "Categoría C" if score_global < 80 else "Categoría B", delta="Objetivo Target: ≥90% para Cat. A")

st.divider()
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 Desviado": "#ff7f0e", "🟡 En Alerta": "#bcbd22", "🔴 Crítico": "#d62728", "🔴 Crítico (Nota 0)": "#7f1d1d"}), use_container_width=True)

# 4. DIAGNÓSTICO DE CAUSA RAÍZ REAL (RECUPERADO AL 100%)
st.divider()
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
c_left, c_right = st.columns(2)
with c_left:
    df_quejas = pd.DataFrame({
        "Motivo de la Queja": ["Falta de Kit de Seguridad", "Falta de Presentes / Merch", "Falta de Máquina de Café"],
        "Impacto %": [36.0, 20.0, 16.0]
    })
    st.plotly_chart(px.pie(df_quejas, values="Impacto %", names="Motivo de la Queja", color_discrete_sequence=px.colors.sequential.Reds_r, title="Distribución de Quejas de Clientes"), use_container_width=True)
with c_right:
    st.markdown("""
    **Análisis de la Mejora Actual (Puesto 26 ➔ 24):**
    *   **Área Ventas (Subió a 40.7%)**: Las primeras entregas con presupuestos liberados para kits de seguridad de emergencia en Tartagal y Jujuy ayudaron a amortiguar la caída de las encuestas de satisfacción.
    *   **Focos Críticos a Resolver**: Ventas Especiales (0.0%) y KINTO (35.8%) siguen congelados debido a retrasos en las entregas de flotas corporativas y la falta de amenities para clientes de movilidad.
    """)

# PLAN DE ACCIÓN COMPLETO SEMÁFORO
st.subheader("📋 Plan de Acción Comercial - Seguimiento Operativo")
plan_data = {
    "Sucursal": ["Salta - Jujuy - Tartagal", "Salta - Jujuy", "Salta - Jujuy - Tartagal"],
    "Sector": ["Comercial", "USI", "Posventa"],
    "Problema Detected": ["Unidades retiradas sin obsequio de entrega", "Falta de stock y de aprobación de presupuestos", "Retiro de máquina de café en salas de espera"],
    "Causa Raíz": ["Demoras en circuito administrative de aprobación", "Falta de fluidez y ausencia de presupuesto fijo", "Optimización de costos mal orientada"],
    "Acción Correctiva Obligatoria": ["Consultar presupuesto de kits de seguridad alternativos", "Diseñar e implementar propuesta de presupuesto fijo", "Restaurar servicio de amenities and máquina de café"],
    "Responsable": ["Asesores UCT / Resp. Comercial", "Gerencia Comercial", "Responsable Posventa"],
    "Estatus Actual": ["En Proceso", "Pendiente", "Restablecido"]
}
st.dataframe(pd.DataFrame(plan_data), use_container_width=True)

# 5. CONSOLIDADO POR PESTAÑAS Y SIMULADOR EMT COMPACTADO
st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")

pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.markdown("### 📊 Resumen consolidado por grandes grupos de auditoría")
    st.dataframe(df_areas, use_container_width=True)
else:
    st.markdown("### 🎯 Módulo de Preparación EMT: Modifica los selectores para evaluar el impacto")
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
        "Puntaje Maximo": list(g_mx := (100 for _ in range(9))),
        "Puntaje Simulado": p_list,
        "Estado": ["🟢 Conforme" if x > 0 else "🔴 Alerta" for x in p_list]
    })

    st.metric(label="🏆 NOTA CONSOLIDADA DE AUDITORÍA EMT SIMULADA", value=f"{tot_sim} / 900 Puntos", delta=f"{pct_emt:.1f}% Cumplimiento")
    st.dataframe(df_emt, use_container_width=True)
