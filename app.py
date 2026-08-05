import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión Integral", layout="wide", page_icon="🚗")
st.title("🚗 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Ecosistema Sincronizado - Datos Oficiales e Informe de Calidad de la Red TASA")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL: CONTROL DE RIESGOS PENALIDADES DE CAMPO
st.sidebar.header("🚨 Zona de Control de Riesgos")
if st.session_state.reestablecer:
    penalidad_fp = st.sidebar.toggle("Fair Play Detectado (-10 pts Global)", value=False, key="fp_real")
    penalidad_mov = st.sidebar.toggle("Falta Certificación Movilidad (-5.0 pts Ventas)", value=False, key="mov_real")
    visitas_fm = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fp = st.sidebar.toggle("Fair Play Detectado (-10 pts Global)", value=False)
    penalidad_mov = st.sidebar.toggle("Falta Certificación Movilidad (-5.0 pts Ventas)", value=False)
    visitas_fm = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85)

# Lógica e Impactos de Penalidades del Manual TASA
puntos_a_restar_global = 10.0 if penalidad_fp else 0.0
castigo_posventa_fieldman = 40.0 if visitas_fm < 85 else 0.0

if visitas_fm < 85: 
    st.sidebar.error("❌ Penalidad Posventa Activa (-40% en Score del área por Pág. 40).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman a salvo (≥85%).")

