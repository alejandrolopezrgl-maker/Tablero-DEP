import streamlit as st
import pandas as pd
import plotly.express as px
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
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts Global)", value=False, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5.0 pts Ventas)", value=False, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts Global)", value=False)
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5.0 pts Ventas)", value=False)
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85)

# Lógica e Impactos de Penalidades del Manual
puntos_a_restar_global = 10.0 if penalidad_fair_play else 0.0
castigo_posventa_fieldman = 40.0 if visitas_fieldman < 85 else 0.0

if visitas_fieldman < 85: 
    st.sidebar.error("❌ Penalidad Posventa Activa (-40% en Score del área por Pág. 40).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman a salvo (≥85%).")

if st.sidebar.button("🔄 Restablecer Valores Oficiales de Junio"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. BASE DE DATOS ESTRATÉGICA EXTRACTADA DIRECTAMENTE DEL POWER BI TOYOTA
base_ventas_lux = 55.7 if not penalidad_movilidad else (55.7 - 5.0)
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
if penalidad_movilidad:
    score_global_final -= 1.1

# Cálculo Dinámico y Exacto del Ranking
if score_global_final == 62.0:
    puesto_calculado = 24
elif score_global_final > 62.0:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(1, puesto_calculado)
else:
    puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
    puesto_calculado = min(43, puesto_calculado)

# 4. CAPA DE ENRUTAMIENTO POR PESTAÑAS (3 TABS DEFINIDOS)
tab_dashboard, tab_calidad, tab_plan = st.tabs(["📊 Dashboard del Dealer", "🕵️ Análisis Clínico de Calidad (CSI/NPS)", "📋 Plan de Acción Interactiva"])
with tab_dashboard:
    # 5. PANEL EJECUTIVO DE MÉTRICAS SANEADO
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
    with col2: st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🏆" if puesto_calculado <= 24 else f"Puesto {puesto_calculado} 🚨", delta="Puesto 4 en TPA Red 🏆")
    with col3: st.metric("Pilar Posventa Real", f"{base_posventa_lux:.1f}%")

    # 6. VISUALIZACIÓN GRÁFICA COMPARATIVA POR UNIDADES DE NEGOCIO (ESTILO POWER BI)
    st.subheader("🏁 Cumplimiento por Áreas de Negocio: Autolux vs Lote Líder de la Red")
    df_melted = df_bench.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_bench = px.bar(
        df_melted, x="Área", y="Cumplimiento %", color="Concesionario",
        barmode="group", text_auto=".1f", title="Brecha de Desempeño por Unidades de Negocio",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#d62728", "DPQ - Puesto 5": "#1f77b4", "GON - Puesto 10": "#7f7f7f"}
    )
    fig_bench.update_layout(xaxis_title="Unidad / Canal", yaxis_title="Efectividad %")
    st.plotly_chart(fig_bench, use_container_width=True)

    # 7. AUDITORÍA INTERNA DE MOVIMIENTO TOYOTA (EMT)
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
        acu_i = st.slider("I: Servicios Conectados (100)", 0, 100, 100)
    score_total_emt = acu_a + acu_b + acu_c + acu_d + acu_e + acu_f + acu_g + acu_h + acu_i
    st.success(f"🎉 Estándar EMT Asegurado: {score_total_emt} / 900 puntos ({(score_total_emt / 900.0) * 100:.1f}%).")

with tab_calidad:
    st.subheader("🕵️ Informe Clínico sobre Desvíos de Calidad y Experiencia del Cliente")
    st.markdown("Análisis pormenorizado de los factores físicos e intangibles que impulsaron la caída en Calidad del **Puesto 8 al 39**.")
    
    col_pie_left, col_pie_right = st.columns([1.2, 1.0])
    with col_pie_left:
        df_quejas_sincronizado = pd.DataFrame({
            "Factor de Desvío": [
                "Falta de Kit de Seguridad (36%)", 
                "Falta de Presentes / Merchandising (20%)", 
                "Falta de Máquina de Café (16%)",
                "Seguimiento Post-Entrega / SSI (13%)",
                "Procesos Operativos de Taller / CSI (15%)"
            ], 
            "Impacto %": [36.0, 20.0, 16.0, 13.0, 15.0]
        })
        
        fig_pie_oficial = px.pie(
            df_quejas_sincronizado, values="Impacto %", names="Factor de Desvío",
            color_discrete_sequence=["#1F4E78", "#5B9BD5", "#A5D6A7", "#E57373", "#90A4AE"],
            title="Estructura de Impactos en Encuestas de Calidad (Base 100%)"
        )
        
        fig_pie_oficial.update_layout(
            height=500, margin=dict(l=10, r=10, t=50, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5)
        )
        fig_pie_oficial.update_traces(textinfo="value", textposition="inside")
        st.plotly_chart(fig_pie_oficial, use_container_width=True)
        
    with col_pie_right:
        st.info("💡 **Diagnóstico Raíz Saneado**: La caída se asocia a una percepción de *'pérdida de beneficios'* materiales en showroom y desvíos blandos en la atención y plazos de Posventa.")
        st.markdown("""
        ### 📋 Desglose Técnico de Desvíos de Calidad Observados:
        *   **Falta de Kit de Seguridad (36%)**: Los clientes manifiestan descontento severo porque el kit pasó a ser arancelado o no viene como 'obsequio' de cortesía corporativa al retirar el vehículo.
        *   **Falta de Presentes / Detalles de Marketing (20%)**: Menciones críticas asociadas a la falta de recuerdos o atenciones especiales (ej. llaveros o matafuegos) tras concretar una inversión 0km.
        *   **Falta de Máquina de Café (16%)**: Verbatines de Posventa. Califican de 'miserable' el retiro de la expendedora gratuita y la instalación de terminales chicas.
        *   **Seguimiento Post-Entrega SSI (13%)**: Ausencia de llamados comerciales de cortesía programados dentro de las 48 horas posteriores a la entrega física de la unidad.
        *   **Procesos Operativos de Taller / CSI (15%)**: Foco de fricción en la atención dura del taller. Concentrado en demoras en la promesa de entrega (5%), falta de claridad al explicar la factura (4%), trato frío en recepción (3%) y detalles de limpieza al devolver la unidad (3%).
        """)

    st.divider()
    st.subheader("💬 La Voz del Cliente (Verbatines de Auditoría TASA)")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.error("**Foco Entregas & Marketing (SSI)**\n* *'Me dan el auto y ya no te dan ni un miserable kit de seguridad.'*\n* *'En Salta cuando compré el Toyota Etios me regalaron heladera, kit, llavero y matafuegos. En Tartagal no me dieron ni un vaso de agua.'*\n* *'La vez pasada te daban una linterna buenísima, esta vez una planta.'*")
    with col_v2:
        st.error("**Foco Espera & Taller (CSI)**\n* *'SACARON LA MÁQUINA DE CAFÉ DEL LUGAR DE ESPERA, UNA ACTITUD TOTALMENTE MISERABLE.'*\n* *'Hay que esperar dos horas... ahora hay una máquina muy chica que nadie sabe usar, es tedioso, por el precio deberían dar como antes.'*")
with tab_plan:
    st.subheader("📋 Planilla de Seguimiento y Agenda de Compromisos DEP")
    st.markdown("Hacé **doble clic en cualquier celda** de las columnas libres para registrar comentarios y gestionar plazos reales:")

    if "db_final_dep_excel_v1" not in st.session_state:
        # Los 19 desvíos DEP mapeados estrictamente en la matriz de la foto
        data_rows = [
            [1, "14-jul", "Coordinación", "Seguimiento Transversal", "Tableros desvinculados", "Centralizar tablero único", "ALTA", "Reporte online", "Alejandro López", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Reportes transversales"],
            [2, "14-jul", "Calidad", "Kits de Seguridad", "Falta kit de obsequio", "Incorporar kits de seguridad de Autolux en cada entrega", "ALTA", "Remitos firmados", "A. Aguilar", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Validar stock central"],
            [3, "14-jul", "Calidad", "Módulos de Café", "Expendedoras retiradas", "Compra e instalación de módulos de café en showroom", "ALTA", "Factura de compra", "A. Aguilar", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Gestión salas de espera"],
            [4, "14-jul", "Calidad", "Fidelización", "Baja percepción", "Lanzar campaña de fidelización con sorteos activos", "ALTA", "Evolución score", "A. Aguilar", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Bases con Marketing"],
            [5, "14-jul", "Calidad", "Auditoría Interna", "Desvíos blandos", "Implementar auditorías internas Mystery Shopper", "ALTA", "Reporte auditoría", "A. Aguilar", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Sucursales Salta/Tartagal"],
            [6, "14-jul", "Calidad", "Tablero KPIs", "Falta visibilidad", "Desarrollar tablero de control de KPIs operativos", "ALTA", "Dashboard operativo", "A. Aguilar", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Extracción Salesforce"],
            [7, "14-jul", "Calidad", "Alistamiento UCT", "Demoras preparación", "Reorganizar proceso de preparación y alistamiento UCT", "ALTA", "Minuta de proceso", "Pablo Carrizo", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Garantizar estándar"],
            [8, "14-jul", "RRHH", "Personal TPA", "Sobrecarga admin", "Incorporar 2 colaboradores administrativos para TPA", "ALTA", "Alta de nómina", "A. Di Costanzo", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Vacantes activas"],
            [9, "14-jul", "RRHH", "Capacitación", "Certificaciones ok", "Ejecutar plan de capacitación semestral obligatorio", "ALTA", "% de cumplimiento", "A. Di Costanzo", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Foco asesores sin reválida"],
            [10, "14-jul", "RRHH", "Ausentismo", "Fricciones taller", "Controlar índice de rotación y ausentismo en taller", "ALTA", "Reporte mensual", "A. Di Costanzo", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Mitigar demoras de entrega"],
            [11, "14-jul", "Facilities", "Obras Las Lajitas", "Riesgo penalidad", "Negociar reprogramación de obras en Las Lajitas", "ALTA", "Minuta fieldman", "D. Colque / A. Di Costanzo", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Evitar impactos manual"],
            [12, "14-jul", "Facilities", "Sucursal Salta", "Adecuación edilicia", "Planificar adecuación edilicia para sucursal Salta", "ALTA", "Plan aprobado", "D. Colque / A. Di Costanzo", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Alineación estructural"],
            [13, "14-jul", "CRM", "Salesforce", "Boletos estancados", "Control diario de asignación de boletos Salesforce", "ALTA", "Reporte CRM diario", "A. Aguilar / L. de los Ríos", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Evitar caídas de leads"],
            [14, "14-jul", "CRM", "Prospectos", "Demoras atención", "Responder prospectos digitales en menos de 2 horas", "ALTA", "Dashboard Salesforce", "A. Aguilar / L. de los Ríos", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Guardias fines de semana"],
            [15, "14-jul", "CRM", "Filtro Boletos", "Boletos vencidos", "Eliminar boletos vencidos sin actividad comercial", "ALTA", "Auditoría sistema", "A. Aguilar / L. de los Ríos", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Limpieza de base al 80%"],
            [16, "14-jul", "Posventa", "Campañas Airbags", "Baja tasa contacto", "Incrementar tasa de contacto para campañas de Airbags", "ALTA", "% avance campaña", "Daniel Colque", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Llamados sobre históricas"],
            [17, "14-jul", "TCFA y Seguros", "Método", "Desvío pólizas", "Revisar método analítico de crecimiento de pólizas", "ALTA", "Fórmula homologada", "L. de los Ríos / Romina R.", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Consistencia comisiones"],
            [18, "14-jul", "TCFA y Seguros", "App Seguros", "Baja activación", "Campaña de difusión para activación de App Seguros", "ALTA", "Tasa activación", "L. de los Ríos / Romina R.", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Promoción tótems salón"],
            [19, "14-jul", "KINTO", "Siniestros One", "Flujos sueltos", "Rediseñar proceso de seguimiento de siniestros One", "ALTA", "Flujograma unificado", "Aaron Martearena", "14/07/2026", "31/07/2026", "25/07/2026", "EN PROCESO", "Respuesta de flota Kinto"]
        ]
        columnas_foto = [
            "#", "Fecha de Alta", "Gerencia / Área / Sector", "Tema / Proyecto", 
            "Situación actual", "Acción", "Prioridad", "Indicador de eficiencia / Entregable", 
            "Responsable", "Fecha de Inicio", "Fecha de finalización", "Fecha de control", 
            "Estado", "Observación"
        ]
        st.session_state.db_final_dep_excel_v1 = pd.DataFrame(data_rows, columns=columnas_foto)

    lista_responsables = ["Todos"] + sorted(list(st.session_state.db_final_dep_excel_v1["Responsable"].unique()))
    filtro_lider = st.selectbox("👤 Filtrar Vista por Responsable:", lista_responsables)
    df_vista = st.session_state.db_final_dep_excel_v1 if filtro_lider == "Todos" else st.session_state.db_final_dep_excel_v1[st.session_state.db_final_dep_excel_v1["Responsable"] == filtro_lider]

    df_editado = st.data_editor(
        df_vista,
        column_config={
            "#": st.column_config.NumberColumn(disabled=True), "Fecha de Alta": st.column_config.TextColumn(disabled=True),
            "Gerencia / Área / Sector": st.column_config.TextColumn(disabled=True), "Tema / Proyecto": st.column_config.TextColumn(disabled=True),
            "Situación actual": st.column_config.TextColumn(disabled=True), "Acción": st.column_config.TextColumn(disabled=True),
            "Prioridad": st.column_config.TextColumn(disabled=True), "Indicador de eficiencia / Entregable": st.column_config.TextColumn(disabled=True),
            "Responsable": st.column_config.TextColumn(disabled=True), "Fecha de Inicio": st.column_config.TextColumn(),
            "Fecha de finalización": st.column_config.TextColumn(), "Fecha de control": st.column_config.TextColumn(),
            "Estado": st.column_config.SelectboxColumn(options=["PENDIENTE", "EN PROCESO", "COMPLETADO"], default="EN PROCESO"), "Observación": st.column_config.TextColumn()
        },
        use_container_width=True, key="editor_dep_foto_v3", hide_index=True
    )

    if st.button("💾 Guardar Cambios Actuales"):
        for _, row in df_editado.iterrows():
            idx_original = row["#"] - 1
            st.session_state.db_final_dep_excel_v1.iloc[idx_original] = row
        st.success("🎉 Agenda de compromisos DEP guardada en memoria local de la sesión.")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.db_final_dep_excel_v1.to_excel(writer, sheet_name='Agenda', index=False)
        worksheet = writer.sheets['Agenda']
        
        fill_blue_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        font_white_header = Font(name='Arial', size=10, bold=True, color="FFFFFF")
        font_body = Font(name='Arial', size=10, bold=False, color="000000")
        border_thin = Border(left=Side(style='thin', color='CCCCCC'), right=Side(style='thin', color='CCCCCC'), top=Side(style='thin', color='CCCCCC'), bottom=Side(style='thin', color='CCCCCC'))
        
        for col_idx in range(1, len(st.session_state.db_final_dep_excel_v1.columns) + 1):
            cell = worksheet.cell(row=1, column=col_idx)
            cell.fill = fill_blue_header; cell.font = font_white_header; cell.border = border_thin
            
        for row_idx in range(2, len(st.session_state.db_final_dep_excel_v1) + 2):
            for col_idx in range(1, len(st.session_state.db_final_dep_excel_v1.columns) + 1):
                cell = worksheet.cell(row=row_idx, column=col_idx)
                cell.font = font_body; cell.border = border_thin
                
        for col_idx in range(1, len(st.session_state.db_final_dep_excel_v1.columns) + 1):
            col_letter = get_column_letter(col_idx); max_len = 0
            for row_idx in range(1, len(st.session_state.db_final_dep_excel_v1) + 2):
                val = worksheet.cell(row=row_idx, column=col_idx).value
                if val: max_len = max(max_len, len(str(val)))
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 11)

    st.download_button(label="📥 Descargar Agenda de Seguimiento Formateada (Excel)", data=buffer.getvalue(), file_name="Plan_de_Accion_PVT_JULIO_26_Saneado.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
