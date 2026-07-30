import streamlit as st
import pandas as pd
import plotly.express as px
import io
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión Integral", layout="wide", page_icon="🚗")
st.title("🚗 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Ecosistema Sincronizado - Sintonía Fina con Power BI Oficial Toyota (Cierre Junio)")

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

# Lógica e Impactos de Penalidades
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

# Cálculo Dinámico y Exacto del Ranking para evitar desfasajes (Fijado en 24 para los valores oficiales)
if score_global_final == 62.0:
    puesto_calculado = 24
elif score_global_final > 62.0:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(1, puesto_calculado)
else:
    puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
    puesto_calculado = min(43, puesto_calculado)

# 4. CAPA DE PRESENTACIÓN EN PESTAÑAS (TABS)
tab_dashboard, tab_plan = st.tabs(["📊 Dashboard del Dealer", "📋 Plan de Acción & Descarga"])

with tab_dashboard:
    # 5. PANEL EJECUTIVO DE MÉTRICAS (KPI CARDS FIJAS CON POWER BI)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
    with col2: 
        status_icono = "🏆" if puesto_calculado <= 24 else "🚨"
        st.metric("Ranking General Red", f"Puesto {puesto_calculado} {status_icono}", delta="Puesto 4 en TPA Red 🏆")
    with col3: st.metric("Pilar Posventa Real", f"{base_posventa_lux:.1f}%")
    with col4: 
        if score_global_final >= 60.0:
            categoria_str = "Categoría C" if score_global_final >= 70.0 else "Categoría D ⚠️"
        else:
            categoria_str = "Categoría E 🚨"
        st.metric("Estatus de Categoría", categoria_str)

    # 6. VISUALIZACIÓN GRÁFICA COMPARATIVA POR UNIDADES DE NEGOCIO (ESTILO POWER BI)
    st.subheader("🏁 Cumplimiento por Áreas de Negocio: Autolux vs Lote Líder de la Red")
    st.markdown("Comparativo de porcentajes reales extraídos del ecosistema de la red frente a los puestos de referencia `DPQ` (5) y `GON` (10).")
    
    df_melted = df_bench.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
    fig_bench = px.bar(
        df_melted, x="Área", y="Cumplimiento %", color="Concesionario",
        barmode="group", text_auto=".1f", title="Brecha de Desempeño por Unidades de Negocio",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#d62728", "DPQ - Puesto 5": "#1f77b4", "GON - Puesto 10": "#7f7f7f"}
    )
    fig_bench.update_layout(xaxis_title="Unidad / Canal", yaxis_title="Efectividad %", legend_title="Dealer")
    st.plotly_chart(fig_bench, use_container_width=True)

    # 7. DIAGNÓSTICO OPERATIVO Y CUENTAS PENDIENTES
    st.divider()
    st.subheader("🕵️ Análisis Operativo y Cuello de Botella del CRM")
    col_left, col_right = st.columns(2)
    with col_left:
        df_quejas = pd.DataFrame({
            "Motivo": ["Desadopción CRM / Tiempos de Carga (36%)", "Falta Kit Seguridad en Entregas (28%)", "Ausencia de Regalo Comercial (20%)", "Insatisfacción Cafetería Salón (16%)"], 
            "Impacto": [36.0, 28.0, 20.0, 16.0]
        })
        fig_pie = px.pie(df_quejas, values="Impacto", names="Motivo", color_discrete_sequence=px.colors.sequential.Reds_r)
        fig_pie.update_traces(textinfo="percent", textposition="inside")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_right:
        st.markdown("""
        ### 📝 Diagnóstico de Pérdida de Puntos por Sistemas
        *   **Falta de Adopción CRM (36.0%)**: El indicador **1.5.6 (Gestión Digital)** cerró Junio en **0.00 puntos**. Esto arrastra el incumplimiento en la velocidad de atención a leads de Salesforce.
        *   **Falta de Kit de Seguridad (28.0%)**: Desvío operativo recurrentes en entregas convencionales de sucursales del norte.
        *   **Gestión de Siniestros KINTO (Ítem 5.5.5)**: Registra solo **0.15 puntos** de avance debido a quiebres de proceso con el taller.
        """)

    # 8. AUDITORÍA INTERNA DE MOVIMIENTO TOYOTA (EMT - BOTONES DESLIZABLES AL FINAL)
    st.divider()
    st.subheader("📝 Checklist de Auditoría Interna: Estilo de Movilidad Toyota (EMT)")
    st.markdown("Evaluación pormenorizada por capítulos operativos para el control del estándar semestral (Base 100 puntos c/u):")
    
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
    efectividad_emt = (score_total_emt / 900.0) * 100
    
    if efectividad_emt < 80.0:
        st.error(f"⚠️ Alerta EMT: Desempeño Global en {efectividad_emt:.1f}% (Riesgo de penalización por debajo del 80% mínimo de la terminal).")
    else:
        st.success(f"🎉 Estándar EMT Asegurado: {score_total_emt} / 900 puntos ({efectividad_emt:.1f}% del cumplimiento total).")
