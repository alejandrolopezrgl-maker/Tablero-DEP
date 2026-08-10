import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux", layout="wide", page_icon="🚗")
st.title("🚗 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Datos Oficiales e Informe de Calidad de la Red TASA")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL: CONTROL DE RIESGOS PENALIDADES DE CAMPO
st.sidebar.header("🚨 Zona de Control de Riesgos")
if st.session_state.reestablecer:
    penalidad_fp = st.sidebar.toggle("Fair Play Global (-10 pts)", value=False, key="fp_real")
    penalidad_mov = st.sidebar.toggle("Falta Movilidad (-5.0 pts)", value=False, key="mov_real")
    visitas_fm = st.sidebar.slider("% Compromisos Fieldman", 0, 100, 85, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fp = st.sidebar.toggle("Fair Play Global (-10 pts)", value=False)
    penalidad_mov = st.sidebar.toggle("Falta Movilidad (-5.0 pts Ventas)", value=False)
    visitas_fm = st.sidebar.slider("% Compromisos Fieldman", 0, 100, 85)

puntos_a_restar_global = 10.0 if penalidad_fp else 0.0
castigo_posventa_fieldman = 40.0 if visitas_fm < 85 else 0.0

if visitas_fm < 85: 
    st.sidebar.error("❌ Penalidad Posventa Activa (-40% en Score del área).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman a salvo (≥85%).")

# 3. BASE DE DATOS ESTRATÉGICA EXTRACTADA DIRECTAMENTE DEL POWER BI TOYOTA
base_ventas_lux = 55.7 if not penalidad_mov else (55.7 - 5.0)
base_posventa_lux = 91.7 - (91.7 * (castigo_posventa_fieldman / 100))

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
esp_simulada = st.session_state.sim_pilar_especiales if st.session_state.sim_pilar_especiales is not None else 49.0
usd_simulada = st.session_state.sim_pilar_usados if st.session_state.sim_pilar_usados is not None else 75.8
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
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.165) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (usd_simulada * 0.06) + 
        (esp_simulada * 0.05) + (tcfa_simulada * 0.04) + (esg_simulada * 0.01)
    )
    score_global_final = score_global_final - puntos_a_restar_global - penalidad_estandar_emt
    if penalidad_mov: score_global_final -= 1.1

# DATAFRAME OPERATIVO COMPLETO
data_operativa = {
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "GENERAL"],
    "Autolux (LUX)": [v_simulada, esp_simulada, p_simulada, tpa_simulada, kinto_simulada, usd_simulada, tcfa_simulada, esg_simulada, g_simulada],
    "DPQ - Puesto 5": [72.3, 55.0, 91.0, 85.0, 68.5, 78.0, 88.0, 25.0, 59.8],
    "GON - Puesto 10": [68.0, 50.0, 88.5, 71.0, 65.2, 74.0, 79.0, 26.0, 79.0]
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
    for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg", "db_plan_puro_19_v2", "db_ampliacion_2_limpia"]: 
        if k in st.session_state: st.session_state[k] = None
    for ek in emt_keys: st.session_state[ek] = 100
    st.session_state.reestablecer = True
    st.rerun()

tab_dashboard, tab_calidad, tab_plan = st.tabs(["📊 Dashboard del Dealer", "🕵️ Análisis de Calidad por Sucursal", "📋 Plan de Acción Interactiva"])

with tab_dashboard:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Cumplimiento DEP Score Global", f"{score_global_final:.1f}%")
    with col2: 
        if puesto_calculado < 24: st.metric("Ranking Proyectado Red", f"Puesto {puesto_calculado} 🏆", delta=f"¡Subiendo {24 - puesto_calculado} puestos!")
        elif puesto_calculado > 24: st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🚨", delta=f"¡Bajando {puesto_calculado - 24} puestos!")
        else: st.metric("Ranking General Red", f"Puesto 24 🚗", help="Posición base oficial de Autolux")
    with col3: st.metric("Impacto Penalidad EMT", f"-{penalidad_estandar_emt:.1f} pts" if penalidad_estandar_emt > 0 else "0.0 pts (Ok)")

    st.subheader("🏁 Desempeño Operativo por Unidades de Negocio (Incluyendo Pilar GENERAL)")
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

with tab_calidad:
    st.subheader("🕵️ Informe Clínico de Calidad: Análisis de Pareto por Sucursal")
    df_p = pd.DataFrame()
    df_p["Categoría"] = ["Demoras y puntualidad", "Comunicación y seguimiento", "Administración y documentación", "Cortesías y obsequios", "Atención y actitud", "Instalaciones y comodidad", "Preparación y accesorios", "Explicación del vehículo", "Protocolo y personalización", "Producto o marca"]
    # Datos de ejemplo corregidos (reemplazar con los tuyos)
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

