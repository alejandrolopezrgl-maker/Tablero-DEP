import streamlit as st
import pandas as pd
import plotly.express as px
import io
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión Integral", layout="wide", page_icon="🚗")
st.title("🚗 Tablero de Control y Dashboard Evolutivo DEP - Autolux")
st.caption("Ecosistema Sincronizado - Datos Oficiales de la Red TASA (Cierre Acumulado a Junio)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL: CONTROL DE RIESGOS Y MICRO-SIMULADOR EMT (900 PUNTOS TOYOTA)
st.sidebar.header("🚨 Zona de Control de Riesgos")
if st.session_state.reestablecer:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts Global)", value=False, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación EMT (-5.0 pts Calidad)", value=False, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85, key="fm_real")
    st.sidebar.markdown("---")
    st.sidebar.markdown("✏️ **Auditoría Interna EMT (Score Real)**")
    score_emt = st.sidebar.slider("Puntos Obtenidos (Base 900 pts)", 0, 900, 900, key="emt_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts Global)", value=False)
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación EMT (-5.0 pts Calidad)", value=False)
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, 85)
    st.sidebar.markdown("---")
    st.sidebar.markdown("✏️ **Auditoría Interna EMT (Score Real)**")
    score_emt = st.sidebar.slider("Puntos Obtenidos (Base 900 pts)", 0, 900, 900)

# Lógica de Impacto de Penalidades según Manual de TASA
puntos_a_restar_global = 10.0 if penalidad_fair_play else 0.0
castigo_posventa_fieldman = 3.4 if visitas_fieldman < 85 else 0.0

# Cálculo dinámico de efectividad EMT
efectividad_emt = (score_emt / 900.0) * 100.0
if penalidad_movilidad:
    st.sidebar.error(f"❌ EMT Fuera de Norma ({efectividad_emt:.1f}%): Penalidad Activa (-5.0 pts en Calidad).")
    base_calidad_lux = 55.7 - 5.0
else:
    st.sidebar.success(f"🟢 EMT Aprobado ({efectividad_emt:.1f}%): Proceso de Movilidad Validado.")
    base_calidad_lux = 55.7

if visitas_fieldman < 85: 
    st.sidebar.error("❌ Penalidad Ítem 3.5.7.a Activa (-40% Puntos Negativos en Posventa).")
else: 
    st.sidebar.success("🟢 Compromisos Fieldman a salvo (≥85%).")

