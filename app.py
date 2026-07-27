import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

# Títulos de la Aplicación Operativa
st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado a Junio 2026 | Sincronizado con Reporte Oficial de Concesionarios")

# 2. BARRA LATERAL (SIDEBAR): CONTROL DE RIESGOS Y PENALIDADES DIRECTAS
st.sidebar.header("🚨 Zona Roja: Penalidades Directas")
st.sidebar.markdown("Filtros de control para simular el impacto en auditorías:")

penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=False)
penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=False)
visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, 78)

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

# Valores base extraídos de la pantalla oficial enviada
score_global_base = 61.20
score_global_calculado = score_global_base - puntos_a_restar_global

if score_global_calculado >= 90:
    categoria_dinamica = "Categoría A"
    delta_color_cat = "normal"
elif score_global_calculado >= 80:
    categoria_dinamica = "Categoría B"
    delta_color_cat = "off"
else:
    categoria_dinamica = "Categoría C"
    delta_color_cat = "inverse"

# 3. CUADRO DE MANDO PRINCIPAL (MÉTRICAS OFICIALES)
st.header("📌 Resumen Ejecutivo de Desvíos")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Cumplimiento General DEP", value=f"{score_global_calculado:.1f}%", delta=f"-{puntos_a_restar_global}% Penalidad" if puntos_a_restar_global > 0 else "Estable", delta_color="inverse" if puntos_a_restar_global > 0 else "normal")
with col2:
    st.metric(label="Ranking General Oficial", value="Puesto 26 🏆", delta="Posición consolidada al 26/6/26")
with col3:
    st.metric(label="Pilar Posventa (Líder)", value="98.0%", delta="Máximo desempeño histórico", delta_color="normal")
with col4:
    st.metric(label="Estatus de Categoría", value=categoria_dinamica, delta="Requiere ≥90% para Cat. A", delta_color=delta_color_cat)

st.divider()

# 4. GRÁFICO OFICIAL DE CUMPLIMIENTO POR ÁREA
st.subheader("📉 Cumplimiento Real por Área Evaluada (Foto del Tablero Oficial)")

df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [26.0, 30.0, 98.0, 69.0, 33.0, 73.0, 63.0, 57.0, 61.0],
    "Estado": ["🔴 Crítico", "🔴 Crítico", "🟢 Excelente", "🟡 Desviado", "🔴 Crítico", "🟡 En Alerta", "🟡 Desviado", "🟡 Desviado", "🟡 Desviado"]
})

# Filtro multiselección para limpiar gráficos en reuniones
filtros = st.multiselect("🔍 Filtrar áreas específicas para enfocar el análisis:", options=df_areas["Área"].unique(), default=[])
df_plot_areas = df_areas[df_areas["Área"].isin(filtros)] if filtros else df_areas

fig_areas = px.bar(
    df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f",
    color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 Desviado": "#ff7f0e", "🟡 En Alerta": "#bcbd22", "🔴 Crítico": "#d62728"},
    title="Porcentajes de Desempeño por Pilar de Negocio"
)
st.plotly_chart(fig_areas, use_container_width=True)

st.divider()

# 5. DIAGNÓSTICO FÍSICO DE CAUSA RAÍZ
st.subheader("🕵️ Análisis Operativo: ¿Por qué Ventas tiene 26% y KINTO 33%?")
col_left, col_right = st.columns(2)

with col_left:
    df_quejas = pd.DataFrame({
        "Motivo de la Queja": ["Falta de Kit de Seguridad", "Falta de Presentes / Merch", "Falta de Máquina de Café"],
        "Impacto %": [36.0, 20.0, 16.0]
    })
    fig_pie = px.pie(df_quejas, values="Impacto %", names="Motivo de la Queja", color_discrete_sequence=px.colors.sequential.Reds_r)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown("""
    **Factores Críticos en Sucursales (Salta / Tartagal):**
    *   **Área Ventas (26%)**: El desplome es causado por la insatisfacción de las encuestas de entrega de unidades. Los clientes penalizan la falta de kits de seguridad y obsequios corporativos básicos.
    *   **Área KINTO (33%)**: Se registran quejas por demoras en la entrega física de la flota de movilidad y la ausencia de amenities en los sectores de espera de los clientes comerciales.
    """)

st.divider()

# 6. CONSOLIDADO DE PESTAÑAS Y SIMULADOR EMT (PREVENTIVO SEPTIEMBRE 2026)
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")

pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    df_cat = pd.DataFrame({
        "Categoría de Medición": ["Calidad", "Programas", "RRHH", "Facilities (Instalaciones)", "Targets (Metas)"],
        "Cumplimiento Oficial": ["51.0%", "100.0%", "89.0%", "100.0%", "47.0%"],
        "Alerta de Gestión": ["🔴 Falla Grave por Encuestas", "🟢 Óptimo", "🟡 Margen de Mejora", "🟢 Estándar de Sucursal OK", "🔴 Brecha en Objetivos Volumen"]
    })
    st.dataframe(df_cat, use_container_width=True)

elif pestaña == "Simulador Preventivo EMT":
    st.info("🎯 **Módulo de Preparación EMT:** La auditoría inicia oficialmente en Septiembre 2026. Modifica los selectores para predecir escenarios:")
    
    estatus_kinto = st.selectbox("Estatus pilar C - KINTO:", ["🟢 100% Cumplido", "🔴 Desviado por Flota / Siniestros (-100 pts)"])
    estatus_digital = st.selectbox("Estatus pilar H - Convencional (Gestión Digital):", ["🟢 100% Cumplido", "🔴 Desviado por Demora en Leads (-100 pts)"])
    
    p_kinto = 100 if "🟢" in estatus_kinto else 0
    p_dig = 100 if "🟢" in estatus_digital else 0
    total_sim = 700 + p_kinto + p_dig
    
    df_emt = pd.DataFrame({
        "Macro-Capítulo EMT": ["A - Estructura", "B - Servicio", "C - Kinto", "D - Club Toyota", "E - TPA", "F - TFS", "G - Usados", "H - Convencional", "I - Servicios Conectados"],
        "Puntaje Máximo":,
        "Puntaje Simulado": [100, 100, p_kinto, 100, 100, 100, 100, p_dig, 100],
        "Estatus": ["🟢 Conforme", "🟢 Conforme", "🟢 Conforme" if p_kinto > 0 else "🔴 Alerta", "🟢 Conforme", "🟢 Conforme", "🟢 Conforme", "🟢 Conforme", "🟢 Conforme" if p_dig > 0 else "🔴 Alerta", "🟢 Conforme"]
    })
    st.dataframe(df_emt, use_container_width=True)
