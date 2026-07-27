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

# Valores por defecto para la simulación o el reinicio
default_fair_play = False
default_movilidad = False
default_fieldman = 78

# Si el usuario presionó reestablecer, forzamos los valores reales oficiales
if st.session_state.reestablecer:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=default_fair_play, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=default_movilidad, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, default_fieldman, key="fm_real")
    st.session_state.reestablecer = False  # Apagamos el gatillo
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

# Botón estratégico de reinicio rápido en la barra lateral
st.sidebar.divider()
if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

# Valores base oficiales actualizados al nuevo reporte (Puesto 24)
score_global_base = 62.00
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

# 4. CUADRO DE MANDO PRINCIPAL (MÉTRICAS OFICIALES NUEVAS)
st.header("📌 Resumen Ejecutivo de Desvíos")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Cumplimiento General DEP", value=f"{score_global_calculado:.1f}%", delta=f"-{puntos_a_restar_global}% Penalidad" if puntos_a_restar_global > 0 else "Subió +0.8%", delta_color="normal" if puntos_a_restar_global == 0 else "inverse")
with col2:
    st.metric(label="Ranking General Oficial", value="Puesto 24 🏆", delta="Escaló desde el Puesto 26")
with col3:
    st.metric(label="Pilar Posventa (Líder)", value="90.5%", delta="Desempeño destacado en red", delta_color="normal")
with col4:
    st.metric(label="Estatus de Categoría", value=categoria_dinamica, delta="Objetivo Target: ≥90% para Cat. A", delta_color=delta_color_cat)

st.divider()

# 5. GRÁFICO OFICIAL ACTUALIZADO POR ÁREA
st.subheader("📉 Cumplimiento Real por Área Evaluada (Nueva Foto Consolidada)")

df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [40.7, 0.0, 90.5, 59.1, 35.8, 75.8, 75.0, 25.0, 44.2],
    "Estado": ["🔴 Crítico", "🔴 Crítico (Nota 0)", "🟢 Excelente", "🟡 Desviado", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

filtros = st.multiselect("🔍 Filtrar áreas específicas para enfocar el análisis:", options=df_areas["Área"].unique(), default=[])
df_plot_areas = df_areas[df_areas["Área"].isin(filtros)] if filtros else df_areas

fig_areas = px.bar(
    df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f",
    color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 Desviado": "#ff7f0e", "🟡 En Alerta": "#bcbd22", "🔴 Crítico": "#d62728", "🔴 Crítico (Nota 0)": "#7f1d1d"},
    title="Porcentajes de Desempeño por Pilar de Negocio"
)
st.plotly_chart(fig_areas, use_container_width=True)

st.divider()

# 6. DIAGNÓSTICO FÍSICO DE CAUSA RAÍZ
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
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
    **Análisis de la Mejora Actual (Puesto 26 ➔ 24):**
    *   **Área Ventas (Subió a 40.7%)**: Las primeras entregas con presupuestos liberados para kits de seguridad de emergencia en Tartagal y Jujuy ayudaron a amortiguar la caída de las encuestas de satisfacción.
    *   **Focos Críticos a Resolver**: Ventas Especiales (0.0%) y KINTO (35.8%) siguen congelados debido a retrasos en las entregas de flotas corporativas y la falta de amenities para clientes de movilidad.
    """)

st.divider()

# 7. CONSOLIDADO POR CATEGORÍAS Y SIMULADOR EMT
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")

pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    df_cat = pd.DataFrame({
        "Categoría de Medición (Acumulado Junio)": ["Calidad", "Programas", "RRHH", "Facilities (Instalaciones)", "Targets (Metas)"],
        "Cumplimiento Oficial Autolux": ["69.2%", "76.8%", "87.0%", "40.0%", "55.1%"],
        "Ranking en la Red": ["Puesto 18", "Puesto 43", "Puesto 14", "Puesto 39", "Puesto 12"]
    })
    st.dataframe(df_cat, use_container_width=True)

elif pestaña == "Simulador Preventivo EMT":
    st.info("🎯 **Módulo de Preparación EMT:** La auditoría inicia oficialmente en Septiembre 2026. Modifica los selectores para predecir escenarios:")
    
    estatus_kinto = st.selectbox("Estatus pilar C - KINTO:", ["🟢 100% Cumplido", "🔴 Desviado por Flota / Siniestros (-100 pts)"])
    estatus_digital = st.selectbox("Estatus pilar H - Convencional (Gestión Digital):", ["🟢 100% Cumplido", "🔴 Desviado por Demora en Leads (-100 pts)"])
    
    p_kinto = 100 if "🟢" in estatus_kinto else 0
    p_dig = 100 if "🟢" in estatus_digital else 0
    
    df_emt = pd.DataFrame()
    df_emt["Macro-Capítulo EMT"] = ["A - Estructura", "B - Servicio", "C - Kinto", "D - Club Toyota", "E - TPA", "F - TFS", "G - Usados", "H - Convencional", "I - Servicios Conectados"]
    df_emt["Puntaje Máximo"] = [100, 100, 100, 100, 100, 100, 100, 100, 100]
    df_emt["Puntaje Simulado"] = [100, 100, p_kinto, 100, 100, 100, 100, p_dig, 100]
    df_emt["Estatus"] = ["🟢 Conforme", "🟢 Conforme", "🟢 Conforme" if p_kinto > 0 else "🔴 Alerta", "🟢 Conforme", "🟢 Conforme", "🟢 Conforme", "🟢 Conforme", "🟢 Conforme" if p_dig > 0 else "🔴 Alerta", "🟢 Conforme"]
    
    st.dataframe(df_emt, use_container_width=True)
