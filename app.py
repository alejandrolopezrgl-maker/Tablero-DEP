import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

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
        if k in st.session_state: st.session_state[k] = 0.0
    st.rerun()

# --- DECLARACIÓN DE LAS PESTAÑAS (SIN DESEMPEÑO REGIONAL) ---
tab_dashboard, tab_evolucion, tab_calidad, tab_plan, tab_docs = st.tabs([
    "📊 Dashboard del Dealer", 
    "📈 Evolución Junio vs. Julio",
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

# ==========================================
# 3. PESTAÑA: ANÁLISIS DE CALIDAD
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
# 4. PESTAÑA: PLAN DE ACCIÓN INTERACTIVO
# ==========================================
with tab_plan:
    st.header("🎯 Proyección Estratégica Cierre Agosto: Avance en el Resultado Consolidado")
    st.markdown("""
    Esta proyección se basa en las brechas oficiales de **Julio 2026** (66,16 pts / 68,56% / Puesto 21)[cite: 2], 
    integrando las 5 palancas operativas directas de corte mensual: **Posventa, TCFA, KINTO, Servicios Conectados y Cuotas TPA**[cite: 2].
    Se excluyen métricas bloqueadas por arrastre histórico anual (CRM y encuestas UCT)[cite: 4].
    """)

    # 1. Métricas de Impacto Global
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        st.metric(label="📊 Score Actual (Julio)", value="68,56%", delta="66,16 pts (Puesto 21)")
    with c_p2:
        st.metric(label="🟢 Escenario 1: Táctico", value="71,12%", delta="+2,47 pts ➔ Puesto 16 🏆")
    with c_p3:
        st.metric(label="🟡 Escenario 2: Sólido", value="72,65%", delta="+3,94 pts ➔ Puesto 12 🌟")
    with c_p4:
        st.metric(label="🚀 Escenario 3: Óptimo", value="73,35%", delta="+4,62 pts ➔ Puesto 12 🏎️")

    st.markdown("---")

    # 2. Explicación Detallada de los 3 Escenarios (CON LOS 5 PILARES)
    st.subheader("🔍 Desglose Explicativo de los 3 Posibles Escenarios (5 Palancas Clave)")
    
    col_esc1, col_esc2, col_esc3 = st.columns(3)
    
    with col_esc1:
        st.success("### 🟢 Escenario 1: Táctico\n**Meta: +2,47 pts ➔ 68,63 pts (71,12% - P16)**")
        st.markdown("""
        **¿Cómo se construyó?:**
        * **Posventa (+0,70 pts):** Campañas Airbags (3.5.2)[cite: 2] pasa de 0,35 a 1,05 pts (subiendo al escalón 70%-89%).
        * **TCFA (+0,40 pts):** Cartera de Seguros (7.5.5)[cite: 2] revierte la fuga (-3,65%) pasando a saldo neto positivo (>0%).
        * **KINTO (+0,70 pts):** Ocupación y Bookings de Kinto Share suben al 100% (+0,70 pts)[cite: 2].
        * **Servicios Conectados (+0,51 pts):** Pasa de la franja 70-79% al escalón **80%-90% de Onboarding** (de 0,85 a 1,36 pts)[cite: 2, 5].
        * **TPA Cuotas Emitidas (+0,16 pts):** Sube de la franja 6-9,99% al escalón **10%-13,99% de crecimiento** vs Dic'25 (de 0,96 a 1,12 pts)[cite: 2, 6].
        
        **Impacto en Ranking Red:**
        Supera de forma inmediata a **BOS (P17), HOM (P18), DEC (P19), ZEN (P20) y LUP (P16)**[cite: 2], posicionando a Autolux en el **Puesto 16**.
        """)

    with col_esc2:
        st.info("### 🟡 Escenario 2: Sólido\n**Meta: +3,94 pts ➔ 70,10 pts (72,65% - P12)**")
        st.markdown("""
        **¿Cómo se construyó?:**
        * **Posventa (+1,05 pts):** Campañas Airbags alcanza el 100% de la meta mensual (1,40 / 1,40 pts)[cite: 2].
        * **TCFA (+0,60 pts):** Cartera positiva (+0,40 pts)[cite: 2] + volumen prendario (+0,12 pts)[cite: 2] + seguros 0km (+0,08 pts)[cite: 2].
        * **KINTO (+1,00 pts):** Share pleno (+0,70 pts)[cite: 2] + regularización de Siniestros y Alistamiento One (+0,30 pts)[cite: 2].
        * **Servicios Conectados (+0,85 pts):** Protocolo estricto en entregas: alcanza **≥90% de Full Onboarding** (100% de puntos: 1,70 / 1,70 pts)[cite: 2, 5].
        * **TPA Cuotas Emitidas (+0,44 pts):** Recaudación de cobranzas alcanza **≥14% de crecimiento** vs Dic'25 (100% de puntos: 1,40 / 1,40 pts)[cite: 2, 6].
        
        **Impacto en Ranking Red:**
        Autolux entra al **Top 12 nacional**, superando a competidores históricos como **KAI (P15), ANZ (P14), HAI (P13) y RIC (P12)**[cite: 2].
        """)

    with col_esc3:
        st.warning("### 🚀 Escenario 3: Óptimo\n**Meta: +4,62 pts ➔ 70,78 pts (73,35% - P12)**")
        st.markdown("""
        **¿Cómo se construyó?:**
        * **Posventa pleno (+1,05 pts):** Score perfecto de 27,00 sobre 27,00 en el área de mayor peso del concesionario[cite: 2].
        * **TCFA pleno (+0,68 pts):** 4,00 sobre 4,00 puntos con liquidaciones prendarias y seguros al 100%[cite: 2].
        * **KINTO (+1,60 pts):** Share pleno (+0,70 pts)[cite: 2] + Siniestros One (+0,30 pts)[cite: 2] + primer lote de encuestas NPS Kinto One positivas (+0,60 pts)[cite: 2].
        * **Servicios Conectados pleno (+0,85 pts):** Activación total de la App My Toyota en entregas (1,70 / 1,70 pts)[cite: 2, 5].
        * **TPA Cuotas Emitidas pleno (+0,44 pts):** Crecimiento de emisión consolidado en el escalón máximo (1,40 / 1,40 pts)[cite: 2, 6].
        
        **Impacto en Ranking Red:**
        Consolida el **Puesto 12**, recortando la brecha con **DPQ (Puesto 11: 73,56%)** a solo 0,21 puntos y quedando a tiro del **Top 10 de SENNA (74,74%)**[cite: 2].
        """)

    st.markdown("---")

    # 3. Gráficos Comparativos y Cascada de Puntos
    col_gr1, col_gr2 = st.columns(2)
    
    with col_gr1:
        escenarios = ["Julio Real (P21)", "Escenario 1 (P16)", "Escenario 2 (P12)", "Escenario 3 (P12)", "SENNA (P10 - Top 10)", "PRANA (P5 - Top 5)"]
        valores_esc = [68.56, 71.12, 72.65, 73.35, 74.74, 76.91]
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
        pilares_aporte = ["Posventa (+1,05)", "TCFA (+0,68)", "KINTO (+1,60)", "Serv. Conect. (+0,85)", "TPA Cuotas (+0,44)", "Ganancia Total"]
        puntos_aporte = [1.05, 0.68, 1.60, 0.85, 0.44, 4.62]
        
        fig_aportes = go.Figure(go.Bar(
            x=pilares_aporte,
            y=puntos_aporte,
            marker_color=["#1F4E78", "#5B9BD5", "#f39c12", "#00A86B", "#9B59B6", "#27ae60"],
            text=[f"+{v:.2f}" for v in puntos_aporte],
            textposition="outside"
        ))
        fig_aportes.update_layout(
            title="<b>Aporte de Puntos por Indicador (Escenario Óptimo)</b>",
            yaxis=dict(title="Puntos Directos Ganables", range=[0, 5.5]),
            margin=dict(t=60, b=40),
            height=430
        )
        st.plotly_chart(fig_aportes, use_container_width=True)

    # 4. Matriz Táctica de Ejecución Agosto
    st.subheader("📋 Matriz Táctica de Ejecución Agosto (Responsables y Palancas Clave)")
    
    df_proy_detalle = pd.DataFrame({
        "Área": ["Posventa", "Posventa", "TCFA", "TCFA", "TCFA", "KINTO", "KINTO", "KINTO", "General", "TPA"],
        "Código": ["3.5.2", "3.5.1", "7.5.5", "7.5.1", "7.5.2 / 7.5.4", "5.5.1 / 5.5.3", "5.5.4 / 5.5.5", "5.1.3 / 5.5.6", "9.5.3", "4.5.4"],
        "Indicador TASA": [
            "Campañas de Seguridad Airbags (ABI 414/415)", 
            "CPUS (Mantenimiento de Volumen)", 
            "Crecimiento Cartera de Seguros", 
            "Financiación Prendaria ($ Liquidados)", 
            "Seguros 0km y Fidelidad Prendaria", 
            "Ocupación y Bookings Kinto Share", 
            "Alistamiento y Gestión Siniestros One", 
            "NPS y Bookings Corporativos Kinto One", 
            "Servicios Conectados (Full Onboarding App)", 
            "Cuotas Emitidas TPA (Crecimiento vs Dic'25)"
        ],
        "Julio Real": ["0,35 / 1,40 pts", "1,70 / 1,70 pts", "0,00 / 0,40 pts", "1,56 / 1,68 pts", "1,20 / 1,36 pts", "0,70 / 1,40 pts", "0,30 / 0,60 pts", "0,00 / 1,80 pts", "0,85 / 1,70 pts", "0,96 / 1,40 pts"],
        "Escala / Criterio Oficial": [
            "Escalones: ≥90% (1,40 pts) | 70-89% (1,05 pts) | 50-69% (0,70 pts)",
            "Tolerancia: ≥98% otorga 100% de puntos (1,70 pts)",
            "Saldo neto mensual: Variación > 0% otorga 100% de puntos (0,40 pts)",
            "M$ Liquidados sobre meta mensual asignada por TCFA",
            "Penetración sobre ventas convencionales y prendas cerradas",
            "Ocupación ≥70% y cumplimiento de bookings del mes",
            "Fast track <10 días y regularización de siniestros pendientes",
            "Encuestas NPS promotoras y contratos corporativos vigentes",
            "Escalones: ≥90% (100% pts) | 80-89% (80% pts) | 70-79% (50% pts)",
            "Escalones vs Dic'25: ≥14% (100% pts) | 10-13,99% (80% pts) | 6-9,99% (70% pts)"
        ],
        "Objetivo Agosto": ["1,40 pts (+1,05)", "1,70 pts (Sostener)", "0,40 pts (+0,40)", "1,68 pts (+0,12)", "1,36 pts (+0,16)", "1,40 pts (+0,70)", "0,60 pts (+0,30)", "1,40 pts (+1,40)", "1,70 pts (+0,85)", "1,12 a 1,40 pts (+0,44)"],
        "Ganancia Pts": ["+1,05 pts", "0,00 pts", "+0,40 pts", "+0,12 pts", "+0,16 pts", "+0,70 pts", "+0,30 pts", "+1,40 pts", "+0,85 pts", "+0,44 pts"],
        "Responsable": ["Daniel Colque", "Daniel Colque", "Juan Vazquez", "Juan Vazquez", "Juan Vazquez", "Aaron Martearena", "Aaron Martearena", "Aaron Martearena", "Romina R. / Entregas", "Adrián Di Costanzo"],
        "Acción Crítica Innegociable": [
            "Llamados proactivos masivos a clientes con infladores pendientes ABI 414/415[cite: 2].",
            "Mantener turnos al día para no caer del umbral de tolerancia del 98%[cite: 2].",
            "Retención preventiva de renovaciones y emisión obligatoria antes del retiro 0km[cite: 2].",
            "Acelerar liquidación prendaria de boletos cerrados en Hilux y Corolla Cross[cite: 2].",
            "Vincular seguro TCFA en cada prenda cerrada en el salón comercial[cite: 2].",
            "Poner flota ociosa de Share en reemplazo de taller y convenios corporativos[cite: 2].",
            "Ajustar tiempos de taller a <10 días en fast track y regularizar partes[cite: 2].",
            "Confirmar telefónicamente encuestas positivas con administradores de flota[cite: 2].",
            "Protocolo entrega: cliente sale con app My Toyota validada (Target ≥90% para 100% pts)[cite: 5].",
            "Cobranza mora cuota 2 a 6 y reenganche de planes para sostener crecimiento de emisión[cite: 6]."
        ]
    })
    
    st.dataframe(df_proy_detalle, use_container_width=True, hide_index=True)

# ==========================================
# 5. PESTAÑA: DOCUMENTACIÓN Y FUENTES
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
