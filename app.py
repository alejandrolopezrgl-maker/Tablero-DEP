import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

# Títulos de la Aplicación Operativa
st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado Mayo - Junio 2026 | Datos Consolidados sin Dependencia de Red")

# 2. BARRA LATERAL (SIDEBAR): CONTROL DE RIESGOS Y PENALIDADES DIRECTAS
st.sidebar.header("🚨 Zona Roja: Penalidades Directas")
st.sidebar.markdown("Filtros dinámicos basados en penalidades activas según reporte:")

penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=False)
penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=False)
visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, 78)

st.sidebar.divider()
st.sidebar.subheader("Estatus de Alertas")
if visitas_fieldman < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa: Cumplimiento <85% genera castigo en Puntos Negativos del área.")
if penalidad_fair_play:
    st.sidebar.error("🛑 Penalidad Fair Play Activa: -10 puntos automáticos sobre la nota general.")
if penalidad_movilidad:
    st.sidebar.warning("⚠️ Penalidad Movilidad: -5 puntos directos por falta de certificación.")

# 3. CUADRO DE MANDO PRINCIPAL (KPI CARDS REALES A JUNIO)
st.header("📌 Resumen Ejecutivo de Desvíos")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Ventas - SSI Acumulado", value="93.40%", delta="-2.20% vs Target (95.6%)", delta_color="inverse")
with col2:
    st.metric(label="Ventas - NPS Comercial", value="78.10%", delta="-8.90% vs Target (87.0%)", delta_color="inverse")
with col3:
    st.metric(label="KINTO ONE - NPS", value="44.40%", delta="-45.60% vs Target (90.0%)", delta_color="inverse")
with col4:
    st.metric(label="Evolución de Ranking Calidad", value="Puesto 39 🔻", delta="Desplome desde el Puesto 8", delta_color="inverse")

st.divider()

# 4. GRÁFICO DE BRECHAS REALES (TABLA DE INDICADORES DE JUNIO)
st.subheader("📉 Brecha de Calidad Real vs Target por Indicador (Puro y Acumulado)")