if st.sidebar.button("🔄 Restablecer Valores Oficiales de Junio"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. BASE DE DATOS MATRICIAL: AJUSTADA A SÁBANA OFICIAL (LUX VS PUESTO 5 DPQ VS PUESTO 10 GON)
base_targets_lux = 55.1 - castigo_posventa_fieldman

data_transversal = {
    "Pilar Operativo (TASA)": ["Calidad", "Programas", "Recursos Humanos", "Facilities", "Targets"],
    "Autolux (LUX) - Puesto 24": [base_calidad_lux, 97.3, 91.9, 82.0, base_targets_lux],
    "DPQ - Puesto 5": [72.3, 97.3, 85.0, 82.0, 68.5],
    "GON - Puesto 10": [68.0, 97.3, 88.5, 82.0, 65.2]
}
df_bench = pd.DataFrame(data_transversal)

# Ponderaciones oficiales fijadas sobre el 100% global
pesos = {"Calidad": 22.0, "Programas": 8.8, "Recursos Humanos": 12.1, "Facilities": 7.5, "Targets": 44.5}
score_ponderado_lux = sum((df_bench.at[i, "Autolux (LUX) - Puesto 24"] / 100.0) * pesos[df_bench.at[i, "Pilar Operativo (TASA)"]] for i in range(len(df_bench)))
score_global_final = score_ponderado_lux - puntos_a_restar_global

# Cálculo dinámico del ranking móvil basado en la escala real
if score_global_final >= 62.0:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(1, puesto_calculado)
else:
    puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
    puesto_calculado = min(43, puesto_calculado)

# 4. CAPA DE PRESENTACIÓN EN PESTAÑAS (TABS)
tab_dashboard, tab_plan = st.tabs(["📊 Dashboard del Dealer", "📋 Plan de Acción & Descarga"])

with tab_dashboard:
    # 5. PANEL EJECUTIVO DE MÉTRICAS (KPI CARDS)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
    with col2: 
        status_icono = "🏆" if puesto_calculado <= 24 else "🚨"
        st.metric("Ranking General Red", f"Puesto {puesto_calculado} {status_icono}", delta="Brecha móvil real")
    with col3: st.metric("Eficiencia en Programas", f"{df_bench.at[1, 'Autolux (LUX) - Puesto 24']:.1f}%", delta="Colíderes de la Red TASA")
    with col4: 
        if score_global_final >= 90.0 and base_calidad_lux >= 70.0: categoria = "Categoría A 🥇"
        elif score_global_final >= 80.0 and base_calidad_lux >= 60.0: categoria = "Categoría B 🥈"
        elif score_global_final >= 70.0: categoria = "Categoría C 🥉"
        elif score_global_final >= 60.0: categoria = "Categoría D ⚠️"
        else: categoria = "Categoría E 🚨"
        st.metric("Estatus de Categoría", categoria)

    # MAPA CENTRAL DE CATEGORÍAS OPERATIVAS (ACU) SEGÚN AUDITORÍA
    st.divider()
    st.subheader("🗂️ Estructura Central de Capítulos Operativos (ACU - 900 pts)")
    st.markdown("Distribución modular de las auditorías semestrales Toyota 'Best in Town' integradas en el ecosistema:")
    
    col_acu1, col_acu2, col_acu3 = st.columns(3)
    with col_acu1:
        st.info("**Bloque Central e Infraestructura**\n*   **A:** Estructura Central (100 pts)\n*   **B:** Servicio al Cliente (100 pts)\n*   **D:** Club Toyota (100 pts)")
    with col_acu2:
        st.success("**Bloque Corporativo y Canales**\n*   **C:** Kinto Movilidad (100 pts)\n*   **E:** Toyota Plan de Ahorro (100 pts)\n*   **G:** Vehículos Usados (100 pts)")
    with col_acu3:
        st.warning("**Bloque de Operación y Ventas**\n*   **H:** Canal Convencional (100 pts)\n*   **F:** Toyota Financial Services (100 pts)\n*   **I:** Servicios Conectados (100 pts)")

    # 6. VISUALIZACIÓN GRÁFICA COMPARATIVA ACTUALIZADA
    st.subheader("🏁 Benchmarking de Desempeño: Autolux vs Líderes de la Red (DPQ y GON)")
    st.markdown("Comparación de efectividad por pilares para identificar las brechas operativas directas contra el Puesto 5 y el Puesto 10 de la red.")
    
    df_melted = df_bench.melt(id_vars=["Pilar Operativo (TASA)"], var_name="Concesionario", value_name="Efectividad %")
    fig_bench = px.bar(
        df_melted, x="Pilar Operativo (TASA)", y="Efectividad %", color="Concesionario",
        barmode="group", text_auto=".1f", title="Análisis de Brecha Operativa Cruzada (Cierre Junio)",
        color_discrete_map={"Autolux (LUX) - Puesto 24": "#d62728", "DPQ - Puesto 5": "#1f77b4", "GON - Puesto 10": "#7f7f7f"}
    )
    st.plotly_chart(fig_bench, use_container_width=True)

    # 7. DIAGNÓSTICO OPERATIVO Y CUENTAS PENDIENTES
    st.divider()
    st.subheader("🕵️ Cuellos de Botella Críticos Identificados a Junio")
    col_left, col_right = st.columns(2)
    with col_left:
        df_quejas = pd.DataFrame({
            "Motivo": ["Desadopción CRM / Cargas Ventas (36%)", "Kit Seguridad Entregas (28%)", "Regalo Comercial (20%)", "Cafetería Salón (16%)"], 
            "Impacto": [36.0, 28.0, 20.0, 16.0]
        })
        fig_pie = px.pie(df_quejas, values="Impacto", names="Motivo", color_discrete_sequence=px.colors.sequential.Reds_r)
        fig_pie.update_traces(textinfo="percent", textposition="inside")
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_right:
        st.markdown("""
        ### 📝 Puntos Clínicos a Revertir Urgente
        *   **Brecha en Calidad (-16.6% vs DPQ)**: El pilar Calidad sigue mostrando el mayor desvío competitivo. El puesto 5 (`DPQ`) tracciona un **72.3%** frente a nuestro **55.7%**.
        *   **Ventaja en Recursos Humanos (+6.9% vs DPQ)**: Autolux supera al Puesto 5 de la red en retención y planes de capacitación interna.
        *   **Oportunidad en Targets (-13.4% vs DPQ)**: El área comercial es clave. `DPQ` alcanza un **68.5%** en patentamientos; traccionar este pilar es lo que más nos acercará al Top 10.
        """)
with tab_plan:
    st.subheader("📋 Plan de Acción Operativo Homologado")
    plan_data = {
        "Área / Sector": ["CRM", "Calidad", "Calidad", "Calidad", "RRHH", "Facilities", "Posventa", "TCFA", "KINTO"],
        "Responsable Directo": ["A. Aguilar / L. de los Ríos", "A. Aguilar / P. Carrizo", "A. Aguilar / P. Carrizo", "A. Aguilar / P. Carrizo", "A. Di Costanzo / Equipo RRHH", "D. Colque / A. Di Costanzo", "Daniel Colque", "L. de los Ríos / Romina R.", "Aaron Martearena"],
        "Compromiso de Mejora (Acción Obligatoria)": [
            "Saneamiento urgente de Salesforce: responder prospectos < 2 hs y purgar boletos vencidos (Ítem 1.5.6).",
            "Incorporación regular de kits de seguridad como obsequio corporativo en cada entrega de unidad.",
            "Lanzamiento de campaña de fidelización con sorteos activos para revertir la nota de encuestas SSI.",
            "Compra e instalación inmediata de módulos de café para optimizar la experiencia en el showroom (Ítem 1.4.1).",
            "Incorporación de 2 colaboradores administrativos a declarar en nómina para blindar capacitación de Posventa.",
            "Negociación formal con el fieldman de TASA para reprogramar observaciones edilicias en Las Lajitas.",
            "Aumento en el ritmo de llamadas para acelerar el avance de las campañas de Airbags ABI 414/415.",
            "Revisión y reestructuración del método analítico para el cálculo de crecimiento de pólizas TCFA.",
            "Rediseño operativo del proceso de seguimiento de siniestros Kinto One integrado con el taller de Posventa."
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
