# ==========================================
# 6. PESTAÑA: DOCUMENTACIÓN Y FUENTES
# ==========================================
with tab_docs:
    st.subheader("📚 Centro de Documentación y Fuentes Oficiales TASA")
    st.markdown("Consulte las reglas metodológicas, las planillas de origen y la matriz completa de indicadores DEP 2026:")

    c_doc1, c_doc2 = st.columns(2)
    
    with c_doc1:
        st.info("📄 **Manual Oficial DEP 2026**\n\nNormativa de Toyota Argentina con la descripción, criterios de calificación y ponderaciones por área.")
        try:
            with open("Manual DEP 2026.pdf", "rb") as pdf_file:
                st.download_button(
                    label="📥 Descargar Manual DEP 2026 (PDF)",
                    data=pdf_file,
                    file_name="Manual DEP 2026.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.warning("⚠️ El archivo 'Manual DEP 2026.pdf' no se encuentra en el repositorio.")

    with c_doc2:
        st.success("📊 **Planilla Acumulada Oficial (Red TASA)**\n\nResultados oficiales de la Red comercial extraídos directamente del sistema de auditoría Power BI.")
        try:
            with open("15437_DES015-26 DEP 2026 - ACUM. JUN 2.xlsx", "rb") as excel_file:
                st.download_button(
                    label="📥 Descargar Planilla Acumulada (Excel)",
                    data=excel_file,
                    file_name="15437_DES015-26 DEP 2026 - ACUM. JUN 2.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        except FileNotFoundError:
            st.warning("⚠️ El archivo Excel acumulado no se encuentra en el repositorio.")

    st.divider()
    st.subheader("🔍 Catálogo Completo de Indicadores del Manual DEP 2026")

    items_manual = [
        ("1.1.1", "Ventas", "Calidad", "SSI - Sales Satisfaction Index", "Mensual", "4,5%"),
        ("1.1.2", "Ventas", "Calidad", "ICQ - Índice de Contención de Quejas", "Cuatrimestral", "1,5%"),
        ("1.1.3", "Ventas", "Calidad", "NPS - Net Promoter Score Ventas", "Mensual", "1,2%"),
        ("1.4.1", "Ventas", "Facilities", "Imagen, Mantenimiento y 5S: Exterior e interior", "Semestral", "3,0%"),
        ("1.5.1", "Ventas", "Targets", "Cumplimiento de objetivos acumulados Hilux, SW4 & Hiace", "Mensual", "3,0%"),
        ("1.5.2", "Ventas", "Targets", "Cumplimiento de obj. acumulados Corolla, CCross, Yaris, Yaris Cross", "Mensual", "3,0%"),
        ("1.5.3", "Ventas", "Targets", "Patentamientos vs declaración de ventas", "Mensual", "2,1%"),
        ("1.5.4", "Ventas", "Targets", "Extrazona / Cobertura", "Mensual", "0,7%"),
        ("1.5.5", "Ventas", "Targets", "Actualización Salesforce: Lista de Espera y Patentamientos", "Mensual", "1,5%"),
        ("1.5.6", "Ventas", "Targets", "Gestión Digital y Adopción CRM", "Mensual", "1,5%"),
        ("2.5.1", "Ventas Especiales", "Targets", "Cumplimiento de plan de negocios (VE + Kinto ONE)", "Cuatrimestral", "3,5%"),
        ("2.5.2", "Ventas Especiales", "Targets", "Lista de espera actualizada", "Cuatrimestral", "1,5%"),
        ("3.1.1", "Posventa", "Calidad", "CSI - Customer Satisfaction Index Posventa", "Mensual", "2,7%"),
        ("3.1.2", "Posventa", "Calidad", "FIR - Fix It Right", "Mensual", "2,7%"),
        ("3.1.3", "Posventa", "Calidad", "ICQ - Índice de Contención de Quejas Posventa", "Cuatrimestral", "1,0%"),
        ("3.1.4", "Posventa", "Calidad", "NPS - Net Promoter Score Posventa", "Mensual", "1,4%"),
        ("3.1.5", "Posventa", "Calidad", "CSI de Chapa y Pintura (B&P)", "Mensual", "0,7%"),
        ("3.2.1", "Posventa", "Programas", "Certificación TSM-FIR", "Semestral", "1,4%"),
        ("3.2.2", "Posventa", "Programas", "Programas de excelencia (Mantenimiento Express - Lavado)", "Semestral", "2,0%"),
        ("3.2.3", "Posventa", "Programas", "EcoDealer / ISO 14001", "Semestral", "1,0%"),
        ("3.2.4", "Posventa", "Programas", "Sostenimiento periódico de la operación (Visitas Fieldman)", "Mensual", "4,0%"),
        ("3.3.1", "Posventa", "RRHH", "Índice de rotación del personal de posventa", "Anual", "1,4%"),
        ("3.3.2", "Posventa", "RRHH", "Dotación de personal de posventa", "Semestral", "2,7%"),
        ("3.5.1", "Posventa", "Targets", "CPUS - Unidades Atendidas en Taller", "Mensual", "1,7%"),
        ("3.5.2", "Posventa", "Targets", "Campañas de Seguridad Airbags (ABI 414/415)", "Mensual", "1,4%"),
        ("3.5.3", "Posventa", "Targets", "Objetivo de Accesorios", "Mensual", "1,0%"),
        ("3.5.4", "Posventa", "Targets", "Objetivo de Neumáticos", "Mensual", "1,0%"),
        ("3.5.5", "Posventa", "Targets", "Performance de garantías (RDG)", "Mensual", "0,6%"),
        ("3.5.6", "Posventa", "Targets", "Nivelación de pedidos de repuestos", "Mensual", "0,3%"),
        ("3.5.7", "Posventa", "Targets", "Puntos Negativos (Compromisos Fieldman / Obj. Cualitativos)", "Cuatrimestral", "-3,4%"),
        ("4.1.1", "TPA", "Calidad", "ICQ - Índice de Contención de Quejas TPA", "Mensual", "0,8%"),
        ("4.1.2", "TPA", "Calidad", "NPS Transaccional (Suscriptor - Adjudicado - Entregado)", "Cuatrimestral", "0,8%"),
        ("4.3.1", "TPA", "RRHH", "Estructura de RRHH de administración TPA", "Semestral", "0,6%"),
        ("4.5.1", "TPA", "Targets", "Suscripciones (Mix de modelos & Venta Online)", "Mensual", "2,0%"),
        ("4.5.2", "TPA", "Targets", "Pedidos confirmados", "Mensual", "1,4%"),
        ("4.5.3", "TPA", "Targets", "Caída temprana (Baja en primeros 6 meses)", "Mensual", "2,0%"),
        ("4.5.4", "TPA", "Targets", "Cuotas emitidas (Crecimiento de cartera)", "Mensual", "1,4%"),
        ("5.1.1", "KINTO", "Calidad", "ICQ - Share", "Mensual", "0,2%"),
        ("5.1.2", "KINTO", "Calidad", "NPS - Share", "Mensual", "0,6%"),
        ("5.1.3", "KINTO", "Calidad", "NPS - One", "Mensual", "0,6%"),
        ("5.5.1", "KINTO", "Targets", "Porcentaje de ocupación - Share", "Mensual", "0,7%"),
        ("5.5.2", "KINTO", "Targets", "Flota mínima - Share", "Mensual", "0,7%"),
        ("5.5.3", "KINTO", "Targets", "Bookings - Share", "Mensual", "0,7%"),
        ("5.5.4", "KINTO", "Targets", "Preparación y entregas de unidades - One", "Trimestral", "0,3%"),
        ("5.5.5", "KINTO", "Targets", "Gestión de siniestros - One", "Trimestral", "0,3%"),
        ("5.5.6", "KINTO", "Targets", "PN Corporativo - Bookings - One", "Mensual", "1,2%"),
        ("5.5.7", "KINTO", "Targets", "Devolución y Venta de unidades - One", "Mensual", "0,7%"),
        ("6.1.1", "Usados", "Calidad", "SSI - Sales Satisfaction Index Usados Certificados (UCT)", "Mensual", "0,8%"),
        ("6.1.2", "Usados", "Calidad", "NPS - Net Promoter Score Usados Certificados (UCT)", "Mensual", "0,8%"),
        ("6.5.1", "Usados", "Targets", "Ventas UCT (Oro y Plata)", "Mensual", "3,2%"),
        ("6.5.2", "Usados", "Targets", "Trade In % (Toma/Compra vs Venta Convencional)", "Mensual", "1,2%"),
        ("7.5.1", "TCFA", "Targets", "Financiación (M$ Liquidaciones 0km y Usados)", "Mensual", "1,7%"),
        ("7.5.2", "TCFA", "Targets", "Seguros 0km", "Mensual", "0,8%"),
        ("7.5.3", "TCFA", "Targets", "Seguros Usados", "Mensual", "0,6%"),
        ("7.5.4", "TCFA", "Targets", "Fidelidad en 0km (Prendas inscriptas TCFA)", "Mensual", "0,6%"),
        ("7.5.5", "TCFA", "Targets", "Crecimiento Cartera de seguros", "Mensual", "0,4%"),
        ("8.5.1", "ESG", "Targets", "E: Envío de plan con actividades de reducción de emisiones de CO2", "Proyecto", "0,3%"),
        ("8.5.2", "ESG", "Targets", "S: Iniciativa Social alineada a temas materiales de TMC", "Proyecto", "0,35%"),
        ("8.5.3", "ESG", "Targets", "G: Políticas ABAC / Reporte Sustentabilidad", "Proyecto", "0,35%"),
        ("9.1.1", "General", "Calidad", "Excelencia Calidad (Premio por cumplir NPS en todas las áreas)", "Semestral", "1,6%"),
        ("9.2.1", "General", "Programas", "Estilo de Movilidad Toyota - EMT (Puntos Negativos)", "Semestral", "-5,0%"),
        ("9.2.2", "General", "Programas", "Círculos Kaizen", "Anual", "0,4%"),
        ("9.3.1", "General", "RRHH", "Dotación Adecuada (Estructura de Mkt, RRHH y Calidad)", "Semestral", "3,5%"),
        ("9.3.2", "General", "RRHH", "Capacitación (Matriz de niveles aprobados por puesto)", "Semestral", "3,5%"),
        ("9.3.3", "General", "RRHH", "Nivel de rotación de personal general", "Anual", "0,6%"),
        ("9.3.4", "General", "RRHH", "Satisfacción de empleados (Encuesta Clima Laboral)", "Anual", "3,3%"),
        ("9.4.1", "General", "Facilities", "Objetivos cualitativos de Infraestructura (Instalaciones 2.0)", "Anual", "4,5%"),
        ("9.5.1", "General", "Targets", "Absorción de Costos Fijos", "Cuatrimestral", "0,9%"),
        ("9.5.2", "General", "Targets", "Fair Play (Penalización sobreprecios / reventas)", "Anual", "-10,0%"),
        ("9.5.3", "General", "Targets", "Vehículos con Full Onboarding de Servicios Conectados", "Mensual", "1,7%")
    ]

    df_cat = pd.DataFrame(items_manual, columns=["Código TASA", "Área", "Categoría", "Descripción Oficial TASA", "Frecuencia", "% Ponderado Total"])
    filtro_area = st.multiselect("Filtrar por Área:", options=df_cat["Área"].unique(), default=df_cat["Área"].unique())
    df_filtrado = df_cat[df_cat["Área"].isin(filtro_area)]
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
