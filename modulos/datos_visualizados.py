# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 18:09:49 2026

@author: HP 840 G6
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from utils.procesamiento import cargar_datos


BASE = Path(__file__).resolve().parent.parent
RUTA_DICCIONARIO = (
    BASE / "datos" / "diccionario_variables.csv"
)


@st.cache_data
def obtener_diccionario(columnas):
    """
    Carga las descripciones oficiales de las variables.
    Si no existe el diccionario, genera una plantilla.
    """
    if RUTA_DICCIONARIO.exists():
        diccionario = pd.read_csv(RUTA_DICCIONARIO)

        requeridas = {"Variable", "Descripcion"}

        if requeridas.issubset(diccionario.columns):
            diccionario = diccionario[
                ["Variable", "Descripcion"]
            ].copy()

            diccionario["Variable"] = (
                diccionario["Variable"].astype(str)
            )

            diccionario = (
                diccionario.drop_duplicates("Variable")
                .set_index("Variable")
            )

            return {
                col: diccionario["Descripcion"].get(
                    col, "Pendiente de documentar"
                )
                for col in columnas
            }

    return {
        col: "Pendiente de documentar"
        for col in columnas
    }


def informacion_general(df):
    st.subheader("Información general")

    registros, variables = df.shape

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de registros", f"{registros:,}")
    col2.metric("Variables", variables)
    col3.metric(
        "Memoria utilizada",
        f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB"
    )

    st.divider()

    st.subheader("Fuente de información")

    st.write("""
    El conjunto de datos contiene registros
    relacionados con accidentes de tránsito.

    Para esta aplicación se utiliza un dataset
    procesado y seleccionado para su análisis.
    """)

    st.info(
        "Documentar aquí el nombre oficial de la "
        "fuente, institución, periodo de cobertura "
        "y transformaciones realizadas."
    )

    st.subheader("Estructura de los datos")

    estructura = pd.DataFrame({
        "Variable": df.columns,
        "Tipo de dato": df.dtypes.astype(str).values,
        "Registros no nulos": df.notna().sum().values
    })

    st.dataframe(
        estructura,
        use_container_width=True,
        hide_index=True
    )


def explorar_registros(df):
    st.subheader("Exploración de registros")

    columnas = df.columns.tolist()

    seleccionadas = st.multiselect(
        "Columnas que deseas visualizar",
        columnas,
        default=columnas
    )

    if not seleccionadas:
        st.warning("Selecciona al menos una columna.")
        return

    st.markdown("#### Aplicar filtros")

    variable = st.selectbox(
        "Variable para filtrar",
        ["Sin filtro"] + columnas
    )

    filtrado = df

    if variable != "Sin filtro":
        if pd.api.types.is_numeric_dtype(df[variable]):
            serie = df[variable].dropna()

            if not serie.empty:
                minimo = float(serie.min())
                maximo = float(serie.max())

                if minimo == maximo:
                    st.info(
                        f"Todos los valores no nulos "
                        f"de {variable} son {minimo:g}."
                    )
                    filtrado = df[
                        df[variable] == minimo
                    ]
                else:
                    rango = st.slider(
                        "Selecciona el rango",
                        min_value=minimo,
                        max_value=maximo,
                        value=(minimo, maximo)
                    )

                    filtrado = df[
                        df[variable].between(
                            rango[0], rango[1]
                        )
                    ]

        else:
            valores = (
                df[variable]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            valores = sorted(valores)

            if len(valores) > 500:
                st.warning(
                    "La variable tiene demasiados "
                    "valores únicos para mostrar "
                    "un filtro de selección."
                )
            else:
                elegidos = st.multiselect(
                    "Selecciona valores",
                    valores
                )

                if elegidos:
                    filtrado = df[
                        df[variable].astype(str).isin(
                            elegidos
                        )
                    ]

    st.metric(
        "Registros encontrados",
        f"{len(filtrado):,}"
    )

    limite = st.selectbox(
        "Registros para visualizar",
        [10, 50, 100, 500, 1000],
        index=2
    )

    st.dataframe(
        filtrado[seleccionadas].head(limite),
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "Se muestran los primeros registros "
        "del conjunto filtrado."
    )

    if len(filtrado) <= 100000:
        csv = filtrado[seleccionadas].to_csv(
            index=False
        ).encode("utf-8-sig")

        st.download_button(
            "Descargar registros filtrados",
            data=csv,
            file_name="datos_filtrados.csv",
            mime="text/csv"
        )
    else:
        st.info(
            "Para evitar generar descargas muy "
            "grandes en memoria, aplica filtros "
            "hasta obtener 100,000 registros "
            "o menos."
        )


def descripcion_variables(df):
    st.subheader("Descripción de variables")

    st.write(
        "A continuación se presentan las "
        "variables del conjunto de datos."
    )

    descripciones = obtener_diccionario(
        tuple(df.columns)
    )

    informacion = []

    for columna in df.columns:
        informacion.append({
            "Variable": columna,
            "Descripción": descripciones[columna],
            "Tipo de dato": str(df[columna].dtype),
            "Valores únicos": df[columna].nunique()
        })

    tabla = pd.DataFrame(informacion)

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("#### Inspeccionar variable")

    variable = st.selectbox(
        "Selecciona una variable",
        df.columns,
        key="inspeccion"
    )

    st.write("**Descripción:**", descripciones[variable])
    st.write("**Tipo de dato:**", df[variable].dtype)

    st.write("**Ejemplos de valores:**")

    ejemplos = (
        df[variable]
        .dropna()
        .drop_duplicates()
        .head(10)
    )

    st.dataframe(
        ejemplos.reset_index(drop=True),
        use_container_width=True
    )


def estadisticas_descriptivas(df):
    st.subheader("Estadísticas descriptivas")

    st.write(
        "Resumen estadístico de las variables "
        "del conjunto de datos."
    )

    numericas = df.select_dtypes(
        include="number"
    )

    if not numericas.empty:
        st.markdown("#### Variables numéricas")

        st.dataframe(
            numericas.describe().T,
            use_container_width=True
        )

    st.markdown("#### Distribución de frecuencias")

    variable = st.selectbox(
        "Selecciona una variable",
        df.columns,
        key="frecuencias"
    )

    frecuencias = (
        df[variable]
        .astype("string")
        .fillna("Sin dato")
        .value_counts()
        .head(15)
    )

    st.bar_chart(frecuencias)

    st.caption(
        "Se muestran las 15 categorías "
        "o valores más frecuentes."
    )


def mostrar():
    st.title("Datos visualizados")

    st.write("""
    Exploración y descripción del conjunto de datos
    utilizado en el sistema de análisis de
    siniestralidad vial.
    """)

    df = cargar_datos()

    if df is None:
        st.error(
            "No se encontró el dataset. "
            "Coloca dataset_limpio.parquet "
            "o dataset_limpio.csv en datos/."
        )
        return

    pestañas = st.tabs([
        "Información general",
        "Exploración de datos",
        "Descripción de variables",
        "Estadísticas"
    ])

    with pestañas[0]:
        informacion_general(df)

    with pestañas[1]:
        explorar_registros(df)

    with pestañas[2]:
        descripcion_variables(df)

    with pestañas[3]:
        estadisticas_descriptivas(df)
