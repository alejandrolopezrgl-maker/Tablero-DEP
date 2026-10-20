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
st.caption("Programa de Excelencia de Concesionarios Toyota (DEP) | Auditoría Agosto & Proyección Septiembre")

# Pestañas principales (con la nueva Proyección Septiembre 2026)
tabs = st.tabs([
    "📊 Resumen Ejecutivo (Agosto Oficial)",
    "🔮 Proyección Septiembre 2026",
    "🎯 Escenarios y Plan de Acción Q4",
    "📈 Evolución Histórica y Gaps"
])

# ==========================================
# 1. RESUMEN EJECUTIVO (AGOSTO OFICIAL)
# ==========================================
with tabs[0]:
    st.subheader("Estado Oficial de Autolux en la Red Toyota (Cierre Agosto 2026)")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Posición Nacional", "Puesto 24", "de 44 Concesionarios")
    col2.metric("Cumplimiento General", "69,24%", "66,81 / 96,50 pts")
    col3.metric("Corte Top 10 (P10 BHA)", "76,53%", "73,85 pts (Gap: -7,04)")
    col4.metric("Pilares de Élite", "Posventa & TPA", "Top 10 en la Red")

    st.markdown("---")
    
    # Datos oficiales por Área
    df_areas = pd.DataFrame([
        {"Area": "Posventa", "Puntos_Max": 27.0, "Score_LUX": 25.95, "Cumplimiento": 96.11, "Ranking": 9, "Estado": "Élite"},
        {"Area": "Toyota Plan (TPA)", "Puntos_Max": 9.0, "Score_LUX": 7.84, "Cumplimiento": 87.14, "Ranking": 7, "Estado": "Élite"},
        {"Area": "TCFA (Financiera)", "Puntos_Max": 4.0, "Score_LUX": 3.32, "Cumplimiento": 83.00, "Ranking": 17, "Estado": "Sólido"},
        {"Area": "Usados", "Puntos_Max": 6.0, "Score_LUX": 4.40, "Cumplimiento": 73.33, "Ranking": 18, "Estado": "Regular"},
        {"Area": "General", "Puntos_Max": 16.5, "Score_LUX": 11.92, "Cumplimiento": 72.26, "Ranking": 22, "Estado": "Regular"},
        {"Area": "KINTO", "Puntos_Max": 6.0, "Score_LUX": 2.50, "Cumplimiento": 41.67, "Ranking": 41, "Estado": "Crítico"},
        {"Area": "Ventas Convencionales", "Puntos_Max": 22.0, "Score_LUX": 9.02, "Cumplimiento": 41.02, "Ranking": 41, "Estado": "Crítico"},
        {"Area": "ESG", "Puntos_Max": 1.0, "Score_LUX": 0.36, "Cumplimiento": 35.50, "Ranking": 7, "Estado": "Sólido"},
        {"Area": "Ventas Especiales", "Puntos_Max": 5.0, "Score_LUX": 1.50, "Cumplimiento": 30.00, "Ranking": 18, "Estado": "Crítico"},
    ])

    ca1, ca2 = st.columns(2)
    with ca1:
        st.write("#### Cumplimiento por Área (% sobre Objetivo)")
        fig_area = px.bar(
            df_areas.sort_values(by="Cumplimiento", ascending=True),
            x="Cumplimiento", y="Area", orientation="h",
            text="Cumplimiento",
            color="Cumplimiento",
            color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
            range_color=[30, 100]
        )
        fig_area.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
        fig_area.update_layout(showlegend=False, xaxis_title="% Cumplimiento", yaxis_title="")
        st.plotly_chart(fig_area, use_container_width=True)

    with ca2:
        st.write("#### Categorías Transversales")
        df_cat = pd.DataFrame([
            {"Categoría": "Programas", "Cumplimiento": 100.0, "Ranking": 1},
            {"Categoría": "RRHH", "Cumplimiento": 92.0, "Ranking": 5},
            {"Categoría": "Facilities", "Cumplimiento": 82.0, "Ranking": 14},
            {"Categoría": "Targets", "Cumplimiento": 58.0, "Ranking": 18},
            {"Categoría": "Calidad", "Cumplimiento": 63.0, "Ranking": 36},
        ])
        fig_cat = px.bar(
            df_cat, x="Categoría", y="Cumplimiento", text="Cumplimiento",
            color="Cumplimiento",
            color_continuous_scale=["#e74c3c", "#f1c40f", "#2ecc71"],
            range_color=[50, 100]
        )
        fig_cat.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
        fig_cat.update_layout(showlegend=False, yaxis_title="% Cumplimiento")
        st.plotly_chart(fig_cat, use_container_width=True)

    st.write("#### Detalle Oficial de Puntos y Rankings por Área")
    st.dataframe(
        df_areas[["Area", "Score_LUX", "Puntos_Max", "Cumplimiento", "Ranking", "Estado"]].style.format({
            "Score_LUX": "{:.2f} pts",
            "Puntos_Max": "{:.1f} pts",
            "Cumplimiento": "{:.1f}%",
            "Ranking": "#{:.0f}"
        }),
        use_container_width=True
    )

