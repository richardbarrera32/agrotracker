
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="AgroTracker", layout="wide")

st.title("📊 AgroTracker – Dashboard de Precios Agrícolas")

# ✅ Link CSV
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVABBaZE1vF9EYhIwsddfoq3lYfcmRHVu5rNH9ZeTM98eXVIdYGqF2zqZ-QxzGwA/pub?output=csv"

@st.cache_data
def cargar_datos():
    df = pd.read_csv(csv_url, parse_dates=["Fecha"])
    df = df.rename(columns={'Precio (COP/kg)': 'Precio por kilo'})
    return df

df = cargar_datos()

# 🎯 Filtros principales
productos = df['Producto'].dropna().unique()
ciudades = df['Ciudad'].dropna().unique()

producto_sel = st.selectbox("Selecciona un producto", sorted(productos))
ciudad_sel = st.selectbox("Selecciona una ciudad", sorted(ciudades))

# 🔘 Intervalos como botones horizontales
st.markdown("### Intervalo de tiempo")
intervalo_sel = st.radio(
    label="",
    options=["1w", "1m", "3m", "1y", "5y", "YTD", "Max"],
    horizontal=True,
    index=6  # Por defecto "Max"
)

# 📅 Calcular fecha mínima según hoy
hoy = pd.to_datetime(datetime.today().date())

if intervalo_sel == "1w":
    fecha_inicio = hoy - timedelta(weeks=1)
elif intervalo_sel == "1m":
    fecha_inicio = hoy - pd.DateOffset(months=1)
elif intervalo_sel == "3m":
    fecha_inicio = hoy - pd.DateOffset(months=3)
elif intervalo_sel == "1y":
    fecha_inicio = hoy - pd.DateOffset(years=1)
elif intervalo_sel == "5y":
    fecha_inicio = hoy - pd.DateOffset(years=5)
elif intervalo_sel == "YTD":
    fecha_inicio = pd.to_datetime(f"{hoy.year}-01-01")
else:  # Max
    fecha_inicio = df['Fecha'].min()

# 🔍 Filtrar
df_filtrado = df[
    (df['Producto'] == producto_sel) &
    (df['Ciudad'] == ciudad_sel) &
    (df['Fecha'] >= fecha_inicio) &
    (df['Fecha'] <= hoy)
]

# 📈 Gráfico
fig = px.line(df_filtrado, x='Fecha', y='Precio por kilo',
              title=f"Evolución del precio de {producto_sel} en {ciudad_sel} ({intervalo_sel})",
              labels={'Precio por kilo': 'Precio (COP/Kg)', 'Fecha': 'Fecha'},
              markers=True)

st.plotly_chart(fig, use_container_width=True)

# 📄 Tabla
with st.expander("Ver datos en tabla"):
    st.dataframe(df_filtrado)

