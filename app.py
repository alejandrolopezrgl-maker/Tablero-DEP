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
    fig_pie = px.pie(df_quejas, values="Impacto", names="Motivo", color_discrete_sequence=px.colors.sequential.Reds_r)
    fig_pie.update_traces(textinfo="percent", textposition="inside", textfont_size=14)
    st.plotly_chart(fig_pie, use_container_width=True)
with col_right:
    st.markdown("* **Área Ventas (55.7%)**: Kits en Tartagal y Jujuy contuvieron las encuestas.\n* **Focos Críticos**: Ventas Especiales (49.0%) y KINTO (35.8%) demorados por unidades corporativas.")

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
    for col_num, h_name in enumerate(df_plan.columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
        cell.fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
        cell.border = Border(left=Side(style='thin', color='BFBFBF'), right=Side(style='thin', color='BFBFBF'), top=Side(style='thin', color='BFBFBF'), bottom=Side(style='thin', color='BFBFBF'))
    for row in worksheet.iter_rows(min_row=2, max_row=len(df_plan)+1, min_col=1, max_col=len(df_plan.columns)):
        for cell in row:
            cell.border = Border(left=Side(style='thin', color='BFBFBF'), right=Side(style='thin', color='BFBFBF'), top=Side(style='thin', color='BFBFBF'), bottom=Side(style='thin', color='BFBFBF'))
            cell.font = Font(name='Arial', size=10)
    for col in worksheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        worksheet.column_dimensions[get_column_letter(col.column)].width = max(max_len + 3, 12)

st.download_button(label="📥 Descargar Plan de Acción Comercial (.xlsx)", data=buffer.getvalue(), file_name="Plan_de_Accion_Autolux.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")
pestaña = st.radio("Selecciona pestaña:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.dataframe(df_areas[["Área", "Cumplimiento %", "Estado"]], use_container_width=True)
else:
    st.markdown("### 🎯 Módulo de Preparación EMT - 900 Puntos")
    c_a, c_b, c_c = st.columns(3)
    with c_a: sim_est = st.selectbox("Área A - Estructura Central:", ["🟢 Conforme", "🔴 Alerta"])
    with c_b: sim_ser = st.selectbox("Área B - Servicio al Cliente:", ["🟢 Conforme", "🔴 Alerta"])
    with c_c: sim_kin = st.selectbox("Área C - KINTO:", ["🟢 Conforme", "🔴 Alerta"])
    c_d, c_e, c_f = st.columns(3)
    with c_d: sim_clb = st.selectbox("Área D - Club Toyota:", ["🟢 Conforme", "🔴 Alerta"])
    with c_e: sim_tpa = st.selectbox("Área E - Toyota Plan (TPA):", ["🟢 Conforme", "🔴 Alerta"])
    with c_f: sim_tfs = st.selectbox("Área F - Financial (TCFA):", ["🟢 Conforme", "🔴 Alerta"])
    c_g, c_h, c_i = st.columns(3)
    with c_g: sim_usd = st.selectbox("Área G - Usados:", ["🟢 Conforme", "🔴 Alerta"])
    with c_h: sim_dig = st.selectbox("Área H - Convencional (Ventas):", ["🟢 Conforme", "🔴 Alerta"])
    with c_i: sim_con = st.selectbox("Área I - Servicios Conectados:", ["🟢 Conforme", "🔴 Alerta"])

    p_list = [100 if "🟢" in s else 0 for s in [sim_est, sim_ser, sim_kin, sim_clb, sim_tpa, sim_tfs, sim_usd, sim_dig, sim_con]]
    tot_sim = sum(p_list)
    
    df_emt = pd.DataFrame({"Macro-Capítulo EMT": ["A-Estructura", "B-Servicio", "C-Kinto", "D-Club", "E-TPA", "F-TFS", "G-Usados", "H-Convencional", "I-Conectados"], "Puntaje Simulado": p_list, "Estado": ["🟢 Conforme" if x > 0 else "🔴 Alerta" for x in p_list]})
    df_emt["Puntaje Maximo"] = 100
    df_emt = df_emt[["Macro-Capítulo EMT", "Puntaje Maximo", "Puntaje Simulado", "Estado"]]
    st.metric(label="🏆 NOTA CONSOLIDADA DE AUDITORÍA EMT SIMULADA", value=f"{tot_sim} / 900 Puntos", delta=f"{(tot_sim / 900) * 100:.1f}% Cumplimiento")
    st.dataframe(df_emt, use_container_width=True)
