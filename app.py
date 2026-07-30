import streamlit as st
import pandas as pd
import os

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Sistema Integral de Gestión Financiera",
    page_icon="💰",
    layout="wide"
)

USUARIO_CORRECTO = "admin"
CLAVE_CORRECTA = "1234"

# ARCHIVOS PERSISTENTES LOCALES
FILE_CATALOGO = "catalogo_data.csv"
FILE_PRESUPUESTO = "presupuesto_data.csv"
FILE_CASA_DEUDAS = "casa_deudas_data.csv"
FILE_CASA_GASTOS = "casa_gastos_data.csv"
FILE_ANUAL = "presupuesto_anual_data.csv"
FILE_NOMINA_JUANA = "nomina_juana_data.csv"

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
         "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# ==========================================
# FUNCIONES DE CARGA Y GUARDADO DE DATOS
# ==========================================
def cargar_catalogo():
    if os.path.exists(FILE_CATALOGO):
        return pd.read_csv(FILE_CATALOGO)
    return pd.DataFrame([
        {"Concepto": "Arriendo / Hipoteca", "Tipo": "Fijo", "Monto Base (COP)": 1500000},
        {"Concepto": "Servicios Públicos", "Tipo": "Variable", "Monto Base (COP)": 350000},
        {"Concepto": "Mercado General", "Tipo": "Variable", "Monto Base (COP)": 1200000}
    ])

def guardar_catalogo(df):
    df.to_csv(FILE_CATALOGO, index=False)

def cargar_presupuesto():
    if os.path.exists(FILE_PRESUPUESTO):
        df = pd.read_csv(FILE_PRESUPUESTO)
        df["Monto Presupuestado"] = pd.to_numeric(df["Monto Presupuestado"], errors='coerce').fillna(0)
        df["Monto Pagado"] = pd.to_numeric(df["Monto Pagado"], errors='coerce').fillna(0)
        return df
    return pd.DataFrame(columns=["ID", "Mes", "Año", "Concepto", "Tipo", "Monto Presupuestado", "Monto Pagado", "Estado"])

def guardar_presupuesto(df):
    df.to_csv(FILE_PRESUPUESTO, index=False)

