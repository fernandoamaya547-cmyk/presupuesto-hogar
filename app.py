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
# APLICACIÓN GENERAL (USUARIO ÚNICO)
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
        key="key_editor_catalogo_base_v1"
    )
    st.session_state["catalogo_conceptos"] = df_cat_editado

# ----------------------------------------------------
# TAB 2: SELECCIONAR CONCEPTOS Y EDITARLOS LIBREMENTE
# ----------------------------------------------------
with tab_crear_mes:
    st.subheader("2. Seleccionar / Meter Conceptos para el Presupuesto del Mes")
 File "/mount/src/presupuesto-hogar/app.py"

