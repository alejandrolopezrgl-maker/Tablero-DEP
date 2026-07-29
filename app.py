import streamlit as st
import pandas as pd
import plotly.express as px
import io
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión Integral", layout="wide", page_icon="🚗")
st.title("📊 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Ecosistema Sincronizado - Datos Oficiales de la Red TASA (Cierre Acumulado a Junio)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL: SIMULADOR DE PENALIDADES DE CAMPO (REGLAMENTO TASA)
st.sidebar.header("🚨 Zona de Control de Riesgos")
if st.session_state.reestablecer:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts)", value=False, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5 pts)", value=False, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts)", value=False)
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5 pts)", value=False)
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85)

puntos_a_restar_global = 10 if penalidad_fair_play else 0
castigo_posventa_fieldman = 40.0 if visitas_fieldman < 85 else 0.0

if visitas_fieldman < 85: 
    st.sidebar.error("❌ Penalidad Posventa Activa (-40% en Score del área por Pág. 40).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman a salvo (≥85%).")

if st.sidebar.button("🔄 Restablecer Valores Oficiales de Junio"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. BASE DE DATOS ESTRATÉGICA DE LA RED (BENCHMARKING)
base_ventas_lux = 55.7 if not penalidad_movilidad else (55.7 - 5.0)
base_posventa_lux = 91.7 - (91.7 * (castigo_posventa_fieldman / 100))

data_competitiva = {
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Autolux (LUX)": [base_ventas_lux, 49.0, base_posventa_lux, 72.8, 35.8, 75.8, 73.0, 25.0, 67.6],
    "Tsuyoi (TSU)": [50.9, 79.0, 95.1, 36.2, 41.0, 78.7, 92.0, 25.0, 47.9],
    "Zento (ZEN)": [49.0, 0.0, 88.0, 42.0, 55.0, 55.0, 59.0, 26.0, 63.0]
}
df_bench = pd.DataFrame(data_competitiva)
score_global_final = 62.0 - puntos_a_restar_global
if penalidad_movilidad: 
    score_global_final -= 1.1

# 4. CAPA DE VISUALIZACIÓN EJECUTIVA (METRICS)
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
with col2: st.metric("Ranking General Red", "Puesto 24 🏆" if score_global_final >= 62.0 else "Puesto 28 🟡", delta="Puesto 4 en TPA Red 🏆")
with col3: st.metric("Pilar Posventa Real", f"{base_posventa_lux:.1f}%")
with col4: 
    if base_ventas_lux < 70.0:
        st.metric("Estatus de Categoría", "Riesgo Cat. E ⚠️", delta="Bloqueo por Mínimo en Ventas")
    else:
        st.metric("Estatus de Categoría", "Categoría C" if score_global_final >= 60.0 else "Categoría D ⚠️")

if base_ventas_lux < 70.0:
    st.error(f"🚨 CLÁUSULA DE BLOQUEO ACTIVA: El pilar de Ventas se encuentra en {base_ventas_lux:.1f}% (Mínimo requerido por TASA = 70.0%). Riesgo de degradación automática a Categoría E.")

# 5. MÓDULO DE VISTA EJECUTIVA: COMPARTIVA DE RENDIMIENTO CONTRA LÍDERES
st.divider()
st.subheader("🏁 Vista Ejecutiva: Benchmarking de Desempeño contra Líderes de la Red")
st.markdown("Comparación detallada de Autolux (`LUX`) frente a los líderes de la red Toyota: `TSU` (Tsuyoi) y `ZEN` (Zento) para identificar brechas de puntaje.")

df_melted = df_bench.melt(id_vars=["Área"], var_name="Concesionario", value_name="Cumplimiento %")
fig_bench = px.bar(
    df_melted, x="Área", y="Cumplimiento %", color="Concesionario",
    barmode="group", text_auto=".1f", title="Brecha de Desempeño por Unidades de Negocio",
    color_discrete_map={"Autolux (LUX)": "#d62728", "Tsuyoi (TSU)": "#1f77b4", "Zento (ZEN)": "#2ca02c"}
)
st.plotly_chart(fig_bench, use_container_width=True)
# 6. ANÁLISIS OPERATIVO Y DIAGNÓSTICO DE DESVÍOS CRÍTICOS (CRM E INFORME DE QUEJAS)
st.divider()
st.subheader("🕵️ Análisis Operativo y Cuello de Botella del CRM (Indicador 1.5.6)")
col_left, col_right = st.columns(2)
with col_left:
    df_quejas = pd.DataFrame({
        "Motivo": ["Desadopción CRM / Tiempos de Carga (36%)", "Falta Kit Seguridad en Entregas (28%)", "Ausencia de Regalo Comercial (20%)", "Insatisfacción Cafetería Salón (16%)"], 
        "Impacto": [36.0, 28.0, 20.0, 16.0]
    })
    fig_pie = px.pie(df_quejas, values="Impacto", names="Motivo", color_discrete_sequence=px.colors.sequential.Reds_r, title="Distribución de Focos de Desvíos de Calidad")
    fig_pie.update_traces(textinfo="percent", textposition="inside", textfont_size=14)
    st.plotly_chart(fig_pie, use_container_width=True)
with col_right:
    st.markdown("""
    ### 📝 Diagnóstico de Pérdida de Puntos por Sistemas
    *   **Falta de Adopción CRM (36.0%)**: El indicador **1.5.6 (Gestión Digital)** cerró Junio en **0.00 puntos**. Esto arrastra el incumplimiento en la velocidad de atención a leads de Salesforce.
    *   **Falta de Kit de Seguridad (28.0%)**: Desvío operativo recurrente en entregas convencionales de sucursales del norte.
    *   **Gestión de Siniestros KINTO (Ítem 5.5.5)**: Registra solo **0.15 puntos** de avance debido a quiebres de proceso con el taller.
    """)

# 7. PLAN DE ACCIÓN GENERAL INTEGRADO (CON COMPROMISOS Y FECHAS DE MEDICIÓN REALES)
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

# 8. MOTOR DE EXPORTACIÓN DIRECTA A EXCEL CON ESTILOS CORPORATIVOS
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_plan.to_excel(writer, sheet_name='Plan de Accion DEP', index=False)
    worksheet = writer.sheets['Plan de Accion DEP']
    f_header = Font(name='Arial', size=11, bold=True, color='FFFFFF')
    fill_header = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    thin_border = Border(left=Side(style='thin', color='BFBFBF'), right=Side(style='thin', color='BFBFBF'), top=Side(style='thin', color='BFBFBF'), bottom=Side(style='thin', color='BFBFBF'))
    
    for col_num, header in enumerate(df_plan.columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.font = f_header
        cell.fill = fill_header
        cell.border = thin_border
    for row in worksheet.iter_rows(min_row=2, max_row=len(df_plan)+1, min_col=1, max_col=len(df_plan.columns)):
        for cell in row:
            cell.border = thin_border
            cell.font = Font(name='Arial', size=10)
    for col_num, col_name in enumerate(df_plan.columns, 1):
        max_len = max(df_plan[col_name].astype(str).map(len).max(), len(col_name))
        worksheet.column_dimensions[get_column_letter(col_num)].width = max(max_len + 3, 12)

st.download_button(label="📥 Descargar Plan de Acción General Auditado (.xlsx)", data=buffer.getvalue(), file_name="Plan_de_Accion_DEP_Autolux_Completo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 9. CONSULTA DETALLADA DE DATOS DE REGLAMENTO (SIMULADOR DE AUDITORÍA EMT)
st.divider()
st.subheader("📂 Consulta Estática de Hojas de Datos (DEP & Auditoría EMT)")
pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Estructura de Desglose de Cierre", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Estructura de Desglose de Cierre":
    st.dataframe(df_bench, use_container_width=True)
else:
    st.markdown("### 📋 Simulador Oficial EMT - Desglose por ACU's (Target de Sostenimiento)")
    st.caption("Ajustá las notas estimadas para cada Macro-Capítulo (Base de 100 puntos c/u) y oprimí el botón de cálculo:")
    
    with st.form("formulario_emt_estabilizado"):
        c_a, c_b, c_c = st.columns(3)
        with c_a: acu_a = st.slider("A - Estructura Central:", 0, 100, 100, step=5)
        with c_b: acu_b = st.slider("B - Servicio al Cliente:", 0, 100, 100, step=5)
        with c_c: acu_c = st.slider("C - KINTO:", 0, 100, 100, step=5)
            
        c_d, c_e, c_f = st.columns(3)
        with c_d: acu_d = st.slider("D - Club Toyota:", 0, 100, 100, step=5)
        with c_e: acu_e = st.slider("E - Toyota Plan (TPA):", 0, 100, 100, step=5)
        with c_f: acu_f = st.slider("F - Financial (TCFA):", 0, 100, 100, step=5)
            
        c_g, c_h, c_i = st.columns(3)
        with c_g: acu_g = st.slider("G - Usados:", 0, 100, 100, step=5)
        with c_h: acu_h = st.slider("H - Convencional (Ventas):", 0, 100, 100, step=5)
        with c_i: acu_i = st.slider("I - Servicios Conectados:", 0, 100, 100, step=5)
        
        boton_calcular = st.form_submit_button("🚀 Calcular Nota Consolidada EMT")

    if boton_calcular or "pct_emt_calc" in st.session_state:
        tot_sim = acu_a + acu_b + acu_c + acu_d + acu_e + acu_f + acu_g + acu_h + acu_i
        pct_emt = (tot_sim / 900) * 100
        st.session_state.pct_emt_calc = pct_emt
        st.divider()
        st.metric(label="🏆 NOTA CONSOLIDADA ESTIMADA DE AUDITORÍA EMT", value=f"{st.session_state.pct_emt_calc:.1f}%")
