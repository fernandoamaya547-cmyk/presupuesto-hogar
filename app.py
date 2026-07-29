import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gestor de Presupuesto Familiar", page_icon="🏠", layout="wide")

# Archivos de datos
CONCEPTOS_FILE = "conceptos.csv"
PRESUPUESTO_FILE = "presupuesto.csv"
PAGOS_FILE = "pagos.csv"
INGRESOS_FILE = "ingresos_generales.csv"

# Funciones de carga de datos
def cargar_datos():
    if not os.path.exists(CONCEPTOS_FILE):
        pd.DataFrame(columns=["ID", "Concepto", "Tipo"]).to_csv(CONCEPTOS_FILE, index=False)
    if not os.path.exists(PRESUPUESTO_FILE):
        pd.DataFrame(columns=["Mes", "ID_Concepto", "Concepto", "Tipo", "Monto_Presupuestado"]).to_csv(PRESUPUESTO_FILE, index=False)
    if not os.path.exists(PAGOS_FILE):
        pd.DataFrame(columns=["ID_Pago", "Mes", "ID_Concepto", "Concepto", "Monto_Pagado", "Fecha_Pago", "Estado"]).to_csv(PAGOS_FILE, index=False)
    if not os.path.exists(INGRESOS_FILE):
        pd.DataFrame(columns=["Mes", "Fuente", "Monto_Ingreso", "Destino_Asignado"]).to_csv(INGRESOS_FILE, index=False)

cargar_datos()

# -------------------------------------------------------------
# NAVEGACIÓN PRINCIPAL: SELECCIÓN DE VENTANA
# -------------------------------------------------------------
st.sidebar.title("🏠 Sistema Presupuestal")
ventana_principal = st.sidebar.radio(
    "Selecciona la Ventana:",
    ["🏠 Presupuesto de Pagos Casa", "🏛️ Presupuesto General Casa"]
)

st.sidebar.markdown("---")

# =============================================================
# VENTANA 1: PRESUPUESTO DE PAGOS CASA
# =============================================================
if ventana_principal == "🏠 Presupuesto de Pagos Casa":
    st.title("🏠 Presupuesto de Pagos Casa")
    st.caption("Gestión detallada de conceptos, presupuesto asignado, órdenes de pago y cumplimiento.")
    
    sub_menu = st.sidebar.selectbox("Módulo de Pagos", [
        "📊 Dashboard de Cumplimiento",
        "📝 Gestión de Conceptos",
        "📅 Presupuesto Mensual de Pagos",
        "💳 Registrar / Cerrar Orden de Pago"
    ])
    
    # 1.1 DASHBOARD DE CUMPLIMIENTO
    if sub_menu == "📊 Dashboard de Cumplimiento":
        st.header("📊 Resumen de Cumplimiento de Pagos")
        df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
        df_pagos = pd.read_csv(PAGOS_FILE)
        
        if df_presupuesto.empty:
            st.info("Aún no tienes presupuestos de pagos registrados.")
        else:
            mes_sel = st.selectbox("Seleccionar Mes", df_presupuesto["Mes"].unique())
            
            df_p_mes = df_presupuesto[df_presupuesto["Mes"] == mes_sel]
            df_pag_mes = df_pagos[df_pagos["Mes"] == mes_sel]
            
            total_presupuestado = df_p_mes["Monto_Presupuestado"].sum()
            total_pagado = df_pag_mes["Monto_Pagado"].sum()
            pendiente = total_presupuestado - total_pagado
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Presupuestado Pagos", f"${total_presupuestado:,.0f} COP")
            col2.metric("Total Pagado Real", f"${total_pagado:,.0f} COP")
            col3.metric("Pendiente por Pagar", f"${pendiente:,.0f} COP", delta_color="inverse")
            
            st.subheader("Detalle Presupuestado vs. Pagado")
            st.dataframe(df_p_mes, use_container_width=True)

    # 1.2 GESTIÓN DE CONCEPTOS
    elif sub_menu == "📝 Gestión de Conceptos":
        st.header("📝 Gestión de Conceptos de Gastos")
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

    # 1.3 PRESUPUESTO MENSUAL DE PAGOS
    elif sub_menu == "📅 Presupuesto Mensual de Pagos":
        st.header("📅 Asignación de Presupuesto Mensual de Pagos")
        df_conceptos = pd.read_csv(CONCEPTOS_FILE)
        df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
        
        if df_conceptos.empty:
            st.warning("Primero debes registrar conceptos en el módulo 'Gestión de Conceptos'.")
        else:
            mes_actual = st.text_input("Período (Año-Mes)", value=datetime.now().strftime("%Y-%m"))
            concepto_sel = st.selectbox("Seleccionar Concepto", df_conceptos["Concepto"].tolist())
            monto_presupuestado = st.number_input("Monto Presupuestado ($ COP)", min_value=0, step=50000)
            
            if st.button("Asignar a Presupuesto de Pagos"):
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
                
            st.subheader("Presupuestos Asignados")
            st.dataframe(df_presupuesto, use_container_width=True)

    # 1.4 REGISTRAR / CERRAR ORDEN DE PAGO
    elif sub_menu == "💳 Registrar / Cerrar Orden de Pago":
        st.header("💳 Generación y Cierre de Orden de Pago")
        df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
        df_pagos = pd.read_csv(PAGOS_FILE)
        
        if df_presupuesto.empty:
            st.warning("No hay presupuestos registrados para generar órdenes de pago.")
        else:
            meses = df_presupuesto["Mes"].unique()
            mes_sel = st.selectbox("Filtrar por Mes", meses)
            df_mes = df_presupuesto[df_presupuesto["Mes"] == mes_sel]
            
            concepto_pago = st.selectbox("Obligación / Concepto a Pagar", df_mes["Concepto"].tolist())
            monto_pago = st.number_input("Monto a Pagar Real ($ COP)", min_value=0, step=10000)
            
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

            st.subheader("Histórico de Órdenes Pagadas")
            st.dataframe(df_pagos, use_container_width=True)

