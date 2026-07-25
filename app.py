import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="DEP Autolux - Gestión de Desvíos", layout="wide", page_icon="🚗")

# Títulos de la Aplicación Operativa
st.title("📊 Tablero de Control de Desvíos DEP - Autolux")
st.caption("Ecosistema Integrado Mayo - Junio 2026 | Simulación de Penalizaciones Matemáticas en Tiempo Real")

# 2. BARRA LATERAL (SIDEBAR): CONTROL DE RIESGOS Y PENALIDADES DIRECTAS
st.sidebar.header("🚨 Zona Roja: Penalidades Directas")
st.sidebar.markdown("Interactúa con los filtros para ver el impacto matemático directo en el tablero:")

# Controles interactivos
penalidad_fair_play = st.sidebar.toggle("Fair Play Detectado (-10 pts directos)", value=False)
penalidad_movilidad = st.sidebar.toggle("Falta Certificación Estilo Movilidad (-5 pts)", value=False)
visitas_fieldman = st.sidebar.slider("% Cumplimiento Visitas Fieldman", 0, 100, 78)

# Lógica de cálculo de penalizadores y alertas visuales
puntos_a_restar_global = 0
penalizacion_posventa_activa = False

st.sidebar.divider()
st.sidebar.subheader("Estatus de Alertas")

if visitas_fieldman < 85:
    st.sidebar.error("❌ Penalidad Posventa Activa: Cumplimiento <85% genera castigo automático en Puntos Negativos (-40%).")
    penalizacion_posventa_activa = True
else:
    st.sidebar.success("🟢 Posventa a salvo del castigo de Fieldman (≥85%).")

if penalidad_fair_play:
    st.sidebar.error("🛑 Penalidad Fair Play Activa: -10 puntos automáticos sobre la nota general.")
    puntos_a_restar_global += 10

if penalidad_movilidad:
    st.sidebar.warning("⚠️ Penalidad Movilidad: -5 puntos directos por falta de certificación.")
    puntos_a_restar_global += 5

# 3. VALORES BASE OPERATIVOS DE AUTOLUX
score_global_base = 64.80
brecha_kinto_base = -45.60
brecha_posventa_nps_base = 1.00

# Aplicamos el impacto matemático de la barra lateral en tiempo real
score_global_calculado = score_global_base - puntos_a_restar_global
if penalizacion_posventa_activa:
    brecha_posventa_nps_base = brecha_posventa_nps_base - 40.00  # Castigo severo en el pilar por normas DEP

# Determinamos categoría final dinámica
if score_global_calculado >= 90:
    categoria_dinamica = "Categoría A"
    delta_color_cat = "normal"
elif score_global_calculado >= 80:
    categoria_dinamica = "Categoría B"
    delta_color_cat = "off"
else:
    categoria_dinamica = "Categoría C"
    delta_color_cat = "inverse"

# 4. CUADRO DE MANDO PRINCIPAL (KPI CARDS INTEGRADOS CON TUS FILTROS)
st.header("📌 Resumen Ejecutivo de Desvíos")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Ventas - SSI Acumulado", value="93.40%", delta="-2.20% vs Target (95.6%)", delta_color="inverse")
with col2:
    # Mostramos el impacto dinámico si se activa Fair Play o Movilidad afectando el Score General
    st.metric(label="Resultado Global Autolux", value=f"{score_global_calculado:.2f} pts", delta=f"-{puntos_a_restar_global} pts por penalidad" if puntos_a_restar_global > 0 else "Sin penalidad directa", delta_color="inverse" if puntos_a_restar_global > 0 else "normal")
with col3:
    st.metric(label="KINTO ONE - NPS", value="44.40%", delta=f"{brecha_kinto_base:.2f}% vs Target (90.0%)", delta_color="inverse")
with col4:
    st.metric(label="Categorización Dinámica DEP", value=categoria_dinamica, delta=f"Puesto 39 en el Ranking", delta_color=delta_color_cat)

st.divider()

# 5. GRÁFICO DE BRECHAS REACCIONANDO EN TIEMPO REAL
st.subheader("📉 Brecha de Calidad Real vs Target por Indicador (Puro y Acumulado)")

