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
# CONTROL DE ACCESOS Y AUTENTICACIÓN
# -------------------------------------------------------------
USUARIOS = {
    "admin": {"nombre": "Usuario 1 (Admin)", "password": "123", "rol": "Admin"},
    "usuario2": {"nombre": "Usuario 2 (Consulta Pagos)", "password": "456", "rol": "Restringido"}
}

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None

def login():
    st.title("🔐 Control de Acceso al Sistema Presupuestal")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Iniciar Sesión")
        with st.form("form_login"):
            input_user = st.text_input("Usuario")
            input_pass = st.text_input("Contraseña", type="password")
            btn_login = st.form_submit_button("Ingresar")
            
            if btn_login:
                if input_user in USUARIOS and USUARIOS[input_user]["password"] == input_pass:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario_actual"] = USUARIOS[input_user]
                    st.success(f"Bienvenido {USUARIOS[input_user]['nombre']}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

# Si no está autenticado, mostrar formulario de Login y detener ejecución
if not st.session_state["autenticado"]:
    login()
    st.stop()

# -------------------------------------------------------------
# BARRA LATERAL (USUARIO LOGUEADO Y NAVEGACIÓN)
# -------------------------------------------------------------
usuario_info = st.session_state["usuario_actual"]
st.sidebar.title(f"👤 {usuario_info['nombre']}")

if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = None
    st.rerun()

st.sidebar.markdown("---")

# Definición de ventanas y submódulos disponibles según el rol
if usuario_info["rol"] == "Admin":
    ventanas_disponibles = ["🏠 Presupuesto de Pagos Casa", "🏛️ Presupuesto General Casa"]
else:
    # Usuario 2 accede a la ventana de pagos en modo consulta restringida
    ventanas_disponibles = ["🏠 Presupuesto de Pagos Casa"]

st.sidebar.title("🏠 Navegación")
ventana_principal = st.sidebar.radio("Selecciona la Ventana:", ventanas_disponibles)
st.sidebar.markdown("---")

# =============================================================
# VENTANA 1: PRESUPUESTO DE PAGOS CASA
# =============================================================
if ventana_principal == "🏠 Presupuesto de Pagos Casa":
    st.title("🏠 Presupuesto de Pagos Casa")
    
    if usuario_info["rol"] == "Admin":
        st.caption("Gestión detallada de conceptos, presupuesto asignado, órdenes de pago y cumplimiento.")
        sub_menu_opciones = [
            "📊 Dashboard de Cumplimiento",
            "📝 Gestión de Conceptos",
            "📅 Presupuesto Mensual de Pagos",
            "💳 Registrar / Cerrar Orden de Pago"
        ]
    else:
        st.caption("Vista de consulta: Resumen de pagos, pendientados e histórico mensual.")
        sub_menu_opciones = [
            "📊 Dashboard de Cumplimiento",
            "📜 Histórico de Pagos Mensuales"
        ]
        
    sub_menu = st.sidebar.selectbox("Módulo de Pagos", sub_menu_opciones)
    
    # 1.1 DASHBOARD DE CUMPLIMIENTO
    if sub_menu == "📊 Dashboard de Cumplimiento":
        st.header("📊 Resumen de Cumplimiento de Pagos")
        df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
        df_pagos = pd.read_csv(PAGOS_FILE)
        
        if df_presupuesto.empty:
            st.info("Aún no tienes presupuestos de pagos registrados.")
        else:
            mes_sel = st.selectbox("Seleccionar Mes", df_presupuesto["Mes"].unique())
            
            df_p_mes = df_presupuesto[df_presupuesto["Mes"] == mes_sel].copy()
            df_pag_mes = df_pagos[df_pagos["Mes"] == mes_sel].copy()
            
            total_presupuestado = df_p_mes["Monto_Presupuestado"].sum()
            total_pagado = df_pag_mes["Monto_Pagado"].sum()
            pendiente = total_presupuestado - total_pagado
            
            # Métricas resumen
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Presupuestado (A Pagar)", f"${total_presupuestado:,.0f} COP")
            col2.metric("Total Pagado", f"${total_pagado:,.0f} COP")
            col3.metric("Pendiente por Pagar", f"${pendiente:,.0f} COP", delta_color="inverse")
            
            st.markdown("---")
            
            # Detalle de Items Pagados vs Pendientes
            col_a, col_b = st.columns(2)
            
            conceptos_pagados = df_pag_mes["Concepto"].tolist() if not df_pag_mes.empty else []
            
            with col_a:
                st.subheader("✅ Ítems Pagados")
                if not df_pag_mes.empty:
                    st.dataframe(df_pag_mes[["Concepto", "Monto_Pagado", "Fecha_Pago"]], use_container_width=True)
                else:
                    st.write("No hay pagos realizados aún en este mes.")
                    
            with col_b:
                st.subheader("⏳ Ítems Pendientes por Pagar")
                df_pendientes = df_p_mes[~df_p_mes["Concepto"].isin(conceptos_pagados)]
                if not df_pendientes.empty:
                    st.dataframe(df_pendientes[["Concepto", "Tipo", "Monto_Presupuestado"]], use_container_width=True)
                else:
                    st.success("🎉 ¡Todos los ítems del mes están pagados!")

    # 1.2 HISTÓRICO DE PAGOS MENSUALES (Para Usuario 2)
    elif sub_menu == "📜 Histórico de Pagos Mensuales":
        st.header("📜 Histórico de Pagos Mensuales")
        df_pagos = pd.read_csv(PAGOS_FILE)
        
        if df_pagos.empty:
            st.info("No hay registros de pagos en el histórico.")
        else:
            meses_pagos = df_pagos["Mes"].unique()
            mes_filtro = st.selectbox("Filtrar Histórico por Mes", ["Todos"] + list(meses_pagos))
            
            if mes_filtro != "Todos":
                df_mostrar = df_pagos[df_pagos["Mes"] == mes_filtro]
            else:
                df_mostrar = df_pagos
                
            st.dataframe(df_mostrar[["ID_Pago", "Mes", "Concepto", "Monto_Pagado", "Fecha_Pago", "Estado"]], use_container_width=True)

    # 1.3 GESTIÓN DE CONCEPTOS (Solo Admin)
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

    # 1.4 PRESUPUESTO MENSUAL DE PAGOS (Solo Admin)
    elif sub_menu == "📅 Presupuesto Mensual de Pagos":
        st.header("📅 Asignación de Presupuesto Mensual de Pagos")
        df_conceptos = pd.read_csv(CONCEPTOS_FILE)
        df_presupuesto = pd.read_csv(PRESUPUESTO_FILE)
        
        if df_conceptos.empty:
            st.warning("Primero debes registrar conceptos en el módulo 'Gestión de Conceptos'.")
        else:
            mes_actual = st.text_input("Período (Año-Mes)", value=datetime.now().strftime("%Y-%m"))
            concepto_sel = st.selectbox("Seleccionar Concepto", df_conceptos["Concepto"].tolist())
            monto_presupuestado = st.number_input("Monto Presupuestado ($ COP)", min_value=0, step
