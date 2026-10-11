import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==========================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================================
st.set_page_config(
    page_title="Calidad de Datos - Siniestralidad Vial ATUS",
    page_icon="✅",
    layout="wide"
)

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.labelsize": 10,
    "figure.autolayout": True
})

st.markdown("### Coordinación General de Estadísticas de Tránsito")
st.title("Calidad de Datos - Sistema de Siniestralidad Vial (ATUS)")
st.caption(
    "Módulo para evaluar integridad, completitud, duplicidad y consistencia "
    "del mismo conjunto de datos utilizado por las páginas de análisis y visualización."
)
st.markdown("---")


# ==========================================================
# CARGA DE DATOS
# ==========================================================
@st.cache_data
def cargar_datos():
    try:
        return pd.read_csv("Dataset_limpio_7variables.csv")
    except FileNotFoundError:
        st.error(
            "No se encontró 'Dataset_limpio_7variables.csv'. "
            "Coloca el archivo CSV en la misma carpeta que esta página."
        )
        return None
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return None


df = cargar_datos()

if df is None:
    st.stop()


# ==========================================================
# FILTRO COMPARTIDO CON EL MÓDULO DE ANÁLISIS
# ==========================================================
st.sidebar.markdown("### Parámetros de Filtrado")

if "NIVEL_RIESGO" in df.columns:
    niveles_disponibles = sorted(df["NIVEL_RIESGO"].dropna().astype(str).unique().tolist())
    niveles = ["Todos"] + niveles_disponibles

    riesgo_elegido = st.sidebar.selectbox(
        "Clasificación de Riesgo",
        niveles
    )

    if riesgo_elegido != "Todos":
        df_f = df[df["NIVEL_RIESGO"].astype(str) == riesgo_elegido].copy()
    else:
        df_f = df
else:
    riesgo_elegido = "Todos"
    df_f = df

st.sidebar.markdown("---")
st.sidebar.metric("Registros analizados", f"{len(df_f):,}")
st.sidebar.caption(
    "Este filtro utiliza NIVEL_RIESGO igual que el módulo de gráficas, "
    "por lo que ambos apartados trabajan sobre la misma segmentación."
)


# ==========================================================
# FUNCIONES DE CALIDAD
# ==========================================================
@st.cache_data
def calcular_calidad(datos):
    total_registros = len(datos)
    total_celdas = datos.shape[0] * datos.shape[1]

    nulos_por_columna = datos.isna().sum()
    total_nulos = int(nulos_por_columna.sum())

    completitud = 100.0
    if total_celdas > 0:
        completitud = ((total_celdas - total_nulos) / total_celdas) * 100

    # Filas exactamente iguales considerando las columnas disponibles.
    duplicados_exactos = int(datos.duplicated().sum())

    # Reglas de consistencia básica.
    reglas = {}

    if "CVE_ENT" in datos.columns:
        reglas["CVE_ENT fuera del rango 1-32"] = int(
            (~datos["CVE_ENT"].between(1, 32)).sum()
        )

    if "CVE_MUN" in datos.columns:
        # Se usa un rango general para detectar valores claramente imposibles.
        reglas["CVE_MUN fuera del rango 1-999"] = int(
            (~datos["CVE_MUN"].between(1, 999)).sum()
        )

    if "CVEGEO" in datos.columns:
        reglas["CVEGEO no positivo"] = int(
            (datos["CVEGEO"] <= 0).sum()
        )

    if "MOTOCICLET" in datos.columns:
        moto_num = pd.to_numeric(datos["MOTOCICLET"], errors="coerce")
        invalidos_moto = (
            moto_num.isna()
            | (moto_num < 0)
            | ((moto_num % 1) != 0)
        )
        reglas["MOTOCICLET inválido"] = int(invalidos_moto.sum())

    if "NIVEL_RIESGO" in datos.columns:
        riesgos_validos = {"Bajo", "Medio", "Alto"}
        reglas["NIVEL_RIESGO no reconocido"] = int(
            (~datos["NIVEL_RIESGO"].isin(riesgos_validos)).sum()
        )

    total_inconsistencias = sum(reglas.values())

    return {
        "total_registros": total_registros,
        "total_nulos": total_nulos,
        "completitud": completitud,
        "duplicados_exactos": duplicados_exactos,
        "nulos_por_columna": nulos_por_columna,
        "reglas": reglas,
        "total_inconsistencias": total_inconsistencias
    }


calidad = calcular_calidad(df_f)


# ==========================================================
# 1. RESUMEN GENERAL
# ==========================================================
st.subheader("1. Resumen general de calidad")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Registros", f"{calidad['total_registros']:,}")
c2.metric("Valores nulos", f"{calidad['total_nulos']:,}")
c3.metric("Completitud", f"{calidad['completitud']:.2f}%")
c4.metric("Filas repetidas", f"{calidad['duplicados_exactos']:,}")

st.info(
    "Importante: una fila repetida no necesariamente representa un error. "
    "En este dataset reducido, distintos accidentes pueden compartir exactamente "
    "las mismas 8 características. No deben eliminarse registros solo por coincidir "
    "en estas columnas, a menos que exista un identificador único que confirme la duplicidad."
)


