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

# Cálculo Dinámico del Ranking
if score_global_final == 62.0:
    puesto_calculado = 24
elif score_global_final > 62.0:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(1, puesto_calculado)
else:
    puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
    puesto_calculado = min(43, puesto_calculado)

# 4. CAPA DE ENRUTAMIENTO POR PESTAÑAS (3 TABS)
tab_dashboard, tab_calidad, tab_plan = st.tabs(["📊 Dashboard del Dealer", "🕵️ Análisis Clínico de Calidad (CSI/NPS)", "📋 Plan de Acción Interactiva"])
with tab_dashboard:
    # 5. PANEL EJECUTIVO DE MÉTRICAS (KPI CARDS)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
    with col2: st.metric("Ranking General Red", f"Puesto {puesto_calculado} 🏆" if puesto_calculado <= 24 else f"Puesto {puesto_calculado} 🚨", delta="Puesto 4 en TPA Red 🏆")
    with col3: st.metric("Pilar Posventa Real", f"{base_posventa_lux:.1f}%")
    with col4: 
        categoria_str = "Categoría C" if score_global_final >= 70.0 else ("Categoría D ⚠️" if score_global_final >= 60.0 else "Categoría E 🚨")
        st.metric("Estatus de Categoría", categoria_str)

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
        acu_e = st.slider("E: Toyota Plan de Ahorro (100)", 0, 100, 100)
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
        # DATASET APERTURADO AL 100% REAL CON SSI Y CRM DESGLOSADOS
        df_quejas_sincronizado = pd.DataFrame({
            "Factor de Desvío": [
                "Falta de Kit de Seguridad (36%)", 
                "Falta de Presentes / Merchandising (20%)", 
                "Falta de Máquina de Café (16%)",
                "Desadopción CRM / Leads Ventas (15%)",
                "Seguimiento Post-Entrega / SSI (13%)"
            ], 
            "Impacto %": [36.0, 20.0, 16.0, 15.0, 13.0] # Suma exacta del 100.0%
        })
        
        fig_pie_oficial = px.pie(
            df_quejas_sincronizado, values="Impacto %", names="Factor de Desvío",
            color_discrete_sequence=["#1F4E78", "#5B9BD5", "#A5D6A7", "#FFB74D", "#E57373"],
            title="Estructura Completa de Impactos en Encuestas de Calidad (Base 100%)"
        )
        
        # Ajustes de dimensiones y leyenda abajo para maximizar la torta
        fig_pie_oficial.update_layout(
            height=500,
            margin=dict(l=10, r=10, t=50, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="center", x=0.5)
        )
        fig_pie_oficial.update_traces(textinfo="value", textposition="inside")
        st.plotly_chart(fig_pie_oficial, use_container_width=True)
        
    with col_pie_right:
        st.info("💡 **Diagnóstico Raíz**: La caída no se asocia al producto o al vehículo, sino a una marcada percepción de *'pérdida de beneficios'* y desvíos en el seguimiento y los plazos de respuesta digitales de los asesores comerciales.")
        st.markdown("""
        ### 📋 Desglose Técnico de Desvíos Observados:
        *   **Falta de Kit de Seguridad (36%)**: Los clientes manifiestan descontento severo porque el kit pasó a ser arancelado o no viene como 'obsequio' de cortesía por defecto al retirar la unidad.
        *   **Falta de Presentes / Detalles de Marketing (20%)**: Menciones críticas asociadas a la falta de recuerdos o atenciones especiales (ej. llaveros, matafuegos o primer servicio gratis) tras concretar una inversión 0km.
        *   **Falta de Máquina de Café (16%)**: Verbatines de Posventa. Califican de 'miserable' el retiro de la expendedora gratuita y la instalación de terminales chicas o heladeras cerradas con llave.
        *   **Desadopción CRM y Tiempos de Leads (15%)**: Desvío del indicador **1.5.6**. El equipo demora más de 2 horas en procesar los prospectos digitales asignados en Salesforce.
        *   **Seguimiento Post-Entrega SSI (13%)**: Ausencia de llamados comerciales programados dentro de las 48 horas posteriores a la entrega física de la unidad, lo que afecta las encuestas de satisfacción.
        """)

    st.divider()
    st.subheader("💬 La Voz del Cliente (Verbatines de Auditoría TASA)")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.error("**Foco Entregas & Marketing (SSI)**\n* *'Me dan el auto y ya no te dan ni un miserable kit de seguridad.'*\n* *'En Salta cuando compré el Toyota Etios me regalaron heladera, kit, llavero y matafuegos. En Tartagal no me dieron ni un vaso de agua.'*\n* *'La vez pasada te daban una linterna buenísima, esta vez una planta.'*")
    with col_v2:
        st.error("**Foco Espera & Taller (CSI)**\n* *'SACARON LA MÁQUINA DE CAFÉ DEL LUGAR DE ESPERA, UNA ACTITUD TOTALMENTE MISERABLE.'*\n* *'Hay que esperar dos horas... ahora hay una máquina muy chica que nadie sabe usar, es tedioso, por el precio deberían dar como antes.'*")
