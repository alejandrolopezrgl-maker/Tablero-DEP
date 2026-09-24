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

# --- DECLARACIÓN DE LAS 5 PESTAÑAS ---
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
# 4. PESTAÑA: PLAN DE ACCIÓN INTERACTIVO (CRONOGRAMA SEP / NOV / DIC)
# ==========================================
with tab_plan:
    st.header("🎯 Plan Estratégico Evolutivo: Cronograma de Cumplimiento")
    st.markdown("""
    Este plan sincroniza los compromisos operativos oficiales con las curvas reales de maduración:
    * **Posventa:** Vaticina alcanzar en **diciembre el 70% del target de campañas de Airbags (ABI 414/415)**, lo que asegura el **50% de los puntos DEP (0,70 pts)**[cite: 2].
    * **Calidad y Ventas:** Ejecuta el operativo de **35 encuestas promotoras continuas (Septiembre a Diciembre)** para elevar el SSI de Ventas al **95,6%** (promedio Red 96,1%)[cite: 2].
    * **Palancas Mensuales Inmediatas:** TCFA, KINTO Share, Servicios Conectados, Cuotas TPA y Depuración Salesforce aportan puntos directos mes a mes[cite: 2, 5, 6].
    """)

    # 1. Métricas de Impacto Global
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        st.metric(label="📊 Base Julio (Real)", value="68,56%", delta="66,16 pts (Puesto 21)")
    with c_p2:
        st.metric(label="🟢 Táctico (Septiembre)", value="70,86%", delta="+2,22 pts ➔ Puesto 17 🏆")
    with c_p3:
        st.metric(label="🟡 Sólido (Noviembre)", value="74,28%", delta="+5,52 pts ➔ Puesto 11 🌟")
    with c_p4:
        st.metric(label="🚀 Óptimo (Diciembre)", value="76,20%", delta="+7,37 pts ➔ Puesto 6 / Top 5 🏎️")

    st.markdown("---")

    # 2. Explicación Detallada de los 3 Escenarios Temporales
    st.subheader("🔍 Desglose Explicativo de los 3 Horizontes Temporales")
    
    col_esc1, col_esc2, col_esc3 = st.columns(3)
    
    with col_esc1:
        st.success("### 🟢 Septiembre: Táctico (Corto Plazo)\n**Meta: +2,22 pts ➔ 68,38 pts (70,86% - P17)**")
        st.markdown("""
        **Foco: Victorias Rápidas Mensuales (Sin inercia anual)**
        * **Servicios Conectados (+0,51 pts):** Pasa de la franja 70-79% al escalón **80%-90% de Onboarding** (de 0,85 a 1,36 pts)[cite: 2, 5].
        * **TCFA Cartera (+0,40 pts):** Cartera de Seguros (7.5.5)[cite: 2] revierte la fuga (-3,65%) pasando a saldo neto positivo (>0%).
        * **KINTO Share (+0,70 pts):** Ocupación $\ge 70\%$ y bookings al 100% (de 0,70 a 1,40 pts)[cite: 2].
        * **TPA Cuotas (+0,16 pts):** Freno a la mora temprana; escala a variación 10%-13,99% vs Dic'25 (de 0,96 a 1,12 pts)[cite: 2, 6].
        * **Salesforce Ventas (+0,45 pts):** Depuración y sincronización de boletos vencidos (1.5.5: de 1,05 a 1,50 pts)[cite: 2].
        
        *Calidad y Airbags se mantienen en base mientras inician su curva de recupero.*
        
        **Impacto en Ranking Red:**
        Supera de forma inmediata a **BOS (P17), HOM (P18), DEC (P19) y ZEN (P20)**[cite: 2], trepando al **Puesto 17**.
        """)

    with col_esc2:
        st.info("### 🟡 Noviembre: Sólido (Mediano Plazo)\n**Meta: +5,52 pts ➔ 71,68 pts (74,28% - P11)**")
        st.markdown("""
        **Foco: Consolidación y Primer Impacto de Encuestas**
        * **Servicios Conectados (+0,85 pts):** Protocolo estricto de entrega: alcanza **$\ge 90\%$ Full Onboarding** (1,70 / 1,70 pts)[cite: 2, 5].
        * **TCFA Pleno (+0,68 pts):** Cartera positiva (+0,40)[cite: 2] + Financiación Prendaria (+0,12)[cite: 2] + Seguros (+0,16)[cite: 2].
        * **KINTO Share + One (+1,00 pts):** Share al 100% (+0,70)[cite: 2] + Siniestros y Alistamiento One regularizados (+0,30)[cite: 2].
        * **TPA Cuotas Pleno (+0,44 pts):** Supera el 14% de crecimiento de emisión vs Dic'25 (1,40 / 1,40 pts)[cite: 2, 6].
        * **Posventa Campañas (+0,35 pts):** Airbags avanza al ritmo del plan hacia el 70% de cumplimiento (alcanza el escalón de 50% de pts = 0,70 pts)[cite: 2].
        * **Calidad SSI Ventas (+1,75 pts):** Las primeras 20 encuestas promotoras consecutivas logran mover el promedio YTD hacia el escalón intermedio[cite: 2].
        
        **Impacto en Ranking Red:**
        Autolux trepa al **Puesto 11**, superando a **LUP (P16), KAI (P15), ANZ (P14), HAI (P13) y RIC (P12)**[cite: 2], quedando a solo **0,44 pts de SENNA (Top 10)**[cite: 2].
        """)

    with col_esc3:
        st.warning("### 🚀 Diciembre: Óptimo (Cierre Anual)\n**Meta: +7,37 pts ➔ 73,53 pts (76,20% - P6 / Top 5)**")
        st.markdown("""
        **Foco: Maduración Total de Compromisos**
        * **Posventa Campañas 70% (+0,35 pts consolidado):** Cumple con el vaticinio del 70% del target de Airbags, asegurando 0,70 / 1,40 pts[cite: 2].
        * **Calidad SSI al 95,6% (+2,70 pts):** Se completan las **35 encuestas promotoras**, llevando el SSI acumulado de Ventas a 95,6% (muy cerca del promedio Red 96,1%)[cite: 2]. Asegura escalón de puntaje sustancial en 1.1.1[cite: 2].
        * **Kinto One Corporativo (+1,40 pts):** Cierre y facturación de contratos corporativos de flota + encuestas NPS promotoras de empresas[cite: 2].
        * **Todas las palancas tácticas sostenidas al 100%:** Servicios Conectados, TCFA, TPA y Salesforce consolidados[cite: 2].
        
        **Impacto en Ranking Red:**
        Autolux entra triunfalmente al **Top 10 superando a SENNA (74,74%)** y pelea mano a mano el **Puesto 5 con PRANA (76,91%)**[cite: 2].
        """)

    st.markdown("---")

    # 3. Gráficos Comparativos y Cascada de Puntos
    col_gr1, col_gr2 = st.columns(2)
    
    with col_gr1:
        hitos_temporales = ["Julio Real (P21)", "Septiembre (P17)", "Noviembre (P11)", "Diciembre (P6)", "SENNA (P10 - Top 10)", "PRANA (P5 - Top 5)"]
        valores_hitos = [68.56, 70.86, 74.28, 76.20, 74.74, 76.91]
        colores_hitos = ["#d62728", "#2ca02c", "#1f77b4", "#ff7f0e", "#5B9BD5", "#1F4E78"]
        
        fig_cronograma = go.Figure()
        fig_cronograma.add_trace(go.Bar(
            x=hitos_temporales, 
            y=valores_hitos, 
            marker_color=colores_hitos, 
            text=[f"{v:.2f}%" for v in valores_hitos], 
            textposition="inside"
        ))
        fig_cronograma.add_hline(y=74.74, line_dash="dash", line_color="#5B9BD5", annotation_text="Umbral Top 10 SENNA (74,74%)", annotation_position="top left")
        fig_cronograma.update_layout(
            title="<b>Curva de Avance Temporal DEP: Septiembre a Diciembre</b>",
            yaxis=dict(title="Cumplimiento Global %", range=[60, 82]),
            margin=dict(t=60, b=40),
            height=430
        )
        st.plotly_chart(fig_cronograma, use_container_width=True)

    with col_gr2:
        pilares_dic = ["Calidad SSI (+2,70)", "Kinto One (+1,40)", "Serv. Conect. (+0,85)", "TCFA Pleno (+0,68)", "Salesforce (+0,45)", "TPA Cuotas (+0,44)", "Airbags 70% (+0,35)", "Ganancia Total"]
        puntos_dic = [2.70, 1.40, 0.85, 0.68, 0.45, 0.44, 0.35, 7.37]
        
        fig_aportes_dic = go.Figure(go.Bar(
            x=pilares_dic,
            y=puntos_dic,
            marker_color=["#27ae60", "#f39c12", "#00A86B", "#5B9BD5", "#e74c3c", "#9B59B6", "#1F4E78", "#2c3e50"],
            text=[f"+{v:.2f}" for v in puntos_dic],
            textposition="outside"
        ))
        fig_aportes_dic.update_layout(
            title="<b>Distribución de Puntos Netos Ganables a Diciembre</b>",
            yaxis=dict(title="Puntos Directos DEP", range=[0, 8.5]),
            margin=dict(t=60, b=40),
            height=430
        )
        st.plotly_chart(fig_aportes_dic, use_container_width=True)

    # 4. Matriz Táctica de Ejecución Sincronizada
    st.subheader("📋 Matriz Operativa de Compromisos Oficiales (Septiembre - Diciembre)")
    
    df_cronograma_detalle = pd.DataFrame({
        "Área": ["Ventas / Calidad", "Posventa", "General", "TCFA", "TCFA", "KINTO", "KINTO", "TPA", "Ventas CRM"],
        "Código": ["1.1.1", "3.5.2", "9.5.3", "7.5.5", "7.5.1 / 7.5.2", "5.5.1 / 5.5.3", "5.1.3 / 5.5.6", "4.5.4", "1.5.5"],
        "Indicador Oficial": [
            "SSI Ventas (Satisfacción de Entrega)",
            "Campañas Airbags (ABI 414/415)",
            "Servicios Conectados (Full Onboarding)",
            "Crecimiento Cartera de Seguros",
            "Financiación y Seguros 0km",
            "Ocupación y Bookings Kinto Share",
            "NPS y Bookings Kinto One Flotas",
            "Cuotas Emitidas TPA vs Dic'25",
            "Salesforce: Depuración Boletos y Listas"
        ],
        "Base Julio": ["0,00 / 4,50 pts", "0,35 / 1,40 pts", "0,85 / 1,70 pts", "0,00 / 0,40 pts", "2,76 / 3,04 pts", "0,70 / 1,40 pts", "0,00 / 1,80 pts", "0,96 / 1,40 pts", "1,05 / 1,50 pts"],
        "Meta & Horizonte": [
            "35 promotoras ➔ 95,6% SSI (Diciembre)",
            "70% de objetivo ➔ 50% pts (0,70 pts - Diciembre)",
            "≥90% Onboarding (Octubre / Noviembre)",
            "Saldo neto positivo >0% (Septiembre)",
            "100% de liquidaciones y seguros (Noviembre)",
            "Ocupación ≥70% sostenida (Septiembre)",
            "Contrato corporativo cerrado (Diciembre)",
            "Crecimiento ≥14% (Octubre / Noviembre)",
            "Backlog saneado a cero (Septiembre)"
        ],
        "Aporte DEP": ["+2,70 pts", "+0,35 pts", "+0,85 pts", "+0,40 pts", "+0,28 pts", "+0,70 pts", "+1,40 pts", "+0,44 pts", "+0,45 pts"],
        "Responsable": [
            "Alfredo Aguilar / Calidad",
            "Daniel Colque",
            "Romina R. / Entregas",
            "Juan Vazquez",
            "Juan Vazquez",
            "Aaron Martearena",
            "Aaron Martearena",
            "Adrián Di Costanzo",
            "Alfredo Aguilar"
        ],
        "Plan de Acción Táctico Innegociable": [
            "Asegurar 35 encuestas promotoras en entregas para alcanzar 95,6% de SSI y diluir desvíos pasados.",
            "Plan de citación proactiva para completar el 70% de las unidades afectadas con infladores ABI 414/415[cite: 2].",
            "Protocolo de salón: vehículo no se retira sin app My Toyota instalada y validada (Meta ≥90%)[cite: 5].",
            "Control diario de renovaciones de pólizas para evitar fugas y garantizar saldo mensual positivo[cite: 2].",
            "Vincular crédito TCFA y seguro en cada unidad Hilux y Corolla Cross adjudicada o vendida[cite: 2].",
            "Volcar flota ociosa de Share a reemplazos de taller y convenios con empresas de la zona[cite: 2].",
            "Concretar cotización corporativa Kinto One y confirmar encuestas NPS con administradores de flota[cite: 2].",
            "Cobranza intensiva de mora temprana (cuotas 2 a 6) para sostener emisión de cupones $\ge 14\%$[cite: 6].",
            "Limpieza de boletos vencidos sin actividad comercial y carga al día en Salesforce[cite: 2]."
        ]
    })
    
    st.dataframe(df_cronograma_detalle, use_container_width=True, hide_index=True)

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