datos_junio = {
    "Área / KPI": ["PVT CSI", "PVT FIR", "PVT NPS", "VT SSI", "VT NPS", "TPA NPS t", "Usados SSI", "Usados NPS", "KINTO SHARE NPS", "KINTO ONE NPS"],
    "Brecha Real %": [0.90, 2.10, brecha_posventa_nps_base, -2.20, -8.90, -2.50, -10.37, -32.80, 5.90, brecha_kinto_base],
    "Estado": ["🟢 En Objetivo", "🟢 En Objetivo", "🟢 En Objetivo" if brecha_posventa_nps_base >= 0 else "🔴 Castigado por Fieldman", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🔴 Desviado", "🟢 En Objetivo", "🔴 Desviado"]
}
df_junio = pd.DataFrame(datos_junio)

fig_brechas = px.bar(
    df_junio,
    x="Área / KPI",
    y="Brecha Real %",
    color="Estado",
    text_auto=".2f",
    color_discrete_map={"🟢 En Objetivo": "#2ca02c", "🔴 Desviado": "#d62728", "🔴 Castigado por Fieldman": "#7f1d1d"},
    title="Análisis Dinámico de Brechas (El pilar PVT NPS se desplomará si bajas el cumplimiento de Visitas Fieldman <85%)"
)
st.plotly_chart(fig_brechas, use_container_width=True)

if puntos_a_restar_global > 0 or penalizacion_posventa_activa:
    st.error(f"⚠️ **Simulador de Auditoría:** El puntaje actual refleja un descuento activo de -{puntos_a_restar_global} puntos directos y/o penalizaciones estructurales por fallas de cumplimiento normativo.")
else:
    st.warning("💡 **Acción Comercial Urgente:** Se necesitan **55 encuestas perfectas (SSI 100)** en Ventas y **31 encuestas perfectas** en Usados para neutralizar la brecha actual.")

st.divider()

# 6. ANÁLISIS DE CAUSA RAÍZ (LA VOZ DEL CLIENTE)
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

# 7. MONITOREO DEL PLAN DE ACCIÓN COMERCIAL 2026
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

# 8. CONSOLIDADO DE TUS PESTAÑAS DEL EXCEL (INYECCIÓN NATIVA INTERACTIVA)
st.subheader("📂 Consulta de Hojas de Datos (DEP 2026)")

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
    # Reflejamos dinámicamente si hay penalizaciones en la tabla de datos inyectada
    puntos_ventas = 45.20 - (10 if penalidad_fair_play else 0)
    datos_area = {
        "Pilar DEP": ["Ventas (Core)", "Ventas Especiales", "Posventa (Calidad)", "TPA (Ahorro)", "KINTO", "Usados", "TCFA", "ESG", "General"],
        "Ponderación Oficial": ["22.00%", "5.00%", "27.00%", "9.00%", "6.00%", "6.00%", "4.00%", "1.00%", "20.00%"],
        "Puntaje Obtenido (Mayo)": [puntos_ventas, 80.00, 94.70, 72.10, 0.00, 0.00, 100.00, 100.00, 85.00],
        "Desvío Detectado": ["🔴 Castigado por Fair Play" if penalidad_fair_play else "🔴 Severo por SSI/NPS", "🟢 En Objetivo", "🟢 Destacado (CSI 94.7)", "🔴 Bajo Mínimo", "🛑 Penalización 0", "🛑 Penalización 0", "🟢 Óptimo", "🟢 Óptimo", "🟡 Alerta"]
    }
    st.dataframe(pd.DataFrame(datos_area), use_container_width=True)

elif pestaña_seleccionada == "MAY-CATEGORIA":
    datos_cat = {
        "Evaluación General": ["Puntaje Global Requerido", "Mínimo Ventas", "Mínimo Posventa", "Resultado Global Autolux"],
        "Condición Manual DEP": ["≥ 90.00 Puntos (Cat. A)", "≥ 80.00 Puntos", "≥ 70.00 Puntos", f"{score_global_calculado:.2f} Puntos"],
        "Situación Actual": ["🔴 Fuera de Rango", "🔴 Incumplido" if penalidad_fair_play else "🔴 Incumplido (Faltan 55 Encuestas)", "🟢 Cumplido" if not penalizacion_posventa_activa else "🔴 Caído por Fieldman", f"❌ {categoria_dinamica} (Puesto 39)"]
    }
    st.dataframe(pd.DataFrame(datos_cat), use_container_width=True)