with tab_plan:
    st.subheader("📋 Planilla de Seguimiento y Control de Avances por Responsable")
    st.markdown("Hacé **doble clic en cualquier celda** de las columnas libres para registrar tus compromisos de mejora, avances y fechas reales:")

    if "db_final_dep_v300" not in st.session_state:
        # CARGA COMPACTA CONTINUA DE LAS 19 FILAS PARA EVITAR RECORTES EN EL SERVIDOR
        data_rows = [["Coordinación", "Alejandro López", "Centralizar seguimiento transversal y tablero único", "Reporte online", "Quincenal", "", "", "Pendiente"], ["Calidad", "A. Aguilar / P. Carrizo", "Incorporar kits de seguridad de Autolux inyectados en cada entrega", "Remitos con kit firmado", "Mensual", "", "", "Pendiente"], ["Calidad", "A. Aguilar / P. Carrizo", "Compra e instalación de módulos de café y termos en showroom", "Factura de compra y fotos", "30 días", "", "", "Pendiente"], ["Calidad", "A. Aguilar / P. Carrizo", "Lanzar campaña de fidelización con sorteos activos", "Evolución score TASA", "Mensual", "", "", "Pendiente"], ["Calidad", "A. Aguilar / P. Carrizo", "Implementar auditorías internas tipo Mystery Shopper", "Reportes de auditoría", "Trimestral", "", "", "Pendiente"], ["Calidad", "A. Aguilar / P. Carrizo", "Desarrollar tablero de control de KPIs operativos", "Dashboard operativo", "45 días", "", "", "Pendiente"], ["Calidad", "A. Aguilar / P. Carrizo", "Reorganizar proceso de preparación y alistamiento UCT", "Minuta de proceso", "Quincenal", "", "", "Pendiente"], ["RRHH", "A. Di Costanzo", "Incorporar 2 colaboradores administrativos para TPA", "Alta de nómina registrada", "Noviembre", "", "", "Pendiente"], ["RRHH", "A. Di Costanzo", "Ejecutar plan de capacitación semestral obligatorio", "% de cumplimiento", "Cierre Año", "", "", "Pendiente"], ["RRHH", "A. Di Costanzo", "Controlar índice de rotación y ausentismo en taller", "Reporte mensual RRHH", "Mensual", "", "", "Pendiente"], ["Facilities", "D. Colque / A. Di Costanzo", "Negociar reprogramación de obras en Las Lajitas", "Minuta firmada fieldman", "60 días", "", "", "Pendiente"], ["Facilities", "D. Colque / A. Di Costanzo", "Planificar adecuación edilicia para sucursal Salta", "Plan de obra aprobado", "Cierre Año", "", "", "Pendiente"], ["CRM", "A. Aguilar / L. de los Ríos", "Control diario de asignación de boletos Salesforce", "Reporte diario CRM", "Diario", "", "", "Pendiente"], ["CRM", "A. Aguilar / L. de los Ríos", "Responder prospectos digitales en menos de 2 horas", "Dashboard Salesforce", "Semanal", "", "", "Pendiente"], ["CRM", "A. Aguilar / L. de los Ríos", "Eliminar boletos vencidos sin actividad comercial", "Auditoría de sistema", "Mensual", "", "", "Pendiente"], ["Posventa", "Daniel Colque", "Incrementar tasa de contacto para campañas de Airbags", "% de avance de campaña", "Semanal", "", "", "Pendiente"], ["TCFA y Seguros", "L. de los Ríos / Romina R.", "Revisar método analítico de crecimiento de pólizas", "Fórmula homologada", "30 días", "", "", "Pendiente"], ["TCFA y Seguros", "L. de los Ríos / Romina R.", "Campaña de difusión para activación de App Seguros", "Tasa de activación App", "Mensual", "", "", "Pendiente"], ["KINTO", "Aaron Martearena", "Rediseñar proceso de seguimiento de siniestros One", "Flujograma unificado", "45 días", "", "", "Pendiente"]]
        st.session_state.db_final_dep_v300 = pd.DataFrame(data_rows, columns=["Área", "Responsables", "Compromiso de Mejora", "Indicador / Evidencia", "Fecha de Medición", "Comentarios", "Fecha Real", "Estado"])

    lista_responsables = ["Todos"] + sorted(list(st.session_state.db_final_dep_v300["Responsables"].unique()))
    filtro_lider = st.selectbox("👤 Filtrar por Responsable de Mesa:", lista_responsables)
    df_vista = st.session_state.db_final_dep_v300 if filtro_lider == "Todos" else st.session_state.db_final_dep_v300[st.session_state.db_final_dep_v300["Responsables"] == filtro_lider]

    df_editado = st.data_editor(
        df_vista,
        column_config={
            "Área": st.column_config.TextColumn(disabled=True), "Responsables": st.column_config.TextColumn(disabled=True),
            "Compromiso de Mejora": st.column_config.TextColumn(disabled=True), "Indicador / Evidencia": st.column_config.TextColumn(disabled=True),
            "Fecha de Medición": st.column_config.TextColumn(disabled=True), "Estado": st.column_config.SelectboxColumn(options=["Pendiente", "En Proceso", "Completado"], default="Pendiente")
        },
        use_container_width=True, key="editor_dep_definitivo_v300"
    )

    if st.button("💾 Guardar Cambios"):
        for idx, row in df_editado.iterrows(): st.session_state.db_final_dep_v300.loc[idx] = row
        st.success("🎉 Novedades y compromisos guardados en la sesión.")

    # MOTOR DE EXPORTACIÓN CON ENCABEZADOS EN AZUL INSTITUCIONAL Y FONDOS BLANCOS
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.db_final_dep_v300.to_excel(writer, sheet_name='Plan de Accion DEP', index=False)
        worksheet = writer.sheets['Plan de Accion DEP']
        
        fill_blue_header = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        font_white_header = Font(name='Arial', size=11, bold=True, color="FFFFFF")
        font_body = Font(name='Arial', size=10, bold=False, color="000000")
        border_thin = Border(left=Side(style='thin', color='DDDDDD'), right=Side(style='thin', color='DDDDDD'), top=Side(style='thin', color='DDDDDD'), bottom=Side(style='thin', color='DDDDDD'))
        
        for col_idx in range(1, len(st.session_state.db_final_dep_v300.columns) + 1):
            cell = worksheet.cell(row=1, column=col_idx)
            cell.fill = fill_blue_header; cell.font = font_white_header; cell.border = border_thin
            
        for row_idx in range(2, len(st.session_state.db_final_dep_v300) + 2):
            for col_idx in range(1, len(st.session_state.db_final_dep_v300.columns) + 1):
                cell = worksheet.cell(row=row_idx, column=col_idx); cell.font = font_body; cell.border = border_thin
                
        for col_idx in range(1, len(st.session_state.db_final_dep_v300.columns) + 1):
            col_letter = get_column_letter(col_idx); max_len = 0
            for row_idx in range(1, len(st.session_state.db_final_dep_v300) + 2):
                val = worksheet.cell(row=row_idx, column=col_idx).value
                if val: max_len = max(max_len, len(str(val)))
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    st.download_button(label="📥 Descargar Plan de Acción Completo en Excel", data=buffer.getvalue(), file_name="Plan_de_Accion_DEP_Autolux_2026.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
