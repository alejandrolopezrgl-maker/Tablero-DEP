import streamlit as st
import pandas as pd
import plotly.express as px
import io
from openpyxl.styles import Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")
st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Sincronizado con Reporte Oficial de TASA (Puesto 24 Cerrado)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

st.sidebar.header("🚨 Zona de Control DEP")
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
castigo_posventa_fieldman = 10.8 if visitas_fieldman < 85 else 0

if visitas_fieldman < 85: st.sidebar.error("❌ Penalidad Posventa Activa (-10.8%).")
else: st.sidebar.success("🟢 Posventa a salvo (≥85%).")

if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

base_ventas = 55.7 if not penalidad_movilidad else (55.7 - 5.0)
base_posventa = 91.7 - castigo_posventa_fieldman

df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [base_ventas, 49.0, base_posventa, 72.8, 35.8, 75.8, 73.0, 25.0, 67.6],
    "Estado": ["🔴 Crítico", "🔴 Crítico", "🟢 Excelente" if base_posventa >= 80 else "🟡 En Alerta", "🟢 Excelente", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

score_global_final = 62.0 - puntos_a_restar_global
if penalidad_movilidad: score_global_final -= 1.1

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
with col2: st.metric("Ranking General Red", "Puesto 24 🏆" if score_global_final >= 61.9 else "Puesto 28 🟡", delta="Puesto 4 en TPA 🏆")
with col3: st.metric("Pilar Posventa Real", f"{base_posventa:.1f}%")
with col4: st.metric("Estatus de Categoría", "Categoría C" if score_global_final >= 60.0 else "Categoría D/E ⚠️")

st.divider()
filtros = st.multiselect("🔍 Filtrar áreas específicas:", options=df_areas["Área"].unique(), default=[])
df_plot_areas = df_areas[df_areas["Área"].isin(filtros)] if filtros else df_areas
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 En Alerta": "#ff7f0e", "🔴 Crítico": "#d62728"}), use_container_width=True)

st.divider()
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
col_left, col_right = st.columns(2)
with col_left:
    df_quejas = pd.DataFrame({"Motivo": ["Falta Kit Seguridad (36%)", "Otros desvíos (28%)", "Falta Merch (20%)", "Falta Máquina Café (16%)"], "Impacto": [36.0, 28.0, 20.0, 16.0]})
    fig_pie = px.pie(df_quejas, values="Impacto", names="Motivo", color_discrete_sequence=px.colors.sequential.Reds_r, title="Distribución de Quejas")
    fig_pie.update_traces(textinfo="percent", textposition="inside", textfont_size=14)
    st.plotly_chart(fig_pie, use_container_width=True)
with col_right:
    st.markdown("""
    ### 📝 Diagnóstico de Desvíos por Canales
    *   **Falta de Kit de Seguridad (36.0%)**: Desvío más severo detectado en Tartagal y Jujuy.
    *   **Falta de Presentes / Merch (20.0%)**: Quejas por unidades retiradas sin obsequios.
    *   **Falta de Máquina de Café (16.0%)**: Descontento focalizado en salas de espera de Posventa.
    """)

st.subheader("📋 Plan de Acción Comercial")
plan_data = {
    "Sucursal": ["Salta - Jujuy - Tartagal", "Salta - Jujuy", "Salta - Jujuy - Tartagal"],
    "Sector": ["Comercial", "USI", "Posventa"],
    "Problema Detected": ["Unidades sin obsequio", "Falta stock y presupuesto", "Retiro de máquina de café"],
    "Causa Raíz": ["Demoras administrativas", "Ausencia de presupuesto fijo", "Optimización de costos errónea"],
    "Acción Obligatoria": ["Consultar kits alternativos", "Implementar propuesta de presupuesto fijo", "Restaurar máquina de café"],
    "Responsable": ["Asesores UCT", "Gerencia Comercial", "Responsable Posventa"],
    "Estatus Actual": ["En Proceso", "Pendiente", "Restablecido"]
}
df_plan = pd.DataFrame(plan_data)
st.dataframe(df_plan, use_container_width=True)

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
    df_plan.to_excel(writer, sheet_name='Plan de Accion', index=False)
    worksheet = writer.sheets['Plan de Accion']
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

st.download_button(label="📥 Descargar Plan de Acción Comercial (.xlsx)", data=buffer.getvalue(), file_name="Plan_de_Accion_Autolux.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# 6. PESTAÑAS DE HOJAS DE DATOS (REPORTE COMPLETO EMT CON CONTROL ULTRA LIVIANO)
st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")
pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.dataframe(df_areas[["Área", "Cumplimiento %", "Estado"]], use_container_width=True)
else:
    st.markdown("### 📋 Simulador Oficial EMT - Estilo de Movilidad TOYOTA (Target Septiembre)")
    st.caption("Ajusta el puntaje total obtenido en la auditoría sobre la base de 900 puntos máximos oficiales:")
    
    # Barra de control ultra liviana de carga instantánea
    puntaje_real_emt = st.slider("📊 Selecciona el Puntaje Total Obtenido:", min_value=0, max_value=900, value=900, step=5)
    
    pct_emt = (puntaje_real_emt / 900) * 100
    
    st.metric(label="🏆 NOTA CONSOLIDADA DE AUDITORÍA EMT SIMULADA", value=f"{puntaje_real_emt} / 900 Puntos", delta=f"{pct_emt:.1f}% Cumplimiento")
    
    # Gran recuadro de estado dinámico según los criterios de Toyota
    st.markdown("#### 🎯 Estatus de Aprobación de la Marca")
    if pct_emt == 100.0:
        st.success(f"🏆 **Puntaje Perfecto:** {puntaje_real_emt} Puntos — **{pct_emt:.1f}%**. Escenario base ideal sin observaciones.")
    elif pct_emt >= 90.0:
        st.info(f"🟢 **Zona Conforme:** {puntaje_real_emt} Puntos — **{pct_emt:.1f}%**. Perfil apto para aprobación directa de TASA.")
    elif pct_emt >= 75.0:
        st.warning(f"🟡 **Zona de Alerta:** {puntaje_real_emt} Puntos — **{pct_emt:.1f}%**. Se detectan desvíos operativos leves a corregir.")
    else:
        st.error(f"🔴 **Alerta Crítica:** {puntaje_real_emt} Puntos — **{pct_emt:.1f}%**. El concesionario requiere contramedidas urgentes.")