datos_junio = {
    "Área / KPI": ["PVT CSI", "PVT FIR", "PVT NPS", "VT SSI", "VT NPS", "TPA NPS t", "Usados SSI", "Usados NPS", "KINTO SHARE NPS", "KINTO ONE NPS"],
    "Brecha Real %": [0.90, 2.10, 1.00, -2.20, -8.90, -2.50, -10.37, -32.80, 5.90, -45.60],
    "Estado": ["🟢 En Objetivo", "🟢 En Objetivo", "🟢 En Objetivo", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🟢 En Objetivo", "🔴 Desviado"]
}
df_junio = pd.DataFrame(datos_junio)

fig_brechas = px.bar(
    df_junio,
    x="Área / KPI",
    y="Brecha Real %",
    color="Estado",
    text_auto=".2f",
    color_discrete_map={"🟢 En Objetivo": "#2ca02c", "🔴 Desviado": "#d62728"},
    title="Análisis de Brechas a Junio (Valores negativos indican desvíos críticos bajo la meta)"
)
st.plotly_chart(fig_brechas, use_container_width=True)

st.warning("💡 **Acción Comercial Urgente:** Se necesitan **55 encuestas perfectas (SSI 100)** en Ventas y **31 encuestas perfectas** en Usados para neutralizar la brecha actual.")

st.divider()

# 5. ANÁLISIS DE CAUSA RAÍZ (LA VOZ DEL CLIENTE)
st.subheader("🕵️ Causa Raíz Física: El Deterioro de la Experiencia en Sucursal")
col_graf, col_txt = st.columns(2)

with col_graf:
    datos_quejas = {
        "Motivo de la Queja": ["Falta de Kit de Seguridad", "Falta de Presentes / Merchandising", "Falta de Máquina de Café"],
        "Impacto %": [36.0, 20.0, 16.0]
    }
    df_quejas = pd.DataFrame(datos_quejas)
    fig_quejas = px.pie(
        df_quejas, 
        values="Impacto %", 
        names="Motivo de la Queja", 
        color_discrete_sequence=px.colors.sequential.Reds_r,
        title="Distribución del 72% de las Quejas de Clientes"
    )
    st.plotly_chart(fig_quejas, use_container_width=True)

with col_txt:
    st.markdown("""
    **Verbatines Clave de Clientes (Salta / Tartagal):**
    *   *“Me dan el auto y ya no te dan ni un miserable kit de seguridad.”*
    *   *“En Salta me regalaron de todo... en Tartagal no me dieron ni un vaso de agua.”*
    *   *“Sacaron la máquina de café del lugar de espera, una actitud totalmente miserable.”*
    
    👉 **Diagnóstico de Dirección:** La caída en la nota no se debe a fallas del vehículo, sino a la percepción de **'pérdida de beneficios de cortesía'** debido a trabas burocráticas internas.
    """)

st.divider()

# 6. MONITOREO DEL PLAN DE ACCIÓN COMERCIAL 2026
st.subheader("📋 Plan de Acción Comercial - Seguimiento Operativo")

plan_data = {
    "Sucursal": ["Salta - Jujuy - Tartagal", "Salta - Jujuy", "Salta - Jujuy - Tartagal"],
    "Sector": ["Comercial", "USI", "Posventa"],
    "Problema Detectado": ["Unidades retiradas sin obsequio de entrega", "Falta de stock y de aprobación de presupuestos", "Retiro de máquina de café en salas de espera"],
    "Causa Raíz": ["Demoras en circuito administrativo de aprobación", "Falta de fluidez y ausencia de presupuesto fijo", "Optimización de costos mal orientada"],
    "Acción Correctiva Obligatoria": ["Consultar presupuesto de kits de seguridad alternativos", "Diseñar e implementar propuesta de presupuesto fijo", "Restaurar servicio de amenities y máquina de café"],
    "Responsable": ["Asesores UCT / Resp. Comercial", "Gerencia Comercial", "Responsable Posventa"],
    "Estatus Actual": ["En Proceso", "Pendiente", "Restablecido"]
}
df_plan = pd.DataFrame(plan_data)
st.dataframe(df_plan, use_container_width=True)

st.divider()

# 7. CONSOLIDADO DE TUS PESTAÑAS DEL EXCEL (INYECCIÓN NATIVA)
st.subheader("📂 Consulta de Hojas de Datos (DEP 2026)")
st.info("Visualización integrada de tus registros oficiales para el análisis de gestión.")

pestaña_seleccionada = st.radio("Selecciona la pestaña a inspeccionar:", ["COM", "MAY-AREA", "MAY-CATEGORIA"], horizontal=True)

if pestaña_seleccionada == "COM":
    datos_com = {
        "Indicador Crítico": ["SSI Ventas (Comercial)", "NPS Ventas", "NPS TPA Transaccional", "SSI Usados", "NPS KINTO ONE"],
        "Meta Target": [95.60, 87.00, 85.00, 94.50, 90.00],
        "Resultado Mayo": [0.00, 75.20, 81.00, 0.00, 0.00],
        "Resultado Junio": [93.40, 78.10, 82.50, 84.13, 44.40],
        "Estatus Mayo-Junio": ["🔴 Crítico (Nota 0)", "🔴 Desviado", "🔴 Desviado", "🔴 Crítico (Nota 0)", "🔴 Brecha Máxima"]
    }
    st.dataframe(pd.DataFrame(datos_com), use_container_width=True)

elif pestaña_seleccionada == "MAY-AREA":
    datos_area = {
        "Pilar DEP": ["Ventas (Core)", "Ventas Especiales", "Posventa (Calidad)", "TPA (Ahorro)", "KINTO", "Usados", "TCFA", "ESG", "General"],
        "Ponderación Oficial": ["22.00%", "5.00%", "27.00%", "9.00%", "6.00%", "6.00%", "4.00%", "1.00%", "20.00%"],
        "Puntaje Obtenido (Mayo)": [45.20, 80.00, 94.70, 72.10, 0.00, 0.00, 100.00, 100.00, 85.00],
        "Desvío Detectado": ["🔴 Severo por SSI/NPS", "🟢 En Objetivo", "🟢 Destacado (CSI 94.7)", "🔴 Bajo Mínimo", "🛑 Penalización 0", "🛑 Penalización 0", "🟢 Óptimo", "🟢 Óptimo", "🟡 Alerta"]
    }
    st.dataframe(pd.DataFrame(datos_area), use_container_width=True)

elif pestaña_seleccionada == "MAY-CATEGORIA":
    datos_cat = {
        "Evaluación General": ["Puntaje Global Requerido", "Mínimo Ventas", "Mínimo Posventa", "Resultado Global Autolux"],
        "Condición Manual DEP": ["≥ 90.00 Puntos (Cat. A)", "≥ 80.00 Puntos", "≥ 70.00 Puntos", "64.80 Puntos"],
        "Situación Actual": ["🔴 Fuera de Rango", "🔴 Incumplido (Faltan 55 Encuestas)", "🟢 Cumplido", "❌ Categoría C (Puesto 39)"]
    }
    st.dataframe(pd.DataFrame(datos_cat), use_container_width=True)
