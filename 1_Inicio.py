import streamlit as st

# Configuración de la subpágina
st.set_page_config(
    page_title="Inicio - Resumen del Proyecto",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Inicio: Propuesta del Proyecto")
st.write("Resumen ejecutivo del ecosistema de datos de tarificación.")

st.subheader("Puntos clave de la propuesta")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("### 🔌 Fuentes de Datos")
    st.write("Utiliza datos públicos del **INEGI** (parque vehicular, accidentes de tránsito y vehículos robados) combinados con la información interna de pólizas y siniestros de la compañía.")

with col_b:
    st.markdown("### 🤖 Modelos Predictivos")
    st.write("Propone sustituir las tarifas planas actuales por **modelos avanzados** que calculen de forma diferenciada la frecuencia (choques) y la severidad (costo promedio).")

with col_c:
    st.markdown("### 📈 Estrategia Comercial")
    st.write("Busca reducir el índice de siniestralidad combinado (**loss ratio**) y priorizar objetivamente los nuevos mercados para su expansión internacional.")

st.divider()

# 1. Objetivos del Ecosistema de Datos
st.header("1. Objetivos del Ecosistema de Datos")
st.write("El proyecto busca construir un sistema integral que guíe la toma de decisiones mediante las siguientes metas:")

st.markdown("""
- **Integración de fuentes masivas:** Consolidar las bases de datos del INEGI (accidentes, robos y parque vehicular) con el historial interno de pólizas de la empresa.
- **Modelado analítico avanzado:** Desarrollar un modelo de frecuencia (predecir el número de choques) y un modelo de severidad (estimar el costo de cada reclamo) segmentados por geografía.
- **Monitoreo inteligente:** Diseñar un tablero de control (KPIs) y proponer una arquitectura tecnológica en la nube que sea replicable en otros países de Latinoamérica.
""")

st.divider()

# 2. Plan de Análisis Visual (Renderizado con Markdown puro para evitar errores de NumPy)
st.header("2. Plan de Análisis Visual (Gráficas Propuestas)")
st.write("Para explorar la información antes de entrenar los modelos, el pipeline incluye un catálogo de análisis estadísticos:")

st.markdown("""

| N.° | Análisis / Gráfica | Variables Clave | Objetivo Estratégico |
| :--- | :--- | :--- | :--- |
| **1** | Evolución temporal (Línea) | Mes vs. Número de accidentes | Detectar tendencias a largo plazo y estacionalidad. |
| **2** | Concentración por Entidad (Barras) | Estado vs. Volumen de siniestros | Identificar los 'Hotspots' o zonas con mayor acumulación de choques. |
| **3** | Distribución de Riesgo (Boxplot) | Estado vs. Tasa de accidentes por 1,000 vehículos | Evaluar la dispersión del riesgo e identificar estados con comportamiento atípico (outliers). |
| **4** | Patrón de severidad (Histograma) | Distribución del monto de reclamación | Entender el comportamiento de los costos (golpes leves vs. pérdidas totales). |
| **5** | Relación de Riesgo (Dispersión) | Parque vehicular vs. Accidentes | Detectar estados con siniestralidad desproporcionada. |
""")

st.divider()

# 3. Matriz de Beneficios
st.header("3. Matriz de Beneficios Económicos y Operativos")
st.write("La migración de una tarifa plana tradicional a una basada en analítica predictiva generará los siguientes impactos directos:")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("📉 **Reducción del Loss Ratio**\n\nSe proyecta una disminución de 5 a 8 puntos porcentuales en el índice de siniestralidad combinado durante el primer año.")

with col2:
    st.success("🎯 **Tarificación Técnico Óptima**\n\nCapacidad de ofrecer primas más bajas en zonas de bajo riesgo, e incrementar el costo de manera justa en zonas de alta siniestralidad.")

with col3:
    st.warning("🛡️ **Mitigación de Riesgos**\n\nEl sistema incluye alertas de *data drift* (cambios post-despliegue) y validaciones cruzadas para evitar el sobreajuste.")
