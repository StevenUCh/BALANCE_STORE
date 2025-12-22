import pandas as pd
from utils import limpiar_precio, normalizar_modelo

def procesar_datos(ventas_df, inventario_df):

    # Limpieza de precios
    for col in ['Precio Usado', 'Importe']:
        ventas_df[col] = ventas_df[col].apply(limpiar_precio)

    inventario_df['P. Venta'] = inventario_df['P. Venta'].apply(limpiar_precio)
    inventario_df['P. Mayoreo'] = inventario_df['P. Mayoreo'].apply(limpiar_precio)

    # Merge
    df = ventas_df.merge(
        inventario_df[['Código', 'P. Venta', 'P. Mayoreo', 'Existencia']],
        on='Código',
        how='left'
    )

    # Clasificación de venta
    def clasificar(row):
        if row['Precio Usado'] == row['P. Mayoreo']:
            return 'MAYOR'
        elif row['Precio Usado'] == row['P. Venta']:
            return 'DETAL'
        else:
            # Descuento
            if abs(row['Precio Usado'] - row['P. Mayoreo']) < abs(row['Precio Usado'] - row['P. Venta']):
                return 'DESCUENTO MAYOR'
            return 'DESCUENTO DETAL'

    df['Tipo Venta'] = df.apply(clasificar, axis=1)

    # Modelo sin talla
    df['Modelo'] = df['Descripción'].apply(normalizar_modelo)

    # =======================
    # MÉTRICAS
    # =======================

    # Normalizar tipo de venta para reporte
    df['Tipo Reporte'] = df['Tipo Venta'].replace({
        'DESCUENTO MAYOR': 'MAYOR',
        'DESCUENTO DETAL': 'DETAL'
    })

    ventas_totales = (
        df.pivot_table(
            index='Departamento',
            columns='Tipo Reporte',
            values='Importe',
            aggfunc='sum',
            fill_value=0
        )
        .reset_index()
    )

    ventas_totales['TOTAL'] = ventas_totales.get('MAYOR', 0) + ventas_totales.get('DETAL', 0)

    # Fila TOTAL GENERAL VENTAS
    total_ventas = pd.DataFrame([{
        'Departamento': 'TOTAL GENERAL',
        'MAYOR': ventas_totales['MAYOR'].sum(),
        'DETAL': ventas_totales['DETAL'].sum(),
        'TOTAL': ventas_totales['TOTAL'].sum()
    }])

    ventas_totales = pd.concat([ventas_totales, total_ventas], ignore_index=True)

    unidades = (
        df.pivot_table(
            index='Departamento',
            columns='Tipo Reporte',
            values='Cantidad',
            aggfunc='sum',
            fill_value=0
        )
        .reset_index()
    )

    unidades['TOTAL'] = unidades.get('MAYOR', 0) + unidades.get('DETAL', 0)

    # Fila TOTAL GENERAL UNIDADES
    total_unidades = pd.DataFrame([{
        'Departamento': 'TOTAL GENERAL',
        'MAYOR': unidades['MAYOR'].sum(),
        'DETAL': unidades['DETAL'].sum(),
        'TOTAL': unidades['TOTAL'].sum()
    }])

    unidades = pd.concat([unidades, total_unidades], ignore_index=True)


    ventas_modelo = df.groupby('Modelo')['Cantidad'].sum().reset_index()

    # Comisiones
    df['Comision'] = df['Tipo Venta'].apply(
        lambda x: 1000 if 'MAYOR' in x else 2000
    ) * df['Cantidad']

    comisiones = df.groupby('Departamento')['Comision'].sum().reset_index()
    total_comisiones = df['Comision'].sum()

    total_comisiones_df = pd.DataFrame([{
        'Departamento': 'TOTAL GENERAL',
        'Comision': total_comisiones
    }])

    comisiones = pd.concat([comisiones, total_comisiones_df], ignore_index=True)

# Eliminar TOTAL GENERAL si existe
    ventas_totales_clean = ventas_totales[ventas_totales['Departamento'] != 'TOTAL GENERAL']
    comisiones_clean = comisiones[comisiones['Departamento'] != 'TOTAL GENERAL']
    # Balance por Departamento
    balance_depto = ventas_totales_clean.merge(
        comisiones_clean,
        on='Departamento',
        how='left'
    )

    # Reemplazar NaN por 0
    balance_depto['Comision'] = balance_depto['Comision'].fillna(0)

    # Total ventas
    balance_depto['Total_Ventas'] = balance_depto['MAYOR'] + balance_depto['DETAL']

    # Total neto
    balance_depto['Total_Neto'] = balance_depto['Total_Ventas'] - balance_depto['Comision']

    # Fila TOTAL GENERAL
    total_balance = pd.DataFrame([{
        'Departamento': 'TOTAL GENERAL',
        'MAYOR': balance_depto['MAYOR'].sum(),
        'DETAL': balance_depto['DETAL'].sum(),
        'Comision': balance_depto['Comision'].sum(),
        'Total_Ventas': balance_depto['Total_Ventas'].sum(),
        'Total_Neto': balance_depto['Total_Neto'].sum()
    }])

    balance_depto = pd.concat([balance_depto, total_balance], ignore_index=True)


    # Limpiar existencia (viene como texto "6,00")
    inventario_df['Existencia'] = (
        inventario_df['Existencia']
        .astype(str)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
        .fillna(0)
        .astype(int)
    )

    # =========================
    # CONSOLIDADO POR CONJUNTO (SIN TALLA)
    # =========================

    # Normalizar modelo en inventario
    inventario_df['Modelo'] = inventario_df['Producto'].apply(normalizar_modelo)

    inventario_modelo = (
        inventario_df.groupby('Modelo', as_index=False)
        .agg(Inventario=('Existencia', 'sum'))
    )

    ventas_modelo_detalle = (
        df.groupby('Modelo', as_index=False)
        .agg(Vendido=('Cantidad', 'sum'))
    )

    # Merge inventario + ventas
    consolidado_modelo = inventario_modelo.merge(
        ventas_modelo_detalle,
        on='Modelo',
        how='outer'
    )

    consolidado_modelo['Inventario'] = consolidado_modelo['Inventario'].fillna(0).astype(int)
    consolidado_modelo['Vendido'] = consolidado_modelo['Vendido'].fillna(0).astype(int)

    consolidado_modelo['Total'] = (
        consolidado_modelo['Inventario'] + consolidado_modelo['Vendido']
    )


    # =========================
    # CONSOLIDADO POR CÓDIGO
    # =========================

    # Asegurar tipos numéricos
    df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0).astype(int)

    # Ventas por código
    consolidado = (
        df.groupby(['Código', 'Descripción'], as_index=False)
        .agg(Vendidas=('Cantidad', 'sum'))
    )

    # Merge con inventario
    consolidado = consolidado.merge(
        inventario_df[['Código', 'Existencia']],
        on='Código',
        how='left'
    )

    consolidado['Existencia'] = consolidado['Existencia'].fillna(0)
    consolidado['Vendidas'] = consolidado['Vendidas'].fillna(0)

    # TOTAL REAL
    consolidado['Total_General'] = (
        consolidado['Existencia'] + consolidado['Vendidas']
    )

    return {
        'ventas_totales': ventas_totales,
        'unidades': unidades,
        'ventas_modelo': ventas_modelo,
        'comisiones': comisiones,
        'total_comisiones': total_comisiones,
        'consolidado': consolidado,
        'consolidado_modelo': consolidado_modelo,
        'balance_depto' :balance_depto
    }

