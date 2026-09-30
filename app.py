import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Agosto 2026", layout="wide", page_icon="🚗")
st.title("🚗 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Datos Oficiales e Informe de Calidad de la Red TASA (Manual DEP 2026 - Corte Agosto / Publicación Septiembre)")

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
visitas_fm = st.sidebar.slider("% Compromisos Fieldman", 0, 100, 100)

puntos_a_restar_global = 10.0 if penalidad_fp else 0.0
castigo_posventa_fieldman = 40.0 if visitas_fm < 85 else 0.0

if visitas_fm < 85: 
    st.sidebar.error("❌ Penalidad Posventa Activa (-40% en Score del área).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman cumplidos al 100%.")

# 3. VALORES BASE OFICIALES AUTOLUX (CORTE AGOSTO OFICIAL)
b_ventas = 41.0 if not penalidad_mov else (41.0 - 5.0)
b_posventa = 96.0 - (96.0 * (castigo_posventa_fieldman / 100))
b_tpa = 87.0
b_kinto = 42.0
b_tcfa = 83.0
b_general = 72.0
b_especiales = 30.0
b_usados = 73.0
b_esg = 36.0

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

target_p10 = 74.74  # BHA / SENNA (Umbral Top 10)
target_p5 = 76.91   # SAK / PRANA (Umbral Top 5)

if not hay_simulacion and not penalidad_fp and not penalidad_mov and visitas_fm >= 85 and porcentaje_emt >= 80.0:
    score_global_final = 69.2
    puesto_calculado = 24
else:
    score_global_final = (
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.20) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (usd_simulada * 0.06) + 
        (esp_simulada * 0.05) + (tcfa_simulada * 0.04) + (esg_simulada * 0.01)
    ) - puntos_a_restar_global - penalidad_estandar_emt
    if penalidad_mov: score_global_final -= 1.1

    if score_global_final <= 69.2:
        puesto_calculado = int(24 + ((69.2 - score_global_final) / 5.0) * 10)
        puesto_calculado = min(44, max(24, puesto_calculado))
    elif score_global_final >= 99.9:
        puesto_calculado = 1
    elif score_global_final >= target_p5:
        puesto_calculado = max(1, min(5, int(5 - ((score_global_final - target_p5) / (100.0 - target_p5)) * (5 - 1))))
    elif score_global_final >= target_p10:
        puesto_calculado = max(6, min(10, int(10 - ((score_global_final - target_p10) / (target_p5 - target_p10)) * (10 - 6))))
    else:
        puesto_calculado = max(11, min(24, int(24 - ((score_global_final - 69.2) / (target_p10 - 69.2)) * (24 - 11))))

# BENCHMARK OFICIAL AGOSTO
data_operativa = {
    "Área": ["Posventa (27%)", "TPA (9%)", "TCFA (4%)", "Usados (6%)", "General (20%)", "KINTO (6%)", "Ventas (22%)", "ESG (1%)", "Ventas Esp. (5%)"],
    "Autolux (LUX)": [p_simulada, tpa_simulada, tcfa_simulada, usd_simulada, g_simulada, kinto_simulada, v_simulada, esg_simulada, esp_simulada],
    "Líder Red (P1/P5)": [98.0, 92.0, 95.0, 96.0, 85.0, 80.0, 88.0, 70.0, 85.0],
    "Umbral Top 10": [95.0, 85.0, 88.0, 85.0, 80.0, 65.0, 68.0, 50.0, 60.0],
    "Promedio RED": [88.5, 62.0, 64.0, 63.5, 68.0, 55.0, 58.0, 34.0, 52.0]
}
df_bench_op = pd.DataFrame(data_operativa)

data_ranking_global = {
    "Concesionario": ["Líder Red (Puesto 5)", "Top 10 (Puesto 10)", "Autolux (LUX) - Actual", "Promedio RED"],
    "Porcentaje DEP Global": [76.9, 74.7, score_global_final, 67.5]
}
df_bench_ranking = pd.DataFrame(data_ranking_global)

if st.sidebar.button("🔄 Restablecer Valores Oficiales", key="btn_reset_lateral"):
    for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg"]: 
        if k in st.session_state: st.session_state[k] = None
    st.rerun()

