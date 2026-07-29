import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestor de Presupuesto Familiar", page_icon="💰", layout="wide")

# Archivos de datos
CONCEPTOS_FILE = "conceptos.csv"
PRESUPUESTO_FILE = "presupuesto.csv"
PAGOS_FILE = "pagos.csv"

# Funciones de carga de datos
def cargar_datos():
    if not os.path.exists(CONCEPTOS_FILE):
        pd.DataFrame(columns=["ID", "Concepto", "Tipo"]).to_csv(CONCEPTOS_FILE, index=False)
    if not os.path.exists(PRESUPUESTO_FILE):
        pd.DataFrame(columns=["Mes", "ID_Concepto", "Concepto", "Tipo", "Monto_Presupuestado"]).to_csv(PRESUPUESTO_FILE, index=False)
    if not os.path.exists(PAGOS_FILE):
        pd.DataFrame(columns=["ID_Pago", "Mes", "ID_Concepto", "Concepto", "Monto_Pagado", "Fecha_Pago", "Estado"]).to_csv(PAGOS_FILE, index=False)

cargar_datos()

# Interfaz Principal
st.title("💰 Gestor de Presupuesto Familiar ($ COP)")

opcion = st.sidebar.selectbox("Menú de Navegación", [
    "📊 Dashboard / Resumen",
    "📝 Gestión de Conceptos",
    "📅 Presupuesto Mensual",
    "💳 Registrar Pago (Orden de Pago)"
])

# 1. GESTIÓN DE CONCEPTOS
if opcion == "📝 Gestión de Conceptos":
    st.header("Gestión de Conceptos de Gastos")
    df_conceptos = pd.read_csv(CONCEPTOS_FILE)
    
    with st.form("form_concepto"):
        nuevo_concepto = st.text_input("Nombre del Concepto (ej. Arriendo, Luz, Mercado)")
        tipo_concepto = st.selectbox("Tipo de Gasto", ["Fijo", "Variable"])
        btn_guardar = st.form_submit_button("Guardar Concepto")
        
        if btn_guardar and nuevo_concepto:
            nuevo_id = len(df_conceptos) + 1
            nuevo_df = pd.DataFrame([{"ID": nuevo_id, "Concepto": nuevo_concepto, "Tipo": tipo_concepto}])
            df_conceptos = pd.concat([df_conceptos, nuevo_df], ignore_index=True)
            df_conceptos.to_csv(CONCEPTOS_FILE, index=False)
            st.success(f"Concepto '{nuevo_concepto}' registrado correctamente.")
            st.rerun()

    st.subheader("Conceptos Registrados")
    st.dataframe(df_conceptos, use_container_width=True)

# 2. PRESUPUESTO MENSUAL
elif opcion == "📅 Presupuesto Mensual":
    st.header("Asignación de Presupuesto Mensual")
    df_conceptos = pd.read_csv(CONCEPTOS_FILE)
    df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
    
    if df_conceptos.empty:
        st.warning("Primero debes registrar conceptos en el menú 'Gestión de Conceptos'.")
    else:
        mes_actual = st.text_input("Período (Año-Mes)", value=datetime.now().strftime("%Y-%m"))
        concepto_sel = st.selectbox("Seleccionar Concepto", df_conceptos["Concepto"].tolist())
        monto_presupuestado = st.number_input("Monto Presupuestado ($ COP)", min_value=0, step=50000)
        
        if st.button("Asignar a Presupuesto"):
            concepto_info = df_conceptos[df_conceptos["Concepto"] == concepto_sel].iloc[0]
            nuevo_reg = {
                "Mes": mes_actual,
                "ID_Concepto": concepto_info["ID"],
                "Concepto": concepto_sel,
                "Tipo": concepto_info["Tipo"],
                "Monto_Presupuestado": monto_presupuestado
            }
            df_presupuesto = pd.concat([df_presupuesto, pd.DataFrame([nuevo_reg])], ignore_index=True)
            df_presupuesto.to_csv(PRESUPUESTO_FILE, index=False)
            st.success(f"Presupuesto asignado a '{concepto_sel}' para el mes {mes_actual}.")
            st.rerun()
            
        st.subheader("Presupuesto Registrado")
        st.dataframe(df_presupuesto, use_container_width=True)

# 3. REGISTRAR PAGO
elif opcion == "💳 Registrar Pago (Orden de Pago)":
    st.header("Generación y Cierre de Orden de Pago")
    df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
    df_pagos = pd.read_csv(PAGOS_FILE)
    
    if df_presupuesto.empty:
        st.warning("No hay presupuestos registrados para generar órdenes de pago.")
    else:
        meses = df_presupuesto["Mes"].unique()
        mes_sel = st.selectbox("Filtrar por Mes", meses)
        df_mes = df_presupuesto[df_presupuesto["Mes"] == mes_sel]
        
        concepto_pago = st.selectbox("Obligación / Concepto a Pagar", df_mes["Concepto"].tolist())
        monto_pago = st.number_input("Monto a Pagar ($ COP)", min_value=0, step=10000)
        
        if st.button("Generar y Cerrar Orden de Pago"):
            concepto_info = df_mes[df_mes["Concepto"] == concepto_pago].iloc[0]
            id_pago = len(df_pagos) + 1
            nuevo_pago = {
                "ID_Pago": id_pago,
                "Mes": mes_sel,
                "ID_Concepto": concepto_info["ID_Concepto"],
                "Concepto": concepto_pago,
                "Monto_Pagado": monto_pago,
                "Fecha_Pago": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Estado": "Cerrado / Pagado"
            }
            df_pagos = pd.concat([df_pagos, pd.DataFrame([nuevo_pago])], ignore_index=True)
            df_pagos.to_csv(PAGOS_FILE, index=False)
            st.success(f"¡Orden de Pago #{id_pago} CERRADA con éxito para '{concepto_pago}'!")
            st.rerun()

# 4. DASHBOARD / RESUMEN
elif opcion == "📊 Dashboard / Resumen":
    st.header("Resumen General de Cumplimiento")
    df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
    df_pagos = pd.read_csv(PAGOS_FILE)
    
    if df_presupuesto.empty:
        st.info("Aún no tienes presupuestos o pagos registrados.")
    else:
        mes_sel = st.selectbox("Seleccionar Mes para Resumen", df_presupuesto["Mes"].unique())
        
        df_p_mes = df_presupuesto[df_presupuesto["Mes"] == mes_sel]
        df_pag_mes = df_pagos[df_pagos["Mes"] == mes_sel]
        
        total_presupuestado = df_p_mes["Monto_Presupuestado"].sum()
        total_pagado = df_pag_mes["Monto_Pagado"].sum()
        pendiente = total_presupuestado - total_pagado
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Presupuestado", f"${total_presupuestado:,.0f} COP")
        col2.metric("Total Pagado", f"${total_pagado:,.0f} COP")
        col3.metric("Pendiente por Pagar", f"${pendiente:,.0f} COP", delta_color="inverse")
        
        st.subheader("Detalle Presupuestado vs. Pagado")
        st.dataframe(df_p_mes, use_container_width=True)
