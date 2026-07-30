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

# 1. PLANTILLA MAESTRA DE CONCEPTOS Y VALORES BASE
if "plantilla_conceptos" not in st.session_state:
    st.session_state["plantilla_conceptos"] = pd.DataFrame([
        {"Concepto": "Arriendo", "Tipo": "Fijo", "Monto Base (COP)": 1500000},
        {"Concepto": "Servicios Públicos", "Tipo": "Variable", "Monto Base (COP)": 350000},
        {"Concepto": "Mercado", "Tipo": "Variable", "Monto Base (COP)": 800000},
        {"Concepto": "Internet", "Tipo": "Fijo", "Monto Base (COP)": 120000},
        {"Concepto": "Administración", "Tipo": "Fijo", "Monto Base (COP)": 250000},
        {"Concepto": "Imprevistos / Varios", "Tipo": "Variable", "Monto Base (COP)": 200000},
    ])

# 2. BASE DE DATOS DE PRESUPUESTOS MENSUALES GENERADOS
if "presupuesto_db" not in st.session_state:
    st.session_state["presupuesto_db"] = pd.DataFrame([
        {"ID": 101, "Mes": "Julio", "Año": 2026, "Concepto": "Arriendo", "Tipo": "Fijo", "Monto Presupuestado": 1500000, "Monto Pagado": 1500000, "Estado": "Pagado"},
        {"ID": 102, "Mes": "Julio", "Año": 2026, "Concepto": "Servicios Públicos", "Tipo": "Variable", "Monto Presupuestado": 350000, "Monto Pagado": 320000, "Estado": "Pagado"},
        {"ID": 103, "Mes": "Julio", "Año": 2026, "Concepto": "Mercado", "Tipo": "Variable", "Monto Presupuestado": 800000, "Monto Pagado": 0, "Estado": "Pendiente"}
    ])

# ==========================================
# BARRA LATERAL: CONTROL DE ACCESO
# ==========================================
st.sidebar.title("🔐 Control de Acceso")
rol = st.sidebar.selectbox(
    "Selecciona tu perfil:",
    ["Usuario 2 (General / Consulta)", "Admin (Usuario 1)"]
)
st.sidebar.divider()

