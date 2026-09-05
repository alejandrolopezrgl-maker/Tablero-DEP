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
st.caption("Datos Oficiales e Informe de Calidad de la Red TASA (Manual DEP 2026 - Corte Julio)")

# LLAVES EMT DE CONTROL NATIVO
emt_keys = ["emt_a", "emt_b", "emt_c", "emt_d", "emt_e", "emt_f", "emt_g", "emt_h", "emt_i"]
for ek in emt_keys:
    if ek not in st.session_state:
        st.session_state[ek] = 100

for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg"]:
    if k not in st.session_state:
        st.session_state[k] = 0.0

# 2. BARRA LATERAL: CONTROL DE RIESGOS
st.sidebar.header("🚨 Zona de Control de Riesgos")
penalidad_fp = st.sidebar.toggle("Fair Play Global (-10 pts)", value=False)
penalidad_mov = st.sidebar.toggle("No Certificación EMT (-5.0 pts)", value=False)
visitas_fm = st.sidebar.slider("% Compromisos Fieldman", 0, 100, 85)

puntos_a_restar_global = 10.0 if penalidad_fp else 0.0
castigo_posventa_fieldman = 40.0 if visitas_fm < 85 else 0.0

if visitas_fm < 85: 
    st.sidebar.error("❌ Penalidad Posventa Activa (-40% en Score del área).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman a salvo (≥85%).")

# 3. VALORES BASE OFICIALES AUTOLUX (JULIO 2026 OFICIAL)
b_ventas = 38.0 if not penalidad_mov else (38.0 - 5.0)
b_posventa = 96.1 - (96.1 * (castigo_posventa_fieldman / 100))
b_tpa = 87.4
b_kinto = 41.7
b_tcfa = 83.0
b_general = 72.3
b_especiales = 30.0
b_usados = 73.3
b_esg = 35.5

def calcular_mejora(base, pct_avance):
    if pct_avance is None or pct_avance <= 0:
        return base
    brecha = max(0.0, 100.0 - base)
    return min(100.0, base + (brecha * (pct_avance / 100.0)))

v_simulada = calcular_mejora(b_ventas, st.session_state.sim_pilar_ventas)
p_simulada = calcular_mejora(b_posventa, st.session_state.sim_pilar_posventa)
tpa_simulada = calcular_mejora(b_tpa, st.session_state.sim_pilar_tpa)
kinto_simulada = calcular_mejora(b_kinto, st.session_state.sim_pilar_kinto)
tcfa_simulada = calcular_mejora(b_tcfa, st.session_state.sim_pilar_tcfa)
g_simulada = calcular_mejora(b_general, st.session_state.sim_pilar_general)
esp_simulada = calcular_mejora(b_especiales, st.session_state.sim_pilar_especiales)
usd_simulada = calcular_mejora(b_usados, st.session_state.sim_pilar_usados)
esg_simulada = calcular_mejora(b_esg, st.session_state.sim_pilar_esg)

# EVALUACIÓN EMT
total_puntos_emt = sum([st.session_state.get(ek, 100) for ek in emt_keys])
porcentaje_emt = (total_puntos_emt / 900.0) * 100
penalidad_estandar_emt = 0.0 if porcentaje_emt >= 80.0 else ((80.0 - porcentaje_emt) / 80.0) * 5.0

hay_simulacion = any([
    (st.session_state.get("sim_pilar_ventas") or 0) > 0,
    (st.session_state.get("sim_pilar_posventa") or 0) > 0,
    (st.session_state.get("sim_pilar_tpa") or 0) > 0,
    (st.session_state.get("sim_pilar_kinto") or 0) > 0,
    (st.session_state.get("sim_pilar_tcfa") or 0) > 0,
    (st.session_state.get("sim_pilar_general") or 0) > 0,
    (st.session_state.get("sim_pilar_especiales") or 0) > 0,
    (st.session_state.get("sim_pilar_usados") or 0) > 0,
    (st.session_state.get("sim_pilar_esg") or 0) > 0
])

target_p10 = 74.7  # SENNA (SEN)
target_p5 = 76.9   # PRANA (PRN)

