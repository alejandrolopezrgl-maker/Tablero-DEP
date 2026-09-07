# =======================================================
# 3. PESTAÑA: DESEMPEÑO REGIONAL, ÁREA Y CATEGORÍA
# =======================================================
with tab_regional:
    st.subheader("🗺️ Diagnóstico Integral Oficial (Corte Acumulado Julio 2026)")
    st.caption("Consolidado Oficial de Power BI: Áreas Operativas, Categorías Normativas y Benchmarking Regional")

    # Tarjetas métricas superiores consolidadas
    m1, m2, m3, m4 = st.columns(4)
    with m1: 
        st.metric("Score Global Autolux", "68,56 pts", "71,05% del Ideal (P21)")
    with m2: 
        st.metric("Región NOA (Líder)", "71,96 pts", "74,57% del Ideal")
    with m3: 
        st.metric("Pilar Líder en Calidad", "Programas (Puesto 1)", "100,0% Efectividad 🏆")
    with m4: 
        st.metric("Gestión del Capital", "RRHH (Puesto 6)", "91,89% Efectividad 🌟")

    st.markdown("---")

    # DataFrames oficiales de las capturas
    data_area_lux = {
        "Área": ["POSVENTA", "TPA", "TCFA", "USADOS", "GENERAL", "KINTO", "VENTAS", "ESG", "VENTAS ESPECIALES"],
        "Posición Red": [9, 5, 16, 16, 20, 37, 41, 7, 20],
        "Ptj. LUX": [25.95, 7.87, 3.32, 4.40, 11.92, 2.50, 8.35, 0.36, 1.50],
        "Ptj. Ideal": [27.00, 9.00, 4.00, 6.00, 16.50, 6.00, 22.00, 1.00, 5.00],
        "% Ideal LUX": [96.11, 87.42, 83.00, 73.33, 72.26, 41.67, 37.95, 35.50, 30.00]
    }
    df_area = pd.DataFrame(data_area_lux).sort_values(by="% Ideal LUX", ascending=False)

    data_cat_lux = {
        "Categoría": ["PROGRAMAS", "RRHH", "FACILITIES", "TARGETS", "CALIDAD"],
        "Posición Red": [1, 6, 13, 12, 38],
        "Ptj. LUX": [8.80, 11.12, 6.15, 27.90, 12.20],
        "Ptj. Ideal": [8.80, 12.10, 7.50, 46.20, 21.90],
        "% Ideal LUX": [100.00, 91.89, 82.00, 60.38, 55.71]
    }
    df_cat = pd.DataFrame(data_cat_lux).sort_values(by="% Ideal LUX", ascending=False)

    data_regional = {
        "Región": ["NOA (Líder)", "Cuyo", "NEA", "Patagonia", "Centro", "Total RED"],
        "Ptj. Logrado": [71.96, 71.03, 68.57, 68.34, 66.17, 67.50],
        "% Ideal": [74.57, 73.60, 71.05, 70.82, 68.57, 69.95]
    }
    df_reg = pd.DataFrame(data_regional)

    # 1. Gráficos Comparativos en 2 Columnas
    c_g1, c_g2 = st.columns(2)
    with c_g1:
        st.subheader("📊 Cumplimiento por Unidades de Negocio (% Ideal)")
        fig_area = px.bar(
            df_area, 
            x="% Ideal LUX", 
            y="Área", 
            orientation="h",
            text="% Ideal LUX", 
            color="% Ideal LUX",
            color_continuous_scale=["#d62728", "#f39c12", "#27ae60"]
        )
        fig_area.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig_area.update_layout(xaxis=dict(range=[0, 115]), yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_area, use_container_width=True)

    with c_g2:
        st.subheader("🏆 Comparativa de Rendimiento Regional (% Ideal)")
        fig_reg = px.bar(
            df_reg, 
            x="Región", 
            y="% Ideal", 
            text="% Ideal",
            color="Región",
            color_discrete_map={
                "NOA (Líder)": "#1F4E78", 
                "Cuyo": "#5B9BD5", 
                "NEA": "#8FAADC", 
                "Patagonia": "#A6A6A6", 
                "Centro": "#C65911", 
                "Total RED": "#70AD47"
            }
        )
        fig_reg.add_hline(y=71.05, line_dash="dot", line_color="#d62728", annotation_text="Autolux: 71,05%", annotation_position="bottom right")
        fig_reg.update_traces(texttemplate='%{text:.2f}%', textposition='inside')
        fig_reg.update_layout(showlegend=False, yaxis=dict(range=[0, 85]))
        st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("---")

    # 2. Tablas Oficiales Consolidadas
    st.subheader("📋 Tablas Consolidadas Oficiales (Power BI TASA)")
    col_t1, col_t2, col_t3 = st.columns(3)

    with col_t1:
        st.markdown("**1. Logro por Área**")
        df_mostrar_area = df_area.copy()
        df_mostrar_area["% Ideal LUX"] = df_mostrar_area["% Ideal LUX"].map("{:.2f}%".format)
        df_mostrar_area["Ptj. LUX"] = df_mostrar_area["Ptj. LUX"].map("{:.2f}".format)
        df_mostrar_area["Ptj. Ideal"] = df_mostrar_area["Ptj. Ideal"].map("{:.2f}".format)
        st.dataframe(df_mostrar_area, use_container_width=True, hide_index=True)

    with col_t2:
        st.markdown("**2. Logro por Categoría**")
        df_mostrar_cat = df_cat.copy()
        df_mostrar_cat["% Ideal LUX"] = df_mostrar_cat["% Ideal LUX"].map("{:.2f}%".format)
        df_mostrar_cat["Ptj. LUX"] = df_mostrar_cat["Ptj. LUX"].map("{:.2f}".format)
        df_mostrar_cat["Ptj. Ideal"] = df_mostrar_cat["Ptj. Ideal"].map("{:.2f}".format)
        st.dataframe(df_mostrar_cat, use_container_width=True, hide_index=True)

    with col_t3:
        st.markdown("**3. Logro por Región**")
        df_mostrar_reg = df_reg.copy()
        df_mostrar_reg["% Ideal"] = df_mostrar_reg["% Ideal"].map("{:.2f}%".format)
        df_mostrar_reg["Ptj. Logrado"] = df_mostrar_reg["Ptj. Logrado"].map("{:.2f}".format)
        st.dataframe(df_mostrar_reg, use_container_width=True, hide_index=True)
