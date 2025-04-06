# report_generator.py

from fpdf import FPDF
import calendar
from ventas import PDFNoBorders, agregar_kpis_visual, agregar_tabla_ventas
from graficos import grafico_ventas_mensual_apilado, grafico_ventas_por_destino


def generar_informe(df, tipo, est, f_ini, f_fin):
    from google.colab import files

    print("🔍 Aplicando filtros...")

    # 🔎 Filtro principal
    df_filtrado = df[
        (df['Establecimiento'] == est) &
        (df['Fecha'] >= f_ini) &
        (df['Fecha'] <= f_fin)
    ]

    if tipo == "Ventas":
        df_filtrado = df_filtrado[
            (df_filtrado['Movimiento'].str.lower() == 'venta') &
            (df_filtrado['Tipo Movimiento'].str.lower() == 'salida')
        ]

        if df_filtrado.empty:
            print("⚠️ No hay datos para ventas en ese rango.")
            return

        print("🧾 Generando informe PDF...")

        pdf = PDFNoBorders("Informe de Ventas")
        pdf.add_page()

        # ✅ Página 1: KPIs + Tabla detallada
        agregar_kpis_visual(pdf, df, est, f_fin)

        # ➕ Encabezado antes de tabla
        mes_nombre = calendar.month_name[f_fin.month].capitalize()
        periodo_str = f"{f_ini.strftime('%d/%m/%Y')} a {f_fin.strftime('%d/%m/%Y')}"
        titulo_periodo = f"Ventas de {mes_nombre} {f_fin.year} ({periodo_str}) - {est}"

        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, titulo_periodo, ln=True, align="L")

        agregar_tabla_ventas(pdf, df_filtrado)

        # ✅ Página 2: Gráficos visuales
        pdf.add_page()
        grafico_ventas_mensual_apilado(df, pdf=pdf, mostrar_en_colab=False)
        grafico_ventas_por_destino(df, pdf=pdf, mostrar_en_colab=False)

        # 📥 Exportar
        output_path = "informe_ventas.pdf"
        pdf.output(output_path)
        files.download(output_path)

        print("✅ Informe generado y descargado.")

    else:
        print(f"⚠️ Informe para '{tipo}' aún no implementado.")
