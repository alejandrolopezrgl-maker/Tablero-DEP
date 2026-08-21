import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux", layout="wide", page_icon="🚗")
st.title("🚗 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Datos Oficiales e Informe de Calidad de la Red TASA (Manual DEP 2026)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL: CONTROL DE RIESGOS PENALIDADES DE CAMPO
st.sidebar.header("🚨 Zona de Control de Riesgos")
if st.session_state.reestablecer:
    penalidad_fp = st.sidebar.toggle("Fair Play Global (-10 pts)", value=False, key="fp_real")
    penalidad_mov = st.sidebar.toggle("No Certificación EMT (-5.0 pts)", value=False, key="mov_real")
    visitas_fm = st.sidebar.slider("% Compromisos Fieldman", 0, 100, 85, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fp = st.sidebar.toggle("Fair Play Global (-10 pts)", value=False)
    penalidad_mov = st.sidebar.toggle("No Certificación EMT (-5.0 pts)", value=False)
    visitas_fm = st.sidebar.slider("% Compromisos Fieldman", 0, 100, 85)

puntos_a_restar_global = 10.0 if penalidad_fp else 0.0
castigo_posventa_fieldman = 40.0 if visitas_fm < 85 else 0.0

if visitas_fm < 85: 
    st.sidebar.error("❌ Penalidad Posventa Activa (-40% en Score del área).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman a salvo (≥85%).")

# 3. BASE DE DATOS ESTRATÉGICA EXTRACTADA DIRECTAMENTE DEL POWER BI / EXCEL TOYOTA
base_ventas_lux = 25.0 if not penalidad_mov else (25.0 - 5.0)
base_posventa_lux = 95.18 - (95.18 * (castigo_posventa_fieldman / 100))

# INICIALIZACIÓN DE PILARES OPERATIVOS
for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg"]:
    if k not in st.session_state: st.session_state[k] = None

# INICIALIZACIÓN UNIFICADA DE LLAVES EMT DE CONTROL NATIVO
emt_keys = ["emt_a", "emt_b", "emt_c", "emt_d", "emt_e", "emt_f", "emt_g", "emt_h", "emt_i"]
for ek in emt_keys:
    if ek not in st.session_state: st.session_state[ek] = 100

v_simulada = st.session_state.sim_pilar_ventas if st.session_state.sim_pilar_ventas is not None else base_ventas_lux
p_simulada = st.session_state.sim_pilar_posventa if st.session_state.sim_pilar_posventa is not None else base_posventa_lux
tpa_simulada = st.session_state.sim_pilar_tpa if st.session_state.sim_pilar_tpa is not None else 72.8
kinto_simulada = st.session_state.sim_pilar_kinto if st.session_state.sim_pilar_kinto is not None else 35.8
tcfa_simulada = st.session_state.sim_pilar_tcfa if st.session_state.sim_pilar_tcfa is not None else 73.0
g_simulada = st.session_state.sim_pilar_general if st.session_state.sim_pilar_general is not None else 65.6
esp_simulada = st.session_state.sim_pilar_especiales if st.session_state.sim_pilar_especiales is not None else 30.0
usd_simulada = st.session_state.sim_pilar_usados if st.session_state.sim_pilar_usados is not None else 73.3
esg_simulada = st.session_state.sim_pilar_esg if st.session_state.sim_pilar_esg is not None else 25.0

# 4. CAPTURA Y CÁLCULO PREVIO DEL COMPROMISO EMT PARA ACOPLARLO A LA NOTA GLOBAL
total_puntos_emt = sum([st.session_state[ek] for ek in emt_keys])
porcentaje_emt = (total_puntos_emt / 900.0) * 100
penalidad_estandar_emt = 0.0 if porcentaje_emt >= 80.0 else ((80.0 - porcentaje_emt) / 80.0) * 5.0

if (st.session_state.sim_pilar_ventas is None and st.session_state.sim_pilar_general is None and 
    st.session_state.sim_pilar_especiales is None and st.session_state.sim_pilar_usados is None and st.session_state.sim_pilar_esg is None):
    score_global_final = 62.0 - puntos_a_restar_global - penalidad_estandar_emt
    if penalidad_mov: score_global_final -= 1.1
else:
    score_global_final = (
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.20) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (usd_simulada * 0.06) + 
        (esp_simulada * 0.05) + (tcfa_simulada * 0.04) + (esg_simulada * 0.01)
    )
    score_global_final = score_global_final - puntos_a_restar_global - penalidad_estandar_emt
    if penalidad_mov: score_global_final -= 1.1

# DATAFRAME OPERATIVO COMPLETO
data_operativa = {
    "Área": ["Ventas (22%)", "Ventas Especiales (5%)", "Posventa (27%)", "TPA (9%)", "KINTO (6%)", "Usados (6%)", "TCFA (4%)", "ESG (1%)", "GENERAL (20%)"],
    "Autolux (LUX)": [v_simulada, esp_simulada, p_simulada, tpa_simulada, kinto_simulada, usd_simulada, tcfa_simulada, esg_simulada, g_simulada],
    "DPQ - Puesto 5": [61.1, 30.0, 92.5, 78.2, 50.0, 93.3, 100.0, 35.5, 59.8],
    "GON - Puesto 10": [26.8, 86.0, 96.0, 48.5, 58.3, 100.0, 100.0, 35.5, 79.0]
}
df_bench_op = pd.DataFrame(data_operativa)

data_ranking_global = {
    "Concesionario": ["DPQ - Puesto 5", "GON - Puesto 10", "Autolux (LUX) - Puesto 24"],
    "Porcentaje DEP Global": [72.3, 69.8, score_global_final]
}
df_bench_ranking = pd.DataFrame(data_ranking_global)

# MOTOR DE RANKING ELÁSTICO RED
if score_global_final <= 62.0: 
    puesto_calculado = int(24 + ((62.0 - score_global_final)/5.0)*10)
    puesto_calculado = min(43, puesto_calculado)
elif score_global_final >= 99.9: 
    puesto_calculado = 1
elif score_global_final >= 72.3: 
    puesto_calculado = max(1, min(5, int(5 - ((score_global_final - 72.3)/(100.0 - 72.3))*(5 - 1))))
else: 
    puesto_calculado = max(5, min(24, int(24 - ((score_global_final - 62.0)/(72.3 - 62.0))*(24 - 5))))

# ACCIÓN DE RESET CRUZADO NATIVO
if st.sidebar.button("🔄 Restablecer Valores Oficiales", key="btn_reset_lateral"):
    for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg", "db_plan_puro_v14", "db_ampliacion_v14"]: 
        if k in st.session_state: st.session_state[k] = None
    for ek in emt_keys: st.session_state[ek] = 100
    st.session_state.reestablecer = True
    st.rerun()

# --- AQUÍ SE DEFINEN LAS 5 PESTAÑAS VISIBLES ---
tab_dashboard, tab_regional, tab_calidad, tab_plan, tab_docs = st.tabs([
    "📊 Dashboard del Dealer", 
    "🗺️ Desempeño Regional y por Área",
    "🕵️ Análisis de Calidad por Sucursal", 
    "📋 Plan de Acción Interactiva",
    "📚 Documentación y Fuentes"
])

# ==========================================
# 1. PESTAÑA: DASHBOARD DEL DEALER
# ==========================================
with tab_dashboard:
    target_p10 = 69.8
    target_p5 = 72.3
    pts_para_p10 = max(0.0, target_p10 - score_global_final)
    pts_para_p5 = max(0.0, target_p5 - score_global_final)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Cumplimiento DEP Score Global", f"{score_global_final:.1f}%")
    with col2: 
        if puesto_calculado < 24: st.metric("Ranking Proyectado Red", f"Puesto {puesto_calculado} 🏆", delta=f"¡Subiendo {24 - puesto_calculado} puestos!")
        elif puesto_calculado > 24: st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🚨", delta=f"¡Bajando {puesto_calculado - 24} puestos!")
        else: st.metric("Ranking General Red", f"Puesto 24 🚗", help="Posición base oficial de Autolux")
    with col3:
        if pts_para_p5 == 0: st.metric("Puntos para Meta Superlativa", "¡En Puesto 5 o superior! 🎉")
        else: st.metric(label="Puntos Faltantes para Top 10 / Top 5", value=f"+{pts_para_p10:.1f} pts (P10 - GON)", delta=f"+{pts_para_p5:.1f} pts para Puesto 5 (DPQ)", delta_color="inverse")

    st.subheader("🏁 Desempeño Operativo por Unidades de Negocio (Ponderaciones Manual 2026)")
    df_melted_op = df_bench_op.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_op = px.bar(df_melted_op, x="Área", y="Cumplimiento %", color="Concesionario", barmode="group", text_auto=".1f", color_discrete_map={"Autolux (LUX)": "#d62728", "DPQ - Puesto 5": "#1f77b4", "GON - Puesto 10": "#7f7f7f"})
    fig_op.update_layout(xaxis_title="Eje del Concesionario / Unidad Operativa", yaxis_title="Efectividad %", yaxis=dict(range=[0, 105]))
    st.plotly_chart(fig_op, use_container_width=True)

    st.subheader("🏆 Posicionamiento Estratégico: Resultado Consolidado RED")
    fig_gen = px.bar(df_bench_ranking, x="Concesionario", y="Porcentaje DEP Global", color="Concesionario", text_auto=".1f", color_discrete_map={"Autolux (LUX) - Puesto 24": "#990000", "DPQ - Puesto 5": "#4A7ebb", "GON - Puesto 10": "#A6A6A6"})
    fig_gen.update_layout(showlegend=False, yaxis=dict(range=[0, 105]), xaxis_title="Dealer Evaluado", yaxis_title="Score Global %")
    st.plotly_chart(fig_gen, use_container_width=True)

    st.divider()
    st.subheader("📝 Checklist de Auditoría Interna: Estilo de Movilidad Toyota (EMT)")
    col_em1, col_em2, col_em3 = st.columns(3)
    with col_em1:
        st.slider("A: Estructura Central (100)", 0, 100, key="emt_a")
        st.slider("B: Servicio al Cliente (100)", 0, 100, key="emt_b")
        st.slider("C: Kinto Movilidad (100)", 0, 100, key="emt_c")
    with col_em2:
        st.slider("D: Club Toyota (100)", 0, 100, key="emt_d")
        st.slider("E: Toyota Plan de Ahorro (100)", 0, 100, key="emt_e")
        st.slider("F: Toyota Financial Services (100)", 0, 100, key="emt_f")
    with col_em3:
        st.slider("G: Vehículos Usados (100)", 0, 100, key="emt_g")
        st.slider("H: Canal Convencional (100)", 0, 100, key="emt_h")
        st.slider("I: Services Conectados (100)", 0, 100, key="emt_i")
    
    if porcentaje_emt < 80.0: st.error(f"🚨 Alerta DEP: Estándar EMT Asegurado en {total_puntos_emt} / 900 puntos ({porcentaje_emt:.1f}%). Por debajo del umbral mínimo del 80%. Penalidad activa.")
    else: st.success(f"🎉 Estándar EMT Certificado: {total_puntos_emt} / 900 puntos ({porcentaje_emt:.1f}%). Concesionario a salvo.")

# =======================================================
# 2. PESTAÑA: DESEMPEÑO REGIONAL Y POR ÁREA (POWER BI)
# =======================================================
with tab_regional:
    st.subheader("🗺️ Diagnóstico Integral por Áreas y Benchmarking Regional (Power BI)")
    st.markdown("Resultados consolidados oficiales de **Autolux (LUX)** comparados con las 5 regiones operativas de la Red TASA:")

    data_area_lux = {
        "Área": ["TPA", "ESG", "POSVENTA", "USADOS", "TCFA", "GENERAL", "VENTAS ESPECIALES", "VENTAS", "KINTO"],
        "Posición Red": [4, 8, 9, 14, 18, 26, 21, 42, 41],
        "Ptj. LUX": [6.55, 0.25, 25.70, 4.40, 2.92, 10.83, 1.50, 5.50, 2.15],
        "Ptj. Ideal": [9.0, 1.0, 27.0, 6.0, 4.0, 16.5, 5.0, 22.0, 6.0],
        "% Ideal LUX": [72.78, 25.00, 95.19, 73.33, 73.00, 65.65, 30.00, 25.00, 35.83]
    }
    df_area_lux = pd.DataFrame(data_area_lux).sort_values(by="% Ideal LUX", ascending=False)

    data_regional = {
        "Región": ["NOA (Líder)", "Cuyo", "NEA", "Patagonia", "Centro", "Promedio RED"],
        "Ptj. Logrado": [67.65, 65.92, 63.95, 63.27, 61.09, 62.53],
        "% Ideal": [70.10, 68.31, 66.27, 65.56, 63.30, 64.80]
    }
    df_reg = pd.DataFrame(data_regional)

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Score Global Autolux", "61.97 pts", "64.22% del Ideal")
    with m2: st.metric("Líder Regional: NOA", "67.65 pts", "70.10% del Ideal")
    with m3: st.metric("Pilar Más Fuerte (LUX)", "Posventa (Puesto 9)", "95.19% Efectividad")
    with m4: st.metric("Pilar de Mayor Brecha", "Ventas (Puesto 42)", "25.00% Efectividad")

    st.markdown("---")

    c_r1, c_r2 = st.columns(2)
    with c_r1:
        st.subheader("📊 Cumplimiento por Área: Autolux vs. Ideal TASA")
        fig_area = px.bar(
            df_area_lux, 
            x="% Ideal LUX", 
            y="Área", 
            orientation="h",
            text="% Ideal LUX", 
            color="% Ideal LUX",
            color_continuous_scale=["#d62728", "#f39c12", "#27ae60"],
            title="Efectividad de Autolux por Unidad de Negocio (% Ideal)"
        )
        fig_area.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_area.update_layout(xaxis=dict(range=[0, 115]), yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_area, use_container_width=True)

    with c_r2:
        st.subheader("🏆 Comparativa de Rendimiento por Regiones")
        fig_region = px.bar(
            df_reg, 
            x="Región", 
            y="% Ideal", 
            text="% Ideal",
            color="Región",
            color_discrete_map={
                "NOA (Líder)": "#1F4E78", 
                "Cuyo": "#5B9BD5", 
                "NEA": "#8FAADC", 
                "Patagonia": "#A6A6A6", 
                "Centro": "#C65911", 
                "Promedio RED": "#70AD47"
            },
            title="Ranking de Efectividad Regional (% Cumplimiento Ideal)"
        )
        fig_region.add_hline(y=64.22, line_dash="dot", line_color="#d62728", annotation_text="Autolux: 64.22%", annotation_position="bottom right")
        fig_region.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
        fig_region.update_layout(showlegend=False, yaxis=dict(range=[0, 85]))
        st.plotly_chart(fig_region, use_container_width=True)

    st.subheader("📋 Tablas Oficiales de Referencia (Power BI)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Desglose de Puntuación Autolux (LUX)**")
        df_mostrar_area = df_area_lux.copy()
        df_mostrar_area["% Ideal LUX"] = df_mostrar_area["% Ideal LUX"].map("{:.2f}%".format)
        st.dataframe(df_mostrar_area, use_container_width=True, hide_index=True)
    with col_t2:
        st.markdown("**Promedios Regionales Red Toyota**")
        df_mostrar_reg = df_reg.copy()
        df_mostrar_reg["% Ideal"] = df_mostrar_reg["% Ideal"].map("{:.2f}%".format)
        st.dataframe(df_mostrar_reg, use_container_width=True, hide_index=True)

# ==========================================
# 3. PESTAÑA: ANÁLISIS DE CALIDAD
# ==========================================
with tab_calidad:
    st.subheader("🕵️ Informe Clínico de Calidad: Análisis de Pareto por Sucursal")
    df_p = pd.DataFrame()
    df_p["Categoría"] = ["Demoras y puntualidad", "Comunicación y seguimiento", "Administración y documentación", "Cortesías y obsequios", "Atención y actitud", "Instalaciones y comodidad", "Preparación y accesorios", "Explicación del vehículo", "Protocolo y personalización", "Producto o marca"]
    df_p["Jujuy_Menciones"] = [35, 25, 12, 8, 6, 5, 4, 2, 2, 1]
    df_p["Salta_Menciones"] = [18, 32, 22, 10, 7, 4, 3, 2, 1, 1]
    df_p["Tartagal_Menciones"] = [28, 14, 8, 22, 5, 3, 3, 1, 1, 0]

    sucursal = st.selectbox("📍 Seleccione la Sucursal a Diagnosticar:", ["Jujuy", "Salta", "Tartagal"])
    col_menciones = f"{sucursal}_Menciones"
    df_suc = df_p[["Categoría", col_menciones]].copy().sort_values(by=col_menciones, ascending=False)
    df_suc = df_suc[df_suc[col_menciones] > 0]
    total_menciones = df_suc[col_menciones].sum()
    df_suc["Porcentaje"] = (df_suc[col_menciones] / total_menciones) * 100
    df_suc["Acumulado"] = df_suc["Porcentaje"].cumsum()

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(x=df_suc["Categoría"], y=df_suc[col_menciones], name="Cantidad de Menciones", marker_color="#1F4E78", text=df_suc[col_menciones], textposition="inside"))
    fig_pareto.add_trace(go.Scatter(x=df_suc["Categoría"], y=df_suc["Acumulado"], name="Curva Acumulada %", yaxis="y2", mode="lines+markers", line=dict(color="#d62728", width=3)))
    fig_pareto.update_layout(title=f"Diagrama de Pareto de Calidad - Sucursal {sucursal}", xaxis=dict(title="Categorías Críticas", tickangle=-25), yaxis=dict(title="Número de Quejas (Cantidad)"), yaxis2=dict(title="Porcentaje Acumulado %", overlaying="y", side="right", range=[0, 105]), legend=dict(orientation="h", yanchor="top", y=-0.45, xanchor="center", x=0.5), margin=dict(b=140), height=550)
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown("---")
    st.subheader("📌 Diagnóstico Clínico de Foco Estratégico:")
    if sucursal == "Jujuy": st.info("🎯 **Foco Crítico en Jujuy**: El 60% de los desvíos se concentran en **Demoras y Puntualidad** junto a **Comunicación y Seguimiento**. Es urgente atacar estos dos frentes en el taller para estabilizar el SSI operativo.")
    elif sucursal == "Salta": st.info("🎯 **Foco Crítico en Salta**: La debilidad principal radica en **Comunicación y Seguimiento** junto a **Administración de Documentos**. Se debe estandarizar el flujo administrativo en las entregas convencionales.")
    elif sucursal == "Tartagal": st.info("🎯 **Foco Crítico en Tartagal**: Los reclamos están liderados por **Demoras y Puntualidad** y **Cortesías u Obsequios**. Es clave sincronizar los tiempos de alistamiento y revisar la entrega de kits de seguridad.")

