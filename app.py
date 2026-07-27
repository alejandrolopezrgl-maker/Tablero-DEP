import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado a Junio 2026 | Sincronizado con Reporte Oficial (Puesto 24)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL (SIDEBAR): CONTROL DE PENALIDADES
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
st.sidebar.divider()
st.sidebar.subheader("Estatus de Alertas")

if visitas_fieldman < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa: Cumplimiento <85% genera castigo automático.")
else:
    st.sidebar.success("🟢 Posventa a salvo del castigo de Fieldman (≥85%).")

if penalidad_fair_play:
    st.sidebar.error("🛑 Penalidad Fair Play Activa: -10 puntos automáticos.")
    puntos_a_restar_global += 10

if penalidad_movilidad:
    st.sidebar.warning("⚠️ Penalidad Movilidad: -5 puntos directos.")
    puntos_a_restar_global += 5

st.sidebar.divider()
if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. DATOS BASE COMPLETOS POR ÁREA (TPA AJUSTADO AL 72.8%)
df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [40.7, 0.0, 90.5, 72.8, 35.8, 75.8, 75.0, 25.0, 44.2],
    "Estado": ["🔴 Crítico", "🔴 Crítico (Nota 0)", "🟢 Excelente", "🟡 Desviado", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

st.subheader("📉 Cumplimiento Real por Área Evaluada (Nueva Foto Consolidada)")

filtros = st.multiselect("🔍 Filtrar áreas específicas para enfocar el análisis:", options=df_areas["Área"].unique(), default=[])
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
    categoria_dinamica = "Categoría C" if score_global_calculado < 80 else "Categoría B"
else:
    score_global_calculado = df_plot_areas["Cumplimiento %"].mean() - puntos_a_restar_global
    label_ranking = "Puesto 39 🔻"
    delta_ranking = "Retroceso crítico en simulación"
    label_posventa = "Excluido 🚫"
    delta_posventa = "Se quitó el pilar de apoyo"
    color_posventa = "inverse"
    categoria_dinamica = "Alerta Máxima 🛑"

# 4. CUADRO DE MANDO PRINCIPAL
st.header("📌 Resumen Ejecutivo de Desvíos")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Cumplimiento General DEP", value=f"{score_global_calculado:.1f}%", delta=f"-{puntos_a_restar_global}%" if puntos_a_restar_global > 0 else "Subió +0.8%")
with col2: st.metric(label="Ranking General Oficial", value=label_ranking, delta=delta_ranking, delta_color="normal" if posventa_incluida else "inverse")
with col3: st.metric(label="Pilar Posventa (Líder)", value=label_posventa, delta=delta_posventa, delta_color=color_posventa)
with col4: st.metric(label="Estatus de Categoría", value=categoria_dinamica)

st.divider()
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 Desviado": "#ff7f0e", "🟡 En Alerta": "#bcbd22", "🔴 Crítico": "#d62728", "🔴 Crítico (Nota 0)": "#7f1d1d"}), use_container_width=True)

# 5. DIAGNÓSTICO DE CAUSA RAÍZ (GRÁFICO DE TORTA COMPLETO)
st.divider()
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
col_left, col_right = st.columns(2)

with col_left:
    df_quejas = pd.DataFrame({
        "Motivo de la Queja": ["Falta de Kit de Seguridad", "Falta de Presentes / Merch", "Falta de Máquina de Café"],
        "Impacto %": [36.0, 20.0, 16.0]
    })
    fig_pie = px.pie(df_quejas, values="Impacto %", names="Motivo de la Queja", color_discrete_sequence=px.colors.sequential.Reds_r, title="Distribución Completa de Quejas de Clientes")
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown("""
    **Análisis de la Mejora Actual (Puesto 26 ➔ 24):**
    *   **Área Ventas (Subió a 40.7%)**: Las primeras entregas con presupuestos liberados para kits de seguridad de emergencia en Tartagal y Jujuy ayudaron a amortiguar la caída de las encuestas de satisfacción.
    *   **Focos Críticos a Resolver**: Ventas Especiales (0.0%) y KINTO (35.8%) siguen congelados debido a retrasos en las entregas de flotas corporativas y la falta de amenities para clientes de movilidad.
    """)

# 6. MATRIZ DE PLAN DE ACCIÓN OPERATIVO COMPLETA (CUADRO SEMÁFORO)
st.divider()
st.subheader("📋 Plan de Acción Comercial - Seguimiento Operativo Completo")
plan_data = {
    "Sucursal": ["Salta - Jujuy - Tartagal", "Salta - Jujuy", "Salta - Jujuy - Tartagal"],
    "Sector": ["Comercial", "USI", "Posventa"],
    "Problema Detected": ["Unidades retiradas sin obsequio de entrega", "Falta de stock y de aprobación de presupuestos", "Retiro de máquina de café en salas de espera"],
    "Causa Raíz": ["Demoras en circuito administrativo de aprobación", "Falta de fluidez y ausencia de presupuesto fijo", "Optimización de costos mal orientada"],
    "Acción Correctiva Obligatoria": ["Consultar presupuesto de kits de seguridad alternativos", "Diseñar e implementar propuesta de presupuesto fijo", "Restaurar servicio de amenities y máquina de café"],
    "Responsable": ["Asesores UCT / Resp. Comercial", "Gerencia Comercial", "Responsable Posventa"],
    "Estatus Actual": ["En Proceso", "Pendiente", "Restablecido"]
}
st.dataframe(pd.DataFrame(plan_data), use_container_width=True)

# 7. SIMULADOR EMT BLINDADO CONTRA RECORTES DE INTERFAZ
st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")

lista_capitulos = ["A - Estructura Central", "B - Servicio al Cliente", "C - Kinto", "D - Club Toyota", "E - Toyota Plan de Ahorro", "F - Toyota Financial Services", "G - Usados", "H - Convencional", "I - Servicios Conectados"]

base_emt_data = {
    "Capítulo": lista_capitulos,
    "Puntos Máximos": list(gen_max := (100 for _ in range(9))),
    "Puntos Obtenidos (Simulados)": list(gen_sim := (100 for _ in range(9)))
}

st.markdown("### 📋 Simulador Oficial EMT - Estilo de Movilidad TOYOTA (Target Septiembre)")
st.caption("Estructura oficial homologada sobre una base de 900 puntos máximos auditables.")
st.markdown("✏️ **Instrucción:** Modifica la columna **'Puntos Obtenidos (Simulados)'** para ensayar escenarios reales:")

df_editado_emt = st.data_editor(pd.DataFrame(base_emt_data), disabled=["Capítulo", "Puntos Máximos"], use_container_width=True)

suma_max = df_editado_emt["Puntos Máximos"].sum()
suma_obt = df_editado_emt["Puntos Obtenidos (Simulados)"].sum()
pct_emt = (suma_obt / suma_max) * 100

st.markdown("#### 🎯 Resultado Consolidado de la Simulación")
if pct_emt == 100.0:
    st.success(f"🏆 Puntaje Perfecto: {suma_obt:.0f} / {suma_max:.0f} Puntos ({pct_emt:.1f}%) - Escenario ideal.")
elif pct_emt >= 90.0:
    st.info(f"🟢 Zona Conforme: {suma_obt:.0f} / {suma_max:.0f} Puntos ({pct_emt:.1f}%) - Perfil aprobado.")
elif pct_emt >= 75.0:
    st.warning(f"🟡 Zona de Alerta: {suma_obt:.0f} / {suma_max:.0f} Puntos ({pct_emt:.1f}%) - Desvíos leves.")
else:
    st.error(f"🔴 Alerta Crítica: {suma_obt:.0f} / {suma_max:.0f} Puntos ({pct_emt:.1f}%) - Contramedidas urgentes.")