# DECLARACIÓN DE LAS PESTAÑAS
tab_dashboard, tab_evolucion, tab_regional, tab_calidad, tab_plan, tab_docs = st.tabs([
    "📊 Dashboard del Dealer", 
    "📈 Evolución y Paradoja Financiera",
    "🗺️ Desempeño Regional y por Área",
    "🕵️ Análisis de Calidad por Sucursal", 
    "📋 Plan de Acción Táctico y Sólido",
    "📚 Documentación y Fuentes"
])

# ==========================================
# 1. PESTAÑA: DASHBOARD DEL DEALER
# ==========================================
with tab_dashboard:
    pts_para_p10 = max(0.0, target_p10 - score_global_final)
    pts_para_p5 = max(0.0, target_p5 - score_global_final)

    col1, col2, col3 = st.columns(3)
    with col1: 
        st.metric("Cumplimiento DEP Score Global (Agosto)", f"{score_global_final:.1f}%", delta="+0.6% vs Julio (68.6%)")
    with col2: 
        if puesto_calculado < 24: 
            st.metric("Ranking Proyectado Red", f"Puesto {puesto_calculado} 🏆", delta=f"¡Subiendo {24 - puesto_calculado} puestos!")
        elif puesto_calculado > 24: 
            st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🚨", delta=f"Bajando {puesto_calculado - 24} puestos")
        else: 
            st.metric("Ranking General Red", "Puesto 24 🚗", delta="-3 puestos vs Julio (Efecto Competencia Red)", delta_color="inverse")
    with col3:
        if pts_para_p5 == 0: 
            st.metric("Puntos para Meta Superlativa", "¡En Puesto 5 o superior! 🎉")
        else: 
            st.metric(label="Puntos Faltantes para Top 10 / Top 5", value=f"+{pts_para_p10:.1f} pts (P10 - BHA)", delta=f"+{pts_para_p5:.1f} pts para P5 (SAK)", delta_color="inverse")

    st.subheader("🏁 Desempeño Operativo vs. Benchmarks Oficiales (Agosto 2026)")
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
            "Líder Red (P1/P5)": "#1F4E78", 
            "Umbral Top 10": "#5B9BD5", 
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
            "Autolux (LUX) - Actual": "#d62728", 
            "Líder Red (Puesto 5)": "#1F4E78", 
            "Top 10 (Puesto 10)": "#5B9BD5", 
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
# 2. PESTAÑA: EVOLUCIÓN Y PARADOJA FINANCIERA VS. DEP
# =======================================================
with tab_evolucion:
    st.header("⚖️ La Paradoja de Autolux: Solidez Económica vs. Evaluación DEP")
    st.caption("Contraste frontal entre el Reporte Financiero Oficial (Págs. 1 a 12) y el Reporte DEP (Págs. 13 a 25)")

    # Métricas de la paradoja
    c_f1, c_f2, c_f3, c_f4 = st.columns(4)
    with c_f1:
        st.metric("Margen Neto Final", "7,2%", delta="+0,7% vs Red (6,5%) 💰")
    with c_f2:
        st.metric("Absorción por Posventa", "185,8%", delta="+67,8% vs Red (118,0%) 🛡️")
    with c_f3:
        st.metric("Cumplimiento DEP Global", "69,2%", delta="-5,5 pts vs Top 10 (74,7%) ⚠️", delta_color="inverse")
    with c_f4:
        st.metric("Ranking Nacional Red", "Puesto 24", delta="Estancado a pesar de la rentabilidad", delta_color="inverse")

    st.markdown("---")

    col_paradox_txt, col_paradox_chart = st.columns([1, 1])

    with col_paradox_txt:
        st.subheader("💡 ¿Por qué Autolux es Puesto 24 si gana dinero y tiene una gran posventa?")
        st.markdown("""
        El programa **DEP no premia la rentabilidad ni el volumen de pesos**, sino el **desarrollo equilibrado de procesos, calidad y cumplimiento normativo**:

        1. **Blindaje Financiero Récord (Págs. 1 a 12):**
           * Si Autolux dejara de vender 0km por meses, **solo con repuestos y taller paga todos los costos fijos casi dos veces (185,8%)**, frente a una red que apenas cubre el 118%.
           * La venta de repuestos sola cubre el **41,9%** de los gastos de la empresa (vs. 20% promedio nacional).
           * La ganancia neta es superior a la media (7,2% vs 6,5%).

        2. **La Sangría en la Evaluación DEP (Págs. 13 a 25):**
           * Mientras **Posventa rinde al 96% (P9)** y **TPA al 87% (P7)**, dos áreas comerciales clave arrastran el promedio:
             * **Ventas Convencionales:** Cumplimiento de apenas **41%** (**Puesto 41** de 44 concesionarios).
             * **KINTO:** Cumplimiento del **42%** (**Puesto 41** nacional).
             * **Calidad Transversal (CFP):** Cumplimiento del **63%** (**Puesto 36** en la red).
        """)

    with col_paradox_chart:
        st.subheader("📊 Comparativo de Eficiencia: Finanzas vs. Evaluación DEP")
        df_paradox = pd.DataFrame({
            "Dimensión": [
                "Absorción Costos Fijos",
                "Margen Neto del Negocio",
                "Cumplimiento en Posventa",
                "Efectividad en TPA",
                "Satisfacción Cliente (CFP)",
                "Cumplimiento Ventas 0km",
                "Efectividad KINTO"
            ],
            "Autolux (LUX)": [185.8, 110.8, 96.0, 87.0, 63.0, 41.0, 42.0],
            "Benchmark Red (Base 100)": [100.0, 100.0, 88.5, 62.0, 75.0, 58.0, 55.0]
        })
        fig_paradox = go.Figure()
        fig_paradox.add_trace(go.Bar(
            y=df_paradox["Dimensión"], 
            x=df_paradox["Autolux (LUX)"], 
            name="Autolux (Rendimiento relativo)", 
            orientation="h", 
            marker_color=["#2ca02c", "#2ca02c", "#2ca02c", "#2ca02c", "#d62728", "#d62728", "#d62728"],
            text=[f"{v:.1f}%" for v in df_paradox["Autolux (LUX)"]],
            textposition="inside"
        ))
        fig_paradox.add_vline(x=100.0, line_dash="dash", line_color="#70AD47", annotation_text="Línea Media Red (100%)", annotation_position="top right")
        fig_paradox.update_layout(
            xaxis=dict(range=[0, 200], title="% de Efectividad Relativa"),
            yaxis=dict(autorange="reversed"),
            height=420,
            margin=dict(t=30, b=30, l=10, r=10)
        )
        st.plotly_chart(fig_paradox, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Radiografía Oficial de Fugas por Área (Corte Agosto)")

    cf_a1, cf_a2, cf_a3 = st.columns(3)
    with cf_a1:
        st.error("📉 **Ventas 0km: 41% (Puesto 41)**")
        st.markdown("""
        * **Targets de Volumen (6,0 pts perdidos):** Hilux/Hiace en 81,9% (0/3 pts) y Pasajeros en 68,6% (0/3 pts). Al no alcanzar el 100%, se computa 0.
        * **CRM y Leads (1.5.6):** **0 / 1,5 pts**. El equipo comercial tarda **5 horas** promedio en responder leads digitales (TASA exige <2 hs).
        * **Patentamientos (1.5.3):** 86,1% vs 90% exigido (se pierden **1,05 pts**).
        * **Voz del Cliente:** SSI en 94,7 (vs 95,6) y NPS en 83% (vs 87%), penalizados por quejas en **Fecha de Entrega (90,4 pts)** y baja tasa de encuestas (**19,8%**).
        """)

    with cf_a2:
        st.warning("🚗 **KINTO: 42% (Puesto 41)**")
        st.markdown("""
        * **KINTO Share:** Calidad excelente (NPS 98%), pero ocupación en 39% vs 46% meta y reservas en 374 vs 419.
        * **KINTO One:** Fuga casi total de puntos:
          * NPS corporativo en 64,3% vs 90% exigido.
          * Solo 1 contrato cerrado vs 6 target.
          * Entregas (5.5.4) y Siniestros (5.5.5) cobrando solo la mitad (0,15 pts c/u) por demoras administrativas en carga de **Anexo IV**.
        """)

    with cf_a3:
        st.info("⚙️ **Posventa y Usados: Luces y Sombras**")
        st.markdown("""
        * **Posventa (96% - P9):** Pilar estelar. CSI 95 pts, FIR 99%, Repuestos y Neumáticos sobrecumplidos.
          * **Única fuga:** Campañas Airbags (3.5.2) en 57,1% (0,35 de 1,40 pts).
        * **Usados (73% - P18):**
          * Ventas y Trade-In al 100% (4,40 pts).
          * **Calidad Usados en 0 / 1,60 pts:** El NPS cayó a 57,7% por quejas en instalaciones y limpieza deficiente en la entrega.
        """)

# =======================================================
# 3. PESTAÑA: DESEMPEÑO REGIONAL Y POR ÁREA (POWER BI)
# =======================================================
with tab_regional:
    st.subheader("🗺️ Diagnóstico Integral Oficial (Corte Acumulado Agosto 2026)")
    st.caption("Consolidado Oficial de Power BI: Áreas Operativas, Categorías Normativas y Benchmarking Regional")

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Score Global Autolux", "69,20 pts", "Puesto 24 de la Red")
    with m2: st.metric("Región NOA (Líder)", "72,15 pts", "Liderando el Benchmark")
    with m3: st.metric("Pilar Líder en Normas", "Programas (Puesto 1)", "100,0% Efectividad 🏆")
    with m4: st.metric("Gestión del Capital", "RRHH (Puesto 6)", "92,00% Efectividad 🌟")

    st.markdown("---")
    data_area_lux = {
        "Área": ["POSVENTA", "TPA", "TCFA", "USADOS", "GENERAL", "KINTO", "VENTAS", "ESG", "VENTAS ESPECIALES"],
        "Posición Red": [9, 7, 17, 18, 22, 41, 41, 7, 18],
        "Ptj. LUX": [25.95, 7.85, 3.32, 4.40, 11.90, 2.50, 9.00, 0.36, 1.50],
        "Ptj. Ideal": [27.00, 9.00, 4.00, 6.00, 16.50, 6.00, 22.00, 1.00, 5.00],
        "% Ideal LUX": [96.11, 87.22, 83.00, 73.33, 72.12, 41.67, 40.91, 36.00, 30.00]
    }
    df_area = pd.DataFrame(data_area_lux).sort_values(by="% Ideal LUX", ascending=False)

    data_cat_lux = {
        "Categoría": ["PROGRAMAS", "RRHH", "FACILITIES", "CALIDAD (CFP)", "TARGETS"],
        "Posición Red": [1, 6, 13, 36, 18],
        "Ptj. LUX": [8.80, 11.13, 6.15, 13.80, 26.80],
        "Ptj. Ideal": [8.80, 12.10, 7.50, 21.90, 46.20],
        "% Ideal LUX": [100.00, 92.00, 82.00, 63.01, 58.00]
    }
    df_cat = pd.DataFrame(data_cat_lux).sort_values(by="% Ideal LUX", ascending=False)

    data_regional = {
        "Región": ["NOA (Líder)", "Cuyo", "NEA", "Patagonia", "Centro", "Total RED"],
        "Ptj. Logrado": [72.15, 71.30, 68.90, 68.50, 66.40, 67.50],
        "% Ideal": [74.80, 73.90, 71.40, 71.00, 68.80, 70.00]
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
        fig_area.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
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
        fig_reg.add_hline(y=69.20, line_dash="dot", line_color="#d62728", annotation_text="Autolux: 69,2%", annotation_position="bottom right")
        fig_reg.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
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
# 5. PESTAÑA: PLAN DE ACCIÓN TÁCTICO Y SÓLIDO
# ==========================================
with tab_plan:
    st.header("🎯 Plan de Acción Operativo: De la Paradoja al Top 10")
    st.caption("Plan realista basado en las páginas 13 a 25. Sin metas ilusorias: ajuste al 70% en Airbags y foco en 5 palancas recuperables.")

    # 1. Tarjetas Métricas de Escenarios Reales (Sin Óptimo)
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1:
        st.metric(label="📊 Score Actual (Agosto)", value="69,20%", delta="Puesto 24 de la Red")
    with c_p2:
        st.metric(label="🟢 Escenario 1: Táctico Inmediato", value="72,85%", delta="+3,65 pts ➔ Puesto 15 (Freno a sangrías) 🛡️")
    with c_p3:
        st.metric(label="🌟 Escenario 2: Sólido Consolidado", value="75,05%", delta="+5,85 pts ➔ Puesto 9/10 (Top 10 Nacional) 🏆")

    st.markdown("---")

    # 2. Gráficos Comparativos y Cascada de Puntos
    col_gr1, col_gr2 = st.columns(2)
    
    with col_gr1:
        escenarios = ["Agosto Real (P24)", "Escenario 1: Táctico (P15)", "Escenario 2: Sólido (P9/10)", "Umbral Top 10 (BHA)", "Líder Red (SAK)"]
        valores_esc = [69.20, 72.85, 75.05, 74.74, 76.91]
        colores_esc = ["#d62728", "#f39c12", "#2ca02c", "#5B9BD5", "#1F4E78"]
        
        fig_esc = go.Figure()
        fig_esc.add_trace(go.Bar(
            x=escenarios, 
            y=valores_esc, 
            marker_color=colores_esc, 
            text=[f"{v:.2f}%" for v in valores_esc], 
            textposition="inside"
        ))
        fig_esc.add_hline(y=74.74, line_dash="dash", line_color="#5B9BD5", annotation_text="Piso Top 10 BHA (74,74%)", annotation_position="top left")
        fig_esc.update_layout(
            title="<b>Trayectoria Realista de Recuperación vs. Red</b>",
            yaxis=dict(title="Cumplimiento Global %", range=[65, 80]),
            margin=dict(t=50, b=40),
            height=400
        )
        st.plotly_chart(fig_esc, use_container_width=True)

    with col_gr2:
        palancas = [
            "Gestoría 1.5.3 (+1,05)", 
            "CRM Digital 1.5.6 (+1,50)", 
            "Airbags 70% 3.5.2 (+0,70)", 
            "Seguros TCFA 7.5.5 (+0,40)", 
            "Calidad Entregas (+2,20)", 
            "Ganancia Total Sólida"
        ]
        puntos_palanca = [1.05, 1.50, 0.70, 0.40, 2.20, 5.85]
        
        fig_aportes = go.Figure(go.Bar(
            x=palancas,
            y=puntos_palanca,
            marker_color=["#1F4E78", "#1F4E78", "#5B9BD5", "#5B9BD5", "#f39c12", "#27ae60"],
            text=[f"+{v:.2f} pts" for v in puntos_palanca],
            textposition="outside"
        ))
        fig_aportes.update_layout(
            title="<b>Puntos Netos Ganables por Palanca Crítica</b>",
            yaxis=dict(title="Puntos Directos DEP", range=[0, 7.0]),
            margin=dict(t=50, b=40),
            height=400
        )
        st.plotly_chart(fig_aportes, use_container_width=True)

    st.markdown("---")

    # 3. Explicación de los 2 Escenarios Reales
    st.subheader("💡 Definición Operativa de los Dos Escenarios Realistas")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.success("### 🟢 Escenario 1: Táctico Inmediato\n**Meta: +3,65 pts | Score: 72,85% (Puesto 15)**")
        st.markdown("""
        **Premisa:** Detener fugas administrativas y de proceso sin depender de obras edilicias ni contratos corporativos complejos.

        * **Gestoría y Patentamientos (1.5.3 - +1,05 pts):** Liquidar carpetas registrales retenidas para llevar el ratio de patentamientos del 86,1% a $\ge 90\%$.
        * **CRM y Tiempos de Respuesta (1.5.6 - +1,50 pts):** Guardias comerciales activas para responder leads digitales en menos de 2 horas (actualmente tardan 5 horas).
        * **Seguros TCFA (7.5.5 - +0,40 pts):** Detener cancelaciones de seguros y asegurar retención de cartera para pasar de -3,38% a $>0\%$.
        * **Airbags Taller al 70% (3.5.2 - +0,70 pts):** Con el compromiso formal de Posventa de pasar de 209 a 257 infladores atendidos (+48 unidades), se salta del 25% al 75% del puntaje asignado.

        **Impacto:** Autolux sale de la zona baja, supera a 9 concesionarios y se instala en el **Puesto 15**.
        """)

    with col_e2:
        st.info("### 🌟 Escenario 2: Sólido Consolidado\n**Meta: +5,85 pts | Score: 75,05% (Puesto 9/10 - Top 10)**")
        st.markdown("""
        **Premisa:** Sumar al Escenario Táctico la regularización de la Voz del Cliente y desvíos documentales de KINTO y TPA.

        * **Todo el Escenario Táctico cumplido (+3,65 pts).**
        * **Calidad en Ventas 0km (1.1.1 y 1.1.3 - +1,60 pts):**
          * Aumentar la tasa de respuesta de encuestas del **19,8% a $\ge 27,8\%$** (llamado previo de cortesía).
          * Mejorar el compromiso en **Fecha de Entrega** (hoy calificada con 90,4 pts) para cerrar la brecha con la red.
        * **Regularización KINTO One (5.5.4 y 5.5.5 - +0,30 pts):**
          * Cargar los **Anexos IV** en plataforma dentro de los 5 días hábiles post-entrega para destrabar los 0,30 pts plenos.
        * **Contención en TPA (4.1.2 - +0,30 pts):**
          * Elevar el NPS de suscriptores/entregados de 79,8% a 85%.

        **Impacto:** Autolux rompe la barrera del 74,74% de BHA/SENNA y **se consagra en el Top 10 Nacional de Toyota**.
        """)

    st.markdown("---")

    # 4. Matriz Táctica de Ejecución por Responsable
    st.subheader("📋 Matriz Táctica de Ejecución: Responsables y Compromisos Innegociables")
    
    df_matriz_ejecucion = pd.DataFrame({
        "Área": ["Ventas", "Ventas", "Posventa", "TCFA", "Ventas / Calidad", "KINTO", "TPA"],
        "Código": ["1.5.3", "1.5.6", "3.5.2", "7.5.5", "1.1.1 & 1.1.3", "5.5.4 / 5.5.5", "4.1.2"],
        "Indicador Oficial TASA": [
            "Patentamientos vs. Retail Declarado", 
            "Gestión Digital y Adopción CRM", 
            "Campañas Airbags Takata (ABI 414/415)", 
            "Crecimiento Cartera de Seguros", 
            "Satisfacción SSI y NPS Salón 0km", 
            "Preparación, Entrega y Siniestros One", 
            "NPS Transaccional Suscriptor/Entregado"
        ],
        "Agosto Real": [
            "1,05 / 2,10 pts (86,1%)", 
            "0,00 / 1,50 pts (5 hs rta)", 
            "0,35 / 1,40 pts (57,1%)", 
            "0,00 / 0,40 pts (-3,38%)", 
            "1,73 / 5,70 pts (19,8% rtas)", 
            "0,30 / 0,60 pts (Alerta)", 
            "0,40 / 0,80 pts (79,8%)"
        ],
        "Meta Realista": [
            "2,10 pts (+1,05)", 
            "1,50 pts (+1,50)", 
            "1,05 pts (+0,70)", 
            "0,40 pts (+0,40)", 
            "3,93 pts (+2,20)", 
            "0,60 pts (+0,30)", 
            "0,70 pts (+0,30)"
        ],
        "Ganancia": [
            "+1,05 pts", 
            "+1,50 pts", 
            "+0,70 pts", 
            "+0,40 pts", 
            "+2,20 pts", 
            "+0,30 pts", 
            "+0,30 pts"
        ],
        "Responsable Directo": [
            "Gestoría / Adm. Ventas", 
            "Jefe Comercial / Vendedores", 
            "Daniel Colque (Posventa)", 
            "Juan Vázquez (TCFA)", 
            "Jefatura de Calidad / Salón", 
            "Aaron Martearena (KINTO)", 
            "Gerencia TPA"
        ],
        "Acción Crítica Innegociable": [
            "Monitorear diariamente carpetas para que ningún auto quede sin patente al 2º día hábil de N+1 (alcanzar >=90%).",
            "Guardia digital rotativa obligatoria: lead entrante debe responderse en menos de 120 minutos sin excepción.",
            "Llamados proactivos para completar 48 infladores y alcanzar el escalón realista del 70% acordado.",
            "Retención preventiva de pólizas a renovar y seguro obligatorio cotizado antes de entregar cada 0km/Usado.",
            "Comprometer fechas de entrega verídicas (no prometer plazos falsos) y seguimiento telefónico para que completen la encuesta TASA.",
            "Cargar Anexo IV en plataforma dentro de los 5 días hábiles post-entrega física para certificar en sistema.",
            "Seguimiento estrecho en el acto de adjudicación y entrega para evitar caídas tempranas y detractores."
        ]
    })
    
    st.dataframe(df_matriz_ejecucion, use_container_width=True, hide_index=True)

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
        st.success("📊 **Planilla Acumulada Oficial Agosto 2026**\n\nResultados oficiales de la Red comercial (Acumulado Agosto).")
        try:
            with open("15549_DES020-26 -DEP ACUM. AGO.xlsx", "rb") as excel_file:
                st.download_button(
                    label="📥 Descargar Planilla Agosto 2026 (Excel)",
                    data=excel_file,
                    file_name="15549_DES020-26 -DEP ACUM. AGO.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.warning("⚠️ 'Planilla Agosto 2026' no encontrada en el directorio local.")

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
