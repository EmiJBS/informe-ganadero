# core/loader.py

import pandas as pd
import numpy as np

def cargar_excel(files):
    try:
        uploaded = files.upload()
        for filename in uploaded.keys():
            print(f"✅ Archivo cargado: {filename}")
            return pd.read_excel(filename)
    except Exception as e:
        print(f"❌ Error al cargar el archivo: {e}")
        return None

def limpiar_datos(df):
    try:
        print("🔎 Iniciando limpieza y formateo de datos...")

        df.columns = df.columns.str.strip()

        # ✅ Fecha como date y eliminar nulos
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.date
            fecha_nulas = df['Fecha'].isnull().sum()
            if fecha_nulas > 0:
                print(f"⚠️ {fecha_nulas} filas sin fecha válida serán eliminadas.")
            df = df[df['Fecha'].notnull()]
            print(f"✅ Columna 'Fecha' convertida a date. Filas válidas: {len(df)}")

        columnas_texto = [
            'Establecimiento', 'Marca', 'Categoría', 'Tipo Movimiento',
            'Movimiento', 'Destino  Origen', 'Causa', 'Sector', 'Potrero', 'Obs'
        ]
        for col in columnas_texto:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().replace('nan', 'Sin Dato')
                print(f"✅ '{col}' convertida a texto.")

        if 'Carimbo' in df.columns:
            df['Carimbo'] = pd.to_numeric(df['Carimbo'], errors='coerce').fillna(0).astype(int)

        columnas_numericas = [
            'Cantidad', 'Peso Prom. (KgCab)', 'Peso Total (Kg)',
            'Peso Neto', '% Rendimiento', 'Preciokg',
            'Monto Total Gs.', 'Monto total $'
        ]
        for col in columnas_numericas:
            if col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace('.', '', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        columnas_enteras = ['Cantidad', 'Peso Total (Kg)', 'Peso Neto', 'Preciokg', 'Monto Total Gs.']
        for col in columnas_enteras:
            if col in df.columns:
                df[col] = df[col].astype('Int64', errors='ignore')

        if 'Peso Prom. (KgCab)' in df.columns:
            df['Peso Prom. (KgCab)'] = df['Peso Prom. (KgCab)'].apply(
                lambda x: int(x) if pd.notna(x) else np.nan
            )

        print("✅ Limpieza completa.")
        return df

    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return None
