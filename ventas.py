# informes/ventas.py

from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os

# ──────────────────────────────────────────────
# 📄 CLASE PDF PERSONALIZADA CON FOOTER
# ──────────────────────────────────────────────

class PDFNoBorders(FPDF):
    def __init__(self, title="Informe de Ventas"):
        super().__init__(orientation="L", unit="mm", format="A4")
        self.title = title
        self.alias_nb_pages()

    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, self.title, ln=True, align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-10)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()} / {{nb}}", align="C")

    def table_header(self, headers, widths):
        self.set_fill_color(230, 230, 230)
        self.set_font("Arial", "B", 8)
        total_width = sum(widths)
        margin_left = (297 - total_width) / 2
        self.set_x(margin_left)
        for i in range(len(headers)):
            self.cell(widths[i], 6, headers[i], border=1, align='C', fill=True)
        self.ln()

    def table_row(self, row_data, widths, bold=False, borders_mask=None):
        self.set_font("Arial", "B" if bold else "", 8)
        total_width = sum(widths)
        margin_left = (297 - total_width) / 2
        self.set_x(margin_left)
        for i, value in enumerate(row_data):
            border_style = 1 if (borders_mask is None or borders_mask[i]) else 0
            self.cell(widths[i], 6, str(value), border=border_style, align='C')
        self.ln()

# ──────────────────────────────────────────────
# 📊 KPIs VISUALES EN TARJETAS
# ──────────────────────────────────────────────

def agregar_kpis_visual(pdf, df, establecimiento, fecha_limite):
    df_kpi = df.copy()
    df_kpi['Movimiento'] = df_kpi['Movimiento'].astype(str).str.strip().str.lower()
    df_kpi['Tipo Movimiento'] = df_kpi['Tipo Movimiento'].astype(str).str.strip().str.lower()
    df_kpi['Establecimiento'] = df_kpi['Establecimiento'].astype(str).str.strip()

    df_kpi = df_kpi[
        (df_kpi["Establecimiento"] == establecimiento) &
        (df_kpi["Movimiento"] == "venta") &
        (df_kpi["Tipo Movimiento"] == "salida") &
        (df_kpi["Fecha"] <= fecha_limite)
    ]

    if df_kpi.empty:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "⚠️ No hay datos para KPIs de ventas.", ln=True)
        return

    cantidad_total = df_kpi["Cantidad"].sum()
    kg_totales = df_kpi["Peso Total (Kg)"].sum()
    monto_total_gs = df_kpi["Monto Total Gs."].sum()
    precio_promedio_kg = monto_total_gs / kg_totales if kg_totales > 0 else 0
    kg_promedio = kg_totales / cantidad_total if cantidad_total > 0 else 0

    kpis = [
        ("Cantidad Total", f"{cantidad_total:,.0f}".replace(",", ".")),
        ("Kg Totales", f"{kg_totales:,.0f}".replace(",", ".")),
        ("Monto Total Gs.", f"{monto_total_gs:,.0f}".replace(",", ".")),
        ("Precio Promedio/kg", f"{precio_promedio_kg:,.0f}".replace(",", ".")),
        ("Kg Promedio", f"{kg_promedio:,.0f}".replace(",", "."))
    ]

    fig, ax = plt.subplots(1, len(kpis), figsize=(18, 3.5))
    fig.suptitle(
        f"Ventas Acumuladas hasta {fecha_limite.strftime('%d/%m/%Y')} - {establecimiento}",
        fontsize=14
    )

    for i, (titulo, valor) in enumerate(kpis):
        ax[i].set_facecolor("white")
        ax[i].text(0.5, 0.65, valor, fontsize=20, fontweight="bold", ha="center", color="black")
        ax[i].text(0.5, 0.48, titulo, fontsize=13, ha="center", color="black")
        for side in ["left", "right", "top", "bottom"]:
            ax[i].spines[side].set_visible(True)
            ax[i].spines[side].set_edgecolor("black")
            ax[i].spines[side].set_linewidth(1)
        ax[i].tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

    plt.subplots_adjust(left=0.05, right=0.95, top=0.78, bottom=0.2)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
        temp_path = tmpfile.name
        plt.savefig(temp_path, dpi=400, bbox_inches="tight", transparent=False)
        plt.close()

    pdf.image(temp_path, x=10, w=277)
    pdf.ln(2)
    os.remove(temp_path)

