import streamlit as st
import modulo_presupuesto
# Importamos otros módulos conforme los vayamos creando
# import modulo_nomina

st.set_page_config(
    page_title="Plataforma de Gestión Integral",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------------------------------------
# MENÚ LATERAL IZQUIERDO (Segmentos de la aplicación)
# ---------------------------------------------------------
st.sidebar.title("📌 Menú Principal")
st.sidebar.markdown("Selecciona el módulo en el que deseas trabajar:")

opcion_segmento = st.sidebar.radio(
    "Módulos / Segmentos:",
    [
        "📊 Presupuesto Hogar",
        "👥 Nómina y Colaboradores",
        "⚙️ Configuración / General"
    ]
)

st.sidebar.divider()
st.sidebar.info("💡 Consejo: Puedes cambiar de segmento en cualquier momento sin perder la sesión actual.")

# ---------------------------------------------------------
# ENRUTAMIENTO DE LOS SEGMENTOS
# ---------------------------------------------------------
if opcion_segmento == "📊 Presupuesto Hogar":
    modulo_presupuesto.render_presupuesto_hogar()

elif opcion_segmento == "👥 Nómina y Colaboradores":
    st.title("👥 Nómina y Colaboradores")
    st.write("Aquí irá el segmento dedicado a la gestión de nómina (ej. Nómina de Juana).")
    # modulo_nomina.render_nomina()

elif opcion_segmento == "⚙️ Configuración / General":
    st.title("⚙️ Panel de Configuración General")
    st.write("Ajustes generales de la plataforma, monedas, usuarios o backups.")
2. Archivo del Segmento: modulo_presupuesto.py
Movemos toda la lógica existente del Presupuesto de Hogar a una función principal llamada render_presupuesto_hogar() dentro de este archivo.

Python
import streamlit as st
import pandas as pd

def render_presupuesto_hogar():
    st.title("📊 Presupuesto del Hogar")
    st.subheader("Control mensual de gastos fijos y variables")

    # Inicializar estado en session_state si no existe
    if "presupuesto_db" not in st.session_state:
        st.session_state["presupuesto_db"] = pd.DataFrame(columns=[
            "ID", "Concepto", "Tipo", "Monto Presupuestado", "Monto Pagado", "Estado"
        ])

    # Métricas clave en la parte superior
    col1, col2, col3 = st.columns(3)
    
    df = st.session_state["presupuesto_db"]
    presupuestado_total = df["Monto Presupuestado"].sum() if not df.empty else 0
    pagado_total = df["Monto Pagado"].sum() if not df.empty else 0
    pendiente_total = presupuestado_total - pagado_total

    col1.metric("Total Presupuestado", f"${presupuestado_total:,.0f} COP")
    col2.metric("Total Pagado", f"${pagado_total:,.0f} COP")
    col3.metric("Pendiente por Pagar", f"${pendiente_total:,.0f} COP")

    st.markdown("---")

    # Editor interactivo del presupuesto
    st.subheader("📋 Registro e Histórico de Pagos")
    df_editado = st.data_editor(
        st.session_state["presupuesto_db"],
        num_rows="dynamic",
        column_config={
            "Monto Presupuestado": st.column_config.NumberColumn(format="$ %d"),
            "Monto Pagado": st.column_config.NumberColumn(format="$ %d"),
            "Estado": st.column_config.SelectboxColumn(options=["Pendiente", "Pagado"])
        },
        use_container_width=True,
        key="editor_presupuesto_hogar"
    )

    if not df_editado.equals(st.session_state["presupuesto_db"]):
        st.session_state["presupuesto_db"] = df_editado
        st.success("¡Cambios guardados con éxito!")