if st.sidebar.button("🔄 Restablecer Valores Oficiales de Junio"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. BASE DE DATOS ESTRATÉGICA EXTRACTADA DIRECTAMENTE DEL POWER BI TOYOTA
base_ventas_lux = 55.7 if not penalidad_mov else (55.7 - 5.0)
base_posventa_lux = 91.7 - (91.7 * (castigo_posventa_fieldman / 100))

data_competitiva = {
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Autolux (LUX) - Puesto 24": [base_ventas_lux, 49.0, base_posventa_lux, 72.8, 35.8, 75.8, 73.0, 25.0, 67.6],
    "DPQ - Puesto 5": [72.3, 55.0, 91.0, 85.0, 68.5, 78.0, 88.0, 25.0, 72.3],
    "GON - Puesto 10": [68.0, 50.0, 88.5, 71.0, 65.2, 74.0, 79.0, 26.0, 69.8]
}
df_bench = pd.DataFrame(data_competitiva)

# Score Global Base de Autolux (62.0% Oficial a Junio)
score_global_final = 62.0 - puntos_a_restar_global
if penalidad_mov:
    score_global_final -= 1.1

# Cálculo Dinámico y Exacto del Ranking General
if score_global_final == 62.0:
    puesto_calculado = 24
elif score_global_final > 62.0:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(1, puesto_calculado)
else:
    puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
    puesto_calculado = min(43, puesto_calculado)

# 4. CAPA DE ENRUTAMIENTO POR PESTAÑAS (3 TABS DEFINIDOS)
tab_dashboard, tab_calidad, tab_plan = st.tabs(["📊 Dashboard del Dealer", "🕵️ Análisis de Calidad por Sucursal", "📋 Plan de Acción Interactiva"])
with tab_dashboard:
    simulado_score = st.session_state.get("score_simulado_actual", score_global_final)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%", delta=f"{simulado_score - score_global_final:+.1f}% Simulando Target" if simulado_score > score_global_final else None)
    with col2: st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🏆" if puesto_calculado <= 24 else f"Puesto {puesto_calculado} 🚨")
    with col3: st.metric("Pilar Posventa Real", f"{base_posventa_lux:.1f}%")

    # Gráfico 1 - Solo Unidades Operativas de Negocio
    st.subheader("🏁 Desempeño Operativo por Unidades de Negocio (Excluyendo General)")
    df_operativo = df_bench[df_bench["Área"] != "General"]
    df_melted_op = df_operativo.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_op = px.bar(
        df_melted_op, x="Área", y="Cumplimiento %", color="Concesionario", barmode="group", text_auto=".1f",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#d62728", "DPQ - Puesto 5": "#1f77b4", "GON - Puesto 10": "#7f7f7f"}
    )
    fig_op.update_layout(xaxis_title="Unidad / Canal Operativo", yaxis_title="Efectividad %")
    st.plotly_chart(fig_op, use_container_width=True)

    # Gráfico 2 - AJUSTADO TERMINOLOGÍA: Reemplazada la palabra Campeonato por Consolidado RED
    st.subheader("🏆 Posicionamiento Estratégico: Resultado General Corporativo")
    df_general = df_bench[df_bench["Área"] == "General"]
    df_melted_gen = df_general.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    
    fig_gen = px.bar(
        df_melted_gen, x="Concesionario", y="Cumplimiento %", color="Concesionario", text_auto=".1f",
        title="Resultado Consolidado RED - Evaluación DEP Junio 2026",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#990000", "DPQ - Puesto 5": "#4A7ebb", "GON - Puesto 10": "#A6A6A6"}
    )
    fig_gen.update_layout(showlegend=False, yaxis=dict(range=[0, 100]), xaxis_title="Dealer Evaluado", yaxis_title="Score Global %")
    st.plotly_chart(fig_gen, use_container_width=True)

    # Checklist Completo EMT y su simulador
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
    
    # SOLUCIÓN DEFINITIVA SINTAXIS: Se inyectaron los datos fijos de forma directa en las listas sin diccionarios vacíos
    df_p = pd.DataFrame()
    df_p["Categoría"] = ["Demoras y puntualidad", "Comunicación y seguimiento", "Administración y documentación", "Cortesías y obsequios", "Atención y actitud", "Instalaciones y comodidad", "Preparación y accesorios", "Explicación del vehículo", "Protocolo y personalización", "Producto o marca"]
    df_p["Jujuy_Menciones"] = [26, 14, 8, 5, 4, 3, 3, 2, 1, 1]
    df_p["Salta_Menciones"] = [22, 15, 9, 12, 6, 8, 5, 4, 4, 4]
    df_p["Tartagal_Menciones"] = [2, 1, 2, 2, 0, 3, 1, 0, 0, 0]

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
        yaxis=dict(title="Número de Quejas (Cantidad)"), yaxis2=dict(title="Porcentaje Acumulado %", overlaying="y", side="right", range=[0, 105]),
        legend=dict(orientation="h", yanchor="top", y=-0.45, xanchor="center", x=0.5), margin=dict(b=140), height=550
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown("### 💡 Diagnóstico Operativo Prioritario:")
    if sucursal == "Jujuy":
        st.warning("⚠️ **Jujuy (Foco Operaciones)**: Concentración en **Demoras y puntualidad** (36.6%) y **Comunicación** (19.7%). El plan de acción del sector de asesores debe atacar la velocidad en turnos.")
    elif sucursal == "Salta":
        st.warning("⚠️ **Salta (Foco Híbrido)**: Desvío compartido entre **Demoras** (24.7%) y **Cortesías / Obsequios** (13.5%). Vinculado directamente a reclamos por entrega de kits de seguridad.")
    else:
        st.warning("⚠️ **Tartagal (Foco Infraestructura)**: El principal desvío radica en **Instalaciones y comodidad** (27.3%), seguido equitativamente con un 18.2% por Demoras, Administración y Kits.")
with tab_plan:
    st.subheader("📋 Matriz de Compromisos Kaizen y Simulador de Impacto DEP")
    st.markdown("Establece los **Objetivos de Simulación** de forma manual para proyectar la recuperación del indicador global:")

    if "db_dep_simulador_v1" not in st.session_state:
        # Numeración oficial por capítulos y secciones regulatorias TASA, arrancando el Target de simulación manual en 0.0%
        data_rows = [
            [1, "1.5.1: CUMPLIMIENTO DE OBJ. ACUMULADOS DE VTAS HILUX, SW4, HIACE", "Coordinación", "Seguimiento Transversal", "Tableros desvinculados", "Centralizar tablero único", "ALTA", "Reporte online", "Alejandro López", "", "", "EN PROCESO", 0.0],
            [2, "3.2.4: MEJORA CONTINUA CSI EN SHOWROOM", "Calidad", "Kits de Seguridad", "Falta kit de obsequio", "Incorporar kits de seguridad de Autolux", "ALTA", "Remitos firmados", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [3, "3.2.4: MEJORA CONTINUA CSI EN SHOWROOM", "Calidad", "Módulos de Café", "Expendedoras retiradas", "Compra e instalación de módulos de café", "ALTA", "Factura de compra", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [4, "3.2.5: EVOLUCIÓN INDICADOR SSI GENERAL", "Calidad", "Fidelización", "Baja percepción", "Lanzar campaña de fidelización con sorteos", "ALTA", "Evolución score", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [5, "3.2.5: EVOLUCIÓN INDICADOR SSI GENERAL", "Calidad", "Auditoría Interna", "Desvíos blandos", "Implementar auditorías Mystery Shopper", "ALTA", "Reporte auditoría", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [6, "1.2.2: SEGUIMIENTO DE KPIs OPERATIVOS", "Calidad", "Tablero KPIs", "Falta visibilidad", "Desarrollar tablero de control operativo", "ALTA", "Dashboard operativo", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [7, "5.1.4: PROCESOS OPERATIVOS DE TALLER / ALISTAMIENTO", "Calidad", "Alistamiento UCT", "Demoras preparación", "Reorganizar preparación UCT", "ALTA", "Minuta de proceso", "Pablo Carrizo", "", "", "EN PROCESO", 0.0],
            [8, "2.4.1: INFRAESTRUCTURA Y RECURSOS EN CANALES OFICIALES", "RRHH", "Personal TPA", "Sobrecarga admin", "Incorporar 2 colaboradores para TPA", "ALTA", "Alta de nómina", "A. Di Costanzo", "", "", "EN PROCESO", 0.0],
            [9, "4.1.2: CERTIFICACIONES REQUERIDAS DE ASESORES Y TÉCNICOS", "RRHH", "Capacitación", "Certificaciones ok", "Ejecutar plan de capacitación semestral", "ALTA", "% de cumplimiento", "A. Di Costanzo", "", "", "EN PROCESO", 0.0],
            [10, "5.2.3: CLIMA LABORAL E ÍNDICE DE ROTACIÓN EN POSVENTA", "RRHH", "Ausentismo", "Fricciones taller", "Controlar índice de rotación en taller", "ALTA", "Reporte mensual", "A. Di Costanzo", "", "", "EN PROCESO", 0.0],
            [11, "1.4.2: SEGUIMIENTO DE COMPROMISOS Y AUDITORÍA DE CAMPO", "Facilities", "Obras Las Lajitas", "Riesgo penalidad", "Negociar reprogramación de obras", "ALTA", "Minuta fieldman", "Daniel Colque", "", "", "EN PROCESO", 0.0],
            [12, "1.4.2: SEGUIMIENTO DE COMPROMISOS Y AUDITORÍA DE CAMPO", "Facilities", "Sucursal Salta", "Adecuación edilicia", "Planificar adecuación edilicia Salta", "ALTA", "Plan aprobado", "Daniel Colque", "", "", "EN PROCESO", 0.0],
            [13, "2.1.2: PROCESAMIENTO Y GESTIÓN DE LEADS EN SALESFORCE", "CRM", "Salesforce", "Boletos estancados", "Control diario de asignación Salesforce", "ALTA", "Reporte CRM diario", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [14, "2.1.2: PROCESAMIENTO Y GESTIÓN DE LEADS EN SALESFORCE", "CRM", "Prospectos", "Demoras atención", "Responder prospectos digitales < 2 horas", "ALTA", "Dashboard Salesforce", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [15, "2.1.2: PROCESAMIENTO Y GESTIÓN DE LEADS EN SALESFORCE", "CRM", "Filtro Boletos", "Boletos vencidos", "Eliminar boletos vencidos sin actividad", "ALTA", "Auditoría sistema", "A. Aguilar", "", "", "EN PROCESO", 0.0],
            [16, "5.1.5: CUMPLIMIENTO DE CAMPAÑAS ESPECIALES DE AIRBAGS", "Posventa", "Campañas Airbags", "Baja tasa contacto", "Incrementar tasa contacto Airbags", "ALTA", "% avance campaña", "Daniel Colque", "", "", "EN PROCESO", 0.0],
            [17, "6.1.1: COBERTURA Y CRECIMIENTO EN PÓLIZAS DE SEGUROS", "TCFA y Seguros", "Método", "Desvío pólizas", "Revisar método analítico de pólizas", "ALTA", "Fórmula homologada", "L. de los Ríos", "", "", "EN PROCESO", 0.0],
            [18, "6.1.1: COBERTURA Y CRECIMIENTO EN PÓLIZAS DE SEGUROS", "TCFA y Seguros", "App Seguros", "Baja activación", "Campaña de activación de App Seguros", "ALTA", "Tasa activación", "L. de los Ríos", "", "", "EN PROCESO", 0.0],
            [19, "7.3.2: ESTÁNDAR OPERATIVO DE UNIDADES KINTO SHARE", "KINTO", "Siniestros One", "Flujos sueltos", "Rediseñar proceso de siniestros One", "ALTA", "Flujograma unificado", "Aaron Martearena", "", "", "EN PROCESO", 0.0]
        ]
        cols = ["#", "Código Auditoría Manual", "Gerencia / Sector", "Tema / Proyecto", "Situación actual", "Acción Correctiva", "Prioridad", "Indicador / Entregable", "Responsable", "Estimación de Cumplimiento", "Fecha Estimada Cumplimiento", "Estado", "Objetivo Simulación (%)"]
        st.session_state.db_dep_simulador_v1 = pd.DataFrame(data_rows, columns=cols)

    df_ed = st.data_editor(
        st.session_state.db_dep_simulador_v1, use_container_width=True, key="grilla_sim_v2", hide_index=True,
        column_config={
            "#": st.column_config.NumberColumn(disabled=True), "Código Auditoría Manual": st.column_config.TextColumn(disabled=True),
            "Gerencia / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True),
            "Situación actual": st.column_config.TextColumn(disabled=True), "Acción Correctiva": st.column_config.TextColumn(disabled=True),
            "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador / Entregable": st.column_config.TextColumn(disabled=True),
            "Responsable": st.column_config.TextColumn(disabled=True), "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"]),
            "Objetivo Simulación (%)": st.column_config.NumberColumn(min_value=0.0, max_value=100.0, format="%.1f%%"),
            "Estimación de Cumplimiento": st.column_config.TextColumn(), "Fecha Estimada Cumplimiento": st.column_config.TextColumn()
        }
    )

    if st.button("🧮 Simular y Guardar Objetivos Kaizen"):
        st.session_state.db_dep_simulador_v1 = df_ed
        df_activos = df_ed[df_ed["Objetivo Simulación (%)"] > 0]
        promedio_simulado = df_activos["Objetivo Simulación (%)"].mean() if not df_activos.empty else score_global_final
        st.session_state.score_simulado_actual = promedio_simulado
        st.success(f"🎉 Simulación guardada. Si los jefes alcanzan estos objetivos, el score global proyectado será del {promedio_simulado:.1f}%.")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.db_dep_simulador_v1.to_excel(writer, sheet_name='Plan de Accion', index=False)
        ws = writer.sheets['Plan de Accion']
        f_b = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        font_h = Font(name='Arial', size=10, bold=True, color="FFFFFF")
        font_b = Font(name='Arial', size=10, color="000000")
        bdr = Border(left=Side(style='thin', color='CCCCCC'), right=Side(style='thin', color='CCCCCC'), top=Side(style='thin', color='CCCCCC'), bottom=Side(style='thin', color='CCCCCC'))
        
        for c in range(1, len(st.session_state.db_dep_simulador_v1.columns) + 1):
            cell = ws.cell(row=1, column=c)
            cell.fill = f_b; cell.font = font_h; cell.border = bdr
        for r in range(2, len(st.session_state.db_dep_simulador_v1) + 2):
            for c in range(1, len(st.session_state.db_dep_simulador_v1.columns) + 1):
                cell = ws.cell(row=r, column=c)
                cell.font = font_b; cell.border = bdr
        for col_idx in range(1, len(st.session_state.db_dep_simulador_v1.columns) + 1):
            col_letter = get_column_letter(col_idx); m_len = 0
            for row_idx in range(1, len(st.session_state.db_dep_simulador_v1) + 2):
                val = ws.cell(row=row_idx, column=col_idx).value
                if val: m_len = max(m_len, len(str(val)))
            ws.column_dimensions[col_letter].width = max(m_len + 3, 11)

    st.download_button(label="📥 Descargar Agenda de Seguimiento Formateada (Excel)", data=buffer.getvalue(), file_name="Plan_de_Accion_Saneado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
