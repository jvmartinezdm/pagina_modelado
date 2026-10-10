import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página institucional
st.set_page_config(
    page_title="Sistema de Análisis de Siniestralidad Vial - ATUS",
    page_icon="📈",
    layout="wide"
)

# Estilo visual corporativo / institucional minimalista
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'figure.autolayout': True,
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 0.8
})

# Encabezado formal e institucional
st.markdown("### Coordinación General de Estadísticas de Tránsito")
st.title("Panel Analítico de Siniestralidad Vial (ATUS)")
st.markdown("---")

# Carga de datos optimizada y segura
@st.cache_data
def cargar_datos():
    try:
        return pd.read_csv('Dataset_limpio_7variables.csv')
    except Exception as e:
        st.error(f"Error en la carga del repositorio de datos: {e}")
        return None

df = cargar_datos()

if df is not None:
    # Panel lateral de control ejecutivo
    st.sidebar.markdown("### Parámetros de Filtrado")
    if 'NIVEL_RIESGO' in df.columns:
        niveles = ['Todos'] + list(df['NIVEL_RIESGO'].dropna().unique())
        riesgo_elegido = st.sidebar.selectbox("Clasificación de Riesgo", niveles)
        if riesgo_elegido != 'Todos':
            df_f = df[df['NIVEL_RIESGO'] == riesgo_elegido].copy()
        else:
            df_f = df.copy()
    else:
        df_f = df.copy()

    st.sidebar.markdown("---")
    st.sidebar.metric(label="Total de Registros Procesados", value=f"{len(df_f):,}")

    # ==========================================
    # BLOQUE DE VISUALIZACIÓN ANALÍTICA (5 KPIs)
    # ==========================================
    
    col1, col2 = st.columns(2)

    # 1. Evolución temporal (Línea)
    with col1:
        st.markdown("#### 1. Evolución Temporal de Siniestros")
        st.caption("Tendencia acumulada de eventos por demarcación municipal.")
        fig, ax = plt.subplots(figsize=(7, 4))
        
        if 'CVE_MUN' in df_f.columns:
            temp_data = df_f.groupby('CVE_MUN').size().reset_index(name='Conteo').head(25)
            ax.plot(temp_data['CVE_MUN'].astype(str), temp_data['Conteo'], color='#2b5c8f', marker='o', linewidth=1.8, markersize=4)
            ax.set_xlabel("Clave Municipal (CVE_MUN)", color='#333333')
        else:
            temp_data = pd.Series(df_f.index).rolling(window=100, min_periods=1).mean().head(200)
            ax.plot(temp_data.values, color='#2b5c8f', linewidth=1.5)
            ax.set_xlabel("Secuencia de Registros", color='#333333')
            
        ax.set_ylabel("Frecuencia de Accidentes", color='#333333')
        ax.tick_params(axis='x', rotation=45)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)

    # 2. Concentración por Entidad (Barras)
    with col2:
        st.markdown("#### 2. Concentración Geográfica (Hotspots)")
        st.caption("Identificación de entidades federativas con mayor volumen de siniestros.")
        fig, ax = plt.subplots(figsize=(7, 4))
        
        if 'CVE_ENT' in df_f.columns:
            hotspots = df_f['CVE_ENT'].value_counts().head(8).reset_index()
            hotspots.columns = ['CVE_ENT', 'Conteo']
            ax.bar(hotspots['CVE_ENT'].astype(str), hotspots['Conteo'], color='#d95f02', width=0.55)
            ax.set_xlabel("Entidad Federativa (CVE_ENT)", color='#333333')
        ax.set_ylabel("Volumen Acumulado", color='#333333')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)

    col3, col4 = st.columns(2)

    # 3. Distribución de Riesgo (Boxplot)
    with col3:
        st.markdown("#### 3. Distribución y Dispersión de Riesgo")
        st.caption("Análisis de valores atípicos (Outliers) por entidad.")
        fig, ax = plt.subplots(figsize=(7, 4))
        
        if 'CVE_ENT' in df_f.columns and 'CVE_MUN' in df_f.columns:
            box_data = df_f.groupby(['CVE_ENT', 'CVE_MUN']).size().reset_index(name='Frecuencia')
            top_ents = box_data['CVE_ENT'].value_counts().head(5).index
            sns.boxplot(data=box_data[box_data['CVE_ENT'].isin(top_ents)], x='CVE_ENT', y='Frecuencia', ax=ax, palette='Blues', width=0.4, fliersize=2.5)
            ax.set_xlabel("Entidad (CVE_ENT)", color='#333333')
            ax.set_ylabel("Frecuencia Municipal", color='#333333')
        else:
            ax.hist(df_f.index, bins=10, color='#2b5c8f')
            ax.set_xlabel("Distribución", color='#333333')
            
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)

    # 4. Patrón de severidad (Histograma)
    with col4:
        st.markdown("#### 4. Patrón de Severidad por tipología")
        st.caption("Distribución de frecuencia según la naturaleza del evento.")
        fig, ax = plt.subplots(figsize=(7, 4))
        
        if 'TIPACCID' in df_f.columns:
            tipos = df_f['TIPACCID'].value_counts().head(8)
            ax.barh(tipos.index.astype(str), tipos.values, color='#2e8b57', alpha=0.9)
            ax.set_xlabel("Frecuencia de Ocurrencia", color='#333333')
            ax.set_ylabel("Tipología del Accidente", color='#333333')
        else:
            ax.hist(df_f.index, bins=15, color='#2e8b57')
            
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)

    # 5. Relación de Riesgo (Mapa de Calor Analítico)
    st.markdown("#### 5. Matriz de Correlación: Incidencia Urbana vs. Suburbana")
    st.caption("Evaluación analítica del comportamiento cruzado de siniestros por demarcación territorial.")
    fig, ax = plt.subplots(figsize=(10, 4.5))
    
    if 'URBANA' in df_f.columns and 'SUBURBANA' in df_f.columns:
        crosstab_data = pd.crosstab(df_f['SUBURBANA'], df_f['URBANA'])
        sns.heatmap(crosstab_data, annot=True, fmt='d', cmap='OrRd', ax=ax, cbar=True, linewidths=0.5, annot_kws={"size": 9})
        ax.set_xlabel("Zona Urbana", color='#333333')
        ax.set_ylabel("Zona Suburbana", color='#333333')
        plt.xticks(rotation=25, ha='right')
        plt.yticks(rotation=0)
    
    st.pyplot(fig)

else:
    st.warning("No se localizó el archivo 'Dataset_limpio_7variables.csv' en el directorio de trabajo.")