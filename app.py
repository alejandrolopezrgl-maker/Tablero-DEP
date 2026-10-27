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
st.caption("Programa de Excelencia de Concesionarios Toyota (DEP) | Auditoría Oficial Septiembre & Comparativo P5/P10")

# --- NAVEGACIÓN PRINCIPAL ---
tabs = st.tabs([
    "📊 Comparativo Puesto 5 y 10",
    "📈 Evolución Histórica (Jul-Ago-Sep)",
    "🔍 Proyección vs. Real Septiembre",
    "🎯 Plan Táctico de Cierre Q4",
    "🔧 Avance Posventa Octubre"
])

# ==========================================
# 1. COMPARATIVO PUESTO 5 Y 10
# ==========================================
with tabs[0]:
    st.subheader("Dashboard Comparativo: Autolux vs. Puesto 10 y Puesto 5 (Septiembre 2026)")
    
    # Métricas principales
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
            df_bench_total, x="Entidad", y="Puntos", text="Puntos",
            color="Entidad", color_discrete_map={r["Entidad"]: r["Color"] for _, r in df_bench_total.iterrows()}
        )
        fig_bench_total.update_traces(
            texttemplate="%{text:.2f} pts", textposition="inside",
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
          - Prana suma **19,83 pts** en Ventas frente a los **9,63 pts** de Autolux (diferencia de **10,20 pts**).
        """)

    st.write("#### Comparativa Detallada por Área (Puntos Reales DEP Septiembre)")
    df_areas_gap = pd.DataFrame([
        {"Área": "Posventa", "Ponderado": 27.0, "Autolux": 25.95, "Puesto 10 (Prana)": 25.86, "Gap vs P10": +0.09, "Puesto 5 (Sakura)": 25.81, "Gap vs P5": +0.14},
        {"Área": "General", "Ponderado": 16.5, "Autolux": 13.27, "Puesto 10 (Prana)": 12.66, "Gap vs P10": +0.62, "Puesto 5 (Sakura)": 14.12, "Gap vs P5": -0.85},
        {"Área": "Usados", "Ponderado": 6.0, "Autolux": 5.00, "Puesto 10 (Prana)": 4.72, "Gap vs P10": +0.28, "Puesto 5 (Sakura)": 4.40, "Gap vs P5": +0.60},
        {"Área": "KINTO", "Ponderado": 6.0, "Autolux": 3.15, "Puesto 10 (Prana)": 2.35, "Gap vs P10": +0.80, "Puesto 5 (Sakura)": 3.96, "Gap vs P5": -0.81},
        {"Área": "TCFA (Financiera)", "Ponderado": 4.0, "Autolux": 3.32, "Puesto 10 (Prana)": 2.12, "Gap vs P10": +1.20, "Puesto 5 (Sakura)": 2.52, "Gap vs P5": +0.80},
        {"Área": "Toyota Plan (TPA)", "Ponderado": 9.0, "Autolux": 5.88, "Puesto 10 (Prana)": 5.80, "Gap vs P10": +0.08, "Puesto 5 (Sakura)": 8.60, "Gap vs P5": -2.72},
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
# 2. EVOLUCIÓN HISTÓRICA Y GAPS (BARRAS)
# ==========================================
with tabs[1]:
    st.subheader("📈 Evolución Histórica: Julio, Agosto y Septiembre 2026")
    st.caption("Análisis comparativo de los últimos tres meses de medición oficial TASA mediante gráficos de barras.")

    df_hist = pd.DataFrame([
        {"Mes": "Julio 2026", "Puntos": 65.90, "Cumplimiento": 68.29, "Ranking": 25, "Color": "#95a5a6"},
        {"Mes": "Agosto 2026", "Puntos": 66.81, "Cumplimiento": 69.24, "Ranking": 24, "Color": "#3498db"},
        {"Mes": "Septiembre 2026", "Puntos": 68.05, "Cumplimiento": 70.52, "Ranking": 26, "Color": "#2ecc71"}
    ])

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.write("#### Evolución de Puntos Acumulados")
        fig_bar_pts = px.bar(
            df_hist, x="Mes", y="Puntos", text="Puntos",
            color="Mes", color_discrete_map={r["Mes"]: r["Color"] for _, r in df_hist.iterrows()}
        )
        fig_bar_pts.update_traces(
            texttemplate="%{text:.2f} pts", textposition="inside",
            textfont=dict(size=14, color="white", family="Arial Black")
        )
        fig_bar_pts.update_layout(showlegend=False, yaxis_range=[55, 75], yaxis_title="Puntos DEP")
        st.plotly_chart(fig_bar_pts, use_container_width=True)

    with col_h2:
        st.write("#### Evolución del Puesto en el Ranking Nacional")
        fig_bar_rk = px.bar(
            df_hist, x="Mes", y="Ranking", text="Ranking",
            color="Mes", color_discrete_map={r["Mes"]: r["Color"] for _, r in df_hist.iterrows()}
        )
        fig_bar_rk.update_traces(
            texttemplate="Puesto #%{text}", textposition="inside",
            textfont=dict(size=14, color="white", family="Arial Black")
        )
        fig_bar_rk.update_layout(showlegend=False, yaxis_range=[0, 30], yaxis_title="Posición (Menor es mejor)")
        st.plotly_chart(fig_bar_rk, use_container_width=True)

    st.info("""
    **La Paradoja de Septiembre Explicada:**
    * **Autolux creció:** De Julio (65,90 pts) a Septiembre (68,05 pts) se sumaron **+2,15 puntos netos** y el cumplimiento subió del **68,29% al 70,52%**.
    * **Por qué bajamos del puesto 24 al 26:** En el cierre del 3° trimestre, competidores directos sumaron puntaje masivo en Facilities y Caída Temprana (Autos del Sur +7,98 pts, Treos Norte +7,54 pts, Mendez +7,34 pts, Bosetti +2,43 pts). Esto elevó la exigencia de la tabla media.
    """)

# ==========================================
# 3. PROYECCIÓN VS. REAL SEPTIEMBRE
# ==========================================
with tabs[2]:
    st.subheader("🔍 Comparativa: Proyección de Septiembre vs. Real TASA")
    st.caption("Auditoría de desvíos entre los números proyectados y los resultados oficiales emitidos por Toyota.")

    cp1, cp2, cp3 = st.columns(3)
    cp1.metric("Score Proyectado (Prudente)", "69,67 pts", "Puesto #15 estimado")
    cp2.metric("Score Real Oficial TASA", "68,05 pts", "Puesto #26 real")
    cp3.metric("Desvío Neto", "-1,62 pts", "Diferencia de cómputo", delta_color="inverse")

    st.markdown("---")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.write("#### Comparativa Gráfica de Puntos")
        df_comp_proy = pd.DataFrame([
            {"Concepto": "Agosto Base", "Puntos": 66.81, "Tipo": "Histórico"},
            {"Concepto": "Proyección Sept.", "Puntos": 69.67, "Tipo": "Proyectado"},
            {"Concepto": "Real TASA Sept.", "Puntos": 68.05, "Tipo": "Real"}
        ])
        fig_proy = px.bar(
            df_comp_proy, x="Concepto", y="Puntos", text="Puntos",
            color="Tipo", color_discrete_map={"Histórico": "#95a5a6", "Proyectado": "#f39c12", "Real": "#2ecc71"}
        )
        fig_proy.update_traces(texttemplate="%{text:.2f} pts", textposition="inside")
        fig_proy.update_layout(yaxis_range=[60, 75], showlegend=False)
        st.plotly_chart(fig_proy, use_container_width=True)

    with col_p2:
        st.write("#### Causas de las Diferencias Detectadas")
        st.markdown("""
        1. **Aciertos Exactos de la Proyección:**
           * **Facilities (9.4.1):** Se proyectaron 4,50 pts y se confirmaron **4,50 pts (+1,35 pts plenos)**.
           * **Patentamientos vs. Ventas (1.5.3):** Se proyectaron 2,10 pts y se confirmaron **2,10 pts (+1,05 pts plenos)**.
           * **Calidad Usados (6.1.1):** Se proyectaron 0,60 pts y se confirmaron **0,60 pts plenos**.
        2. **Desvíos no imputados por TASA:**
           * **CRM (1.5.6):** Se proyectaron +1,50 pts por cerrar el mes en 1,9 hs, pero TASA computó el promedio acumulado YTD en **4,3 hs**, manteniendo **0,00 pts**.
           * **KINTO (5.5.6):** La planilla interna indicaba 4,16 pts, pero TASA computó **3,15 pts** (dejó en 0 el PN Corporativo One). Desvío: **-1,01 pts**.
           * **Toyota Plan (TPA):** Retroceso en Caída Temprana (4.5.3 de 1,80 a 0,50 pts) y Cuotas emitidas (-0,61 pts).
        """)

    st.write("#### Balance Comparativo Ítem por Ítem")
    df_detalle_comp = pd.DataFrame([
        {"Indicador": "1.4.1 / 9.4.1 Facilities", "Proyectado": "+1,35 pts", "Real TASA": "+1,35 pts", "Estado": "Exacto", "Comentario": "Puntaje perfecto 100%"},
        {"Indicador": "1.5.3 Patentes vs. Ventas", "Proyectado": "+1,05 pts", "Real TASA": "+1,05 pts", "Estado": "Exacto", "Comentario": "90,9% cumplido"},
        {"Indicador": "6.1.1 SSI Usados", "Proyectado": "+0,60 pts", "Real TASA": "+0,60 pts", "Estado": "Exacto", "Comentario": "75% capturado"},
        {"Indicador": "1.5.6 CRM Tiempos de Respuesta", "Proyectado": "+1,50 pts", "Real TASA": "0,00 pts", "Estado": "Diferido", "Comentario": "TASA tomó acumulado 4,3 hs"},
        {"Indicador": "Área KINTO", "Proyectado": "+1,66 pts", "Real TASA": "+0,65 pts", "Estado": "Parcial", "Comentario": "TASA computó 3,15 pts en vez de 4,16"},
        {"Indicador": "TPA (Cuotas y Caída)", "Proyectado": "0,00 pts", "Real TASA": "-1,96 pts", "Estado": "Retroceso", "Comentario": "Caída temprana cayó a 0,50 pts"},
    ])
    st.dataframe(df_detalle_comp, use_container_width=True)

# ==========================================
# 4. PLAN TÁCTICO DE CIERRE Q4
# ==========================================
with tabs[3]:
    st.subheader("🎯 Plan Táctico Q4: Cómo cerrar los 7,13 Puntos hacia el Top 10")
    
    st.markdown("""
    ### La Brecha al Top 10: -7,13 Puntos
    Para alcanzar a Prana (Puesto 10 con 75,18 pts) antes del 31 de diciembre, la estrategia ejecutiva se apoya en 4 palancas:
    
    1. **CRM Acumulado en menos de 2 hs (Recuperación: +1,50 pts):**
       * Sostener la guardia comercial activa en octubre, noviembre y diciembre para bajar el promedio general YTD y destrabar el 1.5.6.
    2. **Campañas de Recall Airbags al 70% (Recuperación: +0,70 pts):**
       * Pasar de 241 a 388 infladores en Posventa. Faltan 147 vehículos para cobrar el 75% del ítem 3.5.2.
    3. **Calidad 0km: Sorteos y Tasa de Respuesta (Recuperación: +2,25 pts):**
       * El SSI puro cerró en 95,0 (a solo 0,6 pts del target). Al ampliar la muestra de encuestas, se salta del 25% al 75% en SSI.
    4. **Contención de Caída Temprana en TPA (Recuperación: +1,30 pts):**
       * Revertir la penalización en 4.5.3 acompañando al ahorrista en las primeras 3 cuotas.
    5. **KINTO One Corporativo (Recuperación: +1,20 pts):**
       * Subir contratos corporativos activos a plataforma para cobrar el indicador 5.5.6.
    """)

# ==========================================
# 5. AVANCE POSVENTA OCTUBRE (DATOS REALES)
# ==========================================
with tabs[4]:
    st.subheader("🔧 Avance Operativo de Posventa (Corte al 26 de Octubre 2026)")
    st.caption("Consolidado de cumplimiento en Repuestos, Servicios y Total por Sucursal.")

    df_pv = pd.DataFrame([
        {"Sucursal": "Lux Salta", "Pct_Repuestos": 66.4, "Pct_Servicios": 72.2, "Pct_Total": 69.30, "Color": "#e63946"},
        {"Sucursal": "Lux Jujuy", "Pct_Repuestos": 70.3, "Pct_Servicios": 63.2, "Pct_Total": 66.75, "Color": "#2a9d8f"},
        {"Sucursal": "Lux Tartagal", "Pct_Repuestos": 50.5, "Pct_Servicios": 70.5, "Pct_Total": 60.50, "Color": "#1d3557"},
        {"Sucursal": "Lux Las Lajitas", "Pct_Repuestos": 41.4, "Pct_Servicios": 62.3, "Pct_Total": 51.85, "Color": "#e9c46a"},
    ])

    col_pv1, col_pv2 = st.columns(2)
    with col_pv1:
        st.write("#### Cumplimiento Total por Sucursal al 26 de Octubre (%)")
        fig_pv = px.bar(
            df_pv, x="Sucursal", y="Pct_Total", text="Pct_Total",
            color="Sucursal", color_discrete_map={r["Sucursal"]: r["Color"] for _, r in df_pv.iterrows()}
        )
        fig_pv.update_traces(
            texttemplate="%{text:.2f}%", textposition="inside",
            textfont=dict(size=14, color="white", family="Arial Black")
        )
        fig_pv.update_layout(showlegend=False, yaxis_range=[0, 100], yaxis_title="% Cumplimiento")
        st.plotly_chart(fig_pv, use_container_width=True)

    with col_pv2:
        st.write("#### Desglose Repuestos vs. Servicios")
        df_melt_pv = df_pv.melt(
            id_vars=["Sucursal"], value_vars=["Pct_Repuestos", "Pct_Servicios"],
            var_name="Rubro", value_name="Cumplimiento"
        )
        fig_grouped = px.bar(
            df_melt_pv, x="Sucursal", y="Cumplimiento", color="Rubro", barmode="group",
            text="Cumplimiento", color_discrete_map={"Pct_Repuestos": "#3498db", "Pct_Servicios": "#e67e22"}
        )
        fig_grouped.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
        fig_grouped.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig_grouped, use_container_width=True)

    st.dataframe(
        df_pv[["Sucursal", "Pct_Repuestos", "Pct_Servicios", "Pct_Total"]].style.format({
            "Pct_Repuestos": "{:.1f}%",
            "Pct_Servicios": "{:.1f}%",
            "Pct_Total": "{:.2f}%"
        }),
        use_container_width=True
    )
