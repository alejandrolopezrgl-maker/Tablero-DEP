import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

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

# INICIALIZACIÓN LIMITADA: Si no existe simulación previa, arranca estrictamente en None
if "sim_pilar_ventas" not in st.session_state: st.session_state.sim_pilar_ventas = None
if "sim_pilar_posventa" not in st.session_state: st.session_state.sim_pilar_posventa = None
if "sim_pilar_tpa" not in st.session_state: st.session_state.sim_pilar_tpa = None
if "sim_pilar_kinto" not in st.session_state: st.session_state.sim_pilar_kinto = None
if "sim_pilar_tcfa" not in st.session_state: st.session_state.sim_pilar_tcfa = None
if "sim_pilar_general" not in st.session_state: st.session_state.sim_pilar_general = None

v_simulada = st.session_state.sim_pilar_ventas if st.session_state.sim_pilar_ventas is not None else base_ventas_lux
p_simulada = st.session_state.sim_pilar_posventa if st.session_state.sim_pilar_posventa is not None else base_posventa_lux
tpa_simulada = st.session_state.sim_pilar_tpa if st.session_state.sim_pilar_tpa is not None else 72.8
kinto_simulada = st.session_state.sim_pilar_kinto if st.session_state.sim_pilar_kinto is not None else 35.8
tcfa_simulada = st.session_state.sim_pilar_tcfa if st.session_state.sim_pilar_tcfa is not None else 73.0
g_simulada = st.session_state.sim_pilar_general if st.session_state.sim_pilar_general is not None else 65.6

# 4. FÓRMULA DE PROYECCIÓN DEL SCORE GLOBAL CON LAS PONDERACIONES EXACTAS
if st.session_state.sim_pilar_ventas is None and st.session_state.sim_pilar_general is None:
    score_global_final = 62.0 - puntos_a_restar_global
    if penalidad_mov: score_global_final -= 1.1
else:
    score_global_final = (
        (p_simulada * 0.27) + (v_simulada * 0.22) + (g_simulada * 0.165) + 
        (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (75.8 * 0.06) + 
        (49.0 * 0.05) + (tcfa_simulada * 0.04) + (25.0 * 0.01)
    )
    score_global_final = score_global_final - puntos_a_restar_global
    if penalidad_mov: score_global_final -= 1.1

# DATAFRAME OPERATIVO CORREGIDO CON LOS PORCENTAJES DE TU CAPTURA
data_operativa = {
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "GENERAL"],
    "Autolux (LUX)": [v_simulada, 49.0, p_simulada, tpa_simulada, kinto_simulada, 75.8, tcfa_simulada, 25.0, g_simulada],
    "DPQ - Puesto 5": [72.3, 55.0, 91.0, 85.0, 68.5, 78.0, 88.0, 25.0, 59.8],
    "GON - Puesto 10": [68.0, 50.0, 88.5, 71.0, 65.2, 74.0, 79.0, 26.0, 79.0]
}
df_bench_op = pd.DataFrame(data_operativa)

# DATAFRAME EXCLUSIVO PARA EL GRÁFICO DE PUESTO Y RANKING GLOBAL COMPARTIDO
data_ranking_global = {
    "Concesionario": ["DPQ - Puesto 5", "GON - Puesto 10", "Autolux (LUX) - Puesto 24"],
    "Porcentaje DEP Global": [72.3, 69.8, score_global_final]
}
df_bench_ranking = pd.DataFrame(data_ranking_global)

# MOTOR DE RANKING ELÁSTICO RED
if score_global_final <= 62.0:
    puesto_calculado = 24
elif score_global_final >= 72.3:
    puesto_calculado = 5
else:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(5, min(24, puesto_calculado))

if st.sidebar.button("🔄 Restablecer Valores Oficiales", key="btn_reset_lateral"):
    st.session_state.sim_pilar_ventas = None
    st.session_state.sim_pilar_posventa = None
    st.session_state.sim_pilar_tpa = None
    st.session_state.sim_pilar_kinto = None
    st.session_state.sim_pilar_tcfa = None
    st.session_state.sim_pilar_general = None
    st.session_state.reestablecer = True
    st.rerun()

