import pandas as pd
import os

# 1. Localizar el archivo que subiste
ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
archivos = [f for f in os.listdir(ruta_carpeta) if f.endswith('.csv') or f.endswith('.xlsx')]

if archivos:
    # Usamos el archivo más reciente o el que coincida con tu subida
    archivo_input = archivos[0] 
    ruta_completa = os.path.join(ruta_carpeta, archivo_input)
    
    # Leer el archivo (detectando si es CSV o Excel)
    if archivo_input.endswith('.csv'):
        df_raw = pd.read_csv(ruta_completa, header=None)
    else:
        df_raw = pd.read_excel(ruta_completa, header=None, engine='openpyxl')

    # 2. Encontrar la fila de encabezados (donde está "Lote")
    idx_inicio = 0
    for i, fila in df_raw.iterrows():
        if 'Lote' in [str(x).strip() for x in fila.values]:
            idx_inicio = i
            break
    
    # Volvemos a leer desde la fila correcta
    df = df_raw.iloc[idx_inicio:].copy()
    df.columns = df.iloc[0] # Asignar la primera fila como nombres de columna
    df = df[1:] # Quitar la fila de nombres de los datos

    # 3. Rellenar Lote y has (ffill)
    df['Lote'] = df['Lote'].ffill()
    df['has'] = df['has'].ffill()
    
    nueva_data = []
    # Identificar las columnas de años (2011.12, etc.)
    columnas_años = [c for c in df.columns if pd.notna(c) and str(c).replace('.', '').isdigit()]

    # Lista de eventos climáticos para separar
    EVENTOS_CLIMATICOS = ['granizo', 'viento cos', 'helada', 'vto cos', 'gra']

    # 4. Procesar el Excel celda por celda
    for i in range(len(df)):
        fila = df.iloc[i]
        
        for año in columnas_años:
            idx = df.columns.get_loc(año)
            
            # El cultivo es lo que está en la columna del año
            valor_celda_cultivo = fila.iloc[idx]
            
            # El rinde es lo que está a la derecha
            valor_derecha = fila.iloc[idx + 1] if idx + 1 < len(df.columns) else None
            
            # Solo procesamos si hay algo escrito en la celda del cultivo
            if pd.notna(valor_celda_cultivo) and str(valor_celda_cultivo).strip() != "":
                texto_original = str(valor_celda_cultivo).strip()
                
                # Si el valor es solo un año (ej. 2011.12), lo ignoramos como cultivo
                if texto_original in columnas_años:
                    continue

                nombre_cultivo = texto_original
                evento = None
                
                # Separar si es un Evento
                if any(e in texto_original.lower() for e in EVENTOS_CLIMATICOS):
                    evento = texto_original
                    nombre_cultivo = None # No aparece como cultivo

                # Validar Rinde
                rinde = None
                try:
                    if pd.notna(valor_derecha):
                        val_num = float(str(valor_derecha).replace(',', '.'))
                        # Si el número parece un año, no es rinde
                        if not (2000 < val_num < 2100):
                            rinde = val_num
                except:
                    # Si a la derecha hay texto de evento, lo guardamos también
                    if any(e in str(valor_derecha).lower() for e in EVENTOS_CLIMATICOS):
                        evento = str(valor_derecha).strip()

                nueva_data.append({
                    'Lote': fila['Lote'],
                    'has': fila['has'],
                    'Campaña': año,
                    'Cultivo': nombre_cultivo,
                    'Rinde': rinde,
                    'Evento': evento
                })

    # 5. Guardar resultado final
    df_final = pd.DataFrame(nueva_data).drop_duplicates()
    df_final.to_csv('Rotacion_Limpia_Qlik.csv', index=False, encoding='utf-8-sig')
    
    print("--- PROCESO COMPLETADO ---")
    print(df_final.head(15))