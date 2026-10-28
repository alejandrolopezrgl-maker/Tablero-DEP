import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Autolux - Tablero Estratégico DEP", 
    layout="wide",
    page_icon="🏆"
)

st.title("🏆 Autolux S.A. - Tablero Estratégico DEP 2026")
st.caption("Programa de Excelencia de Concesionarios Toyota (DEP) | Auditoría Oficial Septiembre & Proyección Octubre")

# --- NAVEGACIÓN PRINCIPAL (5 PESTAÑAS ESTRATÉGICAS) ---
tabs = st.tabs([
    "📊 Comparativo Puesto 5 y 10",
    "🔮 Proyección Octubre 2026",
    "📈 Evolución Histórica (Jul-Ago-Sep-Oct)",
    "🔍 Auditoría Real Septiembre",
    "🎯 Plan Táctico de Cierre Q4"
])

# ==========================================
# 1. COMPARATIVO PUESTO 5 Y 10
# ==========================================
with tabs[0]:
    st.subheader("Dashboard Comparativo: Autolux vs. Puesto 10 y Puesto 5 (Cierre Septiembre)")
    
    # Métricas principales de brecha
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Autolux Actual", "68,05 pts (70,52%)", "Puesto #26")
    c2.metric("Puesto 10 (Prana)", "75,18 pts (77,91%)", "Línea Top 10")
    c3.metric("Faltante para Puesto 10", "-7,13 pts", "-7,38 p.p. de cumplimiento", delta_color="inverse")
    c4.metric("Faltante para Puesto 5 (Sakura)", "-10,42 pts", "78,47 pts (-10,80 p.p.)", delta_color="inverse")

    st.markdown("---")

    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        st.write("#### Brecha de Puntos Totales")
        df_bench_total = pd.DataFrame([
            {"Entidad": "Autolux (Actual)", "Puntos": 68.05, "Puesto": "#26", "Color": "#3498db"},
            {"Entidad": "Puesto 10 (Prana)", "Puntos": 75.18, "Puesto": "#10", "Color": "#f39c12"},
            {"Entidad": "Puesto 5 (Sakura)", "Puntos": 78.47, "Puesto": "#5", "Color": "#2ecc71"}
        ])
        fig_bench_total = px.bar(
            df_bench_total, 
            x="Entidad", 
            y="Puntos", 
            text="Puntos",
            color="Entidad", 
            color_discrete_map={r["Entidad"]: r["Color"] for _, r in df_bench_total.iterrows()}
        )
        fig_bench_total.update_traces(
            texttemplate="%{text:.2f} pts", 
            textposition="inside",
            textfont=dict(size=14, color="white", family="Arial Black")
        )
        fig_bench_total.update_layout(showlegend=False, yaxis_range=[50, 85], yaxis_title="Puntos DEP")
        st.plotly_chart(fig_bench_total, use_container_width=True)

    with col_g2:
        st.write("#### Hallazgo Clave: ¿Dónde está la brecha?")
        st.success("""
        * **Autolux supera a Prana (Puesto 10) en 6 de las 9 áreas evaluadas:**
          - **Posventa:** Autolux (25,95 pts) supera a Prana (25,86 pts) y a Sakura (25,81 pts).
          - **Usados:** Autolux (5,00 pts) supera a Prana (4,72 pts) y a Sakura (4,40 pts).
          - **TCFA:** Autolux (3,32 pts) supera a Prana (2,12 pts) y a Sakura (2,52 pts).
          - **KINTO:** Autolux (3,15 pts) supera a Prana (2,35 pts).
          - **General:** Autolux (13,27 pts) supera a Prana (12,66 pts).
          - **TPA:** Autolux (5,88 pts) supera a Prana (5,80 pts).
        * **El 100% del déficit (-7,13 pts) está en Ventas Convencionales:**
          - Prana suma **19,83 pts** en Ventas frente a los **9,63 pts** de Autolux (diferencia de **-10,20 puntos**).
        """)

    st.write("#### Comparativa Detallada por Área (Puntos Reales DEP Septiembre)")
    df_areas_gap = pd.DataFrame([
        {"Área": "Posventa", "Ponderado": 27.0, "Autolux": 25.95, "Puesto 10 (Prana)": 25.86, "Gap vs P10": 0.09, "Puesto 5 (Sakura)": 25.81, "Gap vs P5": 0.14},
        {"Área": "General", "Ponderado": 16.5, "Autolux": 13.27, "Puesto 10 (Prana)": 12.66, "Gap vs P10": 0.62, "Puesto 5 (Sakura)": 14.12, "Gap vs P5": -0.85},
        {"Área": "Usados", "Ponderado": 6.0, "Autolux": 5.00, "Puesto 10 (Prana)": 4.72, "Gap vs P10": 0.28, "Puesto 5 (Sakura)": 4.40, "Gap vs P5": 0.60},
        {"Área": "KINTO", "Ponderado": 6.0, "Autolux": 3.15, "Puesto 10 (Prana)": 2.35, "Gap vs P10": 0.80, "Puesto 5 (Sakura)": 3.96, "Gap vs P5": -0.81},
        {"Área": "TCFA (Financiera)", "Ponderado": 4.0, "Autolux": 3.32, "Puesto 10 (Prana)": 2.12, "Gap vs P10": 1.20, "Puesto 5 (Sakura)": 2.52, "Gap vs P5": 0.80},
        {"Área": "Toyota Plan (TPA)", "Ponderado": 9.0, "Autolux": 5.88, "Puesto 10 (Prana)": 5.80, "Gap vs P10": 0.08, "Puesto 5 (Sakura)": 8.60, "Gap vs P5": -2.72},
        {"Área": "ESG", "Ponderado": 1.0, "Autolux": 0.36, "Puesto 10 (Prana)": 0.36, "Gap vs P10": 0.00, "Puesto 5 (Sakura)": 0.64, "Gap vs P5": -0.28},
        {"Área": "Ventas Especiales", "Ponderado": 5.0, "Autolux": 1.50, "Puesto 10 (Prana)": 1.50, "Gap vs P10": 0.00, "Puesto 5 (Sakura)": 4.30, "Gap vs P5": -2.80},
        {"Área": "Ventas Convencionales", "Ponderado": 22.0, "Autolux": 9.63, "Puesto 10 (Prana)": 19.83, "Gap vs P10": -10.20, "Puesto 5 (Sakura)": 14.13, "Gap vs P5": -4.50},
    ])
    st.dataframe(
        df_areas_gap.style.format({
            "Ponderado": "{:.1f}",
            "Autolux": "{:.2f}",
            "Puesto 10 (Prana)": "{:.2f}",
            "Gap vs P10": "{:+.2f}",
            "Puesto 5 (Sakura)": "{:.2f}",
            "Gap vs P5": "{:+.2f}",
        }),
        use_container_width=True
    )

# ==========================================
# 2. PROYECCIÓN OCTUBRE 2026
# ==========================================
with tabs[1]:
    st.subheader("🔮 Proyección DEP Octubre 2026 (Consolidado Drive)")
    st.caption("Simulación proyectada basada en los planes de acción de Octubre: recuperación de Ventas, TPA, TCFA y General.")

    co1, co2, co3, co4 = st.columns(4)
    co1.metric("Score Septiembre Real", "68,05 pts (70,5%)", "Puesto #26")
    co2.metric("Score Octubre Proyectado", "71,64 pts (74,2%)", "+3,58 pts netos", delta_color="normal")
    co3.metric("Posición Proyectada", "Puesto #16", "+10 puestos de ascenso", delta_color="normal")
    co4.metric("Brecha Restante Top 10", "-3,54 pts", "Meta Puesto 10 (75,18 pts)", delta_color="inverse")

    st.markdown("---")

    col_po1, col_po2 = st.columns(2)
    with col_po1:
        st.write("#### Cascada de Crecimiento para Octubre (+3,58 pts)")
        fig_oct_waterfall = go.Figure(go.Waterfall(
            name="Octubre",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Septiembre Real", "Ventas (+2,03)", "TPA (+1,30)", "General (+0,18)", "TCFA (+0,08)", "Octubre Proy."],
            textposition="outside",
            text=["68.05", "+2.03", "+1.30", "+0.18", "+0.08", "71.64"],
            y=[68.05, 2.03, 1.30, 0.18, 0.08, 0],
            connector={"line": {"color": "#7f8c8d"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            increasing={"marker": {"color": "#2ecc71"}},
            totals={"marker": {"color": "#3498db"}}
        ))
        fig_oct_waterfall.update_layout(yaxis_title="Puntos DEP", yaxis_range=[65, 74])
        st.plotly_chart(fig_oct_waterfall, use_container_width=True)

    with col_po2:
        st.write("#### Palancas Específicas de Octubre")
        st.markdown("""
        * **Ventas (+2,03 pts):**
          - **SSI 0km (1.1.1):** Pasa de 1,13 a **2,25 pts (+1,12 pts)** alcanzando el escalón del 50% gracias a la mayor tasa de respuesta.
          - **Salesforce (1.5.5):** Pasa de 0,60 a **1,50 pts plenos (+0,90 pts)** al normalizar la lista de espera y legajos.
        * **Toyota Plan (+1,30 pts):**
          - **Caída temprana (4.5.3):** Recupera de 0,50 a **1,80 pts (+1,30 pts)** conteniendo al suscriptor en cuotas 1 a 3.
        * **General (+0,18 pts):**
          - **Capacitación (9.3.2):** Cierre de cursos e inducciones en plataforma Toyota.
        * **TCFA (+0,08 pts):**
          - **Fidelidad y Seguros (7.5.4):** Sostenimiento de pólizas y retención en renovación.
        """)

    st.write("#### Comparativo de Cierre: Septiembre vs. Octubre por Área")
    df_oct_areas = pd.DataFrame([
        {"Área": "Posventa", "Ponderado": 27.0, "Septiembre Real": 25.95, "Octubre Proy.": 25.95, "Variación": 0.00, "Estado": "Sostenido (Top 11)"},
        {"Área": "General", "Ponderado": 16.5, "Septiembre Real": 13.27, "Octubre Proy.": 13.45, "Variación": 0.18, "Estado": "Mejora Capacitación"},
        {"Área": "Ventas Convencionales", "Ponderado": 22.0, "Septiembre Real": 9.63, "Octubre Proy.": 11.65, "Variación": 2.03, "Estado": "Recuperación SSI y Salesforce"},
        {"Área": "Toyota Plan (TPA)", "Ponderado": 9.0, "Septiembre Real": 5.88, "Octubre Proy.": 7.18, "Variación": 1.30, "Estado": "Recuperación Caída Temprana"},
        {"Área": "Usados", "Ponderado": 6.0, "Septiembre Real": 5.00, "Octubre Proy.": 5.00, "Variación": 0.00, "Estado": "Consolidado 83,3%"},
        {"Área": "TCFA (Financiera)", "Ponderado": 4.0, "Septiembre Real": 3.32, "Octubre Proy.": 3.40, "Variación": 0.08, "Estado": "Retención de Seguros"},
        {"Área": "KINTO", "Ponderado": 6.0, "Septiembre Real": 3.15, "Octubre Proy.": 3.15, "Variación": 0.00, "Estado": "Sostenido 52,5%"},
        {"Área": "Ventas Especiales", "Ponderado": 5.0, "Septiembre Real": 1.50, "Octubre Proy.": 1.50, "Variación": 0.00, "Estado": "Sostenido"},
        {"Área": "ESG", "Ponderado": 1.0, "Septiembre Real": 0.36, "Octubre Proy.": 0.36, "Variación": 0.00, "Estado": "Sostenido"},
    ])
    st.dataframe(
        df_oct_areas.style.format({
            "Ponderado": "{:.1f}",
            "Septiembre Real": "{:.2f} pts",
            "Octubre Proy.": "{:.2f} pts",
            "Variación": "{:+.2f} pts"
        }),
        use_container_width=True
    )

# ==========================================
# 3. EVOLUCIÓN HISTÓRICA (JUL-AGO-SEP-OCT)
# ==========================================
with tabs[2]:
    st.subheader("📈 Evolución Histórica: Julio, Agosto, Septiembre y Octubre Proyectado")
    st.caption("Trayectoria mensual del puntaje DEP, porcentaje de cumplimiento y ranking nacional.")

    df_hist = pd.DataFrame([
        {"Mes": "Julio 2026", "Puntos": 65.90, "Cumplimiento": 68.29, "Ranking": 25, "Tipo": "Real", "Color": "#95a5a6"},
        {"Mes": "Agosto 2026", "Puntos": 66.81, "Cumplimiento": 69.24, "Ranking": 24, "Tipo": "Real", "Color": "#3498db"},
        {"Mes": "Septiembre 2026", "Puntos": 68.05, "Cumplimiento": 70.52, "Ranking": 26, "Tipo": "Real", "Color": "#2980b9"},
        {"Mes": "Octubre 2026 (Proy.)", "Puntos": 71.64, "Cumplimiento": 74.24, "Ranking": 16, "Tipo": "Proyectado", "Color": "#2ecc71"}
    ])

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.write("#### Evolución de Puntos Acumulados")
        fig_bar_pts = px.bar(
            df_hist, 
            x="Mes", 
            y="Puntos", 
            text="Puntos",
            color="Mes", 
            color_discrete_map={r["Mes"]: r["Color"] for _, r in df_hist.iterrows()}
        )
        fig_bar_pts.update_traces(
            texttemplate="%{text:.2f} pts", 
            textposition="inside",
            textfont=dict(size=14, color="white", family="Arial Black")
        )
        fig_bar_pts.update_layout(showlegend=False, yaxis_range=[55, 78], yaxis_title="Puntos DEP")
        st.plotly_chart(fig_bar_pts, use_container_width=True)

    with col_h2:
        st.write("#### Evolución del Puesto en el Ranking Nacional")
        fig_bar_rk = px.bar(
            df_hist, 
            x="Mes", 
            y="Ranking", 
            text="Ranking",
            color="Mes", 
            color_discrete_map={r["Mes"]: r["Color"] for _, r in df_hist.iterrows()}
        )
        fig_bar_rk.update_traces(
            texttemplate="Puesto #%{text}", 
            textposition="inside",
            textfont=dict(size=14, color="white", family="Arial Black")
        )
        fig_bar_rk.update_layout(showlegend=False, yaxis_range=[0, 30], yaxis_title="Posición (Menor es mejor)")
        st.plotly_chart(fig_bar_rk, use_container_width=True)

    st.info("""
    **Conclusión del Tramo Octubre:**
    * El salto proyectado para Octubre (+3,58 pts netos) colocaría a Autolux en **71,64 puntos (Puesto 16)**, revirtiendo la caída de septiembre y dejando al concesionario a solo **3,54 puntos del Top 10**.
    """)

# ==========================================
# 4. AUDITORÍA REAL SEPTIEMBRE
# ==========================================
with tabs[3]:
    st.subheader("🔍 Auditoría Oficial Septiembre: Análisis de Desvíos TASA")
    st.caption("Detalle de las diferencias entre el cierre proyectado preliminar y el resultado emitido en la Circular DES026-26.")

    col_au1, col_au2 = st.columns(2)
    with col_au1:
        st.write("#### Balance de Puntos: Proyectado vs. Real")
        df_audit = pd.DataFrame([
            {"Concepto": "Agosto Base", "Puntos": 66.81, "Tipo": "Histórico"},
            {"Concepto": "Proyección Preliminar", "Puntos": 69.67, "Tipo": "Proyectado"},
            {"Concepto": "Real Oficial TASA", "Puntos": 68.05, "Tipo": "Real"}
        ])
        fig_audit = px.bar(
            df_audit, x="Concepto", y="Puntos", text="Puntos",
            color="Tipo", color_discrete_map={"Histórico": "#95a5a6", "Proyectado": "#f39c12", "Real": "#2ecc71"}
        )
        fig_audit.update_traces(texttemplate="%{text:.2f} pts", textposition="inside")
        fig_audit.update_layout(yaxis_range=[60, 75], showlegend=False)
        st.plotly_chart(fig_audit, use_container_width=True)

    with col_au2:
        st.write("#### Factores Clave del Cómputo TASA")
        st.markdown("""
        * **Aciertos confirmados:**
          - **Facilities (9.4.1):** 4,50 pts plenos (+1,35 pts).
          - **Patentamientos (1.5.3):** 2,10 pts plenos (+1,05 pts) con 90,9% de efectividad.
          - **Calidad Usados (6.1.1):** 0,60 pts capturados.
        * **Desvíos no imputados en el acumulado:**
          - **CRM (1.5.6):** Se cerró en 1,9 hs en septiembre, pero TASA computó el acumulado anual en 4,3 hs (0,00 pts).
          - **KINTO (5.5.6):** TASA computó 3,15 pts oficiales (sin el PN Corporativo One).
          - **TPA:** Impacto de Caída Temprana (0,50 pts) y Cuotas (-1,96 pts netos en el área).
        """)

# ==========================================
# 5. PLAN TÁCTICO DE CIERRE Q4
# ==========================================
with tabs[4]:
    st.subheader("🎯 Plan Táctico Q4: Cómo cerrar la brecha hacia el Top 10")
    
    st.markdown("""
    ### La Ruta Definitiva para superar a Prana (75,18 pts)
    Partiendo de los **71,64 puntos proyectados en Octubre**, solo se necesitan **+3,54 puntos** en Noviembre y Diciembre:
    
    1. **CRM Acumulado en menos de 2 hs (Recuperación: +1,50 pts):**
       * Sostener la guardia comercial activa para bajar el promedio YTD y destrabar el 1.5.6.
    2. **Campañas de Recall Airbags al 70% (Recuperación: +0,70 pts):**
       * Pasar de 241 a 388 infladores en Posventa. Faltan 147 vehículos para cobrar el 75% del ítem 3.5.2.
    3. **KINTO One Corporativo (Recuperación: +1,20 pts):**
       * Subir los contratos corporativos vigentes a la intranet de KINTO para cobrar el indicador 5.5.6.
    4. **Sorteos y Dilución en Encuestas 0km (Recuperación: +1,13 pts):**
       * Alcanzar el escalón del 75% o 100% en SSI (1.1.1).
    """)