# ==========================================
# VISTA 1: USUARIO 2 (CONSULTA / DASHBOARD)
# ==========================================
if rol == "Usuario 2 (General / Consulta)":
    st.title("🏠 Presupuesto de Pagos Casa")
    st.info("Perfil: Consulta General — Vista de cumplimiento e histórico de pagos.")

    df = st.session_state["presupuesto_db"]

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        mes_sel = st.selectbox("Filtrar por Mes:", ["Todos"] + list(df["Mes"].unique()))
    with col_f2:
        anio_sel = st.selectbox("Filtrar por Año:", ["Todos"] + list(df["Año"].unique()))

    df_filtrado = df.copy()
    if mes_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_sel]
    if anio_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Año"] == anio_sel]

    st.subheader("📊 Dashboard de Cumplimiento")
    total_presupuestado = df_filtrado["Monto Presupuestado"].sum()
    total_pagado = df_filtrado["Monto Pagado"].sum()
    total_pendiente = total_presupuestado - total_pagado
    porcentaje = (total_pagado / total_presupuestado * 100) if total_presupuestado > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Presupuestado", f"${total_presupuestado:,.0f} COP")
    c2.metric("Total Pagado", f"${total_pagado:,.0f} COP")
    c3.metric("Pendiente por Pagar", f"${total_pendiente:,.0f} COP")
    c4.metric("% Cumplimiento", f"{porcentaje:.1f}%")

    st.divider()
    st.subheader("📋 Histórico de Pagos")
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
# VISTA 2: ADMIN (GESTIÓN RÁPIDA Y DINÁMICA)
# ==========================================
else:
    st.title("⚙️ Panel de Administración y Presupuesto")

    tab_plantilla, tab_liquidar, tab_historial = st.tabs([
        "📝 Plantilla Maestra y Carga Mensual",
        "✅ Cierre / Liquidación de Pagos",
        "📊 Histórico y Resumen General"
    ])

    # ----------------------------------------------------
    # TAB 1: PLANTILLA INTERACTIVA Y GENERACIÓN RÁPIDA
    # ----------------------------------------------------
    with tab_plantilla:
        st.subheader("1. Modifica la Plantilla de Gastos Fijos y Variables")
        st.caption("Puedes cambiar los valores directamente en las celdas, añadir nuevos conceptos o eliminar filas.")

        # Editor interactivo de tabla tipo Excel
        df_editado = st.data_editor(
            st.session_state["plantilla_conceptos"],
            num_rows="dynamic",
            column_config={
                "Monto Base (COP)": st.column_config.NumberColumn(
                    "Monto Base (COP)",
                    format="$%d",
                    min_value=0,
                    step=1000
                ),
                "Tipo": st.column_config.SelectboxColumn(
                    "Tipo de Gasto",
                    options=["Fijo", "Variable"],
                    required=True
                )
            },
            use_container_width=True,
            key="editor_plantilla"
        )

        # Actualizamos el estado con la tabla editada
        st.session_state["plantilla_conceptos"] = df_editado

        st.divider()

        st.subheader("2. Generar Presupuesto del Mes")
        st.write("Selecciona el período para cargar los ítems anteriores de forma automática:")

        col_m1, col_m2, col_m3 = st.columns([2, 2, 3])
        with col_m1:
            mes_destino = st.selectbox(
                "Mes a presupuestar:",
                ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
                index=7  # Agosto por defecto
            )
        with col_m2:
            anio_destino = st.number_input("Año:", min_value=2024, max_value=2030, value=2026)

        with col_m3:
            st.write("") # Espaciador
            st.write("") 
            if st.button("🚀 Cargar Presupuesto para este Mes", use_container_width=True):
                df_db = st.session_state["presupuesto_db"]

                # Verificar si ya existen registros para ese mes/año
                existe = not df_db[(df_db["Mes"] == mes_destino) & (df_db["Año"] == anio_destino)].empty
                
                if existe:
                    st.warning(f"⚠️ Ya existe un presupuesto cargado para {mes_destino} {anio_destino}. Puedes editarlo en la pestaña 'Histórico'.")
                else:
                    # Generar registros automáticamente a partir de la plantilla
                    id_inicial = (df_db["ID"].max() + 1) if not df_db.empty else 101
                    nuevos_registros = []

                    for idx, row in df_editado.iterrows():
                        nuevos_registros.append({
                            "ID": int(id_inicial),
                            "Mes": mes_destino,
                            "Año": anio_destino,
                            "Concepto": row["Concepto"],
                            "Tipo": row["Tipo"],
                            "Monto Presupuestado": row["Monto Base (COP)"],
                            "Monto Pagado": 0,
                            "Estado": "Pendiente"
                        })
                        id_inicial += 1

                    st.session_state["presupuesto_db"] = pd.concat(
                        [df_db, pd.DataFrame(nuevos_registros)],
                        ignore_index=True
                    )
                    st.success(f"🎉 ¡Presupuesto para {mes_destino} {anio_destino} generado exitosamente con {len(nuevos_registros)} conceptos!")
                    st.rerun()

    # ----------------------------------------------------
    # TAB 2: REGISTRAR PAGOS (CIERRE DE ÓRDENES)
    # ----------------------------------------------------
    with tab_liquidar:
        st.subheader("✅ Liquidar / Cerrar Pagos del Mes")
        
        df_pendientes = st.session_state["presupuesto_db"][st.session_state["presupuesto_db"]["Estado"] == "Pendiente"]

        if not df_pendientes.empty:
            col_l1, col_l2 = st.columns([2, 2])
            
            with col_l1:
                id_pago = st.selectbox(
                    "Selecciona el concepto a pagar:",
                    options=df_pendientes["ID"].tolist(),
                    format_func=lambda x: f"#{x} - {df_pendientes[df_pendientes['ID'] == x]['Concepto'].values[0]} ({df_pendientes[df_pendientes['ID'] == x]['Mes'].values[0]})"
                )
                
                info_item = df_pendientes[df_pendientes["ID"] == id_pago].iloc[0]
                st.info(f"**Monto Presupuestado:** ${info_item['Monto Presupuestado']:,.0f} COP")

            with col_l2:
                monto_real = st.number_input(
                    "Valor Real Pagado (COP):",
                    min_value=0,
                    value=int(info_item['Monto Presupuestado']),
                    step=1000
                )

                if st.button("Marcar Pago como Realizado"):
                    idx = st.session_state["presupuesto_db"].index[st.session_state["presupuesto_db"]["ID"] == id_pago].tolist()[0]
                    st.session_state["presupuesto_db"].at[idx, "Monto Pagado"] = monto_real
                    st.session_state["presupuesto_db"].at[idx, "Estado"] = "Pagado"
                    st.success(f"¡Orden #{id_pago} de '{info_item['Concepto']}' actualizada a PAGADO!")
                    st.rerun()
        else:
            st.success("🎉 ¡Excelente! No tienes pagos pendientes registrados.")

    # ----------------------------------------------------
    # TAB 3: EDICIÓN GENERAL Y ELIMINACIÓN DE REGISTROS
    # ----------------------------------------------------
    with tab_historial:
        st.subheader("📊 Histórico Completo de Presupuestos Generados")
        st.caption("Si cometiste un error o duplicaste un mes, puedes editar cualquier casilla o eliminar filas desde esta tabla:")

        # Editor completo de la base de datos acumulada
        df_db_editado = st.data_editor(
            st.session_state["presupuesto_db"],
            num_rows="dynamic",
            column_config={
                "Monto Presupuestado": st.column_config.NumberColumn(format="$%d"),
                "Monto Pagado": st.column_config.NumberColumn(format="$%d"),
                "Estado": st.column_config.SelectboxColumn(options=["Pendiente", "Pagado"])
            },
            use_container_width=True,
            key="editor_db_historico"
        )

        if st.button("💾 Guardar Cambios en Histórico"):
            st.session_state["presupuesto_db"] = df_db_editado
            st.success("¡Base de datos actualizada con éxito!")
            st.rerun()
