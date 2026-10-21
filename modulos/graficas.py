
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils.procesamiento import cargar_datos


# ============================================
# MÓDULO: ANÁLISIS DE SINIESTRALIDAD VIAL
#
# Descripción:
# Presenta cinco gráficas para analizar los
# accidentes de tránsito registrados en ATUS.
# Utiliza filtros y estadísticas por categoría.
# ============================================



# ============================================
# 1. CONFIGURACIÓN DE GRÁFICAS
# ============================================

def configurar_graficas():

    # Configuración manual del estilo de gráficas
    # sin depender de estilos predeterminados.

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "figure.autolayout": True,
        "axes.edgecolor": "#cccccc",
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.alpha": 0.3
    })


# ============================================
# 2. EVOLUCIÓN TEMPORAL DE ACCIDENTES
# ============================================

def grafica_temporal(df):

    st.markdown("#### 1. Evolución de Accidentes")

    if "ANIO" in df.columns:

        st.caption(
            "Número de registros de accidentes por año."
        )

        datos = (
            df.groupby("ANIO")
            .size()
            .sort_index()
        )

        fig, ax = plt.subplots(figsize=(7, 4))

        ax.plot(
            datos.index.astype(str),
            datos.values,
            color="#2b5c8f",
            marker="o",
            linewidth=1.8,
            markersize=4
        )

        ax.set_xlabel("Año")
        ax.set_ylabel("Frecuencia de Accidentes")
        ax.tick_params(axis="x", rotation=45)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        st.pyplot(fig)
        plt.close(fig)

    elif "CVE_MUN" in df.columns:

        st.caption(
            "Frecuencia de accidentes por clave municipal. "
            "No representa una evolución temporal."
        )

        datos = (
            df.groupby("CVE_MUN")
            .size()
            .sort_values(ascending=False)
            .head(15)
        )

        fig, ax = plt.subplots(figsize=(7, 4))

        ax.bar(
            datos.index.astype(str),
            datos.values,
            color="#2b5c8f"
        )

        ax.set_xlabel("Clave Municipal")
        ax.set_ylabel("Frecuencia de Accidentes")
        ax.tick_params(axis="x", rotation=45)

        st.pyplot(fig)
        plt.close(fig)

    else:
        st.warning(
            "No se encontró una variable de año "
            "o municipio para generar esta gráfica."
        )


# ============================================
# 3. CONCENTRACIÓN POR ENTIDAD
# ============================================

def grafica_entidades(df):

    st.markdown(
        "#### 2. Concentración Geográfica (Hotspots)"
    )

    st.caption(
        "Entidades federativas con mayor "
        "volumen de accidentes."
    )

    if "CVE_ENT" not in df.columns:
        st.warning("No existe la variable CVE_ENT.")
        return

    datos = (
        df["CVE_ENT"]
        .value_counts()
        .head(8)
    )

    fig, ax = plt.subplots(figsize=(7, 4))

    ax.bar(
        datos.index.astype(str),
        datos.values,
        color="#d95f02",
        width=0.55
    )

    ax.set_xlabel("Clave de Entidad Federativa")
    ax.set_ylabel("Volumen de Accidentes")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)


# ============================================
# 4. DISTRIBUCIÓN DE RIESGO
# ============================================

def grafica_riesgo(df):

    st.markdown(
        "#### 3. Distribución y Dispersión de Accidentes"
    )

    st.caption(
        "Distribución de frecuencias municipales "
        "para identificar posibles valores atípicos."
    )

    columnas = ["CVE_ENT", "CVE_MUN"]

    if not all(col in df.columns for col in columnas):
        st.warning(
            "Se requieren CVE_ENT y CVE_MUN."
        )
        return

    datos = (
        df.groupby(["CVE_ENT", "CVE_MUN"])
        .size()
        .reset_index(name="Frecuencia")
    )

    principales = (
        df["CVE_ENT"]
        .value_counts()
        .head(5)
        .index
    )

    datos = datos[
        datos["CVE_ENT"].isin(principales)
    ]

    if datos.empty:
        st.info("No hay datos para generar el gráfico.")
        return

    fig, ax = plt.subplots(figsize=(7, 4))

    sns.boxplot(
        data=datos,
        x="CVE_ENT",
        y="Frecuencia",
        color="#5186b5",
        width=0.5,
        fliersize=2.5,
        ax=ax
    )

    ax.set_xlabel("Entidad Federativa")
    ax.set_ylabel("Accidentes por Municipio")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)


# ============================================
# 5. TIPOLOGÍA DE ACCIDENTES
# ============================================

