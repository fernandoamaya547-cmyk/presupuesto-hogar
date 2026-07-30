import streamlit as st
import pandas as pd

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Gestor de Presupuesto Automatizado",
    page_icon="💰",
    layout="wide"
)

# ==========================================
# INICIALIZACIÓN DEL ESTADO (SESSION STATE)
# ==========================================

# 1. CATÁLOGO / BASE DE CONCEPTOS DISPONIBLES
if "catalogo_conceptos" not in st.session_state:
    st.session_state["catalogo_conceptos"] = pd.DataFrame([
        {"Concepto": "Arriendo", "Tipo": "Fijo", "Monto Base (COP)": 1500000},
        {"Concepto": "Servicios Públicos", "Tipo": "Variable", "Monto Base (COP)": 350000},
        {"Concepto": "Mercado", "Tipo": "Variable", "Monto Base (COP)": 800000},
        {"Concepto": "Internet", "Tipo": "Fijo", "Monto Base (COP)": 120000},
        {"Concepto": "Administración", "Tipo": "Fijo", "Monto Base (COP)": 250000},
        {"Concepto": "Imprevistos / Varios", "Tipo": "Variable", "Monto Base (COP)": 200000}
    ])

# 2. BASE DE DATOS DE PRESUPUESTOS MENSUALES GENERADOS
if "presupuesto_db" not in st.session_state:
    st.session_state["presupuesto_db"] = pd.DataFrame([
        {"ID": 101, "Mes": "Julio", "Año": 2026, "Concepto": "Arriendo", "Tipo": "Fijo", "Monto Presupuestado": 1500000, "Monto Pagado": 1500000, "Estado": "Pagado"},
        {"ID": 102, "Mes": "Julio", "Año": 2026, "Concepto": "Servicios Públicos", "Tipo": "Variable", "Monto Presupuestado": 350000, "Monto Pagado": 320000, "Estado": "Pagado"},
        {"ID": 103, "Mes": "Julio", "Año": 2026, "Concepto": "Mercado", "Tipo": "Variable", "Monto Presupuestado": 800000, "Monto Pagado": 0, "Estado": "Pendiente"}
    ])

# ==========================================
# BARRA LATERAL: SELECCIÓN DE DOMINIO / USUARIO
# ==========================================
st.sidebar.title("👥 Control de Usuarios y Dominios")
dominio_seleccionado = st.sidebar.selectbox(
    "Selecciona el módulo / perfil:",
    [
        "Presupuesto de Casa (Consulta / Pagos)",
        "Presupuesto General (Administración)"
    ]
)
st.sidebar.divider()

# ==========================================
# DOMINIO 1: PRESUPUESTO DE CASA (CONSULTA / DASHBOARD)
# ==========================================
if dominio_seleccionado == "Presupuesto de Casa (Consulta / Pagos)":
    st.title("🏠 Presupuesto de Pagos Casa")
    st.info("Módulo: Consulta General — Control de cumplimiento, totales y estado de los pagos del hogar.")

    df = st.session_state["presupuesto_db"]

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        meses = ["Todos"] + list(df["Mes"].unique()) if not df.empty else ["Todos"]
        mes_sel = st.selectbox("Filtrar por Mes:", meses)
    with col_f2:
        anios = ["Todos"] + list(df["Año"].unique()) if not df.empty else ["Todos"]
        anio_sel = st.selectbox("Filtrar por Año:", anios)

    df_filtrado = df.copy()
    if mes_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_sel]
    if anio_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == anio_sel]

    st.subheader("📊 Dashboard de Cumplimiento")
    total_presupuestado = df_filtrado["Monto Presupuestado"].sum() if not df_filtrado.empty else 0
    total_pagado = df_filtrado["Monto Pagado"].sum() if not df_filtrado.empty else 0
    total_pendiente = total_presupuestado - total_pagado
    porcentaje = (total_pagado / total_presupuestado * 100) if total_presupuestado > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Presupuestado", f"${total_presupuestado:,.0f} COP")
    c2.metric("Total Pagado", f"${total_pagado:,.0f} COP")
    c3.metric("Pendiente por Pagar", f"${total_pendiente:,.0f} COP")
    c4.metric("% Cumplimiento", f"{porcentaje:.1f}%")

    st.divider()
    st.subheader("📋 Histórico de Pagos de la Casa")
    if not df_filtrado.empty:
        st.dataframe(
            df_filtrado.style.format({
                "Monto Presupuestado": "${:,.0f} COP",
                "Monto Pagado": "${:,.0f} COP"
            }),
            use_container_width=True
        )
    else:
        st.warning("No hay registros para los filtros seleccionados.")

