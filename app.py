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

# LLAVES EMT DE CONTROL NATIVO
emt_keys = ["emt_a", "emt_b", "emt_c", "emt_d", "emt_e", "emt_f", "emt_g", "emt_h", "emt_i"]
for ek in emt_keys:
    if ek not in st.session_state:
        st.session_state[ek] = 100

for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg"]:
    if k not in st.session_state:
        st.session_state[k] = 0.0

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL: CONTROL DE RIESGOS PENALIDADES DE CAMPO
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

# 3. VALORES BASE OFICIALES DE AUTOLUX
b_ventas = 25.0 if not penalidad_mov else (25.0 - 5.0)
b_posventa = 95.19 - (95.19 * (castigo_posventa_fieldman / 100))
b_tpa = 72.78
b_kinto = 35.83
b_tcfa = 73.00
b_general = 65.65
b_especiales = 30.00
b_usados = 73.33
b_esg = 25.00

# FÓRMULA INCREMENTAL
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

# 4. CAPTURA Y CÁLCULO EMT
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

if not hay_simulacion and not penalidad_fp and not penalidad_mov and visitas_fm >= 85 and porcentaje_emt >= 80.0:
    score_global_final = 62.0
    puesto_calculado = 24
else:
    score_global_final = (
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.20) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (usd_simulada * 0.06) + 
        (esp_simulada * 0.05) + (tcfa_simulada * 0.04) + (esg_simulada * 0.01)
    ) - puntos_a_restar_global - penalidad_estandar_emt
    if penalidad_mov:
        score_global_final -= 1.1

    if score_global_final <= 62.0:
        puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
        puesto_calculado = min(43, max(24, puesto_calculado))
    elif score_global_final >= 99.9:
        puesto_calculado = 1
    elif score_global_final >= 72.3:
        puesto_calculado = max(1, min(5, int(5 - ((score_global_final - 72.3) / (100.0 - 72.3)) * (5 - 1))))
    else:
        puesto_calculado = max(5, min(24, int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))))

# DATAFRAME OPERATIVO
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

# RESET CRUZADO
if st.sidebar.button("🔄 Restablecer Valores Oficiales", key="btn_reset_lateral"):
    for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg", "db_plan_puro_v17", "db_ampliacion_v17"]: 
        if k in st.session_state: st.session_state[k] = None
    st.rerun()

# --- PESTAÑAS PRINCIPALES ---
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
    if sucursal == "Jujuy": st.info("🎯 **Foco Crítico en Jujuy**: El 60% de los desvíos se concentran en **Demoras y Puntualidad** junto a **Comunicación y Seguimiento**.")
    elif sucursal == "Salta": st.info("🎯 **Foco Crítico en Salta**: La debilidad principal radica en **Comunicación y Seguimiento** junto a **Administración de Documentos**.")
    elif sucursal == "Tartagal": st.info("🎯 **Foco Crítico en Tartagal**: Los reclamos están liderados por **Demoras y Puntualidad** y **Cortesías u Obsequios**.")

# ==========================================
# 4. PESTAÑA: PLAN DE ACCIÓN INTERACTIVO
# ==========================================
with tab_plan:
    st.subheader("📋 Matriz de Compromisos Kaizen (Evidencias de Auditoría)")
    st.info("💡 **Simulador Incremental**: Ingrese el % de avance proyectado en cada acción (0% = Estado Actual). Cada mejora cerrará la brecha hacia el 100% y sumará puntos al score global.")

    if "db_plan_puro_v17" not in st.session_state or st.session_state.db_plan_puro_v17
