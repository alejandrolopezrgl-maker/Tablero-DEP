import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux", layout="wide", page_icon="🚗")
st.title("🚗 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Datos Oficiales e Informe de Calidad de la Red TASA (Manual DEP 2026 - Corte Agosto)")

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

# 3. VALORES BASE OFICIALES AUTOLUX (AGOSTO 2026 OFICIAL)
b_ventas = 41.0 if not penalidad_mov else (41.0 - 5.0)
b_posventa = 96.1 - (96.1 * (castigo_posventa_fieldman / 100))
b_tpa = 87.1
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

# METAS OFICIALES AGOSTO (P10 = BHA 76.5%, P5 = SAK 78.7%)
target_p10 = 76.53  # B.H.A.S. (BHA)
target_p5 = 78.73   # SAKURA (SAK)

if not hay_simulacion and not penalidad_fp and not penalidad_mov and visitas_fm >= 85 and porcentaje_emt >= 80.0:
    score_global_final = 69.24
    puesto_calculado = 24
else:
    score_global_final = (
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.20) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (usd_simulada * 0.06) + 
        (esp_simulada * 0.05) + (tcfa_simulada * 0.04) + (esg_simulada * 0.01)
    ) - puntos_a_restar_global - penalidad_estandar_emt
    if penalidad_mov: score_global_final -= 1.1

    if score_global_final <= 69.24:
        puesto_calculado = int(24 + ((69.24 - score_global_final) / 5.0) * 10)
        puesto_calculado = min(44, max(24, puesto_calculado))
    elif score_global_final >= 99.9:
        puesto_calculado = 1
    elif score_global_final >= target_p5:
        puesto_calculado = max(1, min(5, int(5 - ((score_global_final - target_p5) / (100.0 - target_p5)) * (5 - 1))))
    elif score_global_final >= target_p10:
        puesto_calculado = max(6, min(10, int(10 - ((score_global_final - target_p10) / (target_p5 - target_p10)) * (10 - 6))))
    else:
        puesto_calculado = max(11, min(23, int(24 - ((score_global_final - 69.24) / (target_p10 - 69.24)) * (24 - 10))))

# BENCHMARK OFICIAL AGOSTO
data_operativa = {
    "Área": ["Ventas (22%)", "Ventas Especiales (5%)", "Posventa (27%)", "TPA (9%)", "KINTO (6%)", "Usados (6%)", "TCFA (4%)", "ESG (1%)", "GENERAL (20%)"],
    "Autolux (LUX)": [v_simulada, esp_simulada, p_simulada, tpa_simulada, kinto_simulada, usd_simulada, tcfa_simulada, esg_simulada, g_simulada],
    "SAK - Puesto 5": [59.4, 79.0, 95.5, 97.8, 71.8, 73.3, 63.0, 35.5, 77.4],
    "BHA - Puesto 10": [73.8, 30.0, 98.5, 71.1, 68.5, 73.3, 72.0, 35.5, 69.0],
    "Promedio RED": [58.9, 50.8, 90.3, 58.6, 56.0, 65.2, 69.2, 33.2, 67.1]
}
df_bench_op = pd.DataFrame(data_operativa)

data_ranking_global = {
    "Concesionario": ["SAK - Puesto 5", "BHA - Puesto 10", "Autolux (LUX) - Puesto 24", "Promedio RED"],
    "Porcentaje DEP Global": [78.73, 76.53, score_global_final, 69.08]
}
df_bench_ranking = pd.DataFrame(data_ranking_global)

if st.sidebar.button("🔄 Restablecer Valores Oficiales", key="btn_reset_lateral"):
    for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg"]: 
        if k in st.session_state: st.session_state[k] = 0.0
    st.rerun()

