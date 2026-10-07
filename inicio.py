import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Función para cargar datos simulados (Evitamos duplicar código de configuración)
@st.cache_data
def cargar_datos_simulados():
    estados = ['Nuevo León', 'CDMX', 'Jalisco', 'Estado de México', 'Puebla', 
               'Guanajuato', 'Veracruz', 'Chihuahua', 'Baja California', 'Sonora']
    np.random.seed(2026)
    data = {
        'Estado': estados,
        'Lat': [25.68, 19.43, 20.65, 19.35, 19.04, 21.01, 19.17, 28.63, 32.51, 29.08],
        'Lon': [-100.31, -99.13, -103.34, -99.63, -98.20, -101.25, -96.13, -106.06, -117.03, -110.95],
        'Parque_Vehicular': np.random.randint(1000000, 5000000, size=10),
        'Accidentes': np.random.randint(20000, 80000, size=10),
        'Costo_Promedio_Siniestro': np.random.randint(15000, 45000, size=10)
    }
    df = pd.DataFrame(data)
    df['Tasa_Accidentes_por_1000'] = (df['Accidentes'] / df['Parque_Vehicular']) * 1000
    return df

df_riesgo = cargar_datos_simulados()

# --- CONTENIDO DE LA PÁGINA INICIO ---
st.title("📊 Inicio: Planteamiento y Control del Proyecto")
st.caption("Consultora: **DataBridge Analytics** | Cliente: **La Aseguradora** | Septiembre 2026")

# Caja destacada con la Idea Central
st.info(
    "**Idea Central:** Desarrollar un sistema analítico basado en datos oficiales del INEGI "
    "que permita a La Aseguradora evaluar el riesgo de siniestralidad por zona geográfica, "
    "optimizar la tarificación mediante modelos predictivos de frecuencia y severidad, "
    "y fundamentar una estrategia de expansión basada en evidencia cuantitativa."
)

st.divider()

# Sección de los 5 KPIs Estratégicos
st.subheader("📈 KPIs Estratégicos Clave (Año en Curso)")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(label="📉 Loss Ratio (Siniestralidad)", value="62.4%", delta="-4.2%", help="Meta: < 65%")
with col2:
    st.metric(label="📊 Combined Ratio", value="93.1%", delta="-2.5%", help="Meta: < 95%")
with col3:
    st.metric(label="🎯 Penetración Zonas", value="5.8%", delta="+1.3%", help="Meta: > 5% Año 1")
with col4:
    st.metric(label="🔄 Retención de Cartera", value="82.5%", delta="+2.5%", help="Meta: > 80%")
with col5:
    st.metric(label="💰 ROI del Proyecto", value="164.0%", delta="+14.0%", help="Meta: > 150%")

st.divider()

# Gráfico interactivo de riesgo
st.subheader("🗺️ Monitoreo de Riesgo Geográfico (Datos INEGI)")

st.sidebar.header("Filtros de Página Inicio")
estado_seleccionado = st.sidebar.multiselect(
    "Selecciona Estados:",
    options=df_riesgo['Estado'].unique(),
    default=df_riesgo['Estado'].unique()
)

df_filtrado = df_riesgo[df_riesgo['Estado'].isin(estado_seleccionado)]
col_izq, col_der = st.columns([2, 1])

with col_izq:
    fig_mapa = px.scatter_mapbox(
        df_filtrado, lat="Lat", lon="Lon", size="Parque_Vehicular", color="Tasa_Accidentes_por_1000",
        color_continuous_scale=px.colors.sequential.Reds, hover_name="Estado", zoom=4, height=400
    )
    fig_mapa.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_mapa, use_container_width=True)

with col_der:
    st.dataframe(
        df_filtrado[['Estado', 'Tasa_Accidentes_por_1000']], 
        hide_index=True, use_container_width=True
    )
