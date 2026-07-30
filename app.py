import streamlit as st
import pandas as pd
import os

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Gestor de Presupuesto Automatizado",
    page_icon="💰",
    layout="wide"
)

# ARCHIVOS PERSISTENTES LOCALES
FILE_CATALOGO = "catalogo_data.csv"
FILE_PRESUPUESTO = "presupuesto_data.csv"

# ==========================================
# FUNCIONES PARA CARGAR Y GUARDAR DATOS
# ==========================================
def cargar_catalogo():
    if os.path.exists(FILE_CATALOGO):
        return pd.read_csv(FILE_CATALOGO)
    return pd.DataFrame(columns=["Concepto", "Tipo", "Monto Base (COP)"])

def guardar_catalogo(df):
    df.to_csv(FILE_CATALOGO, index=False)

def cargar_presupuesto():
    if os.path.exists(FILE_PRESUPUESTO):
        return pd.read_csv(FILE_PRESUPUESTO)
    return pd.DataFrame(columns=["ID", "Mes", "Año", "Concepto", "Tipo", "Monto Presupuestado", "Monto Pagado", "Estado"])

def guardar_presupuesto(df):
    df.to_csv(FILE_PRESUPUESTO, index=False)

# ==========================================
# INICIALIZACIÓN DEL ESTADO (SESSION STATE)
# ==========================================
if "catalogo_conceptos" not in st.session_state:
    st.session_state["catalogo_conceptos"] = cargar_catalogo()

if "presupuesto_db" not in st.session_state:
    st.session_state["presupuesto_db"] = cargar_presupuesto()

# ==========================================
# APLICACIÓN GENERAL
# ==========================================
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
            nuevo_concepto = st.text_input("Nombre del Concepto:")
        with col_c2:
            tipo_gasto = st.selectbox("Tipo de Gasto:", ["Fijo", "Variable"])
        with col_c3:
            monto_base = st.number_input("Valor Base Sugerido (COP):", min_value=0, value=0, step=10000)
        
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
                guardar_catalogo(st.session_state["catalogo_conceptos"])
                st.success(f"¡Concepto '{nuevo_concepto}' agregado e imprimido en archivo permanente!")
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
        key="key_editor_catalogo_base_v1"
    )
    
    # Guardar cambios si edita la tabla directamente
    if not df_cat_editado.equals(st.session_state["catalogo_conceptos"]):
        st.session_state["catalogo_conceptos"] = df_cat_editado
        guardar_catalogo(df_cat_editado)

# ----------------------------------------------------
# TAB 2: SELECCIONAR CONCEPTOS Y EDITARLOS LIBREMENTE
# ----------------------------------------------------
with tab_crear_mes:
    st.subheader("2. Seleccionar / Meter Conceptos para el Presupuesto del Mes")
    
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
        key="key_editor_crear_mes_v1"
    )

    st.write("")
    if st.button("🚀 Cargar Presupuesto para el Mes Seleccionado", use_container_width=True):
        df_db = st.session_state["presupuesto_db"]

        existe = not df_db[(df_db["Mes"] == mes_destino) & (df_db["Año"] == anio_destino)].empty

        if existe:
            st.warning(f"⚠️ Ya existe un presupuesto cargado para {mes_destino} {anio_destino}.")
        else:
            conceptos_seleccionados = df_seleccion[
                (df_seleccion["Incluir"] == True) & 
                (df_seleccion["Concepto"].dropna() != "")
            ]

            if not conceptos_seleccionados.empty:
                id_inicial = (df_db["ID"].max() + 1) if not df_db.empty and pd.notna(df_db["ID"].max()) else 101
                nuevos_registros = []

                for _, row in conceptos_seleccionados.iterrows():
                    nuevos_registros.append({
                        "ID": int(id_inicial),
                        "Mes": mes_destino,
                        "Año": anio_destino,
                        "Concepto": str(row["Concepto"]).strip(),
                        "Tipo": row["Tipo"] if pd.notna(row["Tipo"]) else "Fijo",
                        "Monto Presupuestado": row["Monto Base (COP)"] if pd.notna(row["Monto Base (COP)"]) else 0,
                        "Monto Pagado": 0,
                        "Estado": "Pendiente"
                    })
                    id_inicial += 1

                st.session_state["presupuesto_db"] = pd.concat(
                    [df_db, pd.DataFrame(nuevos_registros)],
                    ignore_index=True
                )
                guardar_presupuesto(st.session_state["presupuesto_db"])
                st.success(f"🎉 ¡Presupuesto para {mes_destino} {anio_destino} guardado permanentemente!")
                st.rerun()
            else:
                st.error("Debes seleccionar o ingresar al menos un concepto.")

# ----------------------------------------------------
# TAB 3: REGISTRAR PAGOS
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
                
                guardar_presupuesto(st.session_state["presupuesto_db"])
                st.success(f"¡Orden #{id_pago} actualizada y guardada!")
                st.rerun()
    else:
        st.info("No hay pagos pendientes registrados por el momento.")

# ----------------------------------------------------
# TAB 4: HISTORIAL Y EDICIÓN
# ----------------------------------------------------
with tab_historial:
    st.subheader("📊 Histórico Completo de Presupuestos Generados")
    st.caption("Los cambios realizados aquí se guardarán permanentemente al presionar Enter o cambiar de celda:")

    df_db_editado = st.data_editor(
        st.session_state["presupuesto_db"],
        num_rows="dynamic",
        column_config={
            "Monto Presupuestado": st.column_config.NumberColumn(format="$%d"),
            "Monto Pagado": st.column_config.NumberColumn(format="$%d"),
            "Estado": st.column_config.SelectboxColumn(options=["Pendiente", "Pagado"])
        },
        use_container_width=True,
        key="key_editor_historico_db_v1"
    )

    if not df_db_editado.equals(st.session_state["presupuesto_db"]):
        st.session_state["presupuesto_db"] = df_db_editado
        guardar_presupuesto(df_db_editado)
