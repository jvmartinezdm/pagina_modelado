"""ATUS | Severidad estatal. Importable desde app.py mediante mostrar()."""
import io
import json
import zipfile
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE = Path(__file__).resolve().parent.parent
CARPETA_DATOS = BASE / "datos"

AMPLIADO = CARPETA_DATOS / "Dataset_severidad_ampliado.csv.gz"
LIMPIO = CARPETA_DATOS / "Dataset_limpio_7variables.zip"
MAPA = CARPETA_DATOS / "estados_mexico.geojson"
VEHICULOS = {
    'Automóviles': 'AUTOMOVIL', 'Motocicletas': 'MOTOCICLET',
    'Camionetas de carga': 'CAMIONETA', 'Camiones de carga': 'CAMION',
    'Camionetas de pasajeros': 'CAMPASAJ', 'Microbuses': 'MICROBUS',
    'Bicicletas': 'BICICLETA',
}
ESTADOS = ['Aguascalientes','Baja California','Baja California Sur','Campeche',
           'Coahuila','Colima','Chiapas','Chihuahua','Ciudad de México','Durango',
           'Guanajuato','Guerrero','Hidalgo','Jalisco','Estado de México','Michoacán',
           'Morelos','Nayarit','Nuevo León','Oaxaca','Puebla','Querétaro',
           'Quintana Roo','San Luis Potosí','Sinaloa','Sonora','Tabasco','Tamaulipas',
           'Tlaxcala','Veracruz','Yucatán','Zacatecas']

@st.cache_data(show_spinner='Leyendo registros ATUS…')
def leer_datos():
    if AMPLIADO.is_file():
        df = pd.read_csv(AMPLIADO, low_memory=False)
        origen = 'ampliado'
    elif LIMPIO.is_file():
        with zipfile.ZipFile(LIMPIO) as z:
            rutas = [x for x in z.namelist() if x.lower().endswith('.csv')]
            if not rutas:
                raise ValueError('El archivo ZIP no contiene ningún CSV.')
            with z.open(rutas[0]) as entrada:
                df = pd.read_csv(entrada, low_memory=False)
        origen = 'limpio'
    else:
        raise FileNotFoundError('Coloca Dataset_limpio_7variables.zip o Dataset_severidad_ampliado.csv.gz junto a severidad.py')
    df.columns = df.columns.str.strip().str.upper()
    exigidas = {'CVE_ENT', 'NIVEL_RIESGO'}
    if not exigidas.issubset(df.columns):
        raise ValueError(f'Faltan columnas: {sorted(exigidas - set(df.columns))}')
    df['CVE_ENT'] = pd.to_numeric(df['CVE_ENT'], errors='coerce')
    df = df[df['CVE_ENT'].between(1, 32)].copy()
    df['CLAVE'] = df['CVE_ENT'].astype(int).astype(str).str.zfill(2)
    df['NIVEL_RIESGO'] = df['NIVEL_RIESGO'].astype(str).str.strip().str.capitalize()
    df = df[df['NIVEL_RIESGO'].isin(['Bajo', 'Medio', 'Alto'])]
    if 'ANIO' in df:
        df['ANIO'] = pd.to_numeric(df['ANIO'], errors='coerce')
    return df, origen

@st.cache_data(show_spinner=False)
def leer_mapa():
    if not MAPA.is_file():
        return None
    geo = json.loads(MAPA.read_text(encoding='utf-8'))
    if geo.get('type') != 'FeatureCollection':
        raise ValueError('El archivo del mapa no tiene formato FeatureCollection.')
    claves = set()
    for f in geo['features']:
        p = f.setdefault('properties', {})
        clave = next((p[k] for k in ('cve_ent', 'CVE_ENT', 'cvegeo', 'CVEGEO', 'id', 'CODIGO') if k in p), None)
        if clave is None:
            raise ValueError('El mapa no contiene clave CVE_ENT en sus entidades.')
        clave = str(int(clave)).zfill(2)
        p['CLAVE'] = clave
        claves.add(clave)
    if claves != {str(i).zfill(2) for i in range(1,33)}:
        raise ValueError(f'El mapa debe tener 32 entidades distintas, tiene {len(claves)}.')
    return geo

def resumen_estatal(df):
    tabla = pd.crosstab(df['CLAVE'], df['NIVEL_RIESGO'])
    tabla = tabla.reindex(index=[f'{i:02d}' for i in range(1,33)], columns=['Bajo','Medio','Alto'], fill_value=0)
    tabla['Total'] = tabla[['Bajo','Medio','Alto']].sum(axis=1)
    tabla['Porcentaje alto'] = (tabla['Alto'] / tabla['Total'].replace(0, float('nan')) * 100).round(2)
    tabla['Estado'] = ESTADOS
    return tabla.reset_index().rename(columns={'CLAVE':'Clave'})

