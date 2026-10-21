
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from utils.procesamiento import cargar_datos


# ==========================================================
# MÓDULO: CALIDAD DE DATOS
#
# Descripción:
# Evalúa la integridad, completitud, duplicidad
# y consistencia del dataset de accidentes ATUS.
#
# El módulo no modifica ni elimina registros.
# ==========================================================


# ==========================================================
# 1. CONFIGURACIÓN DE GRÁFICAS
# ==========================================================

def configurar_graficas():

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "figure.autolayout": True
    })


# ==========================================================
# 2. CALCULAR INDICADORES DE CALIDAD
# ==========================================================

@st.cache_data
def calcular_calidad(datos):

    total_registros = len(datos)

    total_celdas = (
        datos.shape[0] * datos.shape[1]
    )

    # Calcular valores nulos
    nulos_por_columna = datos.isna().sum()

    total_nulos = int(
        nulos_por_columna.sum()
    )

    # Calcular porcentaje de completitud
    completitud = 100.0

    if total_celdas > 0:

        completitud = (
            (total_celdas - total_nulos)
            / total_celdas
        ) * 100

    # Identificar filas exactamente iguales
    duplicados_exactos = int(
        datos.duplicated().sum()
    )

    # ==========================================
    # VALIDACIONES DE CONSISTENCIA
    # ==========================================

    reglas = {}

    if "CVE_ENT" in datos.columns:

        entidad = pd.to_numeric(
            datos["CVE_ENT"],
            errors="coerce"
        )

        invalidos = (
            entidad.notna()
            & (
                ~entidad.between(1, 32)
                | (entidad % 1 != 0)
            )
        )

        reglas["CVE_ENT fuera de rango"] = int(
            invalidos.sum()
        )

    if "CVE_MUN" in datos.columns:

        municipio = pd.to_numeric(
            datos["CVE_MUN"],
            errors="coerce"
        )

        invalidos = (
            municipio.notna()
            & (
                ~municipio.between(1, 999)
                | (municipio % 1 != 0)
            )
        )

        reglas["CVE_MUN fuera de rango"] = int(
            invalidos.sum()
        )

    if "CVEGEO" in datos.columns:

        geo = pd.to_numeric(
            datos["CVEGEO"],
            errors="coerce"
        )

        reglas["CVEGEO no positivo"] = int(
            (geo.notna() & (geo <= 0)).sum()
        )

    if "MOTOCICLET" in datos.columns:

        motos = pd.to_numeric(
            datos["MOTOCICLET"],
            errors="coerce"
        )

        invalidos = (
            motos.notna()
            & (
                (motos < 0)
                | (motos % 1 != 0)
            )
        )

        reglas["MOTOCICLET inválido"] = int(
            invalidos.sum()
        )

    if "NIVEL_RIESGO" in datos.columns:

        riesgos_validos = {
            "Bajo",
            "Medio",
            "Alto"
        }

        riesgos = (
            datos["NIVEL_RIESGO"]
            .astype("string")
            .str.strip()
            .str.title()
        )

        invalidos = (
            riesgos.notna()
            & ~riesgos.isin(riesgos_validos)
        )

        reglas["NIVEL_RIESGO no reconocido"] = int(
            invalidos.sum()
        )

    total_inconsistencias = sum(
        reglas.values()
    )

    return {
        "total_registros": total_registros,
        "total_nulos": total_nulos,
        "completitud": completitud,
        "duplicados_exactos": duplicados_exactos,
        "nulos_por_columna": nulos_por_columna,
        "reglas": reglas,
        "total_inconsistencias": total_inconsistencias
    }


# ==========================================================
# 3. RESUMEN GENERAL
# ==========================================================

def resumen_general(df, calidad):

    st.subheader("1. Resumen general de calidad")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Registros",
        f"{calidad['total_registros']:,}"
    )

    c2.metric(
        "Valores nulos",
        f"{calidad['total_nulos']:,}"
    )

    c3.metric(
        "Completitud",
        f"{calidad['completitud']:.2f}%"
    )

    c4.metric(
        "Filas repetidas",
        f"{calidad['duplicados_exactos']:,}"
    )

    st.info(
        "Una fila repetida no necesariamente "
        "representa un error. Distintos accidentes "
        "pueden compartir las mismas características. "
        "La eliminación de registros requiere "
        "verificar identificadores únicos."
    )


