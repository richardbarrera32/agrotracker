import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import scipy.stats as stats

# Configuración
st.set_page_config(page_title="AgroTracker", layout="wide")
st.title("📊 AgroTracker – Dashboard de Precios Agrícolas")

# Cargar desde Google Sheets
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTVABBaZE1vF9EYhIwsddfoq3lYfcmRHVu5rNH9ZeTM98eXVIdYGqF2zqZ-QxzGwA/pub?output=csv"

@st.cache_data
def cargar_datos():
    df = pd.read_csv(csv_url, parse_dates=["Fecha"])
    df = df.rename(columns={"Precio (COP/kg)": "Precio por kilo"})
    df["Precio por kilo"] = pd.to_numeric(df["Precio por kilo"], errors="coerce")
    df["Producto"] = df["Producto"].str.strip()
    df["Ciudad"] = df["Ciudad"].str.strip()
    return df

df = cargar_datos()

# Filtros
productos = df["Producto"].dropna().unique()
ciudades = df["Ciudad"].dropna().unique()

producto_sel = st.selectbox("🥑 Selecciona un producto", sorted(productos))
ciudad_sel = st.selectbox("🏙️ Selecciona una ciudad", sorted(ciudades))

df_filtrado = df[(df["Producto"] == producto_sel) & (df["Ciudad"] == ciudad_sel)].copy()
df_filtrado = df_filtrado.sort_values("Fecha")

# Intervalos de tiempo
opciones_rango = {
    "1 semana": 7,
    "1 mes": 30,
    "3 meses": 90,
    "YTD": (pd.Timestamp.today() - pd.Timestamp(pd.Timestamp.today().year, 1, 1)).days,
    "1 año": 365,
    "5 años": 1825,
    "Máximo": None
}
rango_sel = st.selectbox("📆 Selecciona rango de tiempo", list(opciones_rango.keys()))

if opciones_rango[rango_sel]:
    fecha_min = df_filtrado["Fecha"].max() - pd.Timedelta(days=opciones_rango[rango_sel])
    df_filtrado = df_filtrado[df_filtrado["Fecha"] >= fecha_min]

# 🛡️ Último precio confiable desde YTD
dias_para_precio = opciones_rango.get("YTD", 30)
df_base_precio = df[(df["Producto"] == producto_sel) & (df["Ciudad"] == ciudad_sel)].copy()
df_base_precio = df_base_precio.sort_values("Fecha")

if dias_para_precio:
    fecha_limite_precio = df_base_precio["Fecha"].max() - pd.Timedelta(days=dias_para_precio)
    df_base_precio = df_base_precio[df_base_precio["Fecha"] >= fecha_limite_precio]

if not df_base_precio.empty:
    ultimo = df_base_precio.iloc[-1]
    precio_actual = ultimo["Precio por kilo"]
    fecha_valida = ultimo["Fecha"]

    if pd.notna(fecha_valida):
        fecha_formateada = fecha_valida.strftime("%d/%m/%Y")
    else:
        fecha_formateada = "Fecha no disponible"

    st.markdown(
        f"<h4 style='color:black;'>🕒 Último precio: <b>${precio_actual:,.0f}</b> COP/kg "
        f"({fecha_formateada})</h4>",
        unsafe_allow_html=True
    )

# 📈 Evolución de precios
fig = px.line(
    df_filtrado,
    x="Fecha",
    y="Precio por kilo",
    title=f"Evolución del precio de {producto_sel} en {ciudad_sel}",
    labels={"Precio por kilo": "Precio (COP/kg)", "Fecha": "Fecha"},
    markers=True
)
st.plotly_chart(fig, use_container_width=True)

# 📉 Gráfico de retornos diarios
if st.checkbox("📉 Mostrar gráfico de retornos diarios"):
    df_retornos = df_filtrado.copy()
    df_retornos["Retorno diario"] = df_retornos["Precio por kilo"].pct_change()
    fig_ret = px.line(
        df_retornos,
        x="Fecha",
        y="Retorno diario",
        title=f"Retorno diario de {producto_sel} en {ciudad_sel}",
        labels={"Retorno diario": "Retorno (%)"},
        markers=False
    )
    st.plotly_chart(fig_ret, use_container_width=True)

# 📈 Distribución de retornos (campana)
if st.checkbox("📈 Mostrar distribución de retornos (histograma + campana)"):
    df_hist = df_filtrado.copy()
    df_hist["Retorno diario"] = df_hist["Precio por kilo"].pct_change()
    retornos_limpios = df_hist["Retorno diario"].dropna()

    fig_hist = px.histogram(
        retornos_limpios,
        nbins=50,
        marginal="box",
        opacity=0.75,
        title=f"Distribución de retornos – {producto_sel} en {ciudad_sel}",
        labels={"value": "Retorno diario"},
    )
    fig_hist.update_layout(bargap=0.1)
    st.plotly_chart(fig_hist, use_container_width=True)

# 📊 Estadísticas de riesgo
if st.checkbox("📊 Ver estadísticas de riesgo"):
    df_stats = df_filtrado.copy()
    df_stats["Retorno diario"] = df_stats["Precio por kilo"].pct_change()
    r = df_stats["Retorno diario"].dropna()

    media = np.mean(r)
    std = np.std(r)
    skew = stats.skew(r)
    kurt = stats.kurtosis(r)

    st.markdown("### 📌 Indicadores de riesgo:")
    st.markdown(f"**Media diaria:** {media:.4%}")
    st.markdown(f"**Volatilidad (std):** {std:.4%}")
    st.markdown(f"**Skewness (asimetría):** {skew:.4f}")
    st.markdown(f"**Kurtosis (colas extremas):** {kurt:.4f}")

# 📋 Tabla
with st.expander("📋 Ver datos en tabla"):
    st.dataframe(df_filtrado, use_container_width=True)


