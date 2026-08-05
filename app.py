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
    penalidad_mov = st.sidebar.toggle("Falta Movilidad (-5.0 pts Ventas)", value=False, key="mov_real")
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

if st.sidebar.button("🔄 Restablecer Valores Oficiales"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. BASE DE DATOS ESTRATÉGICA EXTRACTADA DIRECTAMENTE DEL POWER BI TOYOTA
base_ventas_lux = 55.7 if not penalidad_mov else (55.7 - 5.0)
base_posventa_lux = 91.7 - (91.7 * (castigo_posventa_fieldman / 100))

# CAPTURA DE VARIABLES SIMULADAS VIVAS CON CONEXIÓN INTER-TAB (ESTADO PERSISTENTE)
v_simulada = st.session_state.get("sim_pilar_ventas", base_ventas_lux)
p_simulada = st.session_state.get("sim_pilar_posventa", base_posventa_lux)
tpa_simulada = st.session_state.get("sim_pilar_tpa", 72.8)
kinto_simulada = st.session_state.get("sim_pilar_kinto", 35.8)
tcfa_simulada = st.session_state.get("sim_pilar_tcfa", 73.0)

# 4. FÓRMULA MATEMÁTICA CON LAS PONDERACIONES OFICIALES DEL MANUAL (PÁG 1)
# Pesos: Posventa 27%, Ventas 22%, General 20%, TPA 9%, Kinto 6%, Usados 6%, Especiales 5%, TCFA 4%, ESG 1%
score_global_final = (
    (p_simulada * 0.27) + (v_simulada * 0.22) + (67.6 * 0.20) + 
    (tpa_simulada * 0.09) + (kinto_simulada * 0.06) + (75.8 * 0.06) + 
    (49.0 * 0.05) + (tcfa_simulada * 0.04) + (25.0 * 0.01)
)
score_global_final = score_global_final - puntos_a_restar_global
if penalidad_mov:
    score_global_final -= 1.1

data_competitiva = {
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Autolux (LUX) - Puesto 24": [v_simulada, 49.0, p_simulada, tpa_simulada, kinto_simulada, 75.8, tcfa_simulada, 25.0, score_global_final],
    "DPQ - Puesto 5": [72.3, 55.0, 91.0, 85.0, 68.5, 78.0, 88.0, 25.0, 72.3],
    "GON - Puesto 10": [68.0, 50.0, 88.5, 71.0, 65.2, 74.0, 79.0, 26.0, 69.8]
}
df_bench = pd.DataFrame(data_competitiva)

# MOTOR DE RANKING ELÁSTICO: Responde directamente al impacto de la simulación
if score_global_final <= 62.0:
    puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
    puesto_calculado = min(43, puesto_calculado)
else:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(1, puesto_calculado)

tab_dashboard, tab_calidad, tab_plan = st.tabs(["📊 Dashboard del Dealer", "🕵️ Análisis de Calidad por Sucursal", "📋 Plan de Acción Interactiva"])
with tab_dashboard:
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Cumplimiento DEP General", f"{score_global_final:.1f}%")
    with col2: 
        if puesto_calculado < 24:
            st.metric("Ranking Proyectado", f"Puesto {puesto_calculado} 🏆", delta=f"¡Subiendo {24 - puesto_calculado} puestos!")
        else:
            st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🚨")
    with col3: st.metric("Pilar Posventa Proyectado", f"{p_simulada:.1f}%")

    st.subheader("🏁 Desempeño Operativo por Unidades de Negocio (Excluyendo General)")
    df_operativo = df_bench[df_bench["Área"] != "General"]
    df_melted_op = df_operativo.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_op = px.bar(
        df_melted_op, x="Área", y="Cumplimiento %", color="Concesionario", barmode="group", text_auto=".1f",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#d62728", "DPQ - Puesto 5": "#1f77b4", "GON - Puesto 10": "#7f7f7f"}
    )
    fig_op.update_layout(xaxis_title="Unidad / Canal Operativo", yaxis_title="Efectividad %")
    st.plotly_chart(fig_op, use_container_width=True)

    st.subheader("🏆 Posicionamiento Estratégico: Resultado General Corporativo")
    df_general = df_bench[df_bench["Área"] == "General"]
    df_melted_gen = df_general.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_gen = px.bar(
        df_melted_gen, x="Concesionario", y="Cumplimiento %", color="Concesionario", text_auto=".1f",
        title="Resultado Consolidado RED - Evaluación DEP Junio 2026",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#990000", "DPQ - Puesto 5": "#4A7ebb", "GON - Puesto 10": "#A6A6A6"}
    )
    fig_gen.update_layout(showlegend=False, yaxis=dict(range=), xaxis_title="Dealer Evaluado", yaxis_title="Score Global %")
    st.plotly_chart(fig_gen, use_container_width=True)

    st.divider()
    st.subheader("📝 Checklist de Auditoría Interna: Estilo de Movilidad Toyota (EMT)")
    col_em1, col_em2, col_em3 = st.columns(3)
    with col_em1:
        acu_a = st.slider("A: Estructura Central (100)", 0, 100, 100)
        acu_b = st.slider("B: Servicio al Cliente (100)", 0, 100, 100)
        acu_c = st.slider("C: Kinto Movilidad (100)", 0, 100, 100)
    with col_em2:
        acu_d = st.slider("D: Club Toyota (100)", 0, 100, 100)
        acu_e = st.slider("E: Toyota Plan de Ahorro (100)", 0, 100, 100, key="slider_tpa_dashboard")
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
    df_p["Jujuy_Menciones"] =
    df_p["Salta_Menciones"] =
    df_p["Tartagal_Menciones"] =

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
        yaxis=dict(title="Número de Quejas (Cantidad)"), yaxis2=dict(title="Porcentaje Acumulado %", overlaying="y", side="right", range=),
        legend=dict(orientation="h", yanchor="top", y=-0.45, xanchor="center", x=0.5), margin=dict(b=140), height=550
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
with tab_plan:
    st.subheader("📋 Matriz de Compromisos Kaizen y Simulador de Impacto DEP")
    st.markdown("Carga los objetivos manuales de los jefes para ver el cambio elástico en el Dashboard:")

    if "db_dep_final_oficial_2026" not in st.session_state:
        cods = ["", "1.1.1 SSI", "1.1.1 SSI", "1.1.1 SSI", "1.1.1 SSI", "1.2.2 KPIs", "UCT", "2.4.1 TPA", "4.1.2 TPA", "3.3.1 Rotación", "1.4.2 Obra", "1.4.2 Obra", "2.1.2 CRM", "2.1.2 CRM", "2.1.2 CRM", "3.5.2 Airbags", "6.1.1 TCFA", "6.1.1 TCFA", "7.3.2 KINTO"]
        secs = ["Coordinación", "Calidad", "Calidad", "Calidad", "Calidad", "Calidad", "Calidad", "RRHH", "RRHH", "RRHH", "Facilities", "Facilities", "CRM", "CRM", "CRM", "Posventa", "TCFA", "TCFA", "KINTO"]
        tems = ["Programa DEP", "Ventas - Kits", "Ventas - Showroom", "Ventas - Fidelidad", "Ventas - Mystery", "Ventas - KPIs", "Usados Certificados", "Estructura TPA", "Capacitación TPA", "Rotación Personal", "Las Lajitas", "Reformas Salta", "Lista de Espera", "Tiempos Salesforce", "Limpieza Sistema", "Campañas Seguridad", "Cartera Seguros", "Servicios Conectados", "Gestión Siniestros"]
        sits = ["Desvinculación", "Falta kit obsequio", "Showroom sin insumos", "Baja tasa encuesta", "Desvíos blandos", "Falta visibilidad", "Estándar flojo UCT", "Sobrecarga admin", "Riesgo al cierre YTD", "Inestabilidad nómina", "Obras pendientes 2025", "Pendiente PN 2026", "Boletos estancados", "Demoras atención", "Boletos vencidos", "Baja tasa contacto", "Desvío pólizas", "Baja activación app", "Flujos sueltos One"]
        accs = ["Tablero único de control, calendario de vencimientos y evidencias", "Kits de seguridad como obsequio de Autolux en las entregas", "Compra de café, termos, etc. Para la sala de espera", "Campaña de fidelización con sorteos activos en encuestas TASA", "Implementación obligatoria de auditorías mystery shopper", "Desarrollo de un tablero único de control de KPIs operativos", "Reorganización completa de toma, entrega y venta de unidades UCT", "Incorporación de 2 colaboradores administrativos", "Plan de seguimiento semestral obligatorio junto a RRHH", "Control y estabilización de la nómina de personal de taller", "Negociación con fieldman TASA sobre obras no hechas de 2025", "Planificar reformas de Chapa, Pintura y traslado de lavaderos", "Seguimiento diario con foco crítico a cierre de mes", "Garantizar atención de prospectos digitales en menos de 2 horas", "Eliminación activa de boletos vencidos sin actividad comercial", "Citaciones masivas Airbags ABI 414/415 para subir de escalón", "Revisar el método de cálculo para crecimiento de pólizas", "Seguimiento focalizado en revendedores y empresas para la app", "Revisar proceso de seguimiento junto al área de Posventa"]
        resps = ["Alejandro López", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Alfredo Aguilar", "Pablo Carrizo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Adrián Di Costanzo", "Daniel Colque", "Daniel Colque", "Alfredo Aguilar", "Lucía de los Ríos", "Lucía de los Ríos", "Daniel Colque", "Lucía de los Ríos", "Romina R.", "Aaron Martearena"]
        
        rows = [[i+1, cods[i], secs[i], tems[i], sits[i], accs[i], "ALTA", "Evidencia", resps[i], "", "", "EN PROCESO", 0.0] for i in range(19)]
        st.session_state.db_dep_final_oficial_2026 = pd.DataFrame(rows, columns=["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "Objetivo Simulación (%)"])

    df_ed = st.data_editor(
        st.session_state.db_dep_final_oficial_2026, use_container_width=True, key="grilla_dep_oficial_final_4", hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(disabled=True), "Código Auditoría Manual": st.column_config.TextColumn(disabled=True), "Gerencia / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True), "Situación actual": st.column_config.TextColumn(disabled=True), "Acción Correctiva": st.column_config.TextColumn(disabled=True), "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador / Entregable": st.column_config.TextColumn(disabled=True), "Responsable": st.column_config.TextColumn(disabled=True), "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"]), "Objetivo Simulación (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.1f%%"),
            "Estimación de Cumplimiento": st.column_config.TextColumn(), "Fecha Estimada Cumplimiento": st.column_config.TextColumn()
        }
    )

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🧮 Simular e Impactar Dashboard"):
            st.session_state.db_dep_final_oficial_2026 = df_ed
            for _, r in df_ed.iterrows():
                tg = r["Objetivo Simulación (%)"]
                if tg > 0:
                    cod = str(r["Código Auditoría Manual"])
                    ger = str(r["Gerencia / Sector"])
                    if "1.1.1" in cod or "Ventas" in ger: st.session_state.sim_pilar_ventas = tg
                    elif "3.5.2" in cod or "Posventa" in ger or "Facilities" in ger: st.session_state.sim_pilar_posventa = tg
                    elif "2.4.1" in cod or "RRHH" in ger: st.session_state.sim_pilar_tpa = tg
                    elif "7.3.2" in cod: st.session_state.sim_pilar_kinto = tg
                    elif "6.1.1" in cod: st.session_state.sim_pilar_tcfa = tg
            st.success("🎉 Simulación completada. Gráficos y Ranking actualizados en la pestaña 1.")
            st.rerun()
    with col_btn2:
        if st.button("🧹 Limpiar Simulación"):
            st.session_state.sim_pilar_ventas = base_ventas_lux
            st.session_state.sim_pilar_posventa = base_posventa_lux
            st.session_state.sim_pilar_tpa = 72.8; st.session_state.sim_pilar_kinto = 35.8; st.session_state.sim_pilar_tcfa = 73.0
            if "db_dep_final_oficial_2026" in st.session_state: del st.session_state.db_dep_final_oficial_2026
            st.success("🧹 Valores Kaizen restablecidos con éxito.")
            st.rerun()

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.db_dep_final_oficial_2026.to_excel(writer, sheet_name='Plan de Accion', index=False)
        ws = writer.sheets['Plan de Accion']
        f_b = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        font_h = Font(name='Arial', size=10, bold=True, color="FFFFFF")
        font_b = Font(name='Arial', size=10, color="000000")
        bdr = Border(left=Side(style='thin', color='CCCCCC'), right=Side(style='thin', color='CCCCCC'), top=Side(style='thin', color='CCCCCC'), bottom=Side(style='thin', color='CCCCCC'))
        
        for c in range(1, len(st.session_state.db_dep_final_oficial_2026.columns) + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill = f_b; cell.font = font_h; cell.border = bdr
        for r in range(2, len(st.session_state.db_dep_final_oficial_2026) + 2):
            for c in range(1, len(st.session_state.db_dep_final_oficial_2026.columns) + 1):
                cell = ws.cell(row=r, column=c)
                cell.font = font_b; cell.border = bdr
        for col_idx in range(1, len(st.session_state.db_dep_final_oficial_2026.columns) + 1):
            col_letter = get_column_letter(col_idx); m_len = 0
            for row_idx in range(1, len(st.session_state.db_dep_final_oficial_2026) + 2):
                val = ws.cell(row=row_idx, column=col_idx).value
                if val: m_len = max(m_len, len(str(val)))
            ws.column_dimensions[col_letter].width = max(m_len + 3, 11)

    st.download_button(label="📥 Descargar Agenda de Seguimiento Formateada (Excel)", data=buffer.getvalue(), file_name="Plan_de_Accion_Oficial_Autolux.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
