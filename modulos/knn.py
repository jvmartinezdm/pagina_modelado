import streamlit as st
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder

# ============================================
# MÓDULO: IMPLEMENTACIÓN DEL ALGORITMO KNN
# Descripción: Predice el nivel de riesgo de un 
# accidente (Bajo, Medio, Alto) con base en datos históricos.
# ============================================

# CONFIGURACIÓN DE COLUMNAS (Ajusta los nombres según tu dataset_limpio.parquet)
COLUMNAS_X = [
    'entidad_federativa', 
    'zona',              # Urbana o Suburbana
    'tipo_accidente', 
    'edad', 
    'sexo', 
    'tipo_vehiculo'
]
COLUMNA_Y = 'nivel_riesgo'  # Variable objetivo (Bajo, Medio, Alto)


@st.cache_resource
def entrenar_modelo_knn():
    """
    Carga el archivo parquet, codifica las variables categóricas
    y entrena el modelo KNN guardando el estado en caché para máxima velocidad.
    """
    try:
        # Cargar base de datos limpia
        df = pd.read_parquet("dataset_limpio.parquet")
        
        # Validar que existan las columnas requeridas
        columnas_requeridas = COLUMNAS_X + [COLUMNA_Y]
        for col in columnas_requeridas:
            if col not in df.columns:
                st.error(f"⚠️ No se encontró la columna '{col}' en dataset_limpio.parquet")
                return None, None
        
        # Eliminar posibles filas con valores nulos en estas columnas de interés
        df_modelo = df[columnas_requeridas].dropna()
        
        # Crear diccionarios para almacenar los encoders de cada variable categórica
        encoders = {}
        columnas_categoricas = ['entidad_federativa', 'zona', 'tipo_accidente', 'sexo', 'tipo_vehiculo']
        
        df_codificado = df_modelo.copy()
        
        # Codificar variables de texto a números
        for col in columnas_categoricas:
            le = LabelEncoder()
            df_codificado[col] = le.fit_transform(df_modelo[col].astype(str))
            encoders[col] = le  # Guardamos el encoder para usarlo en la consulta del usuario
            
        # Separar características (X) y etiqueta objetivo (y)
        X = df_codificado[COLUMNAS_X]
        y = df_codificado[COLUMNA_Y].astype(str)
        
        # Inicializar y entrenar KNN (k=5 por defecto, puedes ajustarlo)
        modelo_knn = KNeighborsClassifier(n_neighbors=5, metric='minkowski', p=2)
        modelo_knn.fit(X, y)
        
        return modelo_knn, encoders

    except Exception as e:
        st.error(f"Error al procesar la base de datos Parquet: {e}")
        return None, None


def mostrar():
    st.title("🤖 Aprendizaje Automático: Algoritmo KNN")
    st.caption("Módulo de clasificación y predicción de niveles de riesgo por accidente")
    st.divider()

    # Cargar y entrenar el modelo desde el archivo Parquet
    modelo_knn, encoders = entrenar_modelo_knn()
    
    if modelo_knn is None or encoders is None:
        st.warning("Por favor verifica la estructura de tu archivo 'dataset_limpio.parquet' para continuar.")
        return

    # INTERFAZ DE USUARIO
    st.subheader("🔮 Consulta de Caso en Registros Históricos")
    st.write("Selecciona las características de un escenario para estimar su nivel de riesgo:")

    col1, col2 = st.columns(2)

    with col1:
        # Cargamos las opciones disponibles directamente de los datos reales usando los encoders
        entidad = st.selectbox("Entidad Federativa", encoders['entidad_federativa'].classes_)
        zona = st.selectbox("Zona geográfica", encoders['zona'].classes_)
        tipo_acc = st.selectbox("Tipo de accidente", encoders['tipo_accidente'].classes_)

    with col2:
        edad = st.slider("Edad del conductor", min_value=15, max_value=95, value=30)
        sexo = st.selectbox("Sexo del conductor", encoders['sexo'].classes_)
        vehiculo = st.selectbox("Tipo de vehículo", encoders['tipo_vehiculo'].classes_)

    st.divider()

    # Procesar la consulta cuando el usuario presione el botón
    if st.button("Consultar Nivel de Riesgo", type="primary"):
        try:
            # 1. Transformar las respuestas de texto del usuario a los números que entiende el KNN
            entrada_usuario = pd.DataFrame([{
                'entidad_federativa': encoders['entidad_federativa'].transform([entidad])[0],
                'zona': encoders['zona'].transform([zona])[0],
                'tipo_accidente': encoders['tipo_accidente'].transform([tipo_acc])[0],
                'edad': edad,
                'sexo': encoders['sexo'].transform([sexo])[0],
                'tipo_vehiculo': encoders['tipo_vehiculo'].transform([vehiculo])[0]
            }])
            
            # Asegurar el orden correcto de las columnas para el modelo
            entrada_usuario = entrada_usuario[COLUMNAS_X]

            # 2. Predecir con el modelo KNN
            prediccion = modelo_knn.predict(entrada_usuario)[0]
            
            # 3. Mostrar el resultado estilizado
            st.markdown("### 📊 Resultado del Análisis del Modelo")
            
            if "bajo" in prediccion.lower():
                st.success(f"🟢 **Nivel de Riesgo: {prediccion.upper()}**\n\nEste perfil coincide con incidentes históricos de baja gravedad o consecuencias menores.")
            elif "medio" in prediccion.lower():
                st.warning(f"🟡 **Nivel de Riesgo: {prediccion.upper()}**\n\nEl escenario se sitúa en un rango de alerta moderada en los registros analizados.")
            else:
                st.error(f"🔴 **Nivel de Riesgo: {prediccion.upper()}**\n\n¡Atención! Este perfil presenta altas coincidencias estadísticas con accidentes graves o siniestros de alta severidad.")
                
        except Exception as err:
            st.error(f"Ocurrió un error al realizar la predicción: {err}")
