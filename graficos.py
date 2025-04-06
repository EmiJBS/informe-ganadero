# graficos.py

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import tempfile
import os

# ──────────────────────────────────────────────
# 📊 Gráfico de columnas apiladas por mes/categoría
# ──────────────────────────────────────────────

def grafico_ventas_mensual_apilado(df, pdf=None, mostrar_en_colab=True):
    df_filtrado = df[
        (df["Movimiento"].str.lower() == "venta") &
        (df["Tipo Movimiento"].str.lower() == "salida")
    ].copy()

    if df_filtrado.empty:
        print("⚠️ No hay datos de ventas para graficar.")
        return

    df_filtrado["Mes"] = pd.to_datetime(df_filtrado["Fecha"]).dt.to_period("M")
    df_filtrado["Mes"] = df_filtrado["Mes"].dt.strftime('%B %y')  # Ej: Julio 24

    pivot = df_filtrado.pivot_table(
        index="Mes",
        columns="Categoría",
        values="Cantidad",
        aggfunc="sum",
        fill_value=0
    ).sort_index()

    fig = go.Figure()

    for categoria in pivot.columns:
        fig.add_trace(go.Bar(
            x=pivot.index,
            y=pivot[categoria],
            name=categoria,
            text=pivot[categoria],
            textposition='auto'
        ))

    fig.update_layout(
        barmode="stack",
        title="Distribución mensual de ventas por categoría",
        xaxis_title="Mes",
        yaxis_title="Cantidad",
        template="plotly_white",  # ✅ estilo limpio
        legend_title="Categoría",
        height=400
    )

    if mostrar_en_colab:
        fig.show()

    if pdf:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.write_image(tmpfile.name, format="png", width=1000, height=500)
            pdf.image(tmpfile.name, x=10, w=135)
            os.remove(tmpfile.name)

# ──────────────────────────────────────────────
# 📊 Gráfico de torta por destino
# ──────────────────────────────────────────────

def grafico_ventas_por_destino(df, pdf=None, mostrar_en_colab=True):
    df_filtrado = df[
        (df["Movimiento"].str.lower() == "venta") &
        (df["Tipo Movimiento"].str.lower() == "salida")
    ].copy()

    if df_filtrado.empty:
        print("⚠️ No hay datos de ventas para gráfico de destino.")
        return

    resumen = df_filtrado.groupby("Destino / Origen")["Cantidad"].sum().reset_index()

    fig = px.pie(
        resumen,
        values="Cantidad",
        names="Destino / Origen",
        title="Distribución de ventas por destino",
        hole=0.3,
        template="plotly_white"  # ✅ limpio y profesional
    )
    fig.update_traces(textinfo='percent+label', textfont_size=12)

    if mostrar_en_colab:
        fig.show()

    if pdf:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
            fig.write_image(tmpfile.name, format="png", width=1000, height=500)
            pdf.image(tmpfile.name, x=150, y=pdf.get_y() - 95, w=135)  # lado derecho
            os.remove(tmpfile.name)