# ==========================================================
# 4. COMPLETITUD POR VARIABLE
# ==========================================================

def completitud_variables(df):

    st.subheader("2. Completitud por variable")

    st.caption(
        "Permite identificar variables "
        "con información faltante."
    )

    resumen = pd.DataFrame({
        "Variable": df.columns,
        "Tipo de dato": [
            str(df[col].dtype)
            for col in df.columns
        ],
        "Nulos": [
            int(df[col].isna().sum())
            for col in df.columns
        ],
        "Valores únicos": [
            int(df[col].nunique(dropna=True))
            for col in df.columns
        ]
    })

    resumen["Completitud (%)"] = (
        100 - (
            resumen["Nulos"]
            / max(len(df), 1)
            * 100
        )
    ).round(2)

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True
    )

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.bar(
        resumen["Variable"],
        resumen["Completitud (%)"],
        color="#2b5c8f"
    )

    ax.set_ylabel("Completitud (%)")
    ax.set_xlabel("Variable")
    ax.set_ylim(0, 105)
    ax.tick_params(axis="x", rotation=35)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)


# ==========================================================
# 5. VALIDACIÓN DE CONSISTENCIA
# ==========================================================

def validar_consistencia(calidad):

    st.subheader("3. Validación de consistencia")

    st.caption(
        "Verificación de reglas básicas de dominio."
    )

    tabla = pd.DataFrame([
        {
            "Regla": regla,
            "Registros que incumplen": cantidad
        }
        for regla, cantidad in calidad["reglas"].items()
    ])

    if tabla.empty:

        st.info(
            "No hay variables con reglas "
            "de consistencia configuradas."
        )

        return

    tabla["Estado"] = (
        tabla["Registros que incumplen"]
        .apply(
            lambda x: (
                "Correcto"
                if x == 0
                else "Revisar"
            )
        )
    )

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True
    )

    if calidad["total_inconsistencias"] == 0:

        st.success(
            "No se detectaron inconsistencias "
            "en las reglas evaluadas."
        )

    else:

        st.warning(
            f"Se detectaron "
            f"{calidad['total_inconsistencias']:,} "
            "incumplimientos de reglas."
        )


# ==========================================================
# 6. REVISIÓN DE VARIABLES CATEGÓRICAS
# ==========================================================

def revisar_categorias(df):

    st.subheader(
        "4. Revisión de variables categóricas"
    )

    columnas = [
        col
        for col in [
            "TIPACCID",
            "URBANA",
            "SUBURBANA",
            "NIVEL_RIESGO"
        ]
        if col in df.columns
    ]

    if not columnas:

        st.info(
            "No se encontraron variables "
            "categóricas configuradas."
        )

        return

    seleccion = st.selectbox(
        "Variable categórica a revisar",
        columnas,
        key="calidad_categoria"
    )

    conteo = (
        df[seleccion]
        .astype("string")
        .fillna("Valor nulo")
        .value_counts()
        .reset_index()
    )

    conteo.columns = [
        seleccion,
        "Frecuencia"
    ]

    st.dataframe(
        conteo,
        use_container_width=True,
        hide_index=True
    )

    mostrar_datos = conteo.head(15)

    fig, ax = plt.subplots(figsize=(10, 4.5))

    ax.barh(
        mostrar_datos[seleccion].astype(str),
        mostrar_datos["Frecuencia"],
        color="#2e8b57"
    )

    ax.set_xlabel("Número de registros")
    ax.set_ylabel(seleccion)
    ax.invert_yaxis()

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)


# ==========================================================
# 7. REVISIÓN DE MOTOCICLETAS
# ==========================================================