# ──────────────────────────────────────────────
# 📋 TABLA DETALLADA DE VENTAS Y RESUMEN
# ──────────────────────────────────────────────

def agregar_tabla_ventas(pdf, df_filtrado):
    if df_filtrado is None or df_filtrado.empty:
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, "⚠️ No se encontraron ventas para el rango seleccionado.", ln=True)
        return

    df = df_filtrado.rename(columns={
        "Peso Prom. (KgCab)": "Peso Prom. (Kg/Cab)",
        "Destino  Origen": "Destino / Origen",
        "Preciokg": "Precio/kg"
    })

    headers = ["Fecha", "Marca", "Categoría", "Cantidad", "Kg Totales",
               "Kg Promedio", "Destino", "Precio/kg", "Monto Total Gs."]
    widths = [25, 20, 38, 18, 25, 25, 50, 20, 30]
    total_width = sum(widths)
    margin_left = (297 - total_width) / 2

    marcas = df["Marca"].dropna().unique()

    for marca in marcas:
        if pdf.get_y() > 180:
            pdf.add_page()

        pdf.set_font("Arial", "B", 10)
        pdf.set_x(margin_left)
        pdf.cell(0, 10, f"Marca: {marca}", ln=True, align="L")

        tabla = df[df["Marca"] == marca]
        pdf.table_header(headers, widths)

        for _, row in tabla.iterrows():
            pdf.table_row([
                row["Fecha"].strftime("%d/%m/%Y") if pd.notnull(row["Fecha"]) else "",
                row["Marca"],
                row["Categoría"],
                f"{int(row['Cantidad']):,}".replace(",", "."),
                f"{int(row['Peso Total (Kg)']):,}".replace(",", "."),
                f"{int(row['Peso Prom. (Kg/Cab)']):,}".replace(",", ".") if pd.notnull(row["Peso Prom. (Kg/Cab)"]) else "0",
                row["Destino / Origen"],
                f"{int(row['Precio/kg']):,}".replace(",", "."),
                f"{int(row['Monto Total Gs.']):,}".replace(",", ".")
            ], widths)

        total_cant = tabla["Cantidad"].sum()
        total_kg = tabla["Peso Total (Kg)"].sum()
        total_monto = tabla["Monto Total Gs."].sum()
        kg_prom = total_kg / total_cant if total_cant > 0 else 0
        precio_kg = total_monto / total_kg if total_kg > 0 else 0

        pdf.set_font("Arial", "B", 8)
        pdf.table_row([
            "", "", "",
            f"{int(total_cant):,}".replace(",", "."),
            f"{int(total_kg):,}".replace(",", "."),
            f"{int(kg_prom):,}".replace(",", "."),
            "",
            f"{int(precio_kg):,}".replace(",", "."),
            f"{int(total_monto):,}".replace(",", ".")
        ], widths, bold=True, borders_mask=[False, False, False, True, True, True, False, True, True])

        pdf.ln(10)

    if pdf.get_y() > 180:
        pdf.add_page()

    resumen_headers = ["Categoría", "Cantidad Total", "Peso Promedio", "Precio/kg", "Monto Total Gs."]
    resumen_widths = [50, 30, 40, 40, 40]
    resumen_total_width = sum(resumen_widths)
    resumen_margin_left = (297 - resumen_total_width) / 2

    pdf.set_font("Arial", "B", 12)
    pdf.set_x(resumen_margin_left)
    pdf.cell(0, 10, "Resumen por Categoría", ln=True, align="L")
    pdf.table_header(resumen_headers, resumen_widths)

    resumen = df.groupby("Categoría").agg(
        Cantidad_Total=("Cantidad", "sum"),
        Peso_Total=("Peso Total (Kg)", "sum"),
        Monto_Total_Gs=("Monto Total Gs.", "sum")
    ).reset_index()

    resumen["Kg Promedio"] = resumen["Peso_Total"] / resumen["Cantidad_Total"]
    resumen["Precio/kg"] = resumen["Monto_Total_Gs"] / resumen["Peso_Total"]

    for _, row in resumen.iterrows():
        pdf.table_row([
            row["Categoría"],
            f"{int(row['Cantidad_Total']):,}".replace(",", "."),
            f"{row['Kg Promedio']:.0f}",
            f"{int(row['Precio/kg']):,}".replace(",", "."),
            f"{int(row['Monto_Total_Gs']):,}".replace(",", ".")
        ], resumen_widths)