def mostrar():
    # Diseño adaptable: ocupa el ancho disponible sin alterar los otros módulos.
    st.markdown("""<style>
      .block-container {max-width: 1500px; padding-top: 2rem; padding-bottom: 3rem;
                        padding-left: 2.2rem; padding-right: 2.2rem;}
      [data-testid="stMetric"] {padding: 0.85rem 1rem; border: 1px solid rgba(150,150,150,.17);
                              border-radius: .65rem; min-height: 105px;}
      [data-testid="stMetricLabel"] p {font-size: .95rem;}
      [data-testid="stMetricValue"] {font-size: clamp(1.4rem, 2vw, 2.1rem);}
      h1, h2, h3 {overflow-wrap: anywhere;}
      @media (max-width: 750px) {.block-container {padding-left: 1rem; padding-right: 1rem;}}
    </style>""", unsafe_allow_html=True)
    st.title('Severidad de los accidentes de tránsito')
    st.caption('ATUS · México · Análisis de las 32 entidades federativas')
    try:
        df, origen = leer_datos()
    except Exception as e:
        st.error(f'No se pudo leer el dataset: {e}')
        return
    if origen == 'limpio':
        st.info('Datos disponibles: este archivo no incluye el año ni todas las categorías de vehículos. Para habilitar ambos filtros, genera el conjunto ampliado con preparar_datos.py.')

    st.subheader('Filtros de consulta')
    a, b, c = st.columns([1, 1.3, 1.35], gap='medium')
    with a:
        if 'ANIO' in df and df['ANIO'].notna().any():
            anios = sorted(df['ANIO'].dropna().astype(int).unique().tolist())
            anio = st.selectbox('Año del accidente', ['Todos los años'] + anios)
            if anio != 'Todos los años':
                df = df[df['ANIO'] == anio]
        else:
            st.selectbox('Año del accidente', ['No disponible'], disabled=True)
    with b:
        disponibles = {nombre:col for nombre,col in VEHICULOS.items() if col in df}
        veh = st.selectbox('Tipo de vehículo involucrado', ['Todos los vehículos'] + list(disponibles))
        if veh != 'Todos los vehículos':
            df = df[pd.to_numeric(df[disponibles[veh]], errors='coerce').fillna(0) > 0]
    with c:
        estado = st.selectbox('Entidad federativa', ['Toda la República'] + ESTADOS)
        if estado != 'Toda la República':
            df = df[df['CVE_ENT'] == ESTADOS.index(estado) + 1]

    st.caption('El filtro de vehículo considera accidentes en los que participó al menos una unidad del tipo seleccionado. Un accidente puede involucrar varios tipos de vehículos.')
    total = len(df)
    bajo = int((df['NIVEL_RIESGO'] == 'Bajo').sum())
    medio = int((df['NIVEL_RIESGO'] == 'Medio').sum())
    alto = int((df['NIVEL_RIESGO'] == 'Alto').sum())
    st.subheader('Indicadores de accidentes')
    c1, c2, c3, c4, c5 = st.columns(5, gap='small')
    c1.metric('Total de accidentes', f'{total:,}')
    c2.metric('Riesgo bajo', f'{bajo:,}')
    c3.metric('Riesgo medio', f'{medio:,}')
    c4.metric('Riesgo alto', f'{alto:,}')
    c5.metric('Porcentaje de riesgo alto', f'{alto/total*100:.2f} %' if total else '—')
    if not total:
        st.info('No hay registros para los filtros seleccionados.')
        return

    resumen = resumen_estatal(df)
    st.subheader('Mapa de severidad por entidad federativa')
    st.caption('La intensidad del color muestra el porcentaje de accidentes de riesgo alto respecto al total registrado en cada entidad. No representa la cantidad absoluta de accidentes.')
    try:
        geo = leer_mapa()
        if geo is None:
            st.warning('Falta estados_mexico.geojson. Ejecuta «python obtener_mapa.py» desde la carpeta del proyecto.')
        else:
            fig = px.choropleth(
                resumen, geojson=geo, locations='Clave', featureidkey='properties.CLAVE',
                color='Porcentaje alto', hover_name='Estado',
                hover_data={'Clave':True,'Total':True,'Bajo':True,'Medio':True,'Alto':True, 'Porcentaje alto':':.2f'},
                color_continuous_scale='YlOrRd', range_color=(0, max(5, float(resumen['Porcentaje alto'].max()))),
                labels={'Porcentaje alto':'Riesgo alto (%)'})
            # Mantener México completo en pantalla aunque se filtre una sola entidad.
            fig.update_geos(
                visible=False, showland=True, landcolor='#f6f7fb',
                projection_type='mercator',
                lonaxis_range=[-118.5, -86.5], lataxis_range=[14, 33.5],
                showcoastlines=False, showframe=False
            )
            fig.update_layout(
                height=580, margin=dict(l=0, r=10, t=5, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                geo=dict(bgcolor='rgba(0,0,0,0)'),
                coloraxis_colorbar=dict(title='Riesgo alto (%)', len=.75, thickness=16)
            )
            st.plotly_chart(fig, width='stretch')
    except Exception as e:
        st.error(f'Error al representar el mapa: {e}')

    st.subheader('Comparación de la severidad entre entidades')
    estados_con_datos = resumen[resumen['Total'] > 0].sort_values('Porcentaje alto', ascending=False)
    fig_barras = px.bar(estados_con_datos, x='Estado', y='Porcentaje alto', hover_data=['Total','Alto'],
                       labels={'Porcentaje alto':'Accidentes de riesgo alto (%)'})
    fig_barras.update_layout(height=340, margin=dict(l=5,r=5,t=15,b=0), xaxis_tickangle=-55)
    st.plotly_chart(fig_barras, width='stretch')
    with st.expander('Consultar y descargar los resultados por entidad', expanded=False):
        st.dataframe(resumen, hide_index=True, width='stretch')
        st.download_button('Descargar resultados en CSV', resumen.to_csv(index=False).encode('utf-8-sig'),
                           file_name='resumen_severidad.csv', mime='text/csv')
    st.caption('Fuente: INEGI, ATUS. NIVEL_RIESGO proviene de la clasificación procesada; confirmar que se usa la misma regla que en los demás módulos.')

if __name__ == '__main__':
    st.set_page_config(page_title='Severidad de accidentes | ATUS', layout='wide', page_icon='🗺️')
    mostrar()