def revisar_motocicletas(df):

    if "MOTOCICLET" not in df.columns:
        return

    st.subheader(
        "5. Revisión de la variable MOTOCICLET"
    )

    st.caption(
        "Se comprueba que los valores sean "
        "numéricos, enteros y no negativos."
    )

    motos = pd.to_numeric(
        df["MOTOCICLET"],
        errors="coerce"
    )

    motos_validas = motos.dropna()

    if motos_validas.empty:

        st.warning(
            "No hay valores numéricos disponibles."
        )

        return

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Valor mínimo",
        f"{motos_validas.min():g}"
    )

    m2.metric(
        "Valor máximo",
        f"{motos_validas.max():g}"
    )

    m3.metric(
        "Promedio",
        f"{motos_validas.mean():.3f}"
    )

    distribucion = (
        motos_validas
        .value_counts()
        .sort_index()
    )

    if len(distribucion) > 30:

        distribucion = (
            motos_validas.value_counts()
            .head(30)
            .sort_index()
        )

        st.caption(
            "Se muestran los 30 valores "
            "más frecuentes."
        )

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.bar(
        distribucion.index.astype(str),
        distribucion.values,
        color="#2b5c8f"
    )

    ax.set_xlabel("Motocicletas involucradas")
    ax.set_ylabel("Frecuencia")

    ax.tick_params(axis="x", rotation=45)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    st.pyplot(fig)
    plt.close(fig)


# ==========================================================
# 8. CONCLUSIÓN AUTOMÁTICA
# ==========================================================

def conclusion_calidad(calidad):

    st.subheader("6. Conclusión de calidad")

    problemas = []

    if calidad["total_nulos"] > 0:

        problemas.append(
            f"{calidad['total_nulos']:,} valores nulos"
        )

    if calidad["total_inconsistencias"] > 0:

        problemas.append(
            f"{calidad['total_inconsistencias']:,} "
            "incumplimientos de reglas"
        )

    if not problemas:

        st.success(
            "No se detectaron valores nulos "
            "ni inconsistencias en las reglas "
            "básicas evaluadas. El resultado no "
            "garantiza la ausencia de otros "
            "problemas de calidad."
        )

    else:

        st.warning(
            "Se recomienda revisar: "
            + ", ".join(problemas)
            + "."
        )

    st.caption(
        "El análisis identifica posibles problemas "
        "de calidad, pero no modifica los datos."
    )


# ==========================================================
# 9. FUNCIÓN PRINCIPAL DEL MÓDULO
# ==========================================================

def mostrar():

    configurar_graficas()

    # Encabezado institucional
    st.markdown(
        "### Coordinación General de "
        "Estadísticas de Tránsito"
    )

    st.title(
        "Calidad de Datos - Siniestralidad Vial ATUS"
    )

    st.caption(
        "Evaluación de integridad, completitud, "
        "duplicidad y consistencia del conjunto "
        "de datos utilizado por los demás módulos."
    )

    st.divider()

    # ==========================================
    # CARGAR DATASET COMPARTIDO
    # ==========================================

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
            "en la carpeta datos."
        )

        return

    if df.empty:

        st.warning(
            "El dataset no contiene registros."
        )

        return

    # ==========================================
    # FILTROS
    # ==========================================

    st.subheader("Parámetros de filtrado")

    df_filtrado = df

    if "NIVEL_RIESGO" in df.columns:

        niveles = sorted(
            df["NIVEL_RIESGO"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        riesgo = st.selectbox(
            "Clasificación de Riesgo",
            ["Todos"] + niveles,
            key="calidad_riesgo"
        )

        if riesgo != "Todos":

            df_filtrado = df[
                df["NIVEL_RIESGO"].astype(str)
                == riesgo
            ].copy()

    else:

        st.info(
            "El dataset no contiene NIVEL_RIESGO. "
            "Se analizarán todos los registros."
        )

    st.metric(
        "Registros analizados",
        f"{len(df_filtrado):,}"
    )

    if df_filtrado.empty:

        st.warning(
            "No hay registros para "
            "el filtro seleccionado."
        )

        return

    st.divider()

    # ==========================================
    # EJECUTAR ANÁLISIS DE CALIDAD
    # ==========================================

    calidad = calcular_calidad(df_filtrado)

    resumen_general(df_filtrado, calidad)

    st.divider()

    completitud_variables(df_filtrado)

    st.divider()

    validar_consistencia(calidad)

    st.divider()

    revisar_categorias(df_filtrado)

    st.divider()

    revisar_motocicletas(df_filtrado)

    st.divider()

    conclusion_calidad(calidad)

    st.divider()

    st.caption(
        "Fuente: Dataset ATUS procesado. "
        "Este módulo realiza una evaluación "
        "descriptiva de la calidad de los datos."
    )
