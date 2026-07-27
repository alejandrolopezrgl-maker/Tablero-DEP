import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

# Títulos de la Aplicación Operativa
st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado a Junio 2026 | Sincronizado con Reporte Oficial (Puesto 24)")

# 2. CONTROL DE MEMORIA PARA EL BOTÓN DE REINICIO
if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 3. BARRA LATERAL (SIDEBAR): CONTROL DE RIESGOS Y PENALIDADES DIRECTAS
st.sidebar.header("🚨 Zona Roja: Penalidades Directas")
st.sidebar.markdown("Filtros de control para simular el impacto en auditorías:")

default_fair_play = False
default_movilidad = False
default_fieldman = 78

if st.session_state.reestablecer:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=default_fair_play, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=default_movilidad, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, default_fieldman, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=default_fair_play)
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=default_movilidad)
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, default_fieldman)

puntos_a_restar_global = 0
penalizacion_posventa_activa = False

st.sidebar.divider()
st.sidebar.subheader("Estatus de Alertas")

if visitas_fieldman < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa: Cumplimiento <85% genera castigo automático en Puntos Negativos del área.")
    penalizacion_posventa_activa = True
else:
    st.sidebar.success("🟢 Posventa a salvo del castigo de Fieldman (≥85%).")

if penalidad_fair_play:
    st.sidebar.error("🛑 Penalidad Fair Play Activa: -10 puntos automáticos sobre la nota general.")
    puntos_a_restar_global += 10

if penalidad_movilidad:
    st.sidebar.warning("⚠️ Penalidad Movilidad: -5 puntos directos por falta de certificación.")
    puntos_a_restar_global += 5

# Botón de reinicio en la barra lateral
st.sidebar.divider()
if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