if not hay_simulacion and not penalidad_fp and not penalidad_mov and visitas_fm >= 85 and porcentaje_emt >= 80.0:
    score_global_final = 68.6
    puesto_calculado = 21
else:
    score_global_final = (
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.20) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (usd_simulada * 0.06) + 
        (esp_simulada * 0.05) + (tcfa_simulada * 0.04) + (esg_simulada * 0.01)
    ) - puntos_a_restar_global - penalidad_estandar_emt
    if penalidad_mov: score_global_final -= 1.1

    if score_global_final <= 68.6:
        puesto_calculado = int(21 + ((68.6 - score_global_final) / 5.0) * 10)
        puesto_calculado = min(44, max(21, puesto_calculado))
    elif score_global_final >= 99.9:
        puesto_calculado = 1
    elif score_global_final >= target_p5:
        puesto_calculado = max(1, min(5, int(5 - ((score_global_final - target_p5) / (100.0 - target_p5)) * (5 - 1))))
    elif score_global_final >= target_p10:
        puesto_calculado = max(6, min(10, int(10 - ((score_global_final - target_p10) / (target_p5 - target_p10)) * (10 - 6))))
    else:
        puesto_calculado = max(11, min(21, int(21 - ((score_global_final - 68.6) / (target_p10 - 68.6)) * (21 - 11))))

# BENCHMARK OFICIAL JULIO CONTRA P5 (PRN) Y P10 (SEN)
data_operativa = {
    "Área": ["Ventas (22%)", "Ventas Especiales (5%)", "Posventa (27%)", "TPA (9%)", "KINTO (6%)", "Usados (6%)", "TCFA (4%)", "ESG (1%)", "GENERAL (20%)"],
    "Autolux (LUX)": [v_simulada, esp_simulada, p_simulada, tpa_simulada, kinto_simulada, usd_simulada, tcfa_simulada, esg_simulada, g_simulada],
    "PRN - Puesto 5": [87.4, 30.0, 97.0, 56.9, 41.7, 96.7, 22.0, 35.5, 76.7],
    "SEN - Puesto 10": [47.8, 30.0, 97.5, 87.3, 33.3, 96.7, 90.0, 35.5, 85.9],
    "Promedio RED": [57.0, 51.4, 88.9, 58.8, 56.3, 62.3, 61.4, 33.2, 66.7]
}
df_bench_op = pd.DataFrame(data_operativa)

data_ranking_global = {
    "Concesionario": ["PRN - Puesto 5", "SEN - Puesto 10", "Autolux (LUX) - Puesto 21", "Promedio RED"],
    "Porcentaje DEP Global": [76.9, 74.7, score_global_final, 67.7]
}
df_bench_ranking = pd.DataFrame(data_ranking_global)

if st.sidebar.button("🔄 Restablecer Valores Oficiales", key="btn_reset_lateral"):
    for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg", "db_plan_puro_v22"]: 
        if k in st.session_state: st.session_state[k] = None
    st.rerun()

# --- DECLARACIÓN DE LAS 6 PESTAÑAS ---
tab_dashboard, tab_evolucion, tab_regional, tab_calidad, tab_plan, tab_docs = st.tabs([
    "📊 Dashboard del Dealer", 
    "📈 Evolución Junio vs. Julio",
    "🗺️ Desempeño Regional y por Área",
    "🕵️ Análisis de Calidad por Sucursal", 
    "📋 Plan de Acción Interactiva",
    "📚 Documentación y Fuentes"
])

