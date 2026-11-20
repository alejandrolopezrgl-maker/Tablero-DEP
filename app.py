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
st.caption(
    "Programa de Excelencia Toyota (DEP) | Cierre Oficial Octubre & Proyección Noviembre"
)

# --- NAVEGACIÓN PRINCIPAL (5 PESTAÑAS ESTRATÉGICAS) ---
tabs = st.tabs([
    "📊 Comparativo Puesto 5 y 10",
    "🔮 Proyección Noviembre 2026",
    "📈 Evolución Histórica (Jul-Nov)",
    "🔍 Auditoría Real Octubre",
    "🎯 Plan Táctico de Cierre Q4"
])

# ==========================================
# 1. COMPARATIVO PUESTO 5 Y 10 (OCTUBRE REAL)
# ==========================================
with tabs[0]:
    st.subheader(
        "Dashboard Comparativo: Autolux vs. Puesto 10 y Puesto 5 (Octubre 2026)"
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Autolux Actual", "68,60 pts (71,09%)", "Puesto #29")
    c2.metric("Puesto 10 (Senna)", "76,77 pts (79,56%)", "Línea Top 10")
    c3.metric(
        "Faltante para Puesto 10",
        "-8,17 pts",
        "-8,47 p.p. de cumplimiento",
        delta_color="inverse"
    )
    c4.metric(
        "Faltante para Puesto 5 (BHAS)",
        "-11,12 pts",
        "79,72 pts (-11,53 p.p.)",
        delta_color="inverse"
    )

    st.markdown("---")

    col_g1, col_g2 = st.columns([1, 1])
    with col_g1:
        st.write("#### Brecha de Puntos Totales (Cierre Octubre)")
        df_bench_total = pd.DataFrame([
            {
                "Entidad": "Autolux (Actual)",
                "Puntos": 68.60,
                "Puesto": "#29",
                "Color": "#3498db"
            },
            {
                "Entidad": "Puesto 10 (Senna)",
                "Puntos": 76.77,
                "Puesto": "#10",
                "Color": "#f39c12"
            },
            {
                "Entidad": "Puesto 5 (B.H.A.S.)",
                "Puntos": 79.72,
                "Puesto": "#5",
                "Color": "#2ecc71"
            }
        ])
        fig_bench = px.bar(
            df_bench_total,
            x="Entidad",
            y="Puntos",
            text="Puntos",
            color="Entidad",
            color_discrete_map={
                r["Entidad"]: r["Color"] for _, r in df_bench_total.iterrows()
            }
        )
        fig_bench.update_traces(
            texttemplate="%{text:.2f} pts",
            textposition="inside",
            textfont=dict(size=14, color="white", family="Arial Black")
        )
        fig_bench.update_layout(
            showlegend=False,
            yaxis_range=[50, 86],
            yaxis_title="Puntos DEP"
        )
        st.plotly_chart(fig_bench, use_container_width=True)

    with col_g2:
        st.write("#### Hallazgo Clave: ¿Dónde está la brecha con el Puesto 10?")
        st.success("""
        * **Autolux supera o empata a Senna (Puesto 10) en 4 áreas:**
          - **KINTO:** Autolux (3,15 pts) supera a Senna (2,00 pts) por **+1,15 pts**.
          - **ESG:** Autolux (0,78 pts — **#1 Nacional**) supera a Senna (0,64 pts).
          - **TCFA:** Empate técnico en el máximo nivel operativo (**3,60 pts**).
          - **Ventas Especiales:** Empate exacto (**1,50 pts**).
        * **Los 4 frentes que explican los -8,17 pts frente al Top 10:**
          - **General (-3,23 pts):** Excelencia Calidad (`9.1.1`) y Capacitación (`9.3.2`).
          - **Toyota Plan (-2,23 pts):** Caída temprana (`4.5.3`) y Cuotas (`4.5.4`).
          - **Usados (-2,08 pts):** Ventas UCT (`6.5.1`) por 1 unidad y NPS Usados (`6.1.2`).
          - **Ventas Convencionales (-1,58 pts):** Salesforce (`1.5.5`) y SSI (`1.1.1`).
        """)

    st.write("#### Comparativa Detallada por Área (Puntos Reales DEP Octubre)")
    df_areas_gap = pd.DataFrame([
        {
            "Área": "Posventa",
            "Ponderado": 27.0,
            "Autolux": 25.95,
            "Puesto 10 (Senna)": 26.30,
            "Gap vs P10": -0.35,
            "Puesto 5 (BHAS)": 26.87,
            "Gap vs P5": -0.92
        },
        {
            "Área": "General",
            "Ponderado": 16.5,
            "Autolux": 13.07,
            "Puesto 10 (Senna)": 16.30,
            "Gap vs P10": -3.23,
            "Puesto 5 (BHAS)": 13.31,
            "Gap vs P5": -0.24
        },
        {
            "Área": "Ventas Convencionales",
            "Ponderado": 22.0,
            "Autolux": 10.75,
            "Puesto 10 (Senna)": 12.33,
            "Gap vs P10": -1.58,
            "Puesto 5 (BHAS)": 16.38,
            "Gap vs P5": -5.63
        },
        {
            "Área": "Toyota Plan (TPA)",
            "Ponderado": 9.0,
            "Autolux": 6.08,
            "Puesto 10 (Senna)": 8.31,
            "Gap vs P10": -2.23,
            "Puesto 5 (BHAS)": 8.13,
            "Gap vs P5": -2.04
        },
        {
            "Área": "Usados",
            "Ponderado": 6.0,
            "Autolux": 3.72,
            "Puesto 10 (Senna)": 5.80,
            "Gap vs P10": -2.08,
            "Puesto 5 (BHAS)": 4.40,
            "Gap vs P5": -0.68
        },
        {
            "Área": "TCFA (Financiera)",
            "Ponderado": 4.0,
            "Autolux": 3.60,
            "Puesto 10 (Senna)": 3.60,
            "Gap vs P10": 0.00,
            "Puesto 5 (BHAS)": 3.72,
            "Gap vs P5": -0.12
        },
        {
            "Área": "KINTO",
            "Ponderado": 6.0,
            "Autolux": 3.15,
            "Puesto 10 (Senna)": 2.00,
            "Gap vs P10": 1.15,
            "Puesto 5 (BHAS)": 5.06,
            "Gap vs P5": -1.91
        },
        {
            "Área": "Ventas Especiales",
            "Ponderado": 5.0,
            "Autolux": 1.50,
            "Puesto 10 (Senna)": 1.50,
            "Gap vs P10": 0.00,
            "Puesto 5 (BHAS)": 1.50,
            "Gap vs P5": 0.00
        },
        {
            "Área": "ESG",
            "Ponderado": 1.0,
            "Autolux": 0.78,
            "Puesto 10 (Senna)": 0.64,
            "Gap vs P10": 0.14,
            "Puesto 5 (BHAS)": 0.36,
            "Gap vs P5": 0.42
        }
    ])
    st.dataframe(
        df_areas_gap.style.format({
            "Ponderado": "{:.1f}",
            "Autolux": "{:.2f}",
            "Puesto 10 (Senna)": "{:.2f}",
            "Gap vs P10": "{:+.2f}",
            "Puesto 5 (BHAS)": "{:.2f}",
            "Gap vs P5": "{:+.2f}"
        }),
        use_container_width=True
    )

# ==========================================
# 2. PROYECCIÓN NOVIEMBRE 2026
# ==========================================
with tabs[1]:
    st.subheader("🔮 Proyección DEP Noviembre 2026")
    st.caption(
        "Simulación basada en Usados UCT, CRM acumulado, Salesforce y Campañas Airbags."
    )

    cn1, cn2, cn3, cn4 = st.columns(4)
    cn1.metric("Score Octubre Real", "68,60 pts (71,09%)", "Puesto #29")
    cn2.metric(
        "Score Noviembre Proyectado",
        "72,98 pts (75,63%)",
        "+4,38 pts netos",
        delta_color="normal"
    )
    cn3.metric(
        "Posición Proyectada",
        "Puesto #17",
        "+12 puestos de ascenso",
        delta_color="normal"
    )
    cn4.metric(
        "Brecha Restante Top 10",
        "-3,79 pts",
        "Meta Puesto 10 (76,77 pts)",
        delta_color="inverse"
    )

    st.markdown("---")

    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.write("#### Cascada de Recuperación Noviembre (+4,38 pts)")
        fig_nov_wat = go.Figure(go.Waterfall(
            name="Noviembre",
            orientation="v",
            measure=[
                "absolute", "relative", "relative",
                "relative", "relative", "total"
            ],
            x=[
                "Octubre Real", "CRM (<2hs)", "Usados UCT",
                "Salesforce", "Airbags 70%", "Noviembre Proy."
            ],
            textposition="outside",
            text=["68.60", "+1.50", "+1.28", "+0.90", "+0.70", "72.98"],
            y=[68.60, 1.50, 1.28, 0.90, 0.70, 0],
            connector={"line": {"color": "#7f8c8d"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            increasing={"marker": {"color": "#2ecc71"}},
            totals={"marker": {"color": "#3498db"}}
        ))
        fig_nov_wat.update_layout(yaxis_title="Puntos DEP", yaxis_range=[66, 75])
        st.plotly_chart(fig_nov_wat, use_container_width=True)

    with col_n2:
        st.write("#### Palancas Operativas Clave de Noviembre")
        st.markdown("""
        * **CRM Tiempos de Respuesta (`1.5.6` — +1,50 pts):**
          - El promedio acumulado bajó de 4,3 hs a 4,1 hs y los no contactados al 11%.
          - Al perforar las 2 hs acumuladas se libera el puntaje pleno.
        * **Ventas Usados UCT (`6.5.1` — +1,28 pts):**
          - En octubre faltó 1 solo auto (141 vs. 142) para cobrar el 100%.
          - Recuperando la cuota mensual se restituyen los 3,20 pts plenos.
        * **Actualización Salesforce (`1.5.5` — +0,90 pts):**
          - Elevar la actualización del 92,5% actual al 100% para pasar de 0,60 a 1,50 pts.
        * **Campañas Recall Airbags (`3.5.2` — +0,70 pts):**
          - Llegar al 70% de avance (292 de 416 unidades; hoy van 229, faltan 63).
        """)

    st.write("#### Comparativo por Área: Octubre Real vs. Noviembre Proyectado")
    df_nov_areas = pd.DataFrame([
        {
            "Área": "Posventa",
            "Max": 27.0,
            "Octubre Real": 25.95,
            "Noviembre Proy.": 26.65,
            "Variación": 0.70,
            "Palanca": "Airbags al 70% (+0,70 pts)"
        },
        {
            "Área": "Ventas Convencionales",
            "Max": 22.0,
            "Octubre Real": 10.75,
            "Noviembre Proy.": 13.15,
            "Variación": 2.40,
            "Palanca": "CRM (+1,50) + Salesforce (+0,90)"
        },
        {
            "Área": "General",
            "Max": 16.5,
            "Octubre Real": 13.07,
            "Noviembre Proy.": 13.07,
            "Variación": 0.00,
            "Palanca": "Sostenido (79,2%)"
        },
        {
            "Área": "Toyota Plan (TPA)",
            "Max": 9.0,
            "Octubre Real": 6.08,
            "Noviembre Proy.": 6.08,
            "Variación": 0.00,
            "Palanca": "Base conservadora (67,6%)"
        },
        {
            "Área": "Usados",
            "Max": 6.0,
            "Octubre Real": 3.72,
            "Noviembre Proy.": 5.00,
            "Variación": 1.28,
            "Palanca": "Recuperación meta UCT (+1,28)"
        },
        {
            "Área": "TCFA (Financiera)",
            "Max": 4.0,
            "Octubre Real": 3.60,
            "Noviembre Proy.": 3.60,
            "Variación": 0.00,
            "Palanca": "Sostenido al 90%"
        },
        {
            "Área": "KINTO",
            "Max": 6.0,
            "Octubre Real": 3.15,
            "Noviembre Proy.": 3.15,
            "Variación": 0.00,
            "Palanca": "Sostenido (52,5%)"
        },
        {
            "Área": "Ventas Especiales",
            "Max": 5.0,
            "Octubre Real": 1.50,
            "Noviembre Proy.": 1.50,
            "Variación": 0.00,
            "Palanca": "Sostenido (30,0%)"
        },
        {
            "Área": "ESG",
            "Max": 1.0,
            "Octubre Real": 0.78,
            "Noviembre Proy.": 0.78,
            "Variación": 0.00,
            "Palanca": "Líder Nacional #1 (77,5%)"
        }
    ])
    st.dataframe(
        df_nov_areas.style.format({
            "Max": "{:.1f}",
            "Octubre Real": "{:.2f} pts",
            "Noviembre Proy.": "{:.2f} pts",
            "Variación": "{:+.2f} pts"
        }),
        use_container_width=True
    )

# ==========================================
# 3. EVOLUCIÓN HISTÓRICA (JUL - NOV)
# ==========================================
with tabs[2]:
    st.subheader("📈 Evolución Histórica: Julio a Noviembre 2026")
    st.caption(
        "Trayectoria mensual del puntaje DEP, cumplimiento y ranking nacional."
    )

    df_hist = pd.DataFrame([
        {
            "Mes": "Julio 2026",
            "Puntos": 65.90,
            "Cumplimiento": 68.29,
            "Ranking": 25,
            "Color": "#95a5a6"
        },
        {
            "Mes": "Agosto 2026",
            "Puntos": 66.81,
            "Cumplimiento": 69.24,
            "Ranking": 24,
            "Color": "#3498db"
        },
        {
            "Mes": "Septiembre 2026",
            "Puntos": 68.05,
            "Cumplimiento": 70.52,
            "Ranking": 26,
            "Color": "#2980b9"
        },
        {
            "Mes": "Octubre 2026 (Real)",
            "Puntos": 68.60,
            "Cumplimiento": 71.09,
            "Ranking": 29,
            "Color": "#1abc9c"
        },
        {
            "Mes": "Noviembre 2026 (Proy.)",
            "Puntos": 72.98,
            "Cumplimiento": 75.63,
            "Ranking": 17,
            "Color": "#2ecc71"
        }
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
            color_discrete_map={
                r["Mes"]: r["Color"] for _, r in df_hist.iterrows()
            }
        )
        fig_bar_pts.update_traces(
            texttemplate="%{text:.2f} pts",
            textposition="inside",
            textfont=dict(size=13, color="white", family="Arial Black")
        )
        fig_bar_pts.update_layout(
            showlegend=False,
            yaxis_range=[55, 78],
            yaxis_title="Puntos DEP"
        )
        st.plotly_chart(fig_bar_pts, use_container_width=True)

    with col_h2:
        st.write("#### Evolución del Puesto en el Ranking Nacional")
        fig_bar_rk = px.bar(
            df_hist,
            x="Mes",
            y="Ranking",
            text="Ranking",
            color="Mes",
            color_discrete_map={
                r["Mes"]: r["Color"] for _, r in df_hist.iterrows()
            }
        )
        fig_bar_rk.update_traces(
            texttemplate="Puesto #%{text}",
            textposition="inside",
            textfont=dict(size=13, color="white", family="Arial Black")
        )
        fig_bar_rk.update_layout(
            showlegend=False,
            yaxis_range=[0, 32],
            yaxis_title="Posición (Menor es mejor)"
        )
        st.plotly_chart(fig_bar_rk, use_container_width=True)

    st.info("""
    **Lectura Estratégica:**
    * Autolux acumula **4 meses consecutivos de crecimiento real de puntaje** (65,90 -> 66,81 -> 68,05 -> 68,60 pts).
    * En octubre, la tabla media estuvo sumamente comprimida: entre el puesto #29 (Autolux, 68,60 pts)
      y el puesto #22 (Mendez, 69,96 pts) hay apenas **1,36 puntos de diferencia**.
    * Capturando las palancas de noviembre (+4,38 pts), se superan 12 concesionarios de una sola vez.
    """)

# ==========================================
# 4. AUDITORÍA REAL OCTUBRE
# ==========================================
with tabs[3]:
    st.subheader("🔍 Auditoría Oficial Octubre: Proyección vs. Real TASA")
    st.caption(
        "Comparativa entre lo proyectado para Octubre (71,64 pts) y el cierre oficial (68,60 pts)."
    )

    ca1, ca2, ca3 = st.columns(3)
    ca1.metric("Score Proyectado Octubre", "71,64 pts", "Puesto #16 estimado")
    ca2.metric("Score Real Oficial TASA", "68,60 pts", "Puesto #29 real")
    ca3.metric(
        "Desvío Neto",
        "-3,04 pts",
        "Diferencia en metas puntuales",
        delta_color="inverse"
    )

    st.markdown("---")

    col_au1, col_au2 = st.columns(2)
    with col_au1:
        st.write("#### Comparativa Gráfica Octubre")
        df_audit = pd.DataFrame([
            {"Concepto": "Septiembre Base", "Puntos": 68.05, "Tipo": "Histórico"},
            {"Concepto": "Proyección Oct.", "Puntos": 71.64, "Tipo": "Proyectado"},
            {"Concepto": "Real TASA Oct.", "Puntos": 68.60, "Tipo": "Real"}
        ])
        fig_audit = px.bar(
            df_audit,
            x="Concepto",
            y="Puntos",
            text="Puntos",
            color="Tipo",
            color_discrete_map={
                "Histórico": "#95a5a6",
                "Proyectado": "#f39c12",
                "Real": "#2ecc71"
            }
        )
        fig_audit.update_traces(texttemplate="%{text:.2f} pts", textposition="inside")
        fig_audit.update_layout(yaxis_range=[64, 74], showlegend=False)
        st.plotly_chart(fig_audit, use_container_width=True)

    with col_au2:
        st.write("#### Análisis de Aciertos y Desvíos de Octubre")
        st.markdown("""
        * **Aciertos plenos y sorpresas positivas:**
          - **SSI 0km (`1.1.1`):** Subió exactamente como proyectamos (+1,13 pts, llegando a 2,25 pts).
          - **ESG (`8.5.2` / `8.5.3`):** Saltó de 0,36 a **0,78 pts (+0,42 pts)** logrando el **Puesto #1 Nacional**.
          - **TCFA:** Alcanzó **3,60 pts (+0,28 pts)** con 90% de cumplimiento.
          - **ICQ TPA (`4.1.1`):** Subió a puntaje perfecto (+0,20 pts).
        * **Desvíos que frenaron el puntaje:**
          - **Usados UCT (`6.5.1` — -1,28 pts):** Se cerraron **141 ventas contra 142 de objetivo** (faltó 1 auto).
          - **Caída Temprana TPA (`4.5.3`):** Siguió en 0,50 pts (20,9% vs target < 15%).
          - **Salesforce (`1.5.5`):** Cerró en 92,5% (0,60 pts) frente al 100% exigido.
        """)

    st.write("#### Balance Detallado por Indicador en Octubre")
    df_oct_det = pd.DataFrame([
        {
            "Indicador": "1.1.1 SSI Ventas 0km",
            "Sep": "1,13 pts",
            "Oct Real": "2,25 pts",
            "Var": "+1,13 pts",
            "Estado": "Cumplido (50%)"
        },
        {
            "Indicador": "Área ESG (Sustentabilidad)",
            "Sep": "0,36 pts",
            "Oct Real": "0,78 pts",
            "Var": "+0,42 pts",
            "Estado": "Puesto #1 Nacional"
        },
        {
            "Indicador": "Área TCFA (Seguros/Créd.)",
            "Sep": "3,32 pts",
            "Oct Real": "3,60 pts",
            "Var": "+0,28 pts",
            "Estado": "90% Cumplimiento"
        },
        {
            "Indicador": "4.1.1 ICQ Toyota Plan",
            "Sep": "0,60 pts",
            "Oct Real": "0,80 pts",
            "Var": "+0,20 pts",
            "Estado": "Puntaje Perfecto"
        },
        {
            "Indicador": "6.5.1 Ventas Usados UCT",
            "Sep": "3,20 pts",
            "Oct Real": "1,92 pts",
            "Var": "-1,28 pts",
            "Estado": "141/142 (Faltó 1 auto)"
        },
        {
            "Indicador": "9.2.2 Círculo de Calidad",
            "Sep": "0,40 pts",
            "Oct Real": "0,20 pts",
            "Var": "-0,20 pts",
            "Estado": "Bajó al 50%"
        }
    ])
    st.dataframe(df_oct_det, use_container_width=True)

# ==========================================
# 5. PLAN TÁCTICO DE CIERRE Q4
# ==========================================
with tabs[4]:
    st.subheader("🎯 Plan Táctico Q4: Cómo cerrar la brecha de 8,17 pts hacia el Top 10")

    st.markdown("""
    ### Hoja de Ruta Final (Noviembre - Diciembre 2026)
    Para superar la línea del Top 10 (**Senna con 76,77 pts**), el plan se enfoca en 6 frentes:

    1. **CRM Acumulado en menos de 2 hs (`1.5.6` — +1,50 pts):**
       * El acumulado ya bajó de 4,3 hs a **4,1 hs** y los no contactados al **11%**.
       * Mantener la guardia comercial activa perforará las 2 hs y liberará los 1,50 pts plenos.
    2. **Recuperación de Ventas Usados UCT (`6.5.1` — +1,28 pts):**
       * Asegurar el cierre mensual por encima del acumulado exigido (en octubre faltó 1 unidad).
    3. **Contención de Caída Temprana TPA (`4.5.3` — +1,30 pts):**
       * Gestionar activamente las cuotas 1 a 3 de los suscriptores para bajar del 20,9% a < 15%.
    4. **KINTO One Corporativo (`5.5.6` — +1,20 pts):**
       * Hoy figura 1 de 6 contratos activos. Cargar las flotas vigentes en plataforma suma 1,20 pts.
    5. **Salesforce al 100% (`1.5.5` — +0,90 pts) y Campañas Airbags al 70% (`3.5.2` — +0,70 pts):**
       * Elevar Salesforce del 92,5% al 100% y completar 63 infladores (de 229 a 292) suman **+1,60 pts**.
    6. **Servicios Conectados (`9.5.3` — +0,85 pts) y SSI 0km al 75% (`1.1.1` — +1,13 pts):**
       * Activar la app Toyota en el 90% de las entregas (hoy 72%) y sostener sorteos de encuestas.
    """)