# ==========================================================
# 2. COMPLETITUD POR VARIABLE
# ==========================================================
st.subheader("2. Completitud por variable")
st.caption("Permite identificar columnas con datos faltantes.")

resumen_columnas = pd.DataFrame({
    "Variable": df_f.columns,
    "Tipo de dato": [str(df_f[col].dtype) for col in df_f.columns],
    "Nulos": [int(df_f[col].isna().sum()) for col in df_f.columns],
    "Valores únicos": [int(df_f[col].nunique(dropna=True)) for col in df_f.columns]
})

resumen_columnas["Completitud (%)"] = (
    100 - (resumen_columnas["Nulos"] / max(len(df_f), 1) * 100)
).round(2)

st.dataframe(
    resumen_columnas,
    use_container_width=True,
    hide_index=True
)

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(
    resumen_columnas["Variable"],
    resumen_columnas["Completitud (%)"]
)
ax.set_ylabel("Completitud (%)")
ax.set_xlabel("Variable")
ax.set_ylim(0, 105)
ax.tick_params(axis="x", rotation=35)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
st.pyplot(fig)


# ==========================================================
# 3. VALIDACIÓN DE CONSISTENCIA
# ==========================================================
st.subheader("3. Validación de consistencia")
st.caption(
    "Se revisan reglas básicas de dominio para las variables utilizadas "
    "posteriormente por los módulos de análisis, severidad y visualización."
)

tabla_reglas = pd.DataFrame(
    [
        {"Regla": regla, "Registros que incumplen": cantidad}
        for regla, cantidad in calidad["reglas"].items()
    ]
)

if not tabla_reglas.empty:
    tabla_reglas["Estado"] = tabla_reglas["Registros que incumplen"].apply(
        lambda x: "Correcto" if x == 0 else "Revisar"
    )

    st.dataframe(
        tabla_reglas,
        use_container_width=True,
        hide_index=True
    )

    if calidad["total_inconsistencias"] == 0:
        st.success("No se detectaron inconsistencias en las reglas básicas evaluadas.")
    else:
        st.warning(
            f"Se detectaron {calidad['total_inconsistencias']:,} incidencias "
            "en las reglas de consistencia."
        )


# ==========================================================
# 4. REVISIÓN DE CATEGORÍAS
# ==========================================================
st.subheader("4. Revisión de variables categóricas")

columnas_categoricas = [
    col for col in ["TIPACCID", "URBANA", "SUBURBANA", "NIVEL_RIESGO"]
    if col in df_f.columns
]

categoria_elegida = st.selectbox(
    "Variable categórica a revisar",
    columnas_categoricas
)

conteo_categorias = (
    df_f[categoria_elegida]
    .fillna("Valor nulo")
    .astype(str)
    .value_counts()
    .reset_index()
)
conteo_categorias.columns = [categoria_elegida, "Frecuencia"]

st.dataframe(
    conteo_categorias,
    use_container_width=True,
    hide_index=True
)

fig, ax = plt.subplots(figsize=(10, 4.5))
mostrar = conteo_categorias.head(15)

ax.barh(
    mostrar[categoria_elegida].astype(str),
    mostrar["Frecuencia"]
)
ax.set_xlabel("Número de registros")
ax.set_ylabel(categoria_elegida)
ax.invert_yaxis()
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
st.pyplot(fig)


# ==========================================================
# 5. REVISIÓN DE MOTOCICLETAS
# ==========================================================
if "MOTOCICLET" in df_f.columns:
    st.subheader("5. Revisión de la variable MOTOCICLET")
    st.caption(
        "Se comprueba que la variable tenga valores numéricos enteros y no negativos. "
        "Los valores altos no se eliminan automáticamente, ya que pueden representar "
        "accidentes donde participaron varias motocicletas."
    )

    motos = pd.to_numeric(df_f["MOTOCICLET"], errors="coerce")

    m1, m2, m3 = st.columns(3)
    m1.metric("Valor mínimo", f"{motos.min():g}")
    m2.metric("Valor máximo", f"{motos.max():g}")
    m3.metric("Promedio", f"{motos.mean():.3f}")

    distribucion_moto = motos.value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(
        distribucion_moto.index.astype(str),
        distribucion_moto.values
    )
    ax.set_xlabel("Motocicletas involucradas")
    ax.set_ylabel("Frecuencia")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    st.pyplot(fig)


# ==========================================================
# 6. CONCLUSIÓN AUTOMÁTICA
# ==========================================================
st.subheader("6. Conclusión de calidad")

problemas = []

if calidad["total_nulos"] > 0:
    problemas.append(
        f"{calidad['total_nulos']:,} valores nulos"
    )

if calidad["total_inconsistencias"] > 0:
    problemas.append(
        f"{calidad['total_inconsistencias']:,} inconsistencias de dominio"
    )

if not problemas:
    st.success(
        "El conjunto de datos presenta una estructura adecuada para continuar "
        "con los módulos de análisis, visualización y modelado. No se detectaron "
        "valores nulos ni inconsistencias en las reglas básicas revisadas."
    )
else:
    st.warning(
        "Antes del modelado conviene revisar: " + ", ".join(problemas) + "."
    )

st.markdown("---")
st.caption(
    "Este módulo no modifica ni elimina registros. Su función es diagnosticar "
    "la calidad del dataset antes de utilizarlo en las demás etapas del proyecto."
)