with tab_plan:
    st.subheader("📋 Matriz de Compromisos Kaizen (Evidencias de Auditoría)")
    st.markdown("Ecosistema primario de seguimiento para los desvíos reales de las jefaturas:")

    if "db_plan_puro_19_v2" not in st.session_state or st.session_state.db_plan_puro_19_v2 is None:
        cods = ["", "1.1.1 SSI", "3.1.1 CSI", "1.1.1 SSI", "1.1.1 SSI", "1.2.2 KPIs", "6.1.1 USADOS", "4.3.1 ESTRUCTURA", "9.3.2 CAPACITACIÓN", "9.3.3 ROTACIÓN", "9.4.1 INSTALACIONES", "9.4.1 INSTALACIONES", "2.1.2 CRM", "2.1.2 CRM", "2.1.2 CRM", "3.5.2 AIRBAGS", "7.1.1 SEGUROS", "7.1.2 APP", "5.1.1 KINTO ONE"]
        secs = ["Coordinación", "Calidad", "Calidad", "Calidad", "Calidad", "Calidad", "Calidad", "RRHH", "RRHH", "RRHH", "Facilities", "Facilities", "CRM", "CRM", "CRM", "Posventa", "TCFA", "TCFA", "KINTO"]
        tems = ["Programa DEP", "Ventas - Kits", "Ventas - Showroom", "Ventas - Fidelidad", "Ventas - Mystery", "Ventas - KPIs", "Usados Certificados", "Estructura TPA", "Capacitación TPA", "Rotación Personal", "Las Lajitas", "Reformas Salta", "Lista de Espera", "Tiempos Salesforce", "Limpieza Sistema", "Campañas Seguridad", "Cartera Seguros", "Servicios Conectados", "Gestión Siniestros"]
        sits = ["Desvinculación", "Falta kit obsequio", "Showroom sin insumos", "Baja tasa encuesta", "Desvíos blandos", "Falta visibilidad", "Estándar flojo UCT", "Sobrecarga admin", "Riesgo al cierre YTD", "Inestabilidad nómina", "Obras pendientes 2025", "Pendiente PN 2026", "Boletos estancados", "Demoras atención", "Boletos vencidos", "Baja tasa contacto", "Desvío pólizas", "Baja activación app", "Flujos sueltos One"]
        accs = ["Tablero único de control, calendario de vencimientos y evidencias transversales", "Kits de seguridad como obsequio de Autolux en las entregas de unidades", "Compra de café, termos, etc. Para la sala de espera de clientes", "Campaña de fidelización con sorteos activos en encuestas de la red", "Implementación obligatoria de auditorías mystery shopper en salones", "Desarrollo de un tablero único de control de KPIs operativos centrales", "Reorganización completa de toma, entrega y venta de unidades UCT", "Incorporación de 2 colaboradores administrativos para el área de planes", "Plan de seguimiento semestral obligatorio junto a Recursos Humanos", "Control y estabilización de la nómina de personal técnico de taller", "Negociación con fieldman TASA sobre obras no hechas planteadas 2025", "Planificar reformas de Chapa, Pintura y traslado físico de lavaderos", "Seguimiento diario con foco crítico a cierre de mes en carpetas", "Garantizar atención de prospectos digitales en menos de 2 horas en CRM", "Eliminación activa de boletos vencidos sin actividad comercial en sistema", "Citaciones masivas Airbags ABI 414/415 para subir de escalón", "Revisar el método de cálculo para crecimiento de pólizas comerciales", "Seguimiento focalizado en revendedores y empresas para la activación app", "Revisar proceso de seguimiento junto al área de Posventa de flota"]
        resps = ["Alejandro López", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Pablo Carrizo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Daniel Colque", "Daniel Colque", "Alfredo Aguilar", "Lucía de los Ríos", "Lucía de los Ríos", "Daniel Colque", "Lucía de los Ríos", "Romina R.", "Aaron Martearena"]
        rows = [[i+1, cods[i], secs[i], tems[i], sits[i], accs[i], "ALTA", "Evidencia", resps[i], "", "", "EN PROCESO", 0.0] for i in range(19)]
        st.session_state.db_plan_puro_19_v2 = pd.DataFrame(rows, columns=["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "Objetivo Simulación (%)"])

    df_ed_1 = st.data_editor(st.session_state.db_plan_puro_19_v2, use_container_width=True, key="grilla1_oficial_v4", hide_index=True, column_config={"#": st.column_config.NumberColumn(disabled=True), "Código Auditoría Manual": st.column_config.TextColumn(disabled=True), "Gerencia / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True), "Situación actual": st.column_config.TextColumn(disabled=True), "Acción Correctiva": st.column_config.TextColumn(disabled=True), "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador / Entregable": st.column_config.TextColumn(disabled=True), "Responsable": st.column_config.TextColumn(disabled=True), "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"]), "Objetivo Simulación (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.1f%%")})

    st.markdown("---")
    st.subheader("🚀 Ampliación de Simulación Estratégica (Para alcanzar el Puesto 1)")
    if "db_ampliacion_2_limpia" not in st.session_state or st.session_state.db_ampliacion_2_limpia is None:
        rows_a = [[1, "1.3.1 ESPECIALES", "Comercial", "Ventas Especiales", "Brecha corporativa", "Plan de reactivación de licitaciones corporativas", "ALTA", "Evidencia", "Alfredo Aguilar", "", "", "EN PROCESO", 0.0], [2, "9.6.1 ESG RED", "Dirección", "Sustentabilidad ESG", "Bajo score social", "Desarrollo de bitácora Kaizen ambiental", "ALTA", "Evidencia", "Alejandro López", "", "", "EN PROCESO", 0.0]]
        st.session_state.db_ampliacion_2_limpia = pd.DataFrame(rows_a, columns=["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "Objetivo Simulación (%)"])

    df_ed_2 = st.data_editor(st.session_state.db_ampliacion_2_limpia, use_container_width=True, key="grilla2_clean_v4", hide_index=True, column_config={"#": st.column_config.NumberColumn(disabled=True), "Código Auditoría Manual": st.column_config.TextColumn(disabled=True), "Gerencia / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True), "Situación actual": st.column_config.TextColumn(disabled=True), "Acción Correctiva": st.column_config.TextColumn(disabled=True), "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador / Entregable": st.column_config.TextColumn(disabled=True), "Responsable": st.column_config.TextColumn(disabled=True), "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"]), "Objetivo Simulación (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.1f%%")})

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("🧮 Simular e Impactar Dashboard"):
            st.session_state.db_plan_puro_19_v2 = df_ed_1
            st.session_state.db_ampliacion_2_limpia = df_ed_2
            for _, r in df_ed_1.iterrows():
                tg = r["Objetivo Simulación (%)"]
                if tg > 0:
                    cod, ger = str(r["Código Auditoría Manual"]), str(r["Gerencia / Sector"])
                    if "1.1.1" in cod or "Ventas" in ger: st.session_state.sim_pilar_ventas = tg
                    elif "3.5.2" in cod or "Posventa" in ger: st.session_state.sim_pilar_posventa = tg
                    elif "4.3.1" in cod: st.session_state.sim_pilar_tpa = tg
                    elif "5.1.1" in cod: st.session_state.sim_pilar_kinto = tg
                    elif "7.1.1" in cod: st.session_state.sim_pilar_tcfa = tg
                    elif "6.1.1" in cod: st.session_state.sim_pilar_usados = tg
                    elif "9.3.2" in cod or "9.3.3" in cod or "9.4.1" in cod or "Facilities" in ger or "RRHH" in ger: st.session_state.sim_pilar_general = tg
            for _, r in df_ed_2.iterrows():
                tg = r["Objetivo Simulación (%)"]
                if tg > 0:
                    cod = str(r["Código Auditoría Manual"])
                    if "1.3.1" in cod: st.session_state.sim_pilar_especiales = tg
                    elif "9.6.1" in cod: st.session_state.sim_pilar_esg = tg
            st.success("🎉 Simulación procesada.")
            st.rerun()
            
    with c_btn2:
        if st.button("🧹 Limpiar Simulación"):
            for k in ["sim_pilar_ventas", "sim_pilar_posventa", "sim_pilar_tpa", "sim_pilar_kinto", "sim_pilar_tcfa", "sim_pilar_general", "sim_pilar_especiales", "sim_pilar_usados", "sim_pilar_esg", "db_plan_puro_19_v2", "db_ampliacion_2_limpia"]: 
                if k in st.session_state: st.session_state[k] = None
            for ek in ["emt_a", "emt_b", "emt_c", "emt_d", "emt_e", "emt_f", "emt_g", "emt_h", "emt_i"]: st.session_state[ek] = 100
            st.success("🧹 Reset completado.")
            st.rerun()

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.db_plan_puro_19_v2.to_excel(writer, sheet_name='Plan de Accion Oficial', index=False)
        st.session_state.db_ampliacion_2_limpia.to_excel(writer, sheet_name='Ampliacion DEP', index=False)
    st.download_button(label="📥 Descargar Agenda en Excel", data=buffer.getvalue(), file_name="Plan_de_Accion_Oficial_Autolux.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
