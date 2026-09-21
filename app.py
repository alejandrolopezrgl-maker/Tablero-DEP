import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# BENCHMARK OFICIAL JULIO
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
    for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg"]: 
        if k in st.session_state: st.session_state[k] = None
    st.rerun()

# DECLARACIÓN DE LAS PESTAÑAS
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

    st.markdown("---")
    st.subheader("🔍 Auditoría Quirúrgica de Indicadores Clave (Desvíos y Tolerancias)")

    col_an1, col_an2 = st.columns(2)
    with col_an1:
        st.error("📉 **TCFA - Indicador 7.5.5: Crecimiento Cartera de Seguros**")
        st.markdown("""
        * **Resultado Auditado en Julio:** **-3,65%** (Meta: > 0%).
        * **Impacto en Puntaje:** **0,00 de 0,40 pts posibles** (Calificación X).
        * **Origen del Cálculo:** Toyota Financiera evalúa mensualmente el balance neto de pólizas activas:
        $$\\frac{\\text{Pólizas Nuevas Altas} - \\text{Pólizas Bajas / Cancelaciones}}{\\text{Meta de Crecimiento del Mes}}$$
        * **Diagnóstico Operativo:** El saldo negativo significa que se perdieron o cancelaron más seguros de los que se lograron suscribir. Para revertirlo se requiere retener renovaciones automáticas y asegurar que ningún 0km/Usado salga del salón sin póliza activa.
        """)

    with col_an2:
        st.info("⚙️ **Posventa - Indicador 3.5.1: CPUS en Taller (Realidad vs Planilla)**")
        st.markdown("""
        * **Meta Oficial Acumulada:** **15.740 unidades**.
        * **Volumen Atendido:** **15.603 unidades** (Faltante real de **137 vehículos** / **99,13%**).
        * **Por qué figura 1,70 / 1,70 pts:** El manual aplica una banda de tolerancia escalonada (al alcanzar $\\ge$ 98% otorga el puntaje completo en esa celda específica).
        * **¿De dónde provino entonces la mejora real de Posventa (+0,9%)?:**
          * **Accesorios (3.5.3):** Sobrecumplimiento de \$817 M vs \$654 M (+124%).
          * **Neumáticos (3.5.4):** 1.838 unidades vendidas vs meta de 1.504 (+122%).
          * **Calidad y FIR:** CSI de taller en 94,67 pts y Fix It Right en 99,0%.
          * **Programas TSM-FIR (3.2.1):** Certificación perfecta al 100%.
        """)