# ==========================================
# 2. PROYECCIÓN SEPTIEMBRE 2026
# ==========================================
with tabs[1]:
    st.subheader("🔮 Proyección DEP Septiembre 2026 (Datos Reales de Cierre)")
    st.info("Esta proyección modela los datos oficiales reportados en septiembre: tiempos de respuesta en CRM (< 2 hs), cierre Q3 de KINTO (69,3%), Usados (75%), Calidad 0km y el ajuste prudente en NPS TPA.")

    base_aug = 66.81
    # Variaciones de puntos
    gain_crm = 1.50          # < 2 hs confirmado (+1.50 pts plenos)
    gain_kinto = 1.66        # 4.16 pts en KINTO Q3 vs 2.50 pts en agosto
    gain_usados_cons = 0.10  # 75% asegurado en Usados
    gain_usados_mod = 0.60   # Si convalida 75% en Calidad Usados
    gain_0km_mod = 1.125     # Si SSI escala a tier 50%
    
    # Impacto TPA NPS (advertencia de desvío de objetivo)
    loss_tpa_prudente = -0.40 # Si TASA quita los 0.40 pts parciales de agosto
    keep_tpa_base = 0.00      # Si TASA mantiene el 50% parcial (0.40 pts)

    score_prud = base_aug + gain_crm + gain_kinto + gain_usados_cons + loss_tpa_prudente
    score_base = base_aug + gain_crm + gain_kinto + gain_usados_cons + keep_tpa_base
    score_fav = base_aug + gain_crm + gain_kinto + gain_usados_mod + gain_0km_mod + keep_tpa_base

    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        st.metric(
            "Escenario Prudente (NPS TPA = 0)", 
            f"{score_prud:.2f} pts", 
            f"+{score_prud - base_aug:.2f} pts (72,20%)", 
            delta_color="normal"
        )
        st.caption("Puesto Proyectado: **#15** (+9 posiciones) | Asume pérdida de los 0,40 pts de TPA NPS.")
    with cp2:
        st.metric(
            "Escenario Base (TPA Parcial 0,40)", 
            f"{score_base:.2f} pts", 
            f"+{score_base - base_aug:.2f} pts (72,62%)", 
            delta_color="normal"
        )
        st.caption("Puesto Proyectado: **#14** (+10 posiciones) | Mantiene tramo del 50% en TPA.")
    with cp3:
        st.metric(
            "Escenario Favorable (Calidad + SSI)", 
            f"{score_fav:.2f} pts", 
            f"+{score_fav - base_aug:.2f} pts (74,30%)", 
            delta_color="normal"
        )
        st.caption("Puesto Proyectado: **#12** (+12 posiciones) | Captura mejoras en Usados y SSI 0km.")

    st.markdown("---")

    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.write("#### Cascada de Variación de Puntos (Escenario Prudente)")
        fig_waterfall = go.Figure(go.Waterfall(
            name="Puntos DEP",
            orientation="v",
            measure=["absolute", "relative", "relative", "relative", "relative", "total"],
            x=["Agosto Base", "CRM (<2h)", "KINTO (Q3)", "Usados (75%)", "NPS TPA (Desvío)", "Septiembre Proy."],
            textposition="outside",
            text=["66.81", "+1.50", "+1.66", "+0.10", "-0.40", f"{score_prud:.2f}"],
            y=[66.81, 1.50, 1.66, 0.10, -0.40, 0],
            connector={"line": {"color": "#7f8c8d"}},
            decreasing={"marker": {"color": "#e74c3c"}},
            increasing={"marker": {"color": "#2ecc71"}},
            totals={"marker": {"color": "#3498db"}}
        ))
        fig_waterfall.update_layout(yaxis_title="Puntos DEP", yaxis_range=[64, 72])
        st.plotly_chart(fig_waterfall, use_container_width=True)

    with col_w2:
        st.write("#### Escalamiento en el Ranking Nacional")
        df_ranking_chart = pd.DataFrame([
            {"Concesionario": "Autolux Agosto (Base)", "Puntos": 66.81, "Puesto": "#24", "Color": "#95a5a6"},
            {"Concesionario": "Haimovich", "Puntos": 68.97, "Puesto": "#15", "Color": "#bdc3c7"},
            {"Concesionario": "Zento", "Puntos": 69.78, "Puesto": "#14", "Color": "#bdc3c7"},
            {"Concesionario": "Autolux Sept. (Prudente)", "Puntos": score_prud, "Puesto": "#15", "Color": "#2ecc71"},
            {"Concesionario": "Autolux Sept. (Base)", "Puntos": score_base, "Puesto": "#14", "Color": "#27ae60"},
            {"Concesionario": "Kansai", "Puntos": 70.14, "Puesto": "#13", "Color": "#bdc3c7"},
            {"Concesionario": "Alianz", "Puntos": 71.00, "Puesto": "#12", "Color": "#bdc3c7"},
            {"Concesionario": "Autolux Sept. (Favorable)", "Puntos": score_fav, "Puesto": "#12", "Color": "#1abc9c"},
            {"Concesionario": "B.H.A.S. (Línea Top 10)", "Puntos": 73.85, "Puesto": "#10", "Color": "#e74c3c"}
        ])
        fig_rank = px.bar(
            df_ranking_chart, x="Puntos", y="Concesionario", orientation="h",
            text="Puesto", color="Concesionario",
            color_discrete_map={row["Concesionario"]: row["Color"] for _, row in df_ranking_chart.iterrows()}
        )
        fig_rank.update_traces(textposition="inside")
        fig_rank.update_layout(showlegend=False, xaxis_range=[65, 75], xaxis_title="Puntos DEP")
        st.plotly_chart(fig_rank, use_container_width=True)

    st.write("#### Balance Detallado por Indicador en Septiembre")
    df_eval_sep = pd.DataFrame([
        {"Indicador": "1.5.6 CRM y Tiempos de Respuesta", "Ponderado": "1,50 pts", "Agosto": "0,00 pts", "Septiembre": "1,50 pts", "Variación": "+1,50 pts", "Estado": "Consolidado (< 2 hs)"},
        {"Indicador": "Área KINTO Completa", "Ponderado": "6,00 pts", "Agosto": "2,50 pts", "Septiembre": "4,16 pts", "Variación": "+1,66 pts", "Estado": "Cierre Q3 Oficial (69,3%)"},
        {"Indicador": "Área Usados", "Ponderado": "6,00 pts", "Agosto": "4,40 pts", "Septiembre": "4,50 pts", "Variación": "+0,10 pts", "Estado": "75% asegurado (SSI 94,0)"},
        {"Indicador": "4.1.2 NPS Toyota Plan (TPA)", "Ponderado": "0,80 pts", "Agosto": "0,40 pts", "Septiembre": "0,00 a 0,40 pts", "Variación": "-0,40 a 0,00 pts", "Estado": "Alerta (Desvío en Target)"},
        {"Indicador": "3.5.2 Campañas Recall Airbags", "Ponderado": "1,40 pts", "Agosto": "0,35 pts", "Septiembre": "0,35 pts", "Variación": "0,00 pts", "Estado": "Avance 241/554 (Objetivo 70% Q4)"},
        {"Indicador": "1.1.1 & 1.1.3 Calidad 0km (SSI/NPS)", "Ponderado": "5,70 pts", "Agosto": "1,73 pts", "Septiembre": "1,73 pts", "Variación": "0,00 pts", "Estado": "SSI YTD 94,9 / NPS YTD 83,8%"},
    ])
    st.dataframe(df_eval_sep, use_container_width=True)