tab_dashboard, tab_calidad, tab_plan = st.tabs(["📊 Dashboard del Dealer", "🕵️ Análisis de Calidad por Sucursal", "📋 Plan de Acción Interactiva"])
with tab_dashboard:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Cumplimiento DEP Score Global", f"{score_global_final:.1f}%")
    with col2: 
        if puesto_calculado < 24:
            st.metric("Ranking Proyectado Red", f"Puesto {puesto_calculado} 🏆", delta=f"¡Subiendo {24 - puesto_calculado} puestos!")
        else:
            st.metric("Ranking General Red", f"Puesto 24 🚗", help="Posición base oficial de Autolux")
    with col3: st.metric("Pilar GENERAL Proyectado", f"{g_simulada:.1f}%")

    # GRÁFICO 1 CORREGIDO: Se inyectó manualmente la expresión del eje Y [0, 100]
    st.subheader("🏁 Desempeño Operativo por Unidades de Negocio (Incluyendo Pilar GENERAL)")
    df_melted_op = df_bench_op.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_op = px.bar(
        df_melted_op, x="Área", y="Cumplimiento %", color="Concesionario", barmode="group", text_auto=".1f",
        color_discrete_map={"Autolux (LUX)": "#d62728", "DPQ - Puesto 5": "#1f77b4", "GON - Puesto 10": "#7f7f7f"}
    )
    fig_op.update_layout(xaxis_title="Eje del Concesionario / Unidad Operativa", yaxis_title="Efectividad %", yaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_op, use_container_width=True)

    # GRÁFICO 2 CORREGIDO: Se inyectó manualmente la expresión del eje Y [0, 100]
    st.subheader("🏆 Posicionamiento Estratégico: Resultado Consolidado RED")
    fig_gen = px.bar(
        df_bench_ranking, x="Concesionario", y="Porcentaje DEP Global", color="Concesionario", text_auto=".1f",
        title="Evaluación DEP Acumulada a Junio - Posición y Porcentaje",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#990000", "DPQ - Puesto 5": "#4A7ebb", "GON - Puesto 10": "#A6A6A6"}
    )
    fig_gen.update_layout(showlegend=False, yaxis=dict(range=[0, 100]), xaxis_title="Dealer Evaluado", yaxis_title="Score Global %")
    st.plotly_chart(fig_gen, use_container_width=True)

    # Checklist de Auditoría Interna: Estilo de Movilidad Toyota (EMT)
    st.divider()
    st.subheader("📝 Checklist de Auditoría Interna: Estilo de Movilidad Toyota (EMT)")
    col_em1, col_em2, col_em3 = st.columns(3)
    with col_em1:
        acu_a = st.slider("A: Estructura Central (100)", 0, 100, 100)
        acu_b = st.slider("B: Servicio al Cliente (100)", 0, 100, 100)
        acu_c = st.slider("C: Kinto Movilidad (100)", 0, 100, 100)
    with col_em2:
        acu_d = st.slider("D: Club Toyota (100)", 0, 100, 100)
        acu_e = st.slider("E: Toyota Plan de Ahorro (100)", 0, 100, 100, key="slider_tpa_dash_v5")
        acu_f = st.slider("F: Toyota Financial Services (100)", 0, 100, 100)
    with col_em3:
        acu_g = st.slider("G: Vehículos Usados (100)", 0, 100, 100)
        acu_h = st.slider("H: Canal Convencional (100)", 0, 100, 100)
        acu_i = st.slider("I: Services Conectados (100)", 0, 100, 100)
    score_total_emt = acu_a + acu_b + acu_c + acu_d + acu_e + acu_f + acu_g + acu_h + acu_i
    st.success(f"🎉 Estándar EMT Asegurado: {score_total_emt} / 900 puntos ({(score_total_emt / 900.0) * 100:.1f}%).")