# =======================================================
# 3. PESTAÑA: DESEMPEÑO REGIONAL Y POR ÁREA (POWER BI)
# =======================================================
with tab_regional:
    st.subheader("🗺️ Diagnóstico Integral Oficial (Corte Acumulado Julio 2026)")
    st.caption("Consolidado Oficial de Power BI: Áreas Operativas, Categorías Normativas y Benchmarking Regional")

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Score Global Autolux", "68,56 pts", "71,05% del Ideal (P21)")
    with m2: st.metric("Región NOA (Líder)", "71,96 pts", "74,57% del Ideal")
    with m3: st.metric("Pilar Líder en Calidad", "Programas (Puesto 1)", "100,0% Efectividad 🏆")
    with m4: st.metric("Gestión del Capital", "RRHH (Puesto 6)", "91,89% Efectividad 🌟")

    st.markdown("---")
    data_area_lux = {
        "Área": ["POSVENTA", "TPA", "TCFA", "USADOS", "GENERAL", "KINTO", "VENTAS", "ESG", "VENTAS ESPECIALES"],
        "Posición Red": [9, 5, 16, 16, 20, 37, 41, 7, 20],
        "Ptj. LUX": [25.95, 7.87, 3.32, 4.40, 11.92, 2.50, 8.35, 0.36, 1.50],
        "Ptj. Ideal": [27.00, 9.00, 4.00, 6.00, 16.50, 6.00, 22.00, 1.00, 5.00],
        "% Ideal LUX": [96.11, 87.42, 83.00, 73.33, 72.26, 41.67, 37.95, 35.50, 30.00]
    }
    df_area = pd.DataFrame(data_area_lux).sort_values(by="% Ideal LUX", ascending=False)

    data_cat_lux = {
        "Categoría": ["PROGRAMAS", "RRHH", "FACILITIES", "TARGETS", "CALIDAD"],
        "Posición Red": [1, 6, 13, 12, 38],
        "Ptj. LUX": [8.80, 11.12, 6.15, 27.90, 12.20],
        "Ptj. Ideal": [8.80, 12.10, 7.50, 46.20, 21.90],
        "% Ideal LUX": [100.00, 91.89, 82.00, 60.38, 55.71]
    }
    df_cat = pd.DataFrame(data_cat_lux).sort_values(by="% Ideal LUX", ascending=False)

    data_regional = {
        "Región": ["NOA (Líder)", "Cuyo", "NEA", "Patagonia", "Centro", "Total RED"],
        "Ptj. Logrado": [71.96, 71.03, 68.57, 68.34, 66.17, 67.50],
        "% Ideal": [74.57, 73.60, 71.05, 70.82, 68.57, 69.95]
    }
    df_reg = pd.DataFrame(data_regional)

    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.subheader("📊 Cumplimiento por Unidades de Negocio (% Ideal)")
        fig_area = px.bar(
            df_area, 
            x="% Ideal LUX", 
            y="Área", 
            orientation="h",
            text="% Ideal LUX", 
            color="% Ideal LUX",
            color_continuous_scale=["#d62728", "#f39c12", "#27ae60"]
        )
        fig_area.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_area.update_layout(xaxis=dict(range=[0, 115]), yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_area, use_container_width=True)

    with c_g2:
        st.subheader("🏆 Comparativa de Rendimiento Regional (% Ideal)")
        fig_reg = px.bar(
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
                "Total RED": "#70AD47"
            }
        )
        fig_reg.add_hline(y=71.05, line_dash="dot", line_color="#d62728", annotation_text="Autolux: 71,05%", annotation_position="bottom right")
        fig_reg.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
        fig_reg.update_layout(showlegend=False, yaxis=dict(range=[0, 85]))
        st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Tablas Consolidadas Oficiales (Power BI TASA)")
    col_t1, col_t2, col_t3 = st.columns(3)

    with col_t1:
        st.markdown("**1. Logro por Área**")
        df_mostrar_area = df_area.copy()
        df_mostrar_area["% Ideal LUX"] = df_mostrar_area["% Ideal LUX"].map("{:.2f}%".format)
        df_mostrar_area["Ptj. LUX"] = df_mostrar_area["Ptj. LUX"].map("{:.2f}".format)
        df_mostrar_area["Ptj. Ideal"] = df_mostrar_area["Ptj. Ideal"].map("{:.2f}".format)
        st.dataframe(df_mostrar_area, use_container_width=True, hide_index=True)

    with col_t2:
        st.markdown("**2. Logro por Categoría**")
        df_mostrar_cat = df_cat.copy()
        df_mostrar_cat["% Ideal LUX"] = df_mostrar_cat["% Ideal LUX"].map("{:.2f}%".format)
        df_mostrar_cat["Ptj. LUX"] = df_mostrar_cat["Ptj. LUX"].map("{:.2f}".format)
        df_mostrar_cat["Ptj. Ideal"] = df_mostrar_cat["Ptj. Ideal"].map("{:.2f}".format)
        st.dataframe(df_mostrar_cat, use_container_width=True, hide_index=True)

    with col_t3:
        st.markdown("**3. Logro por Región**")
        df_mostrar_reg = df_reg.copy()
        df_mostrar_reg["% Ideal"] = df_mostrar_reg["% Ideal"].map("{:.2f}%".format)
        df_mostrar_reg["Ptj. Logrado"] = df_mostrar_reg["Ptj. Logrado"].map("{:.2f}".format)
        st.dataframe(df_mostrar_reg, use_container_width=True, hide_index=True)

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
# 5. PESTAÑA: PLAN DE ACCIÓN INTERACTIVO (REESTRUCTURADO)
# ==========================================
with tab_plan:
    st.header("🎯 Plan Estratégico y Proyección de Cierre de Agosto")
    st.caption("Foco exclusivo en Posventa (PV), TCFA y KINTO: tres palancas con alto retorno en puntos y bajo esfuerzo de inversión.")

    # 1. Tarjetas Métricas de Escenarios
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        st.metric(label="📊 Score Actual (Julio)", value="68,56%", delta="66,16 pts (Puesto 21)")
    with c_p2:
        st.metric(label="🟢 Escenario 1: Táctico", value="70,59%", delta="+1,95 pts ➔ Puesto 17 🏆")
    with c_p3:
        st.metric(label="🟡 Escenario 2: Sólido", value="71,93%", delta="+3,25 pts ➔ Puesto 14 🌟")
    with c_p4:
        st.metric(label="🚀 Escenario 3: Óptimo", value="72,95%", delta="+4,23 pts ➔ Puesto 12 🏎️")

    st.markdown("---")

    # 2. Gráficos Comparativos y Cascada de Puntos
    col_gr1, col_gr2 = st.columns(2)
    
    with col_gr1:
        escenarios = ["Julio Real (P21)", "Escenario 1 Táctico (P17)", "Escenario 2 Sólido (P14)", "Escenario 3 Óptimo (P12)", "SENNA (P10 - Top 10)", "PRANA (P5 - Top 5)"]
        valores_esc = [68.56, 70.59, 71.93, 72.95, 74.74, 76.91]
        colores_esc = ["#d62728", "#2ca02c", "#1f77b4", "#ff7f0e", "#5B9BD5", "#1F4E78"]
        
        fig_esc = go.Figure()
        fig_esc.add_trace(go.Bar(
            x=escenarios, 
            y=valores_esc, 
            marker_color=colores_esc, 
            text=[f"{v:.2f}%" for v in valores_esc], 
            textposition="inside"
        ))
        fig_esc.add_hline(y=74.74, line_dash="dash", line_color="#5B9BD5", annotation_text="Umbral Top 10 SENNA (74,74%)", annotation_position="top left")
        fig_esc.update_layout(
            title="<b>Evolución del Score Consolidado DEP vs. Benchmarks</b>",
            yaxis=dict(title="Cumplimiento Global %", range=[60, 82]),
            margin=dict(t=60, b=40),
            height=430
        )
        st.plotly_chart(fig_esc, use_container_width=True)

    with col_gr2:
        pilares_aporte = ["Posventa (+1,05 pts)", "TCFA (+0,68 pts)", "KINTO (+2,50 pts)", "Ganancia Total Potencial"]
        puntos_aporte = [1.05, 0.68, 2.50, 4.23]
        
        fig_aportes = go.Figure(go.Bar(
            x=pilares_aporte,
            y=puntos_aporte,
            marker_color=["#1F4E78", "#5B9BD5", "#f39c12", "#27ae60"],
            text=[f"+{v:.2f} pts" for v in puntos_aporte],
            textposition="outside"
        ))
        fig_aportes.update_layout(
            title="<b>Puntos Netos a Sumar en Agosto por Departamento</b>",
            yaxis=dict(title="Puntos Directos Ganables", range=[0, 5.0]),
            margin=dict(t=60, b=40),
            height=430
        )
        st.plotly_chart(fig_aportes, use_container_width=True)

    st.markdown("---")

    # 3. Explicación Detallada de los 3 Escenarios de Proyección
    st.subheader("💡 Explicación Estratégica de los 3 Escenarios de Proyección")

    exp_col1, exp_col2, exp_col3 = st.columns(3)

    with exp_col1:
        st.success("### 🟢 Escenario 1: Táctico\n**Meta: +1,95 pts | Score: 70,59% (Puesto 17)**")
        st.markdown("""
        **Premisa:** Resolver los desvíos inmediatos y frenar fugas de puntos sin requerir nuevos contratos complejos.
        
        * **Posventa (+0,70 pts):** En Campañas Airbags (3.5.2) se sube del piso actual (0,35 pts) al escalón intermedio del 70-89% completando llamados pendientes. CPUS se preserva dentro de la tolerancia ($\ge$ 98%).
        * **TCFA (+0,40 pts):** Neutralizar cancelaciones de seguros para que el Crecimiento de Cartera (7.5.5) pase de -3,65% a $>0\%$, recuperando los 0,40 pts íntegros.
        * **KINTO (+0,85 pts):** Kinto Share alcanza el 100% de ocupación y bookings (+0,70 pts) usando autos para sustitución de taller. Se regulariza la gestión de siniestros (+0,15 pts).
        
        **Impacto:** Autolux escala 4 puestos en la red general, superando a Boston, Haimovich, De la Sobera y Zento.
        """)

    with exp_col2:
        st.info("### 🟡 Escenario 2: Sólido\n**Meta: +3,25 pts | Score: 71,93% (Puesto 14)**")
        st.markdown("""
        **Premisa:** Cumplimiento consistente de las metas mensuales regulares en las tres áreas clave.
        
        * **Posventa (+1,05 pts):** Airbags alcanza el 100% del target mensual (1,40 / 1,40 pts). Posventa queda a décimas del puntaje ideal absoluto (27 pts).
        * **TCFA (+0,60 pts):** Cartera en positivo (+0,40 pts) + aceleración en la liquidación de prendas Hilux/Corolla Cross (+0,12 pts) + penetración en seguros 0km (+0,08 pts).
        * **KINTO (+1,60 pts):** Share al 100% (+0,70 pts) + alistamiento y siniestros al día (+0,30 pts) + 1ra encuesta NPS de Kinto One positiva auditada (+0,60 pts).
        
        **Impacto:** Se escalan 7 posiciones en la red nacional, sobrepasando a Luppieri, Kansai, Anzorena y Ricardo Pichetti.
        """)

    with exp_col3:
        st.warning("### 🚀 Escenario 3: Óptimo\n**Meta: +4,23 pts | Score: 72,95% (Puesto 12)**")
        st.markdown("""
        **Premisa:** Desempeño perfecto en Posventa y TCFA sumado al despegue comercial corporativo de Kinto ONE.
        
        * **Posventa (+1,05 pts):** Certificación plena 27,00/27,00 pts en el área.
        * **TCFA (+0,68 pts):** Puntaje perfecto 4,00/4,00 pts (se capturan las 5 metas).
        * **KINTO (+2,50 pts):** Share perfecto (+0,70 pts) + alistamiento y siniestros (+0,30 pts) + NPS One (+0,60 pts) + cierre de los primeros contratos corporativos Kinto One (+0,90 pts).
        
        **Impacto:** Autolux se sitúa en el Puesto 12 y reduce la brecha con SENNA (Puesto 10: 74,74%) a sólo 1,79 puntos, dejando el Top 10 al alcance para el siguiente corte.
        """)

    st.markdown("---")

    # 4. Matriz Táctica de Ejecución por Responsable (con Juan Vazquez en TCFA)
    st.subheader("📋 Matriz Táctica de Ejecución Agosto (¿Cómo se gana cada punto?)")
    
    df_proy_detalle = pd.DataFrame({
        "Área": ["Posventa", "Posventa", "TCFA", "TCFA", "TCFA", "KINTO", "KINTO", "KINTO", "KINTO"],
        "Código": ["3.5.2", "3.5.1", "7.5.5", "7.5.1", "7.5.2 / 7.5.4", "5.5.1 / 5.5.3", "5.5.4 / 5.5.5", "5.1.3", "5.5.6"],
        "Indicador TASA": [
            "Campañas de Seguridad Airbags (ABI 414/415)", 
            "CPUS (Mantenimiento de Volumen)", 
            "Crecimiento Cartera de Seguros", 
            "Financiación Prendaria ($ Liquidados)", 
            "Seguros 0km y Fidelidad Prendaria", 
            "Ocupación y Bookings Kinto Share", 
            "Alistamiento y Gestión Siniestros One", 
            "NPS Kinto One (Encuestas de Clientes)", 
            "PN Corporativo Bookings Kinto One"
        ],
        "Julio Real": ["0,35 / 1,40 pts", "1,70 / 1,70 pts", "0,00 / 0,40 pts", "1,56 / 1,68 pts", "1,20 / 1,36 pts", "0,70 / 1,40 pts", "0,30 / 0,60 pts", "0,00 / 0,60 pts", "0,00 / 1,20 pts"],
        "Objetivo Agosto": ["1,40 pts (+1,05)", "1,70 pts (Sostener)", "0,40 pts (+0,40)", "1,68 pts (+0,12)", "1,36 pts (+0,16)", "1,40 pts (+0,70)", "0,60 pts (+0,30)", "0,60 pts (+0,60)", "0,80 pts (+0,80)"],
        "Ganancia Pts": ["+1,05 pts", "0,00 pts", "+0,40 pts", "+0,12 pts", "+0,16 pts", "+0,70 pts", "+0,30 pts", "+0,60 pts", "+0,80 pts"],
        "Responsable": ["Daniel Colque", "Daniel Colque", "Juan Vazquez", "Juan Vazquez", "Juan Vazquez", "Aaron Martearena", "Aaron Martearena", "Aaron Martearena", "Aaron / Alfredo A."],
        "Acción Crítica Innegociable": [
            "Llamados proactivos masivos a clientes con infladores pendientes ABI 414/415.",
            "Mantener turnos al día para no caer del umbral de tolerancia del 98%.",
            "Retención preventiva de pólizas por vencer y emisión obligatoria antes del retiro 0km.",
            "Acelerar liquidación prendaria de boletos cerrados en Hilux y Corolla Cross.",
            "Vincular seguro TCFA en cada prenda cerrada en el salón comercial.",
            "Poner flota ociosa de Share en reemplazo de taller y convenios corporativos.",
            "Ajustar tiempos de taller a <10 días en fast track y <25 días en parciales.",
            "Confirmar telefónicamente con administradores de flota la respuesta a la encuesta TASA.",
            "Cerrar al menos 2 suscripciones Kinto One con empresas mineras/flotas de la región."
        ]
    })
    
    st.dataframe(df_proy_detalle, use_container_width=True, hide_index=True)

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