# ==========================================
# 3. ESCENARIOS Y PLAN DE ACCIÓN Q4
# ==========================================
with tabs[2]:
    st.subheader("🎯 Plan Táctico de Cierre: Camino Definitivo al Top 10")
    
    st.markdown("""
    ### 1. La Brecha Final hacia Diciembre (Puesto 10: 73,85 pts)
    Habiendo cerrado septiembre en **~69,67 a 70,07 puntos (Puesto 14/15)**, la distancia con el Top 10 se redujo a solo **3,8 puntos**:
    
    * **Paso 1: Patentamientos vs. Declaraciones (1.5.3 - Ganancia: +1,05 pts)**
      * Ingresar carpetas al registro seccional dentro de las 48 hs para elevar el ratio de patentamientos del 86% al $\ge 90\%$.
    
    * **Paso 2: Cumplimiento del 70% en Airbags (3.5.2 - Ganancia: +0,70 pts)**
      * Hoy el taller lleva 241 infladores cambiados. Para cruzar el umbral del 70% (388 unidades) faltan **147 vehículos**.
      * Con ese escalón del 70%, el ítem salta de 0,35 pts a 1,05 pts plenos.
    
    * **Paso 3: Sorteos e Impulso en Encuestas 0km (1.1.1 - Ganancia: +1,13 a +2,25 pts)**
      * El SSI Puro cerró septiembre en 95,0 (a solo 0,6 pts del target de red de 95,6).
      * Aumentar la masa de encuestas con el plan de incentivos diluye quejas aisladas y habilita los escalones del 50% o 75% en SSI.
    
    * **Paso 4: Contención en NPS TPA (4.1.2 - Recuperación: +0,40 pts)**
      * Si TASA no convalida puntos en septiembre por desvío en ahorristas, reforzar el seguimiento del suscriptor adjudicado en el momento de la entrega para recuperar el tramo de 0,40 pts en Q4.
    """)

