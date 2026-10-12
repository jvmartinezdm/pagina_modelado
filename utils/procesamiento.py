
from pathlib import Path
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent.parent
CARPETA_DATOS = BASE / "datos"

@st.cache_data(show_spinner="Cargando dataset...")
def cargar_datos():
    parquet = CARPETA_DATOS / "dataset_limpio.parquet"
    csv = CARPETA_DATOS / "dataset_limpio.csv"

    if parquet.exists():
        return pd.read_parquet(parquet)

    if csv.exists():
        return pd.read_csv(csv, low_memory=False)

    return None
