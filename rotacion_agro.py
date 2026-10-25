import pandas as pd
import os


ruta_carpeta = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_INPUT = 'Rotacion.xlsx'
ARCHIVO_OUTPUT = 'Rotacion_Limpia_Qlik.csv'
ruta_completa = os.path.join(ruta_carpeta, ARCHIVO_INPUT)

if os.path.exists(ruta_completa):
    
    archivo_input = ARCHIVO_INPUT
    
    
    if archivo_input.endswith('.csv'):
        df_raw = pd.read_csv(ruta_completa, header=None)
    else:
        df_raw = pd.read_excel(ruta_completa, header=None, engine='openpyxl')

    
    idx_inicio = 0
    for i, fila in df_raw.iterrows():
        if 'Lote' in [str(x).strip() for x in fila.values]:
            idx_inicio = i
            break
    
    
    df = df_raw.iloc[idx_inicio:].copy()
    df.columns = df.iloc[0] 
    df = df[1:]

    
    df['Lote'] = df['Lote'].ffill()
    df['has'] = df['has'].ffill()
    
    nueva_data = []
    
    columnas_años = [c for c in df.columns if pd.notna(c) and str(c).replace('.', '').isdigit()]

    
    EVENTOS_CLIMATICOS = ['granizo', 'viento cos', 'helada', 'vto cos', 'gra']

    
    for i in range(len(df)):
        fila = df.iloc[i]
        
        for año in columnas_años:
            idx = df.columns.get_loc(año)
            
            
            valor_celda_cultivo = fila.iloc[idx]
            
            
            valor_derecha = fila.iloc[idx + 1] if idx + 1 < len(df.columns) else None
            
            
            if pd.notna(valor_celda_cultivo) and str(valor_celda_cultivo).strip() != "":
                texto_original = str(valor_celda_cultivo).strip()
                
               
                if texto_original in columnas_años:
                    continue

                nombre_cultivo = texto_original
                evento = None
                
                
                if any(e in texto_original.lower() for e in EVENTOS_CLIMATICOS):
                    evento = texto_original
                    nombre_cultivo = None 

                
                rinde = None
                try:
                    if pd.notna(valor_derecha):
                        val_num = float(str(valor_derecha).replace(',', '.'))
                        
                        if not (2000 < val_num < 2100):
                            rinde = val_num
                except:
                    
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

  
    df_final = pd.DataFrame(nueva_data).drop_duplicates()
    df_final.to_csv(os.path.join(ruta_carpeta, ARCHIVO_OUTPUT), index=False, encoding='utf-8-sig')
    
    print("--- PROCESO COMPLETADO ---")
    print(df_final.head(15))
else:
    print(f"No se encontró {ARCHIVO_INPUT} en {ruta_carpeta}")