def cargar_deudas_casa():
    if os.path.exists(FILE_CASA_DEUDAS):
        df = pd.read_csv(FILE_CASA_DEUDAS)
        for col in ["Deuda Total", "Cuota Mensual", "Saldo Pendiente"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    return pd.DataFrame([
        {"Entidad / Acreedor": "Banco A", "Concepto / Deuda": "Tarjeta Crédito", "Deuda Total": 3000000, "Cuota Mensual": 300000, "Saldo Pendiente": 1800000, "Estado": "Activa"}
    ])

def guardar_deudas_casa(df):
    df.to_csv(FILE_CASA_DEUDAS, index=False)

def cargar_gastos_casa():
    if os.path.exists(FILE_CASA_GASTOS):
        df = pd.read_csv(FILE_CASA_GASTOS)
        for col in ["Monto Valor Total", "Aporte Hijos/Terceros", "Monto Responsable Casa"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    return pd.DataFrame([
        {"Categoría": "Hijos", "Concepto": "Universidad", "Asignado a": "Laura", "Monto Valor Total": 800000, "Aporte Hijos/Terceros": 200000, "Monto Responsable Casa": 600000, "Estado Pago": "Pendiente"}
    ])

def guardar_gastos_casa(df):
    df.to_csv(FILE_CASA_GASTOS, index=False)

def cargar_presupuesto_anual():
    if os.path.exists(FILE_ANUAL):
        df = pd.read_csv(FILE_ANUAL)
        for col in MESES + ["Total Anual"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    
    conceptos_defecto = ["Arriendo / Hipoteca", "Servicios Públicos", "Mercado", "Nómina Juana", "Gastos Laura"]
    datos_iniciales = []
    for c in conceptos_defecto:
        row = {"Concepto": c, "Categoría": "Fijo" if c in ["Arriendo / Hipoteca", "Nómina Juana"] else "Variable"}
        for m in MESES:
            row[m] = 1300000 if c == "Nómina Juana" else 300000
        row["Total Anual"] = sum([row[m] for m in MESES])
        datos_iniciales.append(row)
    return pd.DataFrame(datos_iniciales)

def guardar_presupuesto_anual(df):
    df.to_csv(FILE_ANUAL, index=False)

def cargar_nomina_juana():
    if os.path.exists(FILE_NOMINA_JUANA):
        df = pd.read_csv(FILE_NOMINA_JUANA)
        for col in ["Monto Total Nómina", "Cuota Alex", "Pagado Alex", "Cuota Jorge", "Pagado Jorge"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        return df
    
    # Datos iniciales de ejemplo
    return pd.DataFrame([
        {
            "Mes": "Julio", "Año": 2026, "Concepto": "Sueldo y Prestaciones Juana", 
            "Monto Total Nómina": 1400000, "Cuota Alex": 700000, "Pagado Alex": 700000, "Estado Alex": "Pagado",
            "Cuota Jorge": 700000, "Pagado Jorge": 0, "Estado Jorge": "Pendiente"
        }
    ])

def guardar_nomina_juana(df):
    df.to_csv(FILE_NOMINA_JUANA, index=False)

# ==========================================
# INICIALIZACIÓN DE ESTADO
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if "catalogo_conceptos" not in st.session_state:
    st.session_state["catalogo_conceptos"] = cargar_catalogo()

if "presupuesto_db" not in st.session_state:
    st.session_state["presupuesto_db"] = cargar_presupuesto()

if "deudas_casa_db" not in st.session_state:
    st.session_state["deudas_casa_db"] = cargar_deudas_casa()

if "gastos_casa_db" not in st.session_state:
    st.session_state["gastos_casa_db"] = cargar_gastos_casa()

if "presupuesto_anual_db" not in st.session_state:
    st.session_state["presupuesto_anual_db"] = cargar_presupuesto_anual()

if "nomina_juana_db" not in st.session_state:
    st.session_state["nomina_juana_db"] = cargar_nomina_juana()

# ==========================================
# LOGIN
# ==========================================
def pantalla_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 Iniciar Sesión")
        with st.form("form_login"):
            usuario = st.text_input("Usuario")
            clave = st.text_input("Contraseña", type="password")
            if st.form_submit_button("🔑 Ingresar", use_container_width=True):
                if usuario == USUARIO_CORRECTO and clave == CLAVE_CORRECTA:
                    st.session_state["autenticado"] = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")

if not st.session_state["autenticado"]:
    pantalla_login()
    st.stop()

# ==========================================
# NAVEGACIÓN PRINCIPAL
# ==========================================
with st.sidebar:
    st.header("⚙️ Módulos de Control")
    modulo_activo = st.radio(
        "Navegación:",
        [
            "📅 Presupuesto Mensual de Pagos", 
            "🏠 Presupuesto General Casa",
            "👧 Control Gastos de Laura",
            "👵 Nómina Juana (Alex y Jorge)",
            "🗓️ Presupuesto Anual Consolidado"
        ],
        index=3
    )
    st.divider()
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

# ==============================================================================
# MÓDULO: CONTROL DE NÓMINA JUANA (ALEX Y JORGE)
# ==============================================================================
if modulo_activo == "👵 Nómina Juana (Alex y Jorge)":
    st.title("👵 Control de Pagos Nómina Juana")
    st.caption("Seguimiento mensual de sueldo/prestaciones de Juana y división de aportes entre Alex y Jorge.")

    df_nj = st.session_state["nomina_juana_db"]

    # RESUMEN DE MÉTRICAS
    total_nomina_mes = df_nj["Monto Total Nómina"].sum() if not df_nj.empty else 0
    total_pendiente_alex = df_nj[df_nj["Estado Alex"] == "Pendiente"]["Cuota Alex"].sum() if not df_nj.empty else 0
    total_pendiente_jorge = df_nj[df_nj["Estado Jorge"] == "Pendiente"]["Cuota Jorge"].sum() if not df_nj.empty else 0

    col_j1, col_j2, col_j3 = st.columns(3)
    col_j1.metric("💵 Total Nómina Registrada", f"${total_nomina_mes:,.0f} COP")
    col_j2.metric("⏳ Pendiente por Pagar ALEX", f"${total_pendiente_alex:,.0f} COP")
    col_j3.metric("⏳ Pendiente por Pagar JORGE", f"${total_pendiente_jorge:,.0f} COP")

    st.divider()
    st.subheader("📋 Matriz de Pagos Mensuales")

    # TABLA EDITABLE CON DETALLE ALEX Y JORGE
    df_nj_edited = st.data_editor(
        df_nj,
        column_config={
            "Monto Total Nómina": st.column_config.NumberColumn("Total Nómina (COP)", format="$%d"),
            "Cuota Alex": st.column_config.NumberColumn("Aporte Alex", format="$%d"),
            "Pagado Alex": st.column_config.NumberColumn("Pagado Alex", format="$%d"),
            "Estado Alex": st.column_config.SelectboxColumn("Estado Alex", options=["Pendiente", "Pagado"]),
            "Cuota Jorge": st.column_config.NumberColumn("Aporte Jorge", format="$%d"),
            "Pagado Jorge": st.column_config.NumberColumn("Pagado Jorge", format="$%d"),
            "Estado Jorge": st.column_config.SelectboxColumn("Estado Jorge", options=["Pendiente", "Pagado"]),
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_nomina_juana"
    )

    if not df_nj_edited.equals(st.session_state["nomina_juana_db"]):
        st.session_state["nomina_juana_db"] = df_nj_edited
        guardar_nomina_juana(df_nj_edited)
        st.rerun()

    st.divider()
    st.subheader("➕ Registrar Nuevo Período de Nómina")
    with st.form("form_nuevo_mes_juana", clear_on_submit=True):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            mes_j = st.selectbox("Mes:", MESES, index=6)
            anio_j = st.number_input("Año:", min_value=2024, max_value=2030, value=2026)
        with col_f2:
            monto_total_j = st.number_input("Monto Total Sueldo Juana (COP):", min_value=0, value=1400000, step=50000)
            concepto_j = st.text_input("Concepto:", value="Sueldo + Aux. Transporte")
        with col_f3:
            cuota_alex = st.number_input("Aporte Corresponde a Alex (COP):", min_value=0, value=int(monto_total_j/2), step=50000)
            cuota_jorge = st.number_input("Aporte Corresponde a Jorge (COP):", min_value=0, value=int(monto_total_j/2), step=50000)

        if st.form_submit_button("🚀 Programar Mes de Nómina"):
            nueva_fila_j = pd.DataFrame([{
                "Mes": mes_j,
                "Año": anio_j,
                "Concepto": concepto_j,
                "Monto Total Nómina": monto_total_j,
                "Cuota Alex": cuota_alex,
                "Pagado Alex": 0,
                "Estado Alex": "Pendiente",
                "Cuota Jorge": cuota_jorge,
                "Pagado Jorge": 0,
                "Estado Jorge": "Pendiente"
            }])
            st.session_state["nomina_juana_db"] = pd.concat([st.session_state["nomina_juana_db"], nueva_fila_j], ignore_index=True)
            guardar_nomina_juana(st.session_state["nomina_juana_db"])
            st.success("¡Mes de nómina agregado exitosamente!")
            st.rerun()

# ==============================================================================
# OTROS MÓDULOS (PRESUPUESTO MENSUAL, CASA, LAURA, ANUAL)
# ==============================================================================
elif modulo_activo == "📅 Presupuesto Mensual de Pagos":
    st.title("📅 Presupuesto Mensual de Pagos")
    st.dataframe(st.session_state["presupuesto_db"], use_container_width=True)

elif modulo_activo == "🏠 Presupuesto General Casa":
    st.title("🏠 Presupuesto General Casa")
    st.dataframe(st.session_state["gastos_casa_db"], use_container_width=True)

elif modulo_activo == "👧 Control Gastos de Laura":
    st.title("👧 Control Gastos de Laura")
    df_l = st.session_state["gastos_casa_db"]
    st.dataframe(df_l[df_l["Asignado a"].astype(str).str.lower() == "laura"], use_container_width=True)

else:
    st.title("🗓️ Presupuesto Anual Consolidado")
    st.dataframe(st.session_state["presupuesto_anual_db"], use_container_width=True)