def grafica_tipologia(df):

    st.markdown(
        "#### 4. Distribución por Tipo de Accidente"
    )

    st.caption(
        "Frecuencia de accidentes según "
        "su clasificación."
    )

    if "TIPACCID" not in df.columns:
        st.warning("No existe la variable TIPACCID.")
        return

    datos = (
        df["TIPACCID"]
        .value_counts()
        .head(8)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(7, 4))

    ax.barh(
        datos.index.astype(str),
        datos.values,
        color="#2e8b57",
        alpha=0.9
    )

    ax.set_xlabel("Frecuencia")
    ax.set_ylabel("Tipo de Accidente")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)


# ============================================
# 6. MATRIZ URBANA Y SUBURBANA
# ============================================

def grafica_zonas(df):

    st.markdown(
        "#### 5. Matriz de Frecuencias por Zona"
    )

    st.caption(
        "Distribución conjunta de los registros "
        "clasificados como urbanos y suburbanos."
    )

    columnas = ["URBANA", "SUBURBANA"]

    if not all(col in df.columns for col in columnas):
        st.warning(
            "Se requieren URBANA y SUBURBANA."
        )
        return

    tabla = pd.crosstab(
        df["SUBURBANA"],
        df["URBANA"]
    )

    if tabla.empty:
        st.info("No hay registros para comparar.")
        return

    fig, ax = plt.subplots(figsize=(10, 4.5))

    sns.heatmap(
        tabla,
        annot=True,
        fmt="d",
        cmap="OrRd",
        linewidths=0.5,
        annot_kws={"size": 9},
        ax=ax
    )

    ax.set_xlabel("Zona Urbana")
    ax.set_ylabel("Zona Suburbana")

    ax.tick_params(axis="x", rotation=25)
    ax.tick_params(axis="y", rotation=0)

    st.pyplot(fig)
    plt.close(fig)


# ============================================
# 7. FUNCIÓN PRINCIPAL DEL MÓDULO
# ============================================

def mostrar():

    configurar_graficas()

    # Encabezado institucional
    st.markdown(
        "### Coordinación General de "
        "Estadísticas de Tránsito"
    )

    st.title(
        "Panel Analítico de Siniestralidad Vial (ATUS)"
    )

    st.divider()

    # Cargar dataset compartido
    try:
        df = cargar_datos()

    except Exception as error:
        st.error(
            f"Error al cargar el dataset: {error}"
        )
        return

    if df is None:
        st.warning(
            "No se encontró el dataset limpio "
            "en la carpeta de datos."
        )
        return

    # ============================================
    # FILTROS GENERALES
    # ============================================

    st.subheader("Parámetros de Filtrado")

    col_f1, col_f2 = st.columns(2)

    df_filtrado = df

    with col_f1:

        if "NIVEL_RIESGO" in df.columns:

            niveles = (
                df["NIVEL_RIESGO"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            niveles = ["Todos"] + sorted(niveles)

            riesgo = st.selectbox(
                "Clasificación de Riesgo",
                niveles
            )

            if riesgo != "Todos":
                df_filtrado = df_filtrado[
                    df_filtrado["NIVEL_RIESGO"]
                    .astype(str) == riesgo
                ]

        else:
            st.info(
                "No se encontró NIVEL_RIESGO."
            )

    with col_f2:

        if "CVE_ENT" in df.columns:

            entidades = sorted(
                df["CVE_ENT"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            entidad = st.selectbox(
                "Entidad Federativa",
                ["Todas"] + entidades
            )

            if entidad != "Todas":
                df_filtrado = df_filtrado[
                    df_filtrado["CVE_ENT"]
                    .astype(str) == entidad
                ]

    st.divider()

    # ============================================
    # INDICADORES GENERALES
    # ============================================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Registros Totales",
        f"{len(df):,}"
    )

    col2.metric(
        "Registros Filtrados",
        f"{len(df_filtrado):,}"
    )

    if "CVE_ENT" in df_filtrado.columns:
        entidades_total = (
            df_filtrado["CVE_ENT"].nunique()
        )
    else:
        entidades_total = 0

    col3.metric(
        "Entidades Analizadas",
        entidades_total
    )

    if df_filtrado.empty:
        st.warning(
            "No existen registros con los filtros "
            "seleccionados."
        )
        return

    st.divider()

    # ============================================
    # VISUALIZACIONES
    # ============================================

    st.header("Indicadores de Siniestralidad")

    col_a, col_b = st.columns(2)

    with col_a:
        grafica_temporal(df_filtrado)

    with col_b:
        grafica_entidades(df_filtrado)

    col_c, col_d = st.columns(2)

    with col_c:
        grafica_riesgo(df_filtrado)

    with col_d:
        grafica_tipologia(df_filtrado)

    st.divider()

    grafica_zonas(df_filtrado)

    st.divider()

    st.caption(
        "Fuente de información: Dataset ATUS "
        "procesado para el análisis de "
        "siniestralidad vial."
    )