# ==========================================
# 1. PESTAÑA: DASHBOARD DEL DEALER
# ==========================================
with tab_dashboard:
    pts_para_p10 = max(0.0, target_p10 - score_global_final)
    pts_para_p5 = max(0.0, target_p5 - score_global_final)

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Cumplimiento DEP Score Global (Julio)", f"{score_global_final:.1f}%", delta="+6.6% vs Junio (62.0%)")
    with col2: 
        if puesto_calculado < 21: st.metric("Ranking Proyectado Red", f"Puesto {puesto_calculado} 🏆", delta=f"¡Subiendo {21 - puesto_calculado} puestos!")
        elif puesto_calculado > 21: st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🚨", delta=f"¡Bajando {puesto_calculado - 21} puestos!")
        else: st.metric("Ranking General Red", f"Puesto 21 🚗", delta="Subió 3 puestos vs Junio (P24)")
    with col3:
        if pts_para_p5 == 0: st.metric("Puntos para Meta Superlativa", "¡En Puesto 5 o superior! 🎉")
        else: st.metric(label="Puntos Faltantes para Top 10 / Top 5", value=f"+{pts_para_p10:.1f} pts (P10 - SEN)", delta=f"+{pts_para_p5:.1f} pts para Puesto 5 (PRN)", delta_color="inverse")

    st.subheader("🏁 Desempeño Operativo vs. Benchmarks Oficiales (Julio 2026)")
    df_melted_op = df_bench_op.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_op = px.bar(
        df_melted_op, 
        x="Área", 
        y="Cumplimiento %", 
        color="Concesionario", 
        barmode="group", 
        text_auto=".1f", 
        color_discrete_map={
            "Autolux (LUX)": "#d62728", 
            "PRN - Puesto 5": "#1F4E78", 
            "SEN - Puesto 10": "#5B9BD5", 
            "Promedio RED": "#70AD47"
        }
    )
    fig_op.update_layout(xaxis_title="Unidad Operativa", yaxis_title="Efectividad %", yaxis=dict(range=[0, 110]))
    st.plotly_chart(fig_op, use_container_width=True)

    st.subheader("🏆 Posicionamiento Estratégico Consolidado RED")
    fig_gen = px.bar(
        df_bench_ranking, 
        x="Concesionario", 
        y="Porcentaje DEP Global", 
        color="Concesionario", 
        text_auto=".1f", 
        color_discrete_map={
            "Autolux (LUX) - Puesto 21": "#d62728", 
            "PRN - Puesto 5": "#1F4E78", 
            "SEN - Puesto 10": "#5B9BD5", 
            "Promedio RED": "#70AD47"
        }
    )
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
    
    if porcentaje_emt < 80.0: st.error(f"🚨 Alerta DEP: Estándar EMT en {total_puntos_emt} / 900 ({porcentaje_emt:.1f}%). Penalidad activa.")
    else: st.success(f"🎉 Estándar EMT Certificado Oficialmente: {total_puntos_emt} / 900 ({porcentaje_emt:.1f}%). Concesionario a salvo.")

# =======================================================
# 2. PESTAÑA: EVOLUCIÓN JUNIO VS JULIO
# =======================================================
with tab_evolucion:
    st.subheader("📈 Comparativo Evolutivo Oficial: Junio 2026 vs. Julio 2026")
    c_ev1, c_ev2, c_ev3 = st.columns(3)
    with c_ev1: st.metric("Cumplimiento DEP Global", "68,6%", delta="+6,6% vs Junio (62,0%)")
    with c_ev2: st.metric("Posición Ranking Red", "Puesto 21", delta="Subió 3 puestos (era P24)")
    with c_ev3: st.metric("Brecha para Top 10 (SEN)", "6,1 pts", delta="Superando el Promedio RED (67,7%)")

    st.markdown("---")
    df_comp = pd.DataFrame({
        "Área": ["TPA", "Ventas", "ESG", "TCFA", "General", "KINTO", "Posventa", "Ventas Esp.", "Usados"],
        "Junio 2026": [72.8, 25.0, 25.0, 73.0, 65.7, 35.8, 95.2, 30.0, 73.3],
        "Julio 2026": [87.4, 38.0, 35.5, 83.0, 72.3, 41.7, 96.1, 30.0, 73.3],
        "Variación (%)": [+14.6, +13.0, +10.5, +10.0, +6.6, +5.9, +0.9, 0.0, 0.0],
        "Posición Red (Jun ➔ Jul)": ["P4 ➔ P5", "P42 ➔ P41", "P8 ➔ P7", "P18 ➔ P16", "P26 ➔ P20", "P41 ➔ P41", "P9 ➔ P9", "P21 ➔ P20", "P14 ➔ P16"],
        "Estado": ["🟢 Mejoró", "🟢 Mejoró", "🟢 Mejoró", "🟢 Mejoró", "🟢 Mejoró", "🟢 Mejoró", "🟢 Mejoró", "🟡 Quedó Igual", "🟡 Quedó Igual"]
    }).sort_values(by="Variación (%)", ascending=False)

    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(x=df_comp["Área"], y=df_comp["Junio 2026"], name="Junio 2026", marker_color="#A6A6A6", text=df_comp["Junio 2026"], textposition="outside"))
    fig_comp.add_trace(go.Bar(x=df_comp["Área"], y=df_comp["Julio 2026"], name="Julio 2026", marker_color="#1F4E78", text=df_comp["Julio 2026"], textposition="outside"))
    fig_comp.update_layout(title="Comparativa de Cumplimiento por Unidad (Junio vs Julio 2026)", barmode="group", yaxis=dict(range=[0, 110]))
    st.plotly_chart(fig_comp, use_container_width=True)