# =============================================================
# VENTANA 2: PRESUPUESTO GENERAL CASA
# =============================================================
elif ventana_principal == "🏛️ Presupuesto General Casa":
    st.title("🏛️ Presupuesto General Casa")
    st.caption("Módulo Macro: Control de ingresos generales, distribución de fondos y balance global del hogar.")
    
    sub_menu_gen = st.sidebar.selectbox("Módulo General", [
        "📈 Dashboard Financiero Macro",
        "💵 Registro de Ingresos Generales"
    ])
    
    # 2.1 DASHBOARD FINANCIERO MACRO
    if sub_menu_gen == "📈 Dashboard Financiero Macro":
        st.header("📈 Balance General del Hogar")
        df_ingresos = pd.read_csv(INGRESOS_FILE)
        df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
        df_pagos = pd.read_csv(PAGOS_FILE)
        
        meses_disp = list(set(df_ingresos["Mes"].tolist() + df_presupuesto["Mes"].tolist()))
        
        if not meses_disp:
            st.info("Registra ingresos y presupuestos para ver el balance general.")
        else:
            mes_sel = st.selectbox("Seleccionar Período", meses_disp)
            
            ingresos_mes = df_ingresos[df_ingresos["Mes"] == mes_sel]["Monto_Ingreso"].sum()
            gastos_pres_mes = df_presupuesto[df_presupuesto["Mes"] == mes_sel]["Monto_Presupuestado"].sum()
            gastos_reales_mes = df_pagos[df_pagos["Mes"] == mes_sel]["Monto_Pagado"].sum()
            
            saldo_proyectado = ingresos_mes - gastos_pres_mes
            saldo_real = ingresos_mes - gastos_reales_mes
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Ingresos Totales", f"${ingresos_mes:,.0f} COP")
            c2.metric("Presupuesto Gastos Casa", f"${gastos_pres_mes:,.0f} COP")
            c3.metric("Pagos Realizados", f"${gastos_reales_mes:,.0f} COP")
            c4.metric("Saldo Disponible Real", f"${saldo_real:,.0f} COP")
            
            st.markdown("---")
            st.subheader("💡 Resumen Ejecutivo")
            st.write(f"- **Saldo Proyectado:** ${saldo_proyectado:,.0f} COP (Ingresos vs. Presupuestado)")
            st.write(f"- **Saldo Disponible Actual:** ${saldo_real:,.0f} COP (Ingresos vs. Pagos Efectuados)")

    # 2.2 REGISTRO DE INGRESOS GENERALES
    elif sub_menu_gen == "💵 Registro de Ingresos Generales":
        st.header("💵 Registro de Ingresos Generales")
        df_ingresos = pd.read_csv(INGRESOS_FILE)
        
        with st.form("form_ingreso"):
            mes_ingreso = st.text_input("Período (Año-Mes)", value=datetime.now().strftime("%Y-%m"))
            fuente_ingreso = st.text_input("Fuente de Ingreso (ej. Salario, Negocio, Arriendo cobrado)")
            monto_ingreso = st.number_input("Monto ($ COP)", min_value=0, step=100000)
            destino = st.selectbox("Destino Principal", ["Fondo Pagos Casa", "Ahorro / Inversión", "Libre Disposición"])
            
            btn_ingreso = st.form_submit_button("Registrar Ingreso")
            
            if btn_ingreso and fuente_ingreso:
                nuevo_reg = {
                    "Mes": mes_ingreso,
                    "Fuente": fuente_ingreso,
                    "Monto_Ingreso": monto_ingreso,
                    "Destino_Asignado": destino
                }
                df_ingresos = pd.concat([df_ingresos, pd.DataFrame([nuevo_reg])], ignore_index=True)
                df_ingresos.to_csv(INGRESOS_FILE, index=False)
                st.success(f"Ingreso de '{fuente_ingreso}' guardado exitosamente.")
                st.rerun()

        st.subheader("Histórico de Ingresos")
        st.dataframe(df_ingresos, use_container_width=True)
