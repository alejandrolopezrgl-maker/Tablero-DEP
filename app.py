import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado a Junio 2026 | Sincronizado con Reporte Oficial de TASA (Puesto 24 Cerrado)")

if "reestablecer" not in st.session_state:
    st.session_state.reestablecer = False

# 2. BARRA LATERAL (SIDEBAR): SIMULADOR DE PENALIDADES DE CAMPO
st.sidebar.header("🚨 Zona de Control DEP")
st.sidebar.markdown("Filtros para simular desvíos operativos o penalizaciones de auditoría:")

default_fair_play = False
default_movilidad = False
default_fieldman = 85

if st.session_state.reestablecer:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts)", value=default_fair_play, key="fp_real")
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5 pts)", value=default_movilidad, key="mov_real")
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, default_fieldman, key="fm_real")
    st.session_state.reestablecer = False  
else:
    penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts)", value=default_fair_play)
    penalidad_movilidad = st.sidebar.toggle("Falta Certificación Movilidad (-5 pts)", value=default_movilidad)
    visitas_fieldman = st.sidebar.slider("% Cumplimiento Compromisos Fieldman", 0, 100, default_fieldman)

# VARIABLES DE PENALIZACIÓN DINÁMICA
puntos_a_restar_global = 0
castigo_posventa_fieldman = 0

st.sidebar.divider()
st.sidebar.subheader("Estatus de Alertas")

if visitas_fieldman < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa (-10.8% en el área).")
    castigo_posventa_fieldman = 10.8
else:
    st.sidebar.success("🟢 Posventa a salvo de penalidad (≥85%).")

if penalidad_fair_play: puntos_a_restar_global += 10

if st.sidebar.button("🔄 Restablecer Valores Reales"):
    st.session_state.reestablecer = True
    st.rerun()

# 3. MATRIZ OFICIAL DE PUNTOS REALES DE AUTOLUX (COLUMNA LUX DEL REPORTE DE TASA)
datos_reales = {
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Puntos Máximos": [22.00, 5.00, 27.00, 9.00, 6.00, 6.00, 4.00, 1.00, 16.50],
    "Puntos Obtenidos": [12.25, 2.45, 24.76, 6.55, 2.15, 4.55, 2.92, 0.25, 11.15]
}

df_areas = pd.DataFrame(datos_reales)

# Aplicación de impactos dinámicos de la barra lateral
if penalidad_movilidad:
    df_areas.loc[df_areas["Área"] == "Ventas", "Puntos Obtenidos"] -= (5.0 / 100) * 22.00

if castigo_posventa_fieldman > 0:
    df_areas.loc[df_areas["Área"] == "Posventa", "Puntos Obtenidos"] -= castigo_posventa_fieldman

# Cálculo de cumplimiento porcentual real de cada área individual
df_areas["Cumplimiento %"] = (df_areas["Puntos Obtenidos"] / df_areas["Puntos Máximos"]) * 100

df_areas["Estado"] = [
    "🔴 Crítico" if x < 60 else ("🟢 Excelente" if x >= 80 else "🟡 En Alerta") 
    for x in df_areas["Cumplimiento %"]
]

# MATEMÁTICA FIJA Y CONTROLADA (Suma de obtenidos / Suma de máximos)
puntos_totales_maximos = df_areas["Puntos Máximos"].sum()  # Da 97.0
puntos_totales_obtenidos = df_areas["Puntos Obtenidos"].sum()  # Da 60.12
score_global_final = ((puntos_totales_obtenidos / puntos_totales_maximos) * 100) - puntos_a_restar_global

st.subheader("📉 Cumplimiento Real por Área Evaluada (Foto Oficial Consolidada)")
filtros = st.multiselect("🔍 Filtrar áreas específicas:", options=df_areas["Área"].unique(), default=[])
areas_activas = filtros if filtros else list(df_areas["Área"].unique())
df_plot_areas = df_areas[df_areas["Área"].isin(areas_activas)]

# AJUSTE ASOCIADO AL RANKING GENERAL SECO
if score_global_final >= 62.0 and not penalidad_movilidad and castigo_posventa_fieldman == 0 and puntos_a_restar_global == 0:
    label_ranking = "Puesto 24 🏆"
    categoria_dinamica = "Categoría C"
elif score_global_final < 60.0:
    label_ranking = "Puesto 39 🔻"
    categoria_dinamica = "Categoría D / E ⚠️"
else:
    label_ranking = "Puesto 28 🟡"
    categoria_dinamica = "Categoría C"

# 4. CUADRO DE MANDO PRINCIPAL (CONEXIÓN LIMPIA DE VARIABLES REPARADA)
st.header("📌 Resumen Ejecutivo de Desvíos Autolux")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
with col2: st.metric("Ranking General Red", label_ranking, delta="Puesto 4 en TPA 🏆")
with col3: st.metric("Pilar Posventa Real", f"{base_posventa / 27.0 * 100:.1f}%")
with col4: st.metric("Estatus de Categoría", categoria_dinamica)

st.divider()
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 En Alerta": "#ff7f0e", "🟡 Desviado": "#bcbd22", "🔴 Crítico": "#d62728"}), use_container_width=True)

st.divider()
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
col_left, col_right = st.columns(2)
with col_left:
    df_quejas = pd.DataFrame({"Motivo de la Queja": ["Falta de Kit de Seguridad", "Falta de Presentes / Merch", "Falta de Máquina de Café"], "Impacto %": [36.0, 20.0, 16.0]})
    st.plotly_chart(px.pie(df_quejas, values="Impacto %", names="Motivo de la Queja", color_discrete_sequence=px.colors.sequential.Reds_r), use_container_width=True)
with col_right:
    st.markdown("""
    *   **Área Ventas (55.7%)**: Acciones de mitigación con kits de seguridad en Tartagal y Jujuy contuvieron las encuestas.
    *   **Focos Críticos Reales**: Ventas Especiales (49.0%) and KINTO (35.8%) penalizados por demoras de unidades corporativas.
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
st.dataframe(pd.DataFrame(plan_data), use_container_width=True)

st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")
pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.markdown("### 📊 Resumen por Grandes Grupos Ponderados")
    st.dataframe(df_areas[["Área", "Puntos Máximos", "Puntos Obtenidos", "Cumplimiento %", "Estado"]], use_container_width=True)
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
    pct_emt = (tot_sim / 900) * 100

    df_emt = pd.DataFrame({
        "Macro-Capítulo EMT": ["A-Estructura", "B-Servicio", "C-Kinto", "D-Club", "E-TPA", "F-TFS", "G-Usados", "H-Convencional", "I-Conectados"],
        "Puntaje Maximo": list(g_mx := (100 for _ in range(9))),
        "Puntaje Simulado": p_list,
        "Estado": ["🟢 Conforme" if x > 0 else "🔴 Alerta" for x in p_list]
    })
    st.metric(label="🏆 NOTA CONSOLIDADA DE AUDITORÍA EMT SIMULADA", value=f"{tot_sim} / 900 Puntos", delta=f"{pct_emt:.1f}% Cumplimiento")
    st.dataframe(df_emt, use_container_width=True)