with tab_calidad:
    st.subheader("🕵️ Informe Clínico de Calidad: Análisis de Pareto por Sucursal")
    df_p = pd.DataFrame()
    df_p["Categoría"] = ["Demoras y puntualidad", "Comunicación y seguimiento", "Administración y documentación", "Cortesías y obsequios", "Atención y actitud", "Instalaciones y comodidad", "Preparación y accesorios", "Explicación del vehículo", "Protocolo y personalización", "Producto o marca"]
    df_p["Jujuy_Menciones"] = [42, 28, 19, 14, 11, 8, 5, 3, 2, 1]
    df_p["Salta_Menciones"] = [55, 34, 22, 18, 12, 9, 6, 4, 2, 1]
    df_p["Tartagal_Menciones"] = [15, 11, 8, 5, 4, 3, 2, 1, 1, 0]

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
    fig_pareto.update_layout(
        title=f"Diagrama de Pareto de Calidad - Sucursal {sucursal}", xaxis=dict(title="Categorías Críticas", tickangle=-25),
        yaxis=dict(title="Número de Quejas (Cantidad)"), yaxis2=dict(title="Porcentaje Acumulado %", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", yanchor="top", y=-0.45, xanchor="center", x=0.5), margin=dict(b=140), height=550
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
with tab_plan:
    st.subheader("📋 Matriz de Compromisos Kaizen y Simulador de Impacto DEP")
    st.markdown("Carga los objetivos manuales de los jefes para ver el cambio elástico en el Dashboard:")

    if "db_dep_final_oficial_2026_v8" not in st.session_state:
        cods = ["", "1.1.1 SSI (Pág. 5)", "3.1.1 CSI (Pág. 21)", "1.1.1 SSI (Pág. 5)", "1.1.1 SSI (Pág. 5)", "1.2.2 KPIs (Pág. 5)", "6.1.1: USADOS (Pág. 63)", "4.3.1 Estructura (Pág. 41)", "9.3.2 CAPACITACIÓN (Pág. 76)", "9.3.3 ROTACIÓN (Pág. 76)", "9.4.1 INSTALACIONES (Pág. 76)", "9.4.1 INSTALACIONES (Pág. 76)", "2.1.2 CRM (Pág. 5)", "2.1.2 CRM (Pág. 5)", "2.1.2 CRM (Pág. 5)", "3.5.2 Airbags (Pág. 21)", "7.1.1: SEGUROS (Pág. 69)", "7.1.2: APP (Pág. 69)", "5.1.1: KINTO ONE (Pág. 50)"]
        secs = ["Coordinación", "Calidad", "Calidad", "Calidad", "Calidad", "Calidad", "Calidad", "RRHH", "RRHH", "RRHH", "Facilities", "Facilities", "CRM", "CRM", "CRM", "Posventa", "TCFA", "TCFA", "KINTO"]
        tems = ["Programa DEP", "Ventas - Kits", "Ventas - Showroom", "Ventas - Fidelidad", "Ventas - Mystery", "Ventas - KPIs", "Usados Certificados", "Estructura TPA", "Capacitación TPA", "Rotación Personal", "Las Lajitas", "Reformas Salta", "Lista de Espera", "Tiempos Salesforce", "Limpieza Sistema", "Campañas Seguridad", "Cartera Seguros", "Servicios Conectados", "Gestión Siniestros"]
        sits = ["Desvinculación", "Falta kit obsequio", "Showroom sin insumos", "Baja tasa encuesta", "Desvíos blandos", "Falta visibilidad", "Estándar flojo UCT", "Sobrecarga admin", "Riesgo al cierre YTD", "Inestabilidad nómina", "Obras pendientes 2025", "Pendiente PN 2026", "Boletos estancados", "Demoras atención", "Boletos vencidos", "Baja tasa contacto", "Desvío pólizas", "Baja activación app", "Flujos sueltos One"]
        accs = ["Tablero único de control, calendario de vencimientos y evidencias transversales", "Kits de seguridad como obsequio de Autolux en las entregas de unidades", "Compra de café, termos, etc. Para la sala de espera de clientes", "Campaña de fidelización con sorteos activos en encuestas de la red", "Implementación obligatoria de auditorías mystery shopper en salones", "Desarrollo de un tablero único de control de KPIs operativos centrales", "Reorganización completa de toma, entrega y venta de unidades UCT", "Incorporación de 2 colaboradores administrativos para el área de planes", "Plan de seguimiento semestral obligatorio junto a Recursos Humanos", "Control y estabilización de la nómina de personal técnico de taller", "Negociación con fieldman TASA sobre obras no hechas planteadas 2025", "Planificar reformas de Chapa, Pintura y traslado físico de lavaderos", "Seguimiento diario con foco crítico a cierre de mes en carpetas", "Garantizar atención de prospectos digitales en menos de 2 horas en CRM", "Eliminación activa de boletos vencidos sin actividad comercial en sistema", "Citaciones masivas Airbags ABI 414/415 para subir de escalón", "Revisar el método de cálculo para crecimiento de pólizas comerciales", "Seguimiento focalizado en revendedores y empresas para la activación app", "Revisar proceso de seguimiento junto al área de Posventa de flota"]
        resps = ["Alejandro López", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Pablo Carrizo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Daniel Colque", "Daniel Colque", "Alfredo Aguilar", "Lucía de los Ríos", "Lucía de los Ríos", "Daniel Colque", "Lucía de los Ríos", "Romina R.", "Aaron Martearena"]
        
        rows = [[i+1, cods[i], secs[i], tems[i], sits[i], accs[i], "ALTA", "Evidencia", resps[i], "", "", "EN PROCESO", 0.0] for i in range(19)]
        st.session_state.db_dep_final_oficial_2026_v8 = pd.DataFrame(rows, columns=["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "Objetivo Simulación (%)"])

    df_ed = st.data_editor(
        st.session_state.db_dep_final_oficial_2026_v8, use_container_width=True, key="grilla_dep_oficial_final_8", hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(disabled=True), "Código Auditoría Manual": st.column_config.TextColumn(disabled=True), "Gerencia / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True), "Situación actual": st.column_config.TextColumn(disabled=True), "Acción Correctiva": st.column_config.TextColumn(disabled=True), "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador / Entregable": st.column_config.TextColumn(disabled=True), "Responsable": st.column_config.TextColumn(disabled=True), "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"]), "Objetivo Simulación (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.1f%%"),
            "Estimación de Cumplimiento": st.column_config.TextColumn(), "Fecha Estimada Cumplimiento": st.column_config.TextColumn()
        }
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🧮 Simular e Impactar Dashboard"):
            st.session_state.db_dep_final_oficial_2026_v8 = df_ed
            for _, r in df_ed.iterrows():
                tg = r["Objetivo Simulación (%)"]
                if tg > 0:
                    cod = str(r["Código Auditoría Manual"])
                    ger = str(r["Gerencia / Sector"])
                    if "1.1.1" in cod or "Ventas" in ger: st.session_state.sim_pilar_ventas = tg
                    elif "3.5.2" in cod or "Posventa" in ger: st.session_state.sim_pilar_posventa = tg
                    elif "4.3.1" in cod: st.session_state.sim_pilar_tpa = tg
                    elif "5.1.1" in cod: st.session_state.sim_pilar_kinto = tg
                    elif "6.1.1" in cod: st.session_state.sim_pilar_tcfa = tg
                    elif "9.3.2" in cod or "9.3.3" in cod or "9.4.1" in cod or "Facilities" in ger or "RRHH" in ger: st.session_state.sim_pilar_general = tg
            st.success("🎉 Simulación completada. Gráficos y Ranking actualizados de forma elástica.")
            st.rerun()
            
    with col_btn2:
        if st.button("🧹 Limpiar Simulación"):
            st.session_state.sim_pilar_ventas = None
            st.session_state.sim_pilar_posventa = None
            st.session_state.sim_pilar_tpa = None
            st.session_state.sim_pilar_kinto = None
            st.session_state.sim_pilar_tcfa = None
            st.session_state.sim_pilar_general = None
            if "db_dep_final_oficial_2026_v8" in st.session_state:
                del st.session_state.db_dep_final_oficial_2026_v8
            st.success("🧹 Valores de simulación limpiados correctamente.")
            st.rerun()

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.db_dep_final_oficial_2026_v8.to_excel(writer, sheet_name='Plan de Accion', index=False)
        ws = writer.sheets['Plan de Accion']
        f_b = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        font_h = Font(name='Arial', size=10, bold=True, color="FFFFFF")
        font_b = Font(name='Arial', size=10, color="000000")
        bdr = Border(left=Side(style='thin', color='CCCCCC'), right=Side(style='thin', color='CCCCCC'), top=Side(style='thin', color='CCCCCC'), bottom=Side(style='thin', color='CCCCCC'))
        
        for c in range(1, len(st.session_state.db_dep_final_oficial_2026_v8.columns) + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill = f_b; cell.font = font_h; cell.border = bdr
        for r in range(2, len(st.session_state.db_dep_final_oficial_2026_v8) + 2):
            for c in range(1, len(st.session_state.db_dep_final_oficial_2026_v8.columns) + 1):
                cell = ws.cell(row=r, column=c)
                cell.font = font_b; cell.border = bdr
        for col_idx in range(1, len(st.session_state.db_dep_final_oficial_2026_v8.columns) + 1):
            col_letter = get_column_letter(col_idx); m_len = 0
            for row_idx in range(1, len(st.session_state.db_dep_final_oficial_2026_v8) + 2):
                val = ws.cell(row=row_idx, column=col_idx).value
                if val: m_len = max(m_len, len(str(val)))
            ws.column_dimensions[col_letter].width = max(m_len + 3, 11)

    st.download_button(label="📥 Descargar Agenda de Seguimiento Formateada (Excel)", data=buffer.getvalue(), file_name="Plan_de_Accion_Oficial_Autolux.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
