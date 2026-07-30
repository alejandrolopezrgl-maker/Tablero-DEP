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

# Cálculo Dinámico y Exacto del Ranking
if score_global_final == 62.0:
    puesto_calculado = 24
elif score_global_final > 62.0:
    puesto_calculado = int(24 - ((score_global_final - 62.0) / (72.3 - 62.0)) * (24 - 5))
    puesto_calculado = max(1, puesto_calculado)
else:
    puesto_calculado = int(24 + ((62.0 - score_global_final) / 5.0) * 10)
    puesto_calculado = min(43, puesto_calculado)

# 4. CAPA DE PRESENTACIÓN EN PESTAÑAS (TABS)
tab_dashboard, tab_plan = st.tabs(["📊 Dashboard del Dealer", "📋 Plan de Acción Interactiva"])

with tab_dashboard:
    # 5. PANEL EJECUTIVO DE MÉTRICAS (KPI CARDS FIJAS CON POWER BI)
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
    with col2: 
        status_icono = "🏆" if puesto_calculado <= 24 else "🚨"
        st.metric("Ranking General Red", f"Puesto {puesto_calculado} {status_icono}", delta="Puesto 4 en TPA Red 🏆")
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
    fig_bench.update_layout(xaxis_title="Unidad / Canal", yaxis_title="Efectividad %", legend_title="Dealer")
    st.plotly_chart(fig_bench, use_container_width=True)

    # 7. AUDITORÍA INTERNA DE MOVIMIENTO TOYOTA (EMT - BOTONES DESLIZABLES AL FINAL)
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
    efectividad_emt = (score_total_emt / 900.0) * 100
    if efectividad_emt < 80.0:
        st.error(f"⚠️ Alerta EMT: Desempeño Global en {efectividad_emt:.1f}% (Riesgo de penalización).")
    else:
        st.success(f"🎉 Estándar EMT Asegurado: {score_total_emt} / 900 puntos ({efectividad_emt:.1f}% de cumplimiento).")
with tab_plan:
    st.subheader("📋 Planilla de Seguimiento y Control de Avances")
    
    if "tabla_acciones_dep" not in st.session_state:
        # Definición de las 19 filas de acciones (datos completos)
        data_rows = [
            ["Coordinación", "Alejandro López", "Centralizar seguimiento y tablero único.", "Reporte de avances", "Quincenal", "", "", "Pendiente"],
            ["Calidad", "A. Aguilar / P. Carrizo", "Incorporar kits de seguridad en entregas.", "Remitos", "Mensual", "", "", "Pendiente"],
            ["Calidad", "A. Aguilar / P. Carrizo", "Instalación de cafetería/termos.", "Fotos", "30 días", "", "", "Pendiente"],
            ["Calidad", "A. Aguilar / P. Carrizo", "Sorteos para encuestas TASA.", "Score TASA", "Mensual", "", "", "Pendiente"],
            ["Calidad", "A. Aguilar / P. Carrizo", "Mystery Shopper.", "Reporte", "Trimestral", "", "", "Pendiente"],
            ["Calidad", "A. Aguilar / P. Carrizo", "Tablero KPIs calidad.", "Tablero operativo", "45 días", "", "", "Pendiente"],
            ["Calidad", "A. Aguilar / P. Carrizo", "Proceso Usados Certificados.", "Documentación", "Quincenal", "", "", "Pendiente"],
            ["RRHH", "A. Di Costanzo / RRHH", "Incorporar 2 administrativos TPA.", "Alta AFIP", "Oct/Nov", "", "", "Pendiente"],
            ["RRHH", "A. Di Costanzo / RRHH", "Plan capacitación semestral.", "% cumplimiento", "Cierre Año", "", "", "Pendiente"],
            ["RRHH", "A. Di Costanzo / RRHH", "Estabilizar nómina.", "Índice rotación", "Mensual", "", "", "Pendiente"],
            ["Facilities", "D. Colque / A. Di Costanzo", "Obras Las Lajitas (fieldman).", "Minuta", "60 días", "", "", "Pendiente"],
            ["Facilities", "D. Colque / A. Di Costanzo", "Baja PN reformas Salta.", "Plan modificado", "Cierre Año", "", "", "Pendiente"],
            ["CRM", "A. Aguilar / L. de los Ríos", "Control diario boletos.", "Reporte", "Diario", "", "", "Pendiente"],
            ["CRM", "A. Aguilar / L. de los Ríos", "Respuesta < 2 horas.", "Dashboard", "Semanal", "", "", "Pendiente"],
            ["CRM", "A. Aguilar / L. de los Ríos", "Limpieza Salesforce.", "Auditoría", "Mensual", "", "", "Pendiente"],
            ["Posventa", "Daniel Colque", "Campaña Airbags (ABI 414/415).", "% avance", "Semanal", "", "", "Pendiente"],
            ["TCFA", "L. de los Ríos / Romina R.", "Cálculo crecimiento pólizas.", "Fórmula validada", "30 días", "", "", "Pendiente"],
            ["TCFA", "L. de los Ríos / Romina R.", "Activación App.", "Tasa activación", "Mensual", "", "", "Pendiente"],
            ["KINTO", "Aaron Martearena", "Proceso siniestros 'One'.", "Flujograma", "45 días", "", "", "Pendiente"]
        ]
        st.session_state.tabla_acciones_dep = pd.DataFrame(
            data_rows, 
            columns=["Área", "Responsables", "Acción", "Evidencia", "Fecha", "Comentarios", "Fecha Real", "Estado"]
        )

    # Editor y Filtro
    filtro_lider = st.selectbox("👤 Filtrar por Responsable:", ["Todos"] + sorted(list(st.session_state.tabla_acciones_dep["Responsables"].unique())))
    df_vista = st.session_state.tabla_acciones_dep
    if filtro_lider != "Todos": df_vista = df_vista[df_vista["Responsables"] == filtro_lider]

    df_editado = st.data_editor(
        df_vista,
        column_config={
            "Área": st.column_config.TextColumn(disabled=True),
            "Responsables": st.column_config.TextColumn(disabled=True),
            "Estado": st.column_config.SelectboxColumn(options=["Pendiente", "En Proceso", "Completado"], default="Pendiente")
        },
        use_container_width=True, key="data_editor_final"
    )

    if st.button("💾 Guardar Cambios"):
        st.session_state.tabla_acciones_dep.update(df_editado)
        st.success("🎉 Cambios guardados.")

    # Excel Generator
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state.tabla_acciones_dep.to_excel(writer, index=False)
        # Formato estilizado (Azul/Blanco)
        ws = writer.sheets['Sheet1']
        for cell in ws[1]: cell.fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid"); cell.font = Font(color="FFFFFF", bold=True)

    st.download_button("📥 Descargar Excel", buffer.getvalue(), "Plan_Accion_DEP.xlsx", "application/vnd.ms-excel")