# =======================================================
# 3. PESTAÑA: DESEMPEÑO REGIONAL Y POR ÁREA (POWER BI)
# =======================================================
with tab_regional:
    st.subheader("🗺️ Diagnóstico Integral por Áreas y Benchmarking Regional (Julio 2026)")
    
    data_area_lux = {
        "Área": ["POSVENTA", "TPA", "TCFA", "USADOS", "GENERAL", "KINTO", "VENTAS", "ESG", "VENTAS ESP."],
        "Posición Red": [9, 5, 16, 16, 20, 41, 41, 7, 20],
        "% Ideal LUX": [96.1, 87.4, 83.0, 73.3, 72.3, 41.7, 38.0, 35.5, 30.0]
    }
    df_area_lux = pd.DataFrame(data_area_lux)

    fig_area = px.bar(
        df_area_lux, 
        x="% Ideal LUX", 
        y="Área", 
        orientation="h", 
        text="% Ideal LUX", 
        color="% Ideal LUX", 
        color_continuous_scale=["#d62728", "#f39c12", "#27ae60"], 
        title="Efectividad de Autolux por Unidad (% Cumplimiento Oficial Julio)"
    )
    fig_area.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_area.update_layout(xaxis=dict(range=[0, 115]), yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
    st.plotly_chart(fig_area, use_container_width=True)

    st.subheader("📋 Tabla Oficial Comparativa contra P5 (PRN) y P10 (SEN)")
    st.dataframe(df_bench_op, use_container_width=True, hide_index=True)

# ==========================================
# 4. PESTAÑA: ANÁLISIS DE CALIDAD
# ==========================================
with tab_calidad:
    st.subheader("🕵️ Informe Clínico de Calidad: Análisis de Pareto por Sucursal")
    df_p = pd.DataFrame({
        "Categoría": ["Demoras y puntualidad", "Comunicación y seguimiento", "Administración y documentación", "Cortesías y obsequios", "Atención y actitud", "Instalaciones y comodidad", "Preparación y accesorios", "Explicación del vehículo", "Protocolo y personalización", "Producto o marca"],
        "Jujuy_Menciones": [35, 25, 12, 8, 6, 5, 4, 2, 2, 1],
        "Salta_Menciones": [18, 32, 22, 10, 7, 4, 3, 2, 1, 1],
        "Tartagal_Menciones": [28, 14, 8, 22, 5, 3, 3, 1, 1, 0]
    })
    sucursal = st.selectbox("📍 Seleccione la Sucursal a Diagnosticar:", ["Jujuy", "Salta", "Tartagal"])
    col_m = f"{sucursal}_Menciones"
    df_suc = df_p[["Categoría", col_m]].sort_values(by=col_m, ascending=False)
    df_suc = df_suc[df_suc[col_m] > 0]
    df_suc["Porcentaje"] = (df_suc[col_m] / df_suc[col_m].sum()) * 100
    df_suc["Acumulado"] = df_suc["Porcentaje"].cumsum()

    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(x=df_suc["Categoría"], y=df_suc[col_m], name="Quejas", marker_color="#1F4E78", text=df_suc[col_m], textposition="inside"))
    fig_pareto.add_trace(go.Scatter(x=df_suc["Categoría"], y=df_suc["Acumulado"], name="Curva %", yaxis="y2", mode="lines+markers", line=dict(color="#d62728", width=3)))
    fig_pareto.update_layout(title=f"Diagrama de Pareto - Sucursal {sucursal}", yaxis2=dict(title="% Acumulado", overlaying="y", side="right", range=[0, 105]))
    st.plotly_chart(fig_pareto, use_container_width=True)