# ==========================================
# 4. PESTAÑA: PLAN DE ACCIÓN INTERACTIVO
# ==========================================
with tab_plan:
    st.subheader("📋 Matriz de Compromisos Kaizen (Evidencias de Auditoría)")
    st.markdown("Ecosistema primario de seguimiento acoplado a los **Códigos Oficiales del Manual DEP 2026**:")

    if "db_plan_puro_v14" not in st.session_state or st.session_state.db_plan_puro_v14 is None:
        cods = ["", "1.1.1", "3.1.1", "1.1.3", "1.1.1", "1.5.6", "6.1.1", "4.3.1", "9.3.2", "9.3.3", "9.4.1", "9.4.1", "1.5.5", "1.5.6", "1.5.5", "3.5.2", "7.5.5", "9.5.3", "5.5.5"]
        secs = ["Coordinación", "Ventas", "Posventa", "Ventas", "Ventas", "Ventas", "Usados", "TPA", "RRHH", "RRHH", "Facilities", "Facilities", "Ventas", "Ventas", "Ventas", "Posventa", "TCFA", "General", "KINTO"]
        tems = ["Programa DEP - Gobernanza", "Ventas - SSI Kits de Entrega", "Posventa - CSI Taller y Servicio", "Ventas - NPS Fidelidad Encuestas", "Ventas - SSI Mystery Shopper", "Ventas - CRM Adopción Digital", "Usados - SSI Certificados UCT", "TPA - Estructura Adecuada Adm.", "RRHH - Capacitación Matriz por Puesto", "RRHH - Rotación de Personal General", "Facilities - Instalaciones Las Lajitas", "Facilities - Reformas Salta Chapa/Pintura 2.0", "Ventas - Salesforce Lista Espera", "Ventas - CRM Tiempos de Respuesta", "Ventas - Salesforce Depuración Boletos", "Posventa - Campañas de Seguridad Airbags", "TCFA - Crecimiento Cartera Seguros", "General - Servicios Conectados App Onboarding", "KINTO - Gestión de Siniestros One"]
        sits = ["", "Falta kit obsequio en entrega", "Tasa de quejas en servicio post-entrega", "Baja tasa respuesta encuestas NPS", "Desvíos en atención de asesores", "Falta visibilidad avance leads", "Estándar flojo inspección UCT", "Sobrecarga en administración TPA", "Riesgo incumplimiento horas YTD", "Inestabilidad en la nómina general", "Obras pendientes 2025", "Pendiente traslado físico lavaderos", "Boletos estancados en proceso", "Demoras atención prospectos digital", "Boletos vencidos sin actividad", "Baja tasa contacto campañas masivas", "Desvío meta crecimiento pólizas", "Baja tasa activación de la app", "Procesos sueltos en unidades One"]
        accs = ["Tablero único de control, calendario de vencimientos y evidencias transversales", "Kits de seguridad como obsequio de Autolux en las entregas de unidades", "Estandarización de recepción en taller y seguimiento post-servicio", "Campaña de fidelización con sorteos activos en encuestas de la red", "Implementación obligatoria de auditorías mystery shopper en salones", "Desarrollo de un tablero único de control de KPIs CRM centrales", "Reorganización completa de toma, entrega y venta de unidades UCT", "Incorporación de 2 colaboradores administrativos para el área de planes", "Plan de seguimiento semestral obligatorio junto a Recursos Humanos", "Control y estabilización de la nómina general", "Negociación con fieldman TASA sobre obras no hechas planteadas 2025", "Planificar reformas 2.0 de Chapa, Pintura y traslado de lavaderos", "Seguimiento diario con foco crítico a cierre de mes en carpetas", "Garantizar atención de prospectos digitales en menos de 2 horas en CRM", "Eliminación activa de boletos vencidos sin actividad comercial en sistema", "Citaciones masivas Airbags ABI 414/415 para subir de escalón", "Revisar el método de cálculo para crecimiento de pólizas comerciales", "Seguimiento focalizado en revendedores y empresas para la activación app", "Revisar proceso de seguimiento junto al área de Posventa de flota"]
        resps = ["", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Pablo Carrizo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Daniel Colque", "Daniel Colque", "Alfredo Aguilar", "Lucía de los Ríos", "Lucía de los Ríos", "Daniel Colque", "Lucía de los Ríos", "Romina R.", "Aaron Martearena"]
        
        rows = [[i+1, cods[i], secs[i], tems[i], sits[i], accs[i], "ALTA", "Evidencia", resps[i], "", "", "EN PROCESO", 0.0] for i in range(19)]
        st.session_state.db_plan_puro_v14 = pd.DataFrame(rows, columns=["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "Objetivo Simulación (%)"])

    df_ed_1 = st.data_editor(st.session_state.db_plan_puro_v14, use_container_width=True, key="grilla1_v14", hide_index=True, column_config={"#": st.column_config.NumberColumn(disabled=True), "Código Auditoría Manual": st.column_config.TextColumn(disabled=False), "Gerencia / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True), "Situación actual": st.column_config.TextColumn(disabled=False), "Acción Correctiva": st.column_config.TextColumn(disabled=True), "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador / Entregable": st.column_config.TextColumn(disabled=True), "Responsable": st.column_config.TextColumn(disabled=False), "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"]), "Objetivo Simulación (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.1f%%")})

    st.markdown("---")
    st.subheader("🚀 Ampliación de Simulación Estratégica (Para alcanzar el Puesto 1)")
    if "db_ampliacion_v14" not in st.session_state or st.session_state.db_ampliacion_v14 is None:
        rows_a = [
            [1, "2.5.1", "Ventas Especiales", "Licitaciones Corporativas (VE + Kinto ONE)", "Brecha en cumplimiento del plan de negocios corporativo", "Plan de reactivación de licitaciones corporativas y flotas Kinto", "ALTA", "Licitaciones ganadas", "Alfredo Aguilar", "", "", "EN PROCESO", 80.0], 
            [2, "8.5.1", "ESG", "E - Plan de Reducción Emisiones CO2", "Plan de CO2 sin presentar a TASA", "Desarrollo y presentación del plan de reducción de CO2 con metas medibles", "ALTA", "Plan CO2 presentado TASA", "", "", "", "EN PROCESO", 100.0],
            [3, "8.5.3", "ESG", "G - Políticas ABAC y Sustentabilidad", "Reporte ABAC pendiente", "Confección y entrega del reporte formal de políticas ABAC y Compliance", "ALTA", "Reporte ABAC TASA", "", "", "", "EN PROCESO", 100.0]
        ]
        st.session_state.db_ampliacion_v14 = pd.DataFrame(rows_a, columns=["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "Objetivo Simulación (%)"])

    df_ed_2 = st.data_editor(st.session_state.db_ampliacion_v14, use_container_width=True, key="grilla2_v14", hide_index=True, column_config={"#": st.column_config.NumberColumn(disabled=True), "Código Auditoría Manual": st.column_config.TextColumn(disabled=True), "Gerencia / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True), "Situación actual": st.column_config.TextColumn(disabled=True), "Acción Correctiva": st.column_config.TextColumn(disabled=True), "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador / Entregable": st.column_config.TextColumn(disabled=True), "Responsable": st.column_config.TextColumn(disabled=False), "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"]), "Objetivo Simulación (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.1f%%")})

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🧮 Simular e Impactar Dashboard"):
            st.session_state.db_plan_puro_v14 = df_ed_1
            st.session_state.db_ampliacion_v14 = df_ed_2
            for _, r in df_ed_1.iterrows():
                tg = r["Objetivo Simulación (%)"]
                if tg > 0:
                    cod, ger = str(r["Código Auditoría Manual"]), str(r["Gerencia / Sector"])
                    if "1.1" in cod or "1.5" in cod or "Ventas" in ger: st.session_state.sim_pilar_ventas = tg
                    elif "3.1" in cod or "3.5" in cod or "Posventa" in ger: st.session_state.sim_pilar_posventa = tg
                    elif "4.1" in cod or "4.3" in cod or "4.5" in cod: st.session_state.sim_pilar_tpa = tg
                    elif "5.1" in cod or "5.5" in cod: st.session_state.sim_pilar_kinto = tg
                    elif "7.5" in cod: st.session_state.sim_pilar_tcfa = tg
                    elif "6.1" in cod or "6.5" in cod: st.session_state.sim_pilar_usados = tg
                    elif "9.3" in cod or "9.4" in cod or "9.5" in cod or "Facilities" in ger or "RRHH" in ger: st.session_state.sim_pilar_general = tg
            for _, r in df_ed_2.iterrows():
                tg = r["Objetivo Simulación (%)"]
                if tg > 0:
                    cod = str(r["Código Auditoría Manual"])
                    if "2.5" in cod: st.session_state.sim_pilar_especiales = tg
                    elif "8.5" in cod: st.session_state.sim_pilar_esg = tg
            st.success("🎉 Simulación procesada con ponderaciones exactas del Manual DEP 2026.")
            st.rerun()
            
    with c_btn2:
        if st.button("🧹 Limpiar Simulación"):
            for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg", "db_plan_puro_v14", "db_ampliacion_v14"]: 
                if k in st.session_state: st.session_state[k] = None
            for ek in ["emt_a", "emt_b", "emt_c", "emt_d", "emt_e", "emt_f", "emt_g", "emt_h", "emt_i"]: st.session_state[ek] = 100
            st.success("🧹 Reset completado.")
            st.rerun()

    def generar_excel_formateado(df1, df2):
        output = io.BytesIO()
        wb = openpyxl.Workbook()
        header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        data_font = Font(name="Calibri", size=10, bold=False, color="000000")
        thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )
        
        ws1 = wb.active
        ws1.title = "Plan de Accion Oficial"
        ws1.append(list(df1.columns))
        for cell in ws1[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
        for row in df1.itertuples(index=False):
            ws1.append(list(row))
            
        for row in ws1.iter_rows(min_row=2, max_row=ws1.max_row, min_col=1, max_col=ws1.max_column):
            for cell in row:
                cell.font = data_font
                cell.border = thin_border
                if isinstance(cell.value, float) or isinstance(cell.value, int):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    
        for col in ws1.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws1.column_dimensions[col_letter].width = max(max_len + 3, 12)

        ws2 = wb.create_sheet(title="Ampliacion DEP")
        ws2.append(list(df2.columns))
        for cell in ws2[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            
        for row in df2.itertuples(index=False):
            ws2.append(list(row))
            
        for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row, min_col=1, max_col=ws2.max_column):
            for cell in row:
                cell.font = data_font
                cell.border = thin_border
                if isinstance(cell.value, float) or isinstance(cell.value, int):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                    
        for col in ws2.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = openpyxl.utils.get_column_letter(col[0].column)
            ws2.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(output)
        return output.getvalue()

    excel_data = generar_excel_formateado(st.session_state.db_plan_puro_v14, st.session_state.db_ampliacion_v14)
    st.download_button(
        label="📥 Descargar Agenda en Excel Formateado", 
        data=excel_data, 
        file_name="Plan_de_Accion_Oficial_Autolux.xlsx", 
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==========================================
# 5. PESTAÑA: DOCUMENTACIÓN Y FUENTES
# ==========================================
with tab_docs:
    st.subheader("📚 Centro de Documentación y Fuentes Oficiales TASA")
    st.markdown("Consulte las reglas metodológicas, las planillas de origen y la matriz completa de indicadores DEP 2026:")

    c_doc1, c_doc2 = st.columns(2)
    
    with c_doc1:
        st.info("📄 **Manual Oficial DEP 2026**\n\nDocumento normativo de Toyota Argentina con la descripción, criterios de asignación de puntaje y ponderaciones por área.")
        try:
            with open("Manual DEP 2026.pdf", "rb") as pdf_file:
                st.download_button(
                    label="📥 Descargar Manual DEP 2026 (PDF)",
                    data=pdf_file,
                    file_name="Manual DEP 2026.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.warning("⚠️ No se encontró 'Manual DEP 2026.pdf' en el directorio raíz.")

    with c_doc2:
        st.success("📊 **Planilla Acumulada Oficial (Junio 2026)**\n\nResultados oficiales de la Red TASA extraídos directamente del sistema de auditoría Power BI.")
        try:
            with open("15437_DES015-26 DEP 2026 - ACUM. JUN 2.xlsx", "rb") as excel_file:
                st.download_button(
                    label="📥 Descargar Planilla Acumulada (Excel)",
                    data=excel_file,
                    file_name="15437_DES015-26 DEP 2026 - ACUM. JUN 2.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.warning("⚠️ No se encontró la planilla acumulada Excel en el directorio raíz.")

    st.divider()
    st.subheader("🔍 Catálogo Completo de Indicadores del Manual DEP 2026")

    items_manual = [
        ("1.1.1", "Ventas", "Calidad", "SSI - Sales Satisfaction Index", "Mensual", "4,5%"),
        ("1.1.2", "Ventas", "Calidad", "ICQ - Índice de Contención de Quejas", "Cuatrimestral", "1,5%"),
        ("1.1.3", "Ventas", "Calidad", "NPS - Net Promoter Score Ventas", "Mensual", "1,2%"),
        ("1.4.1", "Ventas", "Facilities", "Imagen, Mantenimiento y 5S: Exterior e interior", "Semestral", "3,0%"),
        ("1.5.1", "Ventas", "Targets", "Cumplimiento de objetivos acumulados Hilux, SW4 & Hiace", "Mensual", "3,0%"),
        ("1.5.2", "Ventas", "Targets", "Cumplimiento de obj. acumulados Corolla, CCross, Yaris, Yaris Cross", "Mensual", "3,0%"),
        ("1.5.3", "Ventas", "Targets", "Patentamientos vs declaración de ventas", "Mensual", "2,1%"),
        ("1.5.4", "Ventas", "Targets", "Extrazona / Cobertura", "Mensual", "0,7%"),
        ("1.5.5", "Ventas", "Targets", "Actualización Salesforce: Lista de Espera y Patentamientos", "Mensual", "1,5%"),
        ("1.5.6", "Ventas", "Targets", "Gestión Digital y Adopción CRM", "Mensual", "1,5%"),
        ("2.5.1", "Ventas Especiales", "Targets", "Cumplimiento de plan de negocios (VE + Kinto ONE)", "Cuatrimestral", "3,5%"),
        ("2.5.2", "Ventas Especiales", "Targets", "Lista de espera actualizada", "Cuatrimestral", "1,5%"),
        ("3.1.1", "Posventa", "Calidad", "CSI - Customer Satisfaction Index Posventa", "Mensual", "2,7%"),
        ("3.1.2", "Posventa", "Calidad", "FIR - Fix It Right", "Mensual", "2,7%"),
        ("3.1.3", "Posventa", "Calidad", "ICQ - Índice de Contención de Quejas Posventa", "Cuatrimestral", "1,0%"),
        ("3.1.4", "Posventa", "Calidad", "NPS - Net Promoter Score Posventa", "Mensual", "1,4%"),
        ("3.1.5", "Posventa", "Calidad", "CSI de Chapa y Pintura (B&P)", "Mensual", "0,7%"),
        ("3.2.1", "Posventa", "Programas", "Certificación TSM-FIR", "Semestral", "1,4%"),
        ("3.2.2", "Posventa", "Programas", "Programas de excelencia (Mantenimiento Express - Lavado)", "Semestral", "2,0%"),
        ("3.2.3", "Posventa", "Programas", "EcoDealer / ISO 14001", "Semestral", "1,0%"),
        ("3.2.4", "Posventa", "Programas", "Sostenimiento periódico de la operación (Visitas Fieldman)", "Mensual", "4,0%"),
        ("3.3.1", "Posventa", "RRHH", "Índice de rotación del personal de posventa", "Anual", "1,4%"),
        ("3.3.2", "Posventa", "RRHH", "Dotación de personal de posventa", "Semestral", "2,7%"),
        ("3.5.1", "Posventa", "Targets", "CPUS - Unidades Atendidas en Taller", "Mensual", "1,7%"),
        ("3.5.2", "Posventa", "Targets", "Campañas de Seguridad Airbags (ABI 414/415)", "Mensual", "1,4%"),
        ("3.5.3", "Posventa", "Targets", "Objetivo de Accesorios", "Mensual", "1,0%"),
        ("3.5.4", "Posventa", "Targets", "Objetivo de Neumáticos", "Mensual", "1,0%"),
        ("3.5.5", "Posventa", "Targets", "Performance de garantías (RDG)", "Mensual", "0,6%"),
        ("3.5.6", "Posventa", "Targets", "Nivelación de pedidos de repuestos", "Mensual", "0,3%"),
        ("3.5.7", "Posventa", "Targets", "Puntos Negativos (Compromisos Fieldman / Obj. Cualitativos)", "Cuatrimestral", "-3,4%"),
        ("4.1.1", "TPA", "Calidad", "ICQ - Índice de Contención de Quejas TPA", "Mensual", "0,8%"),
        ("4.1.2", "TPA", "Calidad", "NPS Transaccional (Suscriptor - Adjudicado - Entregado)", "Cuatrimestral", "0,8%"),
        ("4.3.1", "TPA", "RRHH", "Estructura de RRHH de administración TPA", "Semestral", "0,6%"),
        ("4.5.1", "TPA", "Targets", "Suscripciones (Mix de modelos & Venta Online)", "Mensual", "2,0%"),
        ("4.5.2", "TPA", "Targets", "Pedidos confirmados", "Mensual", "1,4%"),
        ("4.5.3", "TPA", "Targets", "Caída temprana (Baja en primeros 6 meses)", "Mensual", "2,0%"),
        ("4.5.4", "TPA", "Targets", "Cuotas emitidas (Crecimiento de cartera)", "Mensual", "1,4%"),
        ("5.1.1", "KINTO", "Calidad", "ICQ - Share", "Mensual", "0,2%"),
        ("5.1.2", "KINTO", "Calidad", "NPS - Share", "Mensual", "0,6%"),
        ("5.1.3", "KINTO", "Calidad", "NPS - One", "Mensual", "0,6%"),
        ("5.5.1", "KINTO", "Targets", "Porcentaje de ocupación - Share", "Mensual", "0,7%"),
        ("5.5.2", "KINTO", "Targets", "Flota mínima - Share", "Mensual", "0,7%"),
        ("5.5.3", "KINTO", "Targets", "Bookings - Share", "Mensual", "0,7%"),
        ("5.5.4", "KINTO", "Targets", "Preparación y entregas de unidades - One", "Trimestral", "0,3%"),
        ("5.5.5", "KINTO", "Targets", "Gestión de siniestros - One", "Trimestral", "0,3%"),
        ("5.5.6", "KINTO", "Targets", "PN Corporativo - Bookings - One", "Mensual", "1,2%"),
        ("5.5.7", "KINTO", "Targets", "Devolución y Venta de unidades - One", "Mensual", "0,7%"),
        ("6.1.1", "Usados", "Calidad", "SSI - Sales Satisfaction Index Usados Certificados (UCT)", "Mensual", "0,8%"),
        ("6.1.2", "Usados", "Calidad", "NPS - Net Promoter Score Usados Certificados (UCT)", "Mensual", "0,8%"),
        ("6.5.1", "Usados", "Targets", "Ventas UCT (Oro y Plata)", "Mensual", "3,2%"),
        ("6.5.2", "Usados", "Targets", "Trade In % (Toma/Compra vs Venta Convencional)", "Mensual", "1,2%"),
        ("7.5.1", "TCFA", "Targets", "Financiación (M$ Liquidaciones 0km y Usados)", "Mensual", "1,7%"),
        ("7.5.2", "TCFA", "Targets", "Seguros 0km", "Mensual", "0,8%"),
        ("7.5.3", "TCFA", "Targets", "Seguros Usados", "Mensual", "0,6%"),
        ("7.5.4", "TCFA", "Targets", "Fidelidad en 0km (Prendas inscriptas TCFA)", "Mensual", "0,6%"),
        ("7.5.5", "TCFA", "Targets", "Crecimiento Cartera de seguros", "Mensual", "0,4%"),
        ("8.5.1", "ESG", "Targets", "E: Envío de plan con actividades de reducción de emisiones de CO2", "Proyecto", "0,3%"),
        ("8.5.2", "ESG", "Targets", "S: Iniciativa Social alineada a temas materiales de TMC", "Proyecto", "0,35%"),
        ("8.5.3", "ESG", "Targets", "G: Políticas ABAC / Reporte Sustentabilidad", "Proyecto", "0,35%"),
        ("9.1.1", "General", "Calidad", "Excelencia Calidad (Premio por cumplir NPS en todas las áreas)", "Semestral", "1,6%"),
        ("9.2.1", "General", "Programas", "Estilo de Movilidad Toyota - EMT (Puntos Negativos)", "Semestral", "-5,0%"),
        ("9.2.2", "General", "Programas", "Círculos Kaizen", "Anual", "0,4%"),
        ("9.3.1", "General", "RRHH", "Dotación Adecuada (Estructura de Mkt, RRHH y Calidad)", "Semestral", "3,5%"),
        ("9.3.2", "General", "RRHH", "Capacitación (Matriz de niveles aprobados por puesto)", "Semestral", "3,5%"),
        ("9.3.3", "General", "RRHH", "Nivel de rotación de personal general", "Anual", "0,6%"),
        ("9.3.4", "General", "RRHH", "Satisfacción de empleados (Encuesta Clima Laboral)", "Anual", "3,3%"),
        ("9.4.1", "General", "Facilities", "Objetivos cualitativos de Infraestructura (Instalaciones 2.0)", "Anual", "4,5%"),
        ("9.5.1", "General", "Targets", "Absorción de Costos Fijos", "Cuatrimestral", "0,9%"),
        ("9.5.2", "General", "Targets", "Fair Play (Penalización sobreprecios / reventas)", "Anual", "-10,0%"),
        ("9.5.3", "General", "Targets", "Vehículos con Full Onboarding de Servicios Conectados", "Mensual", "1,7%")
    ]

    df_cat = pd.DataFrame(items_manual, columns=["Código TASA", "Área", "Categoría", "Descripción Oficial TASA", "Frecuencia", "% Ponderado Total"])
    filtro_area = st.multiselect("Filtrar por Área:", options=df_cat["Área"].unique(), default=df_cat["Área"].unique())
    df_filtrado = df_cat[df_cat["Área"].isin(filtro_area)]
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