# ==========================================
# 4. EVOLUCIÓN HISTÓRICA Y GAPS
# ==========================================
with tabs[3]:
    st.subheader("📈 Evolución Histórica de Autolux en 2026")
    
    df_evo = pd.DataFrame([
        {"Mes": "Mayo 2026", "Puntos": 64.20, "Cumplimiento": 66.53, "Ranking": 28},
        {"Mes": "Junio 2026", "Puntos": 65.10, "Cumplimiento": 67.46, "Ranking": 26},
        {"Mes": "Julio 2026", "Puntos": 65.90, "Cumplimiento": 68.29, "Ranking": 25},
        {"Mes": "Agosto 2026 (Oficial)", "Puntos": 66.81, "Cumplimiento": 69.24, "Ranking": 24},
        {"Mes": "Septiembre 2026 (Proy. Prudente)", "Puntos": score_prud, "Cumplimiento": (score_prud / 96.5) * 100, "Ranking": 15},
        {"Mes": "Meta Diciembre 2026 (Top 10)", "Puntos": 74.50, "Cumplimiento": 77.20, "Ranking": 10},
    ])

    fig_evo = px.line(
        df_evo, x="Mes", y="Cumplimiento", text="Cumplimiento",
        markers=True, title="Evolución de Cumplimiento General (%)"
    )
    fig_evo.update_traces(texttemplate="%{text:.1f}%", textposition="top center")
    fig_evo.add_hline(y=76.53, line_dash="dash", line_color="red", annotation_text="Línea de Corte Top 10 (76,53%)")
    st.plotly_chart(fig_evo, use_container_width=True)