# ==========================================
# 5. PESTAÑA: PLAN DE ACCIÓN INTERACTIVO
# ==========================================
with tab_plan:
    st.subheader("📋 Matriz de Compromisos Kaizen (Evidencias de Auditoría)")
    if "db_plan_puro_v22" not in st.session_state or st.session_state.db_plan_puro_v22 is None:
        cods = ["", "1.1.1", "3.1.1", "1.1.3", "1.1.1", "1.5.6", "6.1.1", "4.3.1", "9.3.2", "9.3.3", "9.4.1", "9.4.1", "1.5.5", "1.5.6", "1.5.5", "3.5.2", "7.5.5", "9.5.3", "5.5.5"]
        secs = ["Coordinación", "Ventas", "Posventa", "Ventas", "Ventas", "Ventas", "Usados", "TPA", "RRHH", "RRHH", "Facilities", "Facilities", "Ventas", "Ventas", "Ventas", "Posventa", "TCFA", "General", "KINTO"]
        tems = ["Programa DEP - Gobernanza", "Ventas - SSI Kits de Entrega", "Posventa - CSI Taller y Servicio", "Ventas - NPS Fidelidad Encuestas", "Ventas - SSI Mystery Shopper", "Ventas - CRM Adopción Digital", "Usados - SSI Certificados UCT", "TPA - Estructura Adecuada Adm.", "RRHH - Capacitación Matriz por Puesto", "RRHH - Rotación de Personal General", "Facilities - Instalaciones Las Lajitas", "Facilities - Reformas Salta Chapa/Pintura 2.0", "Ventas - Salesforce Lista Espera", "Ventas - CRM Tiempos de Respuesta", "Ventas - Salesforce Depuración Boletos", "Posventa - Campañas de Seguridad Airbags", "TCFA - Crecimiento Cartera Seguros", "General - Servicios Conectados App Onboarding", "KINTO - Gestión de Siniestros One"]
        sits = ["", "Falta kit obsequio en entrega", "Tasa de quejas en servicio post-entrega", "Baja tasa respuesta encuestas NPS", "Desvíos en atención de asesores", "Falta visibilidad avance leads", "Estándar flojo inspección UCT", "Sobrecarga en administración TPA", "Riesgo incumplimiento horas YTD", "Inestabilidad en la nómina general", "Obras pendientes 2025", "Pendiente traslado físico lavaderos", "Boletos estancados en proceso", "Demoras atención prospectos digital", "Boletos vencidos sin actividad", "Baja tasa contacto campañas masivas", "Desvío meta crecimiento pólizas", "Baja tasa activación de la app", "Procesos sueltos en unidades One"]
        accs = ["Tablero único de control, calendario de vencimientos y evidencias transversales", "Kits de seguridad como obsequio de Autolux en las entregas de unidades", "Estandarización de recepción en taller y seguimiento post-servicio", "Campaña de fidelización con sorteos activos en encuestas de la red", "Implementación obligatoria de auditorías mystery shopper en salones", "Desarrollo de un tablero único de control de KPIs CRM centrales", "Reorganización completa de toma, entrega y venta de unidades UCT", "Incorporación de 2 colaboradores administrativos para el área de planes", "Plan de seguimiento semestral obligatorio junto a Recursos Humanos", "Control y estabilización de la nómina general", "Negociación con fieldman TASA sobre obras no hechas planteadas 2025", "Planificar reformas 2.0 de Chapa, Pintura y traslado de lavaderos", "Seguimiento diario con foco crítico a cierre de mes en carpetas", "Garantizar atención de prospectos digitales en menos de 2 horas en CRM", "Eliminación activa de boletos vencidos sin actividad comercial en sistema", "Citaciones masivas Airbags ABI 414/415 para subir de escalón", "Revisar el método de cálculo para crecimiento de pólizas comerciales", "Seguimiento focalizado en revendedores y empresas para la activación app", "Revisar proceso de seguimiento junto al área de Posventa de flota"]
        resps = ["", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Pablo Carrizo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Daniel Colque", "Daniel Colque", "Alfredo Aguilar", "Lucía de los Ríos", "Lucía de los Ríos", "Daniel Colque", "Lucía de los Ríos", "Romina R.", "Aaron Martearena"]
        rows = [[i+1, cods[i], secs[i], tems[i], sits[i], accs[i], "ALTA", "Evidencia", resps[i], "", "", "EN PROCESO", 0.0] for i in range(19)]
        st.session_state.db_plan_puro_v22 = pd.DataFrame(rows, columns=["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "% Avance Acción (Simulación)"])

    df_ed_1 = st.data_editor(st.session_state.db_plan_puro_v22, use_container_width=True, key="grilla1_v22", hide_index=True)

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🧮 Simular e Impactar Dashboard"):
            st.session_state.db_plan_puro_v22 = df_ed_1
            for _, r in df_ed_1.iterrows():
                tg = r["% Avance Acción (Simulación)"]
                cod, ger = str(r["Código Auditoría Manual"]), str(r["Gerencia / Sector"])
                if "1.1" in cod or "1.5" in cod or "Ventas" in ger: st.session_state.sim_pilar_ventas = max(st.session_state.sim_pilar_ventas or 0.0, tg)
                elif "3.1" in cod or "3.5" in cod or "Posventa" in ger: st.session_state.sim_pilar_posventa = max(st.session_state.sim_pilar_posventa or 0.0, tg)
                elif "4.1" in cod or "4.3" in cod or "4.5" in cod: st.session_state.sim_pilar_tpa = max(st.session_state.sim_pilar_tpa or 0.0, tg)
                elif "5.1" in cod or "5.5" in cod: st.session_state.sim_pilar_kinto = max(st.session_state.sim_pilar_kinto or 0.0, tg)
                elif "7.5" in cod: st.session_state.sim_pilar_tcfa = max(st.session_state.sim_pilar_tcfa or 0.0, tg)
                elif "6.1" in cod or "6.5" in cod: st.session_state.sim_pilar_usados = max(st.session_state.sim_pilar_usados or 0.0, tg)
                elif "9.3" in cod or "9.4" in cod or "9.5" in cod or "Facilities" in ger or "RRHH" in ger: st.session_state.sim_pilar_general = max(st.session_state.sim_pilar_general or 0.0, tg)
            st.success("🎉 Simulación procesada contra el estándar de Julio.")
            st.rerun()

    with c_btn2:
        if st.button("🧹 Limpiar Simulación"):
            for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg", "db_plan_puro_v22"]: 
                if k in st.session_state: st.session_state[k] = None
            st.success("🧹 Valores restablecidos a Julio (68.6% - P21).")
            st.rerun()

# ==========================================
# 6. PESTAÑA: DOCUMENTACIÓN Y FUENTES
# ==========================================
with tab_docs:
    st.subheader("📚 Centro de Documentación y Fuentes Oficiales TASA")
    st.markdown("Consulte los archivos oficiales de Toyota Argentina y el catálogo de indicadores DEP 2026:")

    c_doc1, c_doc2 = st.columns(2)
    with c_doc1:
        st.info("📄 **Manual Oficial DEP 2026**\n\nNormativa de Toyota Argentina con la descripción, criterios de calificación y ponderaciones por área.")
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
            st.warning("⚠️ 'Manual DEP 2026.pdf' no encontrado.")

    with c_doc2:
        st.success("📊 **Planilla Acumulada Oficial Julio 2026**\n\nResultados oficiales de la Red comercial (Acumulado Julio).")
        try:
            with open("15511_DES016 - DEP 2026 - Acum. Jul'26.xlsx", "rb") as excel_file:
                st.download_button(
                    label="📥 Descargar Planilla Julio 2026 (Excel)",
                    data=excel_file,
                    file_name="15511_DES016 - DEP 2026 - Acum. Jul'26.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.warning("⚠️ '15511_DES016 - DEP 2026 - Acum. Jul'26.xlsx' no encontrado.")

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
