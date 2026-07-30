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
        df = pd.read_csv(FILE_PRESUPUESTO)
        df["Monto Presupuestado"] = pd.to_numeric(df["Monto Presupuestado"], errors='coerce').fillna(0)
        df["Monto Pagado"] = pd.to_numeric(df["Monto Pagado"], errors='coerce').fillna(0)
        return df
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

# ==============================================================================
# BARRA LATERAL CORREDIZA (FILTROS Y RESUMEN RÁPIDO)
# ==============================================================================
with st.sidebar:
    st.header("📊 Resumen e Indicadores")
    st.caption("Métricas consolidadas de tu presupuesto.")

    df_db_sidebar = st.session_state["presupuesto_db"]

    if not df_db_sidebar.empty:
        anios_disponibles = sorted(df_db_sidebar["Año"].unique().tolist())
        anio_sel = st.selectbox("Filtrar por Año:", anios_disponibles, index=len(anios_disponibles)-1, key="sb_anio")
        
        meses_disponibles = ["Todos"] + df_db_sidebar[df_db_sidebar["Año"] == anio_sel]["Mes"].unique().tolist()
        mes_sel = st.selectbox("Filtrar por Mes:", meses_disponibles, key="sb_mes")

        df_filtrado = df_db_sidebar[df_db_sidebar["Año"] == anio_sel]
        if mes_sel != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_sel]

        total_presupuestado = df_filtrado["Monto Presupuestado"].sum()
        total_pagado = df_filtrado["Monto Pagado"].sum()
        total_por_pagar = df_filtrado[df_filtrado["Estado"] == "Pendiente"]["Monto Presupuestado"].sum()

        st.divider()

        st.metric("💰 Total Presupuestado", f"${total_presupuestado:,.0f} COP")
        st.metric("✅ Total Pagado", f"${total_pagado:,.0f} COP")
        st.metric("⏳ Total Por Pagar", f"${total_por_pagar:,.0f} COP")

        st.divider()

        st.subheader("📈 Gráfica del Período")
        datos_grafica = pd.DataFrame({
            "Estado": ["Pagado", "Por Pagar"],
            "Monto (COP)": [total_pagado, total_por_pagar]
        })
        
        st.bar_chart(datos_grafica.set_index("Estado"))
    else:
        st.info("Aún no hay presupuestos cargados para mostrar métricas.")

# ==========================================
# APLICACIÓN GENERAL Y PESTAÑAS
# ==========================================
st.title("⚙️ Presupuesto General - Panel de Control")

tab_inicio, tab_conceptos, tab_crear_mes, tab_liquidar, tab_historial = st.tabs([
    "🏠 Inicio / Dashboard",
    "➕ Catálogo de Conceptos",
    "📅 Generar Presupuesto Mensual",
    "✅ Cierre / Liquidación de Pagos",
    "📊 Histórico General"
])

# ----------------------------------------------------
# TAB 0: INICIO / DASHBOARD DE CONTROL
# ----------------------------------------------------
with tab_inicio:
    st.subheader("🏠 Resumen General y Gráficos de Control")
    st.caption("Visión global de la salud financiera y avance del presupuesto registrado.")

    df_dash = st.session_state["presupuesto_db"]

    if not df_dash.empty:
        # 1. Métricas Principales (KPIs)
        total_global_pres = df_dash["Monto Presupuestado"].sum()
        total_global_pag = df_dash["Monto Pagado"].sum()
        total_global_pend = df_dash[df_dash["Estado"] == "Pendiente"]["Monto Presupuestado"].sum()
        cumplimiento = (total_global_pag / total_global_pres * 100) if total_global_pres > 0 else 0

        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        col_kpi1.metric("💰 Presupuesto Total", f"${total_global_pres:,.0f} COP")
        col_kpi2.metric("✅ Total Pagado", f"${total_global_pag:,.0f} COP")
        col_kpi3.metric("⏳ Pendiente por Pagar", f"${total_global_pend:,.0f} COP")
        col_kpi4.metric("📈 Cumplimiento", f"{cumplimiento:.1f}%")

        st.divider()

        col_g1, col_g2 = st.columns(2)

        # 2. Gráfico Comparativo Presupuestado vs. Pagado por Mes
        with col_g1:
            st.markdown("### 📊 Presupuestado vs. Pag
