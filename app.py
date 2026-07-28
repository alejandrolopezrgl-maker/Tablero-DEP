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

# 3. VALORES PORCENTUALES REALES EXTRAÍDOS DIRECTAMENTE DEL REPORTE DE TASA (COLUMNA LUX)
base_ventas = 55.7 if not penalidad_movilidad else (55.7 - 5.0)
base_posventa = 91.7 - castigo_posventa_fieldman

df_areas = pd.DataFrame({
    "Área": ["Ventas", "Ventas Especiales", "Posventa", "TPA", "KINTO", "Usados", "TCFA", "ESG", "General"],
    "Cumplimiento %": [base_ventas, 49.0, base_posventa, 72.8, 35.8, 75.8, 73.0, 25.0, 67.6],
    "Estado": ["🔴 Crítico", "🔴 Crítico", "🟢 Excelente" if base_posventa >= 80 else "🟡 En Alerta", "🟢 Excelente", "🔴 Crítico", "🟡 En Alerta", "🟡 En Alerta", "🔴 Crítico", "🟡 Desviado"]
})

# FIJAMOS EL SCORE DE LA PLANILLA OFICIAL (62.0%) AFECTADO POR LOS BOTONES LATERALES
score_global_final = 62.0 - puntos_a_restar_global
if penalidad_movilidad:
    score_global_final -= 1.1

st.subheader("📉 Cumplimiento Real por Área Evaluada (Foto Oficial Consolidada)")
filtros = st.multiselect("🔍 Filtrar áreas específicas:", options=df_areas["Área"].unique(), default=[])
areas_activas = filtros if filtros else list(df_areas["Área"].unique())
df_plot_areas = df_areas[df_areas["Área"].isin(areas_activas)]

# AJUSTE ASOCIADO AL RANKING GENERAL SECO
if score_global_final >= 61.9 and not penalidad_movilidad and castigo_posventa_fieldman == 0 and puntos_a_restar_global == 0:
    label_ranking = "Puesto 24 🏆"
    categoria_dinamica = "Categoría C"
elif score_global_final < 60.0:
    label_ranking = "Puesto 39 🔻"
    categoria_dinamica = "Categoría D / E ⚠️"
else:
    label_ranking = "Puesto 28 🟡"
    categoria_dinamica = "Categoría C"

# 4. CUADRO DE MANDO PRINCIPAL
st.header("📌 Resumen Ejecutivo de Desvíos Autolux")
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Cumplimiento DEP Real", f"{score_global_final:.1f}%")
with col2: st.metric("Ranking General Red", label_ranking, delta="Puesto 4 en TPA 🏆")
with col3: st.metric("Pilar Posventa Real", f"{base_posventa:.1f}%")
with col4: st.metric("Estatus de Categoría", categoria_dinamica)

st.divider()
st.plotly_chart(px.bar(df_plot_areas, x="Área", y="Cumplimiento %", color="Estado", text_auto=".1f", color_discrete_map={"🟢 Excelente": "#2ca02c", "🟡 En Alerta": "#ff7f0e", "🔴 Crítico": "#d62728"}), use_container_width=True)

# 5. DIAGNÓSTICO DE CAUSA RAÍZ CON EXPLICACIÓN VISUAL INTEGRADA
st.divider()
st.subheader("🕵️ Análisis Operativo: Plan de Acción Comercial en Sucursales")
col_left, col_right = st.columns(2)

with col_left:
    # Agregamos los porcentajes directamente a las etiquetas de la leyenda para que no se corten
    df_quejas = pd.DataFrame({
        "Motivo de la Queja": [
            "Falta de Kit de Seguridad (36%)", 
            "Otros desvíos menores (28%)", 
            "Falta de Presentes / Merch (20%)", 
            "Falta de Máquina de Café (16%)"
        ],
        "Impacto %": [36.0, 28.0, 20.0, 16.0]
    })
    
    fig_pie = px.pie(
        df_quejas, 
        values="Impacto %", 
        names="Motivo de la Queja", 
        color_discrete_sequence=px.colors.sequential.Reds_r,
        title="Distribución de Quejas"
    )
    # Configuramos para mostrar únicamente los porcentajes adentro de la torta de forma prolija
    fig_pie.update_traces(textinfo="percent", textposition="inside", textfont_size=14)
    fig_pie.update_layout(showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02))
    
    st.plotly_chart(fig_pie, use_container_width=True)

with col_right:
    st.markdown("""
    ### 📝 Diagnóstico de Desvíos por Canales
    
    A la izquierda se observa la ponderación exacta obtenida de las auditorías físicas de campo:
    *   **Falta de Kit de Seguridad (36.0% de impacto)**: Representa el desvío más severo detectado en las entregas de Tartagal y Jujuy.
    *   **Falta de Presentes / Merch (20.0% de impacto)**: Quejas de clientes por unidades retiradas sin obsequios comerciales.
    *   **Falta de Máquina de Café (16.0% de impacto)**: Descontento focalizado en Posventa debido al retiro de amenities en salas de espera.
    *   **Otros desvíos menores (28.0% de impacto)**: Acumulado de observaciones de infraestructura bajo plan de acción.
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

# 6. PESTAÑAS DE HOJAS DE DATOS (REPORTE COMPLETO EMT)
st.divider()
st.subheader("📂 Consulta de Hojas de Datos (DEP & Auditoría EMT)")
pestaña = st.radio("Selecciona la pestaña a inspeccionar:", ["Resumen por Categorías", "Simulador Preventivo EMT"], horizontal=True)

if pestaña == "Resumen por Categorías":
    st.markdown("### 📊 Resumen por Grandes Grupos Ponderados")
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
    pct_emt = (tot_sim / 900) * 100

    df_emt = pd.DataFrame({
        "Macro-Capítulo EMT": ["A-Estructura", "B-Servicio", "C-Kinto", "D-Club", "E-TPA", "F-TFS", "G-Usados", "H-Convencional", "I-Conectados"],
        "Puntaje Simulado": p_list,
        "Estado": ["🟢 Conforme" if x > 0 else "🔴 Alerta" for x in p_list]
    })
    df_emt["Puntaje Maximo"] = 100
    df_emt = df_emt[["Macro-Capítulo EMT", "Puntaje Maximo", "Puntaje Simulado", "Estado"]]
    
    st.metric(label="🏆 NOTA CONSOLIDADA DE AUDITORÍA EMT SIMULADA", value=f"{tot_sim} / 900 Puntos", delta=f"{pct_emt:.1f}% Cumplimiento")
    st.dataframe(df_emt, use_container_width=True)