# --- DECLARACIÓN DE LAS 5 PESTAÑAS ---
tab_dashboard, tab_evolucion, tab_calidad, tab_plan, tab_docs = st.tabs([
    "📊 Dashboard del Dealer", 
    "📈 Evolución Julio vs. Agosto",
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
    with col1: 
        st.metric("Cumplimiento DEP Score Global (Agosto)", f"{score_global_final:.1f}%", delta="+0.7% vs Julio (68.6%)")
    with col2: 
        if puesto_calculado < 24: 
            st.metric("Ranking Proyectado Red", f"Puesto {puesto_calculado} 🏆", delta=f"¡Subiendo {24 - puesto_calculado} puestos!")
        elif puesto_calculado > 24: 
            st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🚨", delta=f"¡Bajando {puesto_calculado - 24} puestos!")
        else: 
            st.metric("Ranking General Red", f"Puesto 24 🚗", delta="-3 puestos vs Julio (Efecto Competencia Red)", delta_color="inverse")
    with col3:
        if pts_para_p5 == 0: 
            st.metric("Puntos para Meta Superlativa", "¡En Puesto 5 o superior! 🎉")
        else: 
            st.metric(
                label="Puntos Faltantes para Top 10 / Top 5", 
                value=f"+{pts_para_p10:.1f} pts (P10 - BHA)", 
                delta=f"+{pts_para_p5:.1f} pts para Puesto 5 (SAK)", 
                delta_color="inverse"
            )

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
            "SAK - Puesto 5": "#1F4E78", 
            "BHA - Puesto 10": "#5B9BD5", 
            "Promedio RED": "#70AD47"
        }
    )
    fig_op.update_layout(xaxis_title="Unidad Operativa", yaxis_title="Efectividad %", yaxis=dict(range=[0, 110]))
    st.plotly_chart(fig_op, use_container_width=True)

    st.subheader("🏆 Posicionamiento Estratégico Consolidado RED (Agosto 2026)")
    fig_gen = px.bar(
        df_bench_ranking, 
        x="Concesionario", 
        y="Porcentaje DEP Global", 
        color="Concesionario", 
        text_auto=".1f", 
        color_discrete_map={
            "Autolux (LUX) - Puesto 24": "#d62728", 
            "SAK - Puesto 5": "#1F4E78", 
            "BHA - Puesto 10": "#5B9BD5", 
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
    
    if porcentaje_emt < 80.0: 
        st.error(f"🚨 Alerta DEP: Estándar EMT en {total_puntos_emt} / 900 ({porcentaje_emt:.1f}%). Penalidad activa.")
    else: 
        st.success(f"🎉 Estándar EMT Certificado Oficialmente: {total_puntos_emt} / 900 ({porcentaje_emt:.1f}%). Concesionario a salvo.")

# =======================================================
# 2. PESTAÑA: EVOLUCIÓN JULIO VS AGOSTO
# =======================================================
with tab_evolucion:
    st.subheader("📈 Comparativo Evolutivo Oficial: Julio 2026 vs. Agosto 2026")
    c_ev1, c_ev2, c_ev3 = st.columns(3)
    with c_ev1: 
        st.metric("Cumplimiento DEP Global", "69,24%", delta="+0,68% (+0,65 pts vs Julio)")
    with c_ev2: 
        st.metric("Posición Ranking Red", "Puesto 24", delta="-3 puestos (Efecto Competencia)", delta_color="inverse")
    with c_ev3: 
        st.metric("Comparativa vs. Promedio RED", "69,24% vs 69,08%", delta="+0,16% por encima de la Red")

    st.markdown("---")
    
    # Explicación del fenómeno de ranking
    st.info("""
    💡 **¿Por qué subió la nota pero bajó el ranking de Autolux?**
    * **Avance Interno Real:** Autolux pasó de **66,165 pts (68,56%)** a **66,815 pts (69,24%)**, sumando **+0,650 puntos netos** y manteniéndose por encima del promedio general del país (69,08%).
    * **Aceleración de la Competencia:** En agosto, 4 concesionarios que venían por detrás tuvieron crecimientos de entre +1,5 y +2,8 puntos y lograron superar provisionalmente a Autolux:
      * **Centro Motor (CEM):** Subió de 67,49% (P26) a 70,31% (P18) `[+2,83%]`.
      * **Del Pilar (ATN):** Subió de 67,83% (P25) a 69,98% (P20) `[+2,15%]`.
      * **Nuñez Auto (NUA):** Subió de 67,46% (P28) a 69,30% (P23) `[+1,84%]`.
      * **Yacopini (YAC):** Subió de 68,12% (P24) a 69,69% (P21) `[+1,56%]`.
    """)

    df_comp = pd.DataFrame({
        "Área": ["Ventas", "TPA", "Posventa", "TCFA", "General", "Usados", "KINTO", "ESG", "Ventas Especiales"],
        "Julio (%)": [38.0, 87.4, 96.1, 83.0, 72.3, 73.3, 41.7, 35.5, 30.0],
        "Agosto (%)": [41.0, 87.1, 96.1, 83.0, 72.3, 73.3, 41.7, 35.5, 30.0],
        "Variación (%)": [+3.1, -0.3, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "Posición Red (Jul ➔ Ago)": ["P41 ➔ P41", "P5 ➔ P7", "P9 ➔ P9", "P16 ➔ P17", "P20 ➔ P22", "P16 ➔ P18", "P41 ➔ P41", "P7 ➔ P7", "P20 ➔ P18"],
        "Estado": ["🟢 Mejoró (+0,68 pts)", "🟡 Ajuste leve (-0,03 pts)", "🟡 Sólido / Igual", "🟡 Sólido / Igual", "🟡 Sólido / Igual", "🟡 Sólido / Igual", "🟡 Sólido / Igual", "🟡 Sólido / Igual", "🟡 Sólido / Igual"]
    }).sort_values(by="Variación (%)", ascending=False)

    st.dataframe(df_comp, use_container_width=True, hide_index=True)

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(x=df_comp["Área"], y=df_comp["Julio (%)"], name="Julio 2026", marker_color="#A6A6A6", text=df_comp["Julio (%)"], textposition="outside"))
    fig_comp.add_trace(go.Bar(x=df_comp["Área"], y=df_comp["Agosto (%)"], name="Agosto 2026", marker_color="#1F4E78", text=df_comp["Agosto (%)"], textposition="outside"))
    fig_comp.update_layout(title="Comparativa de Cumplimiento por Área (Julio vs Agosto 2026)", barmode="group", yaxis=dict(range=[0, 110]))
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")
    st.subheader("🔍 Movimiento Quirúrgico de Indicadores en Agosto")

    col_an1, col_an2 = st.columns(2)
    with col_an1:
        st.success("📈 **Ventas: Primer impacto del Plan de Calidad (+0,675 pts netos)**")
        st.markdown("""
        * **1.1.1 SSI Ventas (+1,125 pts):** Pasó de 0,00 a **1,125 pts** al comenzar a impactar las primeras encuestas promotoras en entregas.
        * **1.1.3 NPS Ventas (+0,600 pts):** Pasó de 0,00 a **0,600 pts** al revertir la franja crítica.
        * **1.5.3 Patentamientos (-1,050 pts):** Desfase de fin de mes (pasó de 2,10 a **1,050 pts**). *De no haberse caído este indicador, la nota de Ventas habría alcanzado 45,8% y Autolux estaría en Puesto 18.*
        """)

    with col_an2:
        st.warning("⚖️ **TPA: Compensación Interna (-0,025 pts netos)**")
        st.markdown("""
        * **4.5.4 Cuotas Emitidas (+0,175 pts):** Creció de 0,96 a **1,14 pts** por la cobranza activa de moras tempranas.
        * **4.1.2 NPS TPA (-0,200 pts):** Ajustó levemente de 0,60 a **0,40 pts** por dispersión transaccional en la etapa de adjudicación.
        * **Veredicto TPA:** Autolux sigue como uno de los líderes indiscutidos del país en Planes de Ahorro (**87,1% vs 58,6% de la Red**).
        """)

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
# 4. PESTAÑA: PLAN DE ACCIÓN INTERACTIVO (ESCENARIOS TÁCTICO / SÓLIDO / ÓPTIMO)
# ==========================================
with tab_plan:
    st.header("🎯 Plan Estratégico: Escenarios de Mejora DEP")
    st.markdown("""
    Este plan consolida los compromisos operativos oficiales distribuidos en **3 escenarios de avance**:
    * **Por qué estuvo bien incluir Posventa, TPA, TCFA y KINTO:** Sirven para defender la ventaja, blindar penalidades y capturar victorias rápidas (ej. Cartera TCFA, Cuotas TPA, Ocupación Kinto).
    * **La palanca decisiva (Ventas y Calidad):** Autolux está a **7,03 pts de B.H.A.S. (Top 10)**. Posventa, TPA, TCFA y Kinto pueden sumar ~2,8 pts combinados; los **4 a 5 pts restantes provienen obligatoriamente de Ventas y Calidad (SSI promotor y blindaje de patentamientos)**.
    """)

    # 1. Métricas de Impacto Global
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        st.metric(label="📊 Base Agosto (Real)", value="69,24%", delta="66,81 pts (Puesto 24)")
    with c_p2:
        st.metric(label="🟢 Táctico", value="71,60%", delta="+2,36 pts ➔ Puesto 16 🏆")
    with c_p3:
        st.metric(label="🟡 Sólido", value="74,80%", delta="+5,56 pts ➔ Puesto 10 (Top 10) 🌟")
    with c_p4:
        st.metric(label="🚀 Óptimo", value="76,85%", delta="+7,61 pts ➔ Puesto 6 / Pelea Top 5 🏎️")

    st.markdown("---")

    # 2. Explicación Detallada de los 3 Escenarios
    st.subheader("🔍 Desglose Explicativo de los 3 Escenarios")
    
    col_esc1, col_esc2, col_esc3 = st.columns(3)
    
    with col_esc1:
        st.success("### 🟢 Táctico\n**Meta: +2,36 pts ➔ 69,18 pts (71,60% - P16)**")
        st.markdown("""
        **Foco: Corrección Inmediata y Victorias Rápidas**
        * **Blindaje de Patentamientos (+1,05 pts):** Recuperar el 100% de cumplimiento en 1.5.3 eliminando el desfase de fin de mes.
        * **Servicios Conectados (+0,51 pts):** Pasa del 76% al escalón **80%-89% de Onboarding** (de 0,85 a 1,36 pts) con 100% en entregas nuevas.
        * **TCFA Cartera (+0,40 pts):** Cartera de Seguros (7.5.5) revierte el saldo a positivo (>0%).
        * **KINTO Share (+0,70 pts):** Ocupación $\ge 70\%$ y bookings al 100% (de 0,70 a 1,40 pts).
        * **Salesforce Ventas (+0,45 pts):** Depuración activa de boletos vencidos (1.5.5).
        
        **Impacto en Ranking Red:**
        Supera de inmediato a **Nuñez Auto (P23), Del Pilar (P20), Yacopini (P21) y Centro Motor (P18)**, subiendo al **Puesto 16**.
        """)

    with col_esc2:
        st.info("### 🟡 Sólido\n**Meta: +5,56 pts ➔ 72,38 pts (74,80% - P10 Top 10)**")
        st.markdown("""
        **Foco: Consolidación de Calidad y Servicios Conectados**
        * **Calidad SSI Ventas (+1,125 pts adicionales):** Las primeras 20 encuestas promotoras continuas consolidan el segundo escalón en 1.1.1 (de 1,125 a 2,250 pts).
        * **Servicios Conectados Pleno (+0,85 pts):** Se quiebra la barrera del **$\ge 90\%$ Onboarding** (1,70 / 1,70 pts) combinando entregas nuevas + campaña de recupero de clientes 2026.
        * **TCFA Pleno (+0,68 pts):** Cartera positiva (+0,40) + Financiación Prendaria (+0,12) + Seguros (+0,16).
        * **TPA Cuotas Pleno (+0,26 pts):** Sostiene crecimiento $\ge 14\%$ en cuotas emitidas (1,40 / 1,40 pts).
        * **Posventa Campañas Airbags (+0,35 pts):** Avanza al 70% de unidades saneadas ABI 414/415 (0,70 / 1,40 pts).
        
        **Impacto en Ranking Red:**
        Autolux trepa al **Puesto 10**, superando a **B.H.A.S. (BHA)** y entrando formalmente al grupo de los 10 mejores del país.
        """)

    with col_esc3:
        st.warning("### 🚀 Óptimo\n**Meta: +7,61 pts ➔ 74,43 pts (76,85% - P6 / Top 5)**")
        st.markdown("""
        **Foco: Máxima Maduración de Todos los Pilares**
        * **Calidad SSI Plena (+2,25 pts adicionales):** Completar las **35 encuestas promotoras**, llevando el SSI de Ventas al 95,6% y desbloqueando el máximo puntaje en 1.1.1 (3,375 a 4,50 pts).
        * **Kinto One Corporativo (+1,40 pts):** Cierre y facturación de contratos corporativos de flotas con empresas de la región.
        * **Posventa Campañas Airbags Consolidado (+0,35 pts):** Sostenido en el escalón de 50% de puntos.
        * **TPA, TCFA y General blindados al 100% de efectividad.**
        
        **Impacto en Ranking Red:**
        Autolux se consolida en el **Puesto 6** y disputa mano a mano el **Puesto 5 con Sakura (78,7%)**.
        """)

    st.markdown("---")

    # 3. Gráficos Comparativos y Cascada de Puntos
    col_gr1, col_gr2 = st.columns(2)
    
    with col_gr1:
        escenarios_labels = ["Agosto Real (P24)", "Táctico (P16)", "Sólido (P10)", "Óptimo (P6)", "BHA (P10 - Top 10)", "SAK (P5 - Top 5)"]
        valores_esc = [69.24, 71.60, 74.80, 76.85, 76.53, 78.73]
        colores_esc = ["#d62728", "#2ca02c", "#1f77b4", "#ff7f0e", "#5B9BD5", "#1F4E78"]
        
        fig_cronograma = go.Figure()
        fig_cronograma.add_trace(go.Bar(
            x=escenarios_labels, 
            y=valores_esc, 
            marker_color=colores_esc, 
            text=[f"{v:.2f}%" for v in valores_esc], 
            textposition="inside"
        ))
        fig_cronograma.add_hline(y=76.53, line_dash="dash", line_color="#5B9BD5", annotation_text="Umbral Top 10 BHA (76,53%)", annotation_position="top left")
        fig_cronograma.update_layout(
            title="<b>Proyección de Avance DEP por Escenarios vs. Metas Agosto</b>",
            yaxis=dict(title="Cumplimiento Global %", range=[62, 82]),
            margin=dict(t=60, b=40),
            height=430
        )
        st.plotly_chart(fig_cronograma, use_container_width=True)

    with col_gr2:
        pilares_opt = ["SSI Ventas (+2,25)", "Patentamientos (+1,05)", "Kinto One (+1,40)", "Serv. Conect. (+0,85)", "TCFA Pleno (+0,68)", "Salesforce (+0,45)", "Airbags (+0,35)", "TPA (+0,26)"]
        puntos_opt = [2.25, 1.05, 1.40, 0.85, 0.68, 0.45, 0.35, 0.26]
        
        fig_aportes_opt = go.Figure(go.Bar(
            x=pilares_opt,
            y=puntos_opt,
            marker_color=["#27ae60", "#2ecc71", "#f39c12", "#00A86B", "#5B9BD5", "#e74c3c", "#1F4E78", "#9B59B6"],
            text=[f"+{v:.2f}" for v in puntos_opt],
            textposition="outside"
        ))
        fig_aportes_opt.update_layout(
            title="<b>Distribución de Puntos Netos Ganables por Acción</b>",
            yaxis=dict(title="Puntos Directos DEP", range=[0, 3.0]),
            margin=dict(t=60, b=40),
            height=430
        )
        st.plotly_chart(fig_aportes_opt, use_container_width=True)

    # 4. Matriz Táctica de Ejecución
    st.subheader("📋 Matriz Operativa de Compromisos Oficiales")
    
    df_cronograma_detalle = pd.DataFrame({
        "Área": ["Ventas", "General", "Ventas / Calidad", "Posventa", "TCFA", "TCFA", "KINTO", "KINTO", "TPA", "Ventas CRM"],
        "Código": ["1.5.3", "9.5.3", "1.1.1", "3.5.2", "7.5.5", "7.5.1 / 7.5.2", "5.5.1 / 5.5.3", "5.1.3 / 5.5.6", "4.5.4", "1.5.5"],
        "Indicador Oficial": [
            "Patentamientos vs Declaración",
            "Servicios Conectados (Full Onboarding)",
            "SSI Ventas (Satisfacción de Entrega)",
            "Campañas Airbags (ABI 414/415)",
            "Crecimiento Cartera de Seguros",
            "Financiación y Seguros 0km",
            "Ocupación y Bookings Kinto Share",
            "NPS y Bookings Kinto One Flotas",
            "Cuotas Emitidas TPA vs Dic'25",
            "Salesforce: Depuración Boletos y Listas"
        ],
        "Base Agosto": [
            "1,05 / 2,10 pts",
            "0,85 / 1,70 pts (76% Real)",
            "1,13 / 4,50 pts", 
            "0,35 / 1,40 pts", 
            "0,00 / 0,40 pts", 
            "2,76 / 3,04 pts", 
            "0,70 / 1,40 pts", 
            "0,00 / 1,80 pts", 
            "1,14 / 1,40 pts", 
            "1,05 / 1,50 pts"
        ],
        "Meta del Escenario": [
            "100% cumplido (Táctico)",
            "76% ➔ ≥90% (80-89% Táctico | ≥90% Sólido)",
            "35 promotoras ➔ 95,6% SSI (Óptimo)",
            "70% de objetivo ➔ 50% pts (0,70 pts - Sólido)",
            "Saldo neto positivo >0% (Táctico)",
            "100% de liquidaciones y seguros (Sólido)",
            "Ocupación ≥70% sostenida (Táctico)",
            "Contrato corporativo cerrado (Óptimo)",
            "Crecimiento ≥14% (Sólido)",
            "Backlog saneado a cero (Táctico)"
        ],
        "Aporte DEP": ["+1,05 pts", "+0,85 pts", "+2,25 pts", "+0,35 pts", "+0,40 pts", "+0,28 pts", "+0,70 pts", "+1,40 pts", "+0,26 pts", "+0,45 pts"],
        "Responsable": [
            "Ventas Convencional",
            "Romina R. / Entregas",
            "Alfredo Aguilar / Calidad",
            "Daniel Colque",
            "Juan Vazquez",
            "Juan Vazquez",
            "Aaron Martearena",
            "Aaron Martearena",
            "Adrián Di Costanzo",
            "Alfredo Aguilar"
        ],
        "Plan de Acción Innegociable": [
            "Sincronizar fechas de patentamiento en el registro para evitar caídas de fin de mes y recuperar 1,05 pts directos.",
            "1) 100% en entregas nuevas: vehículo no sale sin app vinculada. 2) Campaña de recupero de ~15-20 clientes 2026.",
            "Asegurar 35 encuestas promotoras continuas en salones de Salta, Jujuy y Tartagal para elevar el SSI.",
            "Plan de citación activa para alcanzar el 70% de infladores ABI 414/415 reemplazados.",
            "Monitoreo diario de renovaciones de pólizas para sostener balance neto mensual positivo.",
            "Vincular seguro TCFA y crédito en cada unidad adjudicada o vendida.",
            "Asignar flota ociosa de Share a reemplazos de taller y empresas locales.",
            "Concretar licitaciones corporativas y verificar encuestas NPS en empresas.",
            "Cobranza intensiva de cuotas tempranas (2 a 6) para sostener emisión de cupones.",
            "Limpieza inmediata de boletos vencidos sin actividad comercial en CRM."
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
            st.warning("⚠️ '15549_DES020-26 -DEP ACUM. AGO.xlsx' no encontrado.")