# 4. DATOS BASE OFICIALES ACTUALIZADOS POR ÁREA
df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [40.7, 0.0, 90.5, 59.1, 35.8, 75.8, 75.0, 25.0, 44.2],
    "Estado": ["🔴 Crítico", "🔴 Crítico (Nota 0)", "🟢 Excelente", "🟡 Desviado", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

st.subheader("📉 Cumplimiento Real por Área Evaluada (Nueva Foto Consolidada)")

filtros = st.multiselect(
    "🔍 Filtrar áreas específicas para enfocar el análisis:", 
    options=df_areas["Área"].unique(), 
    default=[],
    placeholder="Muestra la radiografía completa si dejas vacío el buscador"
)

areas_activas = filtros if filtros else list(df_areas["Área"].unique())
df_plot_areas = df_areas[df_areas["Área"].isin(areas_activas)]

posventa_incluida = "Posventa" in areas_activas

if posventa_incluida:
    score_global_calculado = 62.00 - puntos_a_restar_global
    label_ranking = "Puesto 24 🏆"
    delta_ranking = "Escaló desde el Puesto 26"
    label_posventa = "90.5%"
    delta_posventa = "Desempeño destacado en red"
    color_posventa = "normal"
    
    if score_global_calculado >= 90:
        categoria_dinamica = "Categoría A"
        delta_color_cat = "normal"
    elif score_global_calculado >= 80:
        categoria_dinamica = "Categoría B"
        delta_color_cat = "off"
    else:
        categoria_dinamica = "Categoría C"
        delta_color_cat = "inverse"
else:
    score_global_calculado = df_plot_areas["Cumplimiento %"].mean() - puntos_a_restar_global
    label_ranking = "Puesto 39 🔻"
    delta_ranking = "Retroceso crítico en simulación"
    label_posventa = "Excluido 🚫"
    delta_posventa = "Se quitó el pilar de apoyo"
    color_posventa = "inverse"
    categoria_dinamica = "Alerta Máxima 🛑"
    delta_color_cat = "inverse"

# 5. CUADRO DE MANDO PRINCIPAL DINÁMICO
st.header("📌 Resumen Ejecutivo de Desvíos")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Cumplimiento General DEP", value=f"{score_global_calculado:.1f}%", delta=f"-{puntos_a_restar_global}% Penalidad" if puntos_a_restar_global > 0 else ("Pilar Posventa Excluido 🔻" if not posventa_incluida else "Subió +0.8%"), delta_color="normal" if (puntos_a_restar_global == 0 and posventa_incluida) else "inverse")
with col2:
    st.metric(label="Ranking General Oficial", value=label_ranking, delta=delta_ranking, delta_color="normal" if posventa_incluida else "inverse")
with col3:
    st.metric(label="Pilar Posventa (Líder)", value=label_posventa, delta=delta_posventa, delta_color=color_posventa)
with col4:
    st.metric(label="Estatus de Categoría", value=categoria_dinamica, delta="Objetivo Target: ≥90% para Cat. A", delta_color=delta_color_cat)

st.divider()

# RENDERIZADO DEL GRÁFICO DE BARRAS
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 Desviado": "#ff7f0e", "🟡 En Alerta": "#bcbd22", "🔴 Crítico": "#d62728", "🔴 Crítico (Nota 0)": "#7f1d1d"}), use_container_width=True)

st.divider()

# 6. RESTAURADO: DIAGNÓSTICO FÍSICO DE CAUSA RAÍZ (LA TORTA)
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
col_left, col_right = st.columns(2)

with col_left:
    df_quejas = pd.DataFrame({
        "Motivo de la Queja": ["Falta de Kit de Seguridad", "Falta de Presentes / Merch", "Falta de Máquina de Café"],
        "Impacto %": [36.0, 20.0, 16.0]
    })
    fig_pie = px.pie(df_quejas, values="Impacto %", names="Motivo de la Queja", color_discrete_sequence=px.colors.sequential.Reds_r, title="Distribución de Quejas de Clientes")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown("""
    **Análisis de la Mejora Actual (Puesto 26 ➔ 24):**
    *   **Área Ventas (Subió a 40.7%)**: Las primeras entregas con presupuestos liberados para kits de seguridad de emergencia en Tartagal y Jujuy ayudaron a amortiguar la caída de las encuestas de satisfacción.
    *   **Focos Críticos a Resolver**: Ventas Especiales (0.0%) y KINTO (35.8%) siguen congelados debido a retrasos en las entregas de flotas corporativas y la falta de amenities para clientes de movilidad.
    """)

st.divider()

# 7. RESTAURADO: MATRIZ DE PLAN DE ACCIÓN OPERATIVO VIGENTE (CUADRO SEMÁFORO)
st.subheader("📋 Plan de Acción Comercial - Seguimiento Operativo")
plan_data = {
    "Sucursal": ["Salta - Jujuy - Tartagal", "Salta - Jujuy", "Salta - Jujuy - Tartagal"],
    "Sector": ["Comercial", "USI", "Posventa"],
    "Problema Detectado": ["Unidades retiradas sin obsequio de entrega", "Falta de stock y de aprobación de presupuestos", "Retiro de máquina de café en salas de espera"],
    "Causa Raíz": ["Demoras en circuito administrativo de aprobación", "Falta de fluidez y ausencia de presupuesto fijo", "Optimización de costos mal orientada"],
    "Acción Correctiva Obligatoria": ["Consultar presupuesto de kits de seguridad alternativos", "Diseñar e implementar propuesta de presupuesto fijo", "Restaurar servicio de amenities y máquina de café"],
    "Responsable": ["Asesores UCT / Resp. Comercial", "Gerencia Comercial", "Responsable Posventa"],
    "Estatus Actual": ["En Proceso", "Pendiente", "Restablecido"]
}
st.dataframe(pd.DataFrame(plan_data), use_container_width=True)

st.divider()

# 8. CONSOLIDADO POR CATEGORÍAS Y SIMULADOR EMT AVANZADO
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")

pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.dataframe(pd.DataFrame({"Categoría de Medición (Acumulado Junio)": ["Calidad", "Programas", "RRHH", "Facilities (Instalaciones)", "Targets (Metas)"], "Cumplimiento Oficial Autolux": ["69.2%", "76.8%", "87.0%", "40.0%", "55.1%"], "Ranking en la Red": ["Puesto 18", "Puesto 43", "Puesto 14", "Puesto 39", "Puesto 12"]}), use_container_width=True)

elif pestaña == "Simulador Preventivo EMT":
    st.info("🎯 **Módulo de Preparación EMT:** Modifica los selectores para evaluar el impacto regulatorio en cualquiera de las áreas clave:")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        sim_kinto = st.selectbox("Área C - KINTO:", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
        sim_tpa = st.selectbox("Área E - Plan de Ahorro:", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
        sim_usados = st.selectbox("Área G - Usados:", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
    with col_s2:
        sim_servicio = st.selectbox("Área B - Servicio al Cliente:", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
        sim_tfs = st.selectbox("Área F - Financiera (TFS):", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
        sim_digital = st.selectbox("Área H - Convencional (Leads):", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
    with col_s3:
        sim_estructura = st.selectbox("Área A - Estructura Central:", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
        sim_club = st.selectbox("Área D - Club Toyota:", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])
        sim_conectados = st.selectbox("Área I - Serv. Conectados:", ["🟢 Conforme", "🔴 Desviado (-100 pts)"])

    p_a = 100 if "🟢" in sim_estructura else 0
    p_b = 100 if "🟢" in sim_servicio else 0
    p_c = 100 if "🟢" in sim_kinto else 0
    p_d = 100 if "🟢" in sim_club else 0
