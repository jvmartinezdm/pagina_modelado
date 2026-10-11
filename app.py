
import streamlit as st
from importlib import import_module

# Configuración general
st.set_page_config(
    page_title="Análisis de Siniestralidad Vial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rutas de cada sección del proyecto
SECCIONES = {
    "Inicio": "modulos.inicio",
    "Datos visualizados": "modulos.datos_visualizados",
    "Análisis": "modulos.analisis",
    "Severidad": "modulos.severidad",
    "Calidad de datos": "modulos.calidad_datos"
}

def ejecutar_seccion(ruta):
    try:
        modulo = import_module(ruta)
        modulo.mostrar()

    except (ImportError, AttributeError) as error:
        st.error(f"No se pudo cargar la sección: {error}")

    except Exception as error:
        st.error(f"Error al ejecutar la sección: {error}")


def main():
    st.sidebar.title("Siniestralidad Vial")
    st.sidebar.caption("Sistema de análisis de accidentes")
    st.sidebar.divider()

    seccion = st.sidebar.radio(
        "Menú principal",
        list(SECCIONES.keys())
    )

    st.sidebar.divider()
    st.sidebar.caption("Proyecto colaborativo - Streamlit")

    ejecutar_seccion(SECCIONES[seccion])


if __name__ == "__main__":
    main()