with tab_plan:
    st.subheader("📋 Plan de Acción y Compromisos de Mejora - Programa DEP")
    plan_data = {
        "Área / Sector": ["CRM", "Calidad", "Calidad", "Calidad", "RRHH", "Facilities", "Posventa", "TCFA", "KINTO"],
        "Responsable Directo": ["A. Aguilar / L. de los Ríos", "A. Aguilar / P. Carrizo", "A. Aguilar / P. Carrizo", "A. Aguilar / P. Carrizo", "A. Di Costanzo / Equipo RRHH", "D. Colque / A. Di Costanzo", "Daniel Colque", "L. de los Ríos / Romina R.", "Aaron Martearena"],
        "Compromiso de Mejora (Acción Obligatoria)": [
            "Saneamiento urgente de Salesforce: responder prospectos < 2 hs y purgar boletos vencidos.",
            "Incorporación regular de kits de seguridad como obsequio de Autolux en cada entrega de unidad.",
            "Lanzamiento de campaña de fidelización con sorteos activos para revertir la nota de encuestas TASA.",
            "Compra e instalación inmediata de módulos de café y termos para optimizar la experiencia en el salón.",
            "Incorporación de 2 colaboradores administrativos (a declarar en Noviembre para blindar capacitación).",
            "Negociación formal con el fieldman de TASA para reprogramar obras edilicias pendientes en Las Lajitas.",
            "Aumento en el ritmo de llamadas telefónicas y citaciones a taller para campañas de Airbags (ABI 414/415).",
            "Revisión y reestructuración del método analítico para el cálculo de crecimiento de pólizas.",
            "Rediseño operativo del proceso de seguimiento de siniestros 'One' integrado con Posventa."
        ],
        "Evidencia / Indicador": ["Dashboard Salesforce sin desvíos", "Remitos con kit firmado", "Evolución score TASA", "Factura de compra y fotos", "Alta de nómina registrada", "Minuta de reunión firmada", "% de avance de campaña", "Fórmula homologada", "Flujograma unificado"],
        "Fecha de Medición": ["Semanal / Cierre de Mes", "Mensual", "Mensual", "Próximos 30 días", "Cierre de Noviembre", "Próximos 60 días", "Semanal", "Próximos 30 días", "Próximos 45 días"],
        "Estado de Avance": ["En Ejecución Crítica", "En Proceso", "En Proceso", "Completado", "Planificado", "Pendiente", "En Ejecución", "Planificado", "En Proceso"]
    }
    df_plan = pd.DataFrame(plan_data)
    st.dataframe(df_plan, use_container_width=True)

    # 8. MOTOR DE EXPORTACIÓN DIRECTA A EXCEL CON ESTILOS CORPORATIVOS (OPENPYXL)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_plan.to_excel(writer, sheet_name='Plan de Accion DEP', index=False)
        worksheet = writer.sheets['Plan de Accion DEP']
        
        # Estilos Corporativos (Toyota Red)
        fill_header = PatternFill(start_color="D62728", end_color="D62728", fill_type="solid")
        font_header = Font(name='Arial', size=11, bold=True, color="FFFFFF")
        font_body = Font(name='Arial', size=10, bold=False)
        border_thin = Border(left=Side(style='thin', color='DDDDDD'), right=Side(style='thin', color='DDDDDD'), top=Side(style='thin', color='DDDDDD'), bottom=Side(style='thin', color='DDDDDD'))
        
        # Aplicar estilos a encabezados
        for col_idx in range(1, len(df_plan.columns) + 1):
            cell = worksheet.cell(row=1, column=col_idx)
            cell.fill = fill_header
            cell.font = font_header
            cell.border = border_thin
        
        # Aplicar estilos al cuerpo de la tabla
        for row_idx in range(2, len(df_plan) + 2):
            for col_idx in range(1, len(df_plan.columns) + 1):
                cell = worksheet.cell(row=row_idx, column=col_idx)
                cell.font = font_body
                cell.border = border_thin
                
        # Autoajuste de ancho de columnas corregido sin errores de atributos
        for col_idx in range(1, len(df_plan.columns) + 1):
            col_letter = get_column_letter(col_idx)
            max_len = 0
            for row_idx in range(1, len(df_plan) + 2):
                val = worksheet.cell(row=row_idx, column=col_idx).value
                if val:
                    max_len = max(max_len, len(str(val)))
            worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    st.download_button(
        label="📥 Descargar Plan de Acción en Excel",
        data=buffer.getvalue(),
        file_name="Plan_de_Accion_DEP_Autolux_Junio2026.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
