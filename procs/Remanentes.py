import pandas as pd
import glob
import shutil
from procs.formats import title,success,warning,error,item

def run(log):
    log.write(f"{title}REMANENTES")
    try:
        rem = glob.glob("*Remanentes*")
        if len(rem)==0:
            log.write(f"{warning}No se encontro archivo.\n")
            return 0
        # Lee el archivo Excel
        archivo = pd.read_excel(rem[0], sheet_name=None)
        lista_datos = (
            []
        )  # Crea una lista vacía para almacenar los datos que cumplan las condiciones

        # Itera sobre cada hoja del archivo
        for nombre_hoja, df in archivo.items():
            # Recorre cada fila del DataFrame y verifica si la segunda columna contiene 'c', 'cc', o 'ccc'
            for i, fila in df.iterrows():
                if fila[1] in ["C", "CC", "CCC", "c", "cc", "ccc"]:
                    # Si la condición se cumple, agrega el dato de la sexta columna a la lista
                    lista_datos.append((fila[5]))

        # Guarda los resultados en un archivo de texto
        with open("out//dnis para reenviar.txt", "w") as archivo_texto:
            for dato in lista_datos:
                archivo_texto.write(str(dato) + "\n")
        shutil.move(rem[0], "in")
        
        log.write(f"{success}El archivo 'out\dnis para reenviar.txt' fue creado con exito.\n")
    except Exception as e:
        log.write(f"Error: {e}\n")

    return 0