# ==========================================
# DOMINIO 2: PRESUPUESTO GENERAL (ADMINISTRACIÓN COMPLETA)
# ==========================================
else:
    st.title("⚙️ Presupuesto General - Panel de Control")

    tab_conceptos, tab_crear_mes, tab_liquidar, tab_historial = st.tabs([
        "➕ Catálogo de Conceptos",
        "📅 Generar Presupuesto Mensual",
        "✅ Cierre / Liquidación de Pagos",
        "📊 Histórico General"
    ])

    # ----------------------------------------------------
    # TAB 1: CATÁLOGO Y REGISTRO DE NUEVO CONCEPTO
    # ----------------------------------------------------
    with tab_conceptos:
        st.subheader("1. Registrar un Nuevo Concepto de Gasto")
        st.caption("Añade conceptos predeterminados que luego podrás seleccionar para cualquier mes.")

        with st.form("form_nuevo_concepto", clear_on_submit=True):
            col_c1, col_c2, col_c3 = st.columns([3, 2, 2])
            with col_c1:
                nuevo_concepto = st.text_input("Nombre del Concepto (ej. Seguro del Carro):")
            with col_c2:
                tipo_gasto = st.selectbox("Tipo de Gasto:", ["Fijo", "Variable"])
            with col_c3:
                monto_base = st.number_input("Valor Base Sugerido (COP):", min_value=0, value=100000, step=10000)
            
            btn_guardar_concepto = st.form_submit_button("➕ Registrar al Catálogo Base")

            if btn_guardar_concepto:
                if nuevo_concepto.strip() != "":
                    nueva_fila = pd.DataFrame([{
                        "Concepto": nuevo_concepto.strip(),
                        "Tipo": tipo_gasto,
                        "Monto Base (COP)": monto_base
                    }])
                    st.session_state["catalogo_conceptos"] = pd.concat(
                        [st.session_state["catalogo_conceptos"], nueva_fila],
                        ignore_index=True
                    )
                    st.success(f"¡Concepto '{nuevo_concepto}' agregado exitosamente!")
                    st.rerun()
                else:
                    st.error("Por favor ingresa un nombre válido para el concepto.")

        st.divider()
        st.subheader("📋 Catálogo Actual de Conceptos")
        
        df_cat_editado = st.data_editor(
            st.session_state["catalogo_conceptos"],
            num_rows="dynamic",
            column_config={
                "Monto Base (COP)": st.column_config.NumberColumn(format="$%d", min_value=0, step=1000),
                "Tipo": st.column_config.SelectboxColumn(options=["Fijo", "Variable"], required=True)
            },
            use_container_width=True,
            key="editor_catalogo_tabla_key"
        )
        st.session_state["catalogo_conceptos"] = df_cat_editado

    # ----------------------------------------------------
    # TAB 2: SELECCIONAR CONCEPTOS Y EDITARLOS LIBREMENTE
    # ----------------------------------------------------
    with tab_crear_mes:
        st.subheader("2. Seleccionar / Meter Conceptos para el Presupuesto del Mes")
        st.caption("Puedes seleccionar conceptos existentes, editar sus nombres o montos, o meter nuevos conceptos en la tabla:")

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            mes_destino = st.selectbox(
                "Mes a presupuestar:",
                ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
                index=7
            )
        with col_m2:
            anio_destino = st.number_input("Año:", min_value=2024, max_value=2030, value=2026)

        st.divider()

        df_cat = st.session_state["catalogo_conceptos"].copy()
        if "Incluir" not in df_cat.columns:
            df_cat.insert(0, "Incluir", True)

        df_seleccion = st.data_editor(
            df_cat,
            num_rows="dynamic",
            column_config={
                "Incluir": st.column_config.CheckboxColumn("¿Incluir este mes?", default=True),
                "Concepto": st.column_config.TextColumn("Nombre del Concepto", required=True),
                "Tipo": st.column_config.SelectboxColumn("Tipo", options=["Fijo", "Variable"], required=True),
                "Monto Base (COP)": st.column_config.NumberColumn("Monto Presupuestado (COP)", format="$%d", step=1000)
            },
            hide_index=True,
            use_container_width=True,
            key="editor_seleccion_mes_tabla_key"
        )

        st.write("")
        if st.button("🚀 Cargar Presupuesto para el Mes Seleccionado", use_container_width=True):
            df_db = st.session_state["presupuesto_db"]

            existe = not df_db[(df_db["Mes"] == mes_destino) & (df_db["Año"] == anio_destino)].empty

            if existe:
                st.warning(f"⚠️ Ya existe un presupuesto cargado para {mes_destino} {anio_destino}. Puedes gestionarlo en la pestaña 'Histórico'.")
            else:
                conceptos_seleccionados = df_seleccion[
                    (df_seleccion["Incluir"] == True) & 
                    (df_seleccion["Concepto"].dropna() != "")
                ]

                if not conceptos_seleccionados.empty:
                    id_inicial = (df_db["ID"].max() + 1) if not df_db.empty else 101
                    nuevos_registros = []

                    for _, row in conceptos_seleccionados.iterrows():
                        nuevos_registros.append({
                            "ID": int(id_inicial),
                            "Mes": mes_destino,
                            "Año": anio_destino,
                            "Concepto": str(row["Concepto"]).strip(),
                            "Tipo": row["Tipo"] if pd.notna(row["Tipo"]) else "Fijo",
