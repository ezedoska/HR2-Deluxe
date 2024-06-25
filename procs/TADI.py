import pandas as pd
from unidecode import unidecode
from procs.DictsAndLists1x import provincias, afipPAIS, ids, generos
import numpy as np
import zipfile
import os
import datetime
from procs.formats import title,success,warning,error,item

def run(log):
    log.write(f"{title}TADI COMBINACION Y LIMPIEZA")

    cdp = "utf8"
    cgf = "utf8"
    try:
        log.write(f"Leyendo...{item}Postulantes")
        # Cargar los datos de los postulantes y adherentes
        postulante_df = pd.read_csv(
            "datos personales_data.csv", dtype=str, delimiter=";", encoding=cdp
        )
    except pd.errors.ParserError as e:
        log.write(f"{error}Error parsing CSV: {e}")
        # Obtén el número de la línea defectuosa
        line_number = int(str(e).split(" ")[-1])
        # Lee solo la línea defectuosa
        with open("datos personales_data.csv", "r", encoding=cdp) as file:
            lines = file.readlines()
            defective_line = lines[
                line_number - 1
            ]  # Resta 1 porque las listas en Python son de base 0
        # Guarda la línea defectuosa en un nuevo archivo CSV
        with open("defective_line.csv", "w", encoding=cdp) as output_file:
            output_file.write(defective_line)
        log.write(
            f"{warning}Error parseando datos, revisar 'defective_line.csv' para saber que linea fue.\n"
        )
        return 0
    except FileNotFoundError as e:
        log.write(f"{warning}No se encontro el archivo de postulantes, verificar.\n")
        return 0
    try:
        log.write(f"Leyendo...{item}Adherentes")
        adherente_df = pd.read_csv(
            "Detalle del grupo familiar_data.csv",
            dtype=str,
            delimiter=";",
            encoding=cgf,
        )
    except Exception as E:
        # Definir las columnas
        columnas = [
            "Fecha de caratulación EE",
            "Número de EE",
            "Numero de Formulario GEDO",
            "CUIT; CUIL o CDI",
            "Tipo",
            "Tipo de documento(ADHERENTE)",
            "Número de Documento(ADHERENTE)",
            "Apellido(ADHERENTE)",
            "Nombre(ADHERENTE)",
            "Parentesco(ADHERENTE)",
            "Sexo(ADHERENTE)",
            "Fecha de Nacimiento(ADHERENTE)",
        ]
        log.write(
            f"{warning}Adherentes no se pudo leer o no esta en la carpeta, verificar."
        )
        # Crear un DataFrame vacío con las columnas
        adherente_df = pd.DataFrame(columns=columnas)

    # Aplicar UNICODE a todo el df
    postulante_df = postulante_df.applymap(
        lambda x: unidecode(str(x)) if pd.notnull(x) and isinstance(x, str) else x
    )
    adherente_df = adherente_df.applymap(
        lambda x: unidecode(str(x)) if pd.notnull(x) and isinstance(x, str) else x
    )
    # Aplicar MAYUS a los todos strings del df
    postulante_df = postulante_df.applymap(
        lambda x: str(x).upper() if pd.notnull(x) and isinstance(x, str) else x
    )
    adherente_df = adherente_df.applymap(
        lambda x: str(x).upper() if pd.notnull(x) and isinstance(x, str) else x
    )
    # Borrar cualquier pipe que pueda romper algo en el df y borrarlo
    postulante_df = postulante_df.applymap(
        lambda x: x.replace("|", "") if isinstance(x, str) else x
    )
    adherente_df = adherente_df.applymap(
        lambda x: x.replace("|", "") if isinstance(x, str) else x
    )
    # Llenar de 0 a la izquierda documentos de 7 digitos
    postulante_df["Nº Documento"] = postulante_df["Nº Documento"].apply(
        lambda x: str(x).zfill(8) if pd.notnull(x) else x
    )

    # Separar Número de EE en 3 columnas
    postulante_df[["Año de Expediente", "Numero de Exp", "Dependencia"]] = (
        postulante_df["Número de EE"].str.extract(r"-(\d{4})-(\d+)-(\S+)$")
    )

    # postulante_df = postulante_df.replace("SIN INFORMACION", np.nan).infer_objects(
    #     copy=False
    # )
    postulante_df = postulante_df.replace(["SIN INFORMACION", "s/n"], np.nan)
    adherente_df = adherente_df.replace(["SIN INFORMACION", "s/n"], np.nan)
    # reemplazamos NaN por espacios vacios
    postulante_df = postulante_df.fillna("")
    adherente_df = adherente_df.fillna("")


    # Limpiamos la actividad 
    log.write(f"Arreglando...{item}Actividades y OS")
    
    mask = postulante_df['Código de Actividad'] == ''
    postulante_df.loc[mask, 'Código de Actividad'] = postulante_df.loc[mask, 'Código de Actividad(alternativo)']
    postulante_df["Código de Actividad"] = postulante_df["Código de Actividad"].astype(
        str
    )
    postulante_df["Código de Actividad"] = postulante_df[
        "Código de Actividad"
    ].str.extract(r"(\d+)")
    postulante_df = postulante_df.drop(columns=["Código de Actividad(alternativo)"])


    # Limpiamos OS
    postulante_df["Obra social elegida"] = postulante_df[
        "Obra social elegida"
    ].str.extract(r"(\d+)")
    
    
    # Arreglamos nombres largos
    postulante_df["Denominación Cooperativa"] = (
        postulante_df["Denominación Cooperativa"].astype(str).str[:49]
    )
    postulante_df["Denominación Proyecto Productivo"] = (
        postulante_df["Denominación Proyecto Productivo"].astype(str).str[:49]
    )
    ###############################################
    # PROCESANDO FECHAS

    # Fijar el año máximo a 2024
    log.write(f"Arreglando...{item}Fechas")

    # Función para corregir los años en el formato de fecha en un DataFrame
    def corregir_anos(df, columna):
        for i, fecha_str in enumerate(df[columna]):
            if pd.notna(fecha_str) and isinstance(
                fecha_str, str
            ):  # Verificar que la fecha no sea nula y sea una cadena
                # Intentar convertir la fecha utilizando pd.to_datetime
                try:
                    fecha = pd.to_datetime(fecha_str, format="%d/%m/%Y")
                except pd.errors.OutOfBoundsDatetime:
                    # Si ocurre un error de OutOfBoundsDatetime, establecer la fecha como "1/1/2000"
                    df.at[i, columna] = "1/1/2000"
                    continue

                # Corregir años mayores a 2024 y años con menos de 4 cifras
                if fecha.year > 2024 or fecha.year < 1930 or len(str(fecha.year)) < 4:
                    df.at[i, columna] = "1/1/2000"

    # Corregir los años en los DataFrames
    corregir_anos(postulante_df, "Fecha de Nacimiento")
    corregir_anos(adherente_df, "Fecha de Nacimiento(ADHERENTE)")

    def formatear_fecha(df, column_name):
        # Remover cualquier información después de la fecha, como horarios
        df[column_name] = df[column_name].str.split().str[0]

        # Convertir la columna de fecha al formato correcto
        df[column_name] = pd.to_datetime(
            df[column_name], format="%d/%m/%Y", errors="coerce"
        )
        df[column_name] = df[column_name].dt.strftime("%d/%m/%Y")

    def procesar_fechas(df, date_columns):
        for column in date_columns:
            formatear_fecha(df, column)

        # Ordenar por la columna de fecha principal (Fecha de caratulación EE)
        df.sort_values(by="Fecha de caratulación EE", ascending=True, inplace=True)

    # Lista de columnas de fecha en postulante_df y adherente_df
    postulante_fechas = [
        "Fecha de caratulación EE",
        "Vencimiento del CERMI",
        "Fecha de Nacimiento",
    ]
    adherente_fechas = ["Fecha de caratulación EE", "Fecha de Nacimiento(ADHERENTE)"]

    # Procesamos
    procesar_fechas(postulante_df, postulante_fechas)
    procesar_fechas(adherente_df, adherente_fechas)

    # Renombramos columnas de CUIT
    postulante_df = postulante_df.rename(columns={"CUIT persona en TAD": "CUIT"})
    adherente_df = adherente_df.rename(columns={"CUIT; CUIL o CDI": "CUIT"})

    postulante_df = postulante_df.drop(columns=["CUIT; CUIL o CDI"])

    # Función para ajustar los valores
    def ajustar_valor(valor):
        if len(valor) == 11:
            return valor[2:-1]
        else:
            return valor

    # Aplicar la función a la columna
    postulante_df["Nº Documento"] = postulante_df["Nº Documento"].apply(ajustar_valor)

    adherente_df["Número de Documento(ADHERENTE)"] = (
        adherente_df["Número de Documento(ADHERENTE)"]
        .astype(str)
        .apply(lambda x: x[:8] if len(x) >= 9 else x)
    )
    log.write(f"Arreglando...{item}Nombres y apellidos")

    # Remover espacios en blanco al principio y al final de nombres y apellidos, tambien espacios dobles en blanco
    def limpiar_nombres(df, column_names):
        for col in column_names:
            df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)

    # Aplicar limpieza a las columnas en postulante_df
    limpiar_nombres(postulante_df, ["Nombre", "Apellido"])

    # Aplicar limpieza a las columnas en adherente_df
    limpiar_nombres(adherente_df, ["Nombre(ADHERENTE)", "Apellido(ADHERENTE)"])

    log.write(f"Arreglando...{item}Codificaciones")

    # Codificamos
    adherente_df["Tipo"] = adherente_df["Tipo"].replace(
        {"ALTA": "1", "MODIFICACION": "2", "BAJA": "3"}
    )
    prov = {k: str(v) for k, v in provincias.items()}
    postulante_df["Provincia"] = postulante_df["Provincia"].replace(prov)
    postulante_df["País de Origen"] = postulante_df["País de Origen"].replace(afipPAIS)
    postulante_df["País de Origen"] = postulante_df["País de Origen"].replace(
        {"REPUBLICA DOMINICANA": "209"}
    )
    # Reemplazar varlores para que sean compatibles con las tablas SOMOSO
    postulante_df["Tipo de Trámite"] = postulante_df["Tipo de Trámite"].replace(
        {"ALTA": "1", "MODIFICACION": "2", "BAJA": "3"}
    )
    postulante_df["Tipo Documento"] = postulante_df["Tipo Documento"].replace(ids)

    postulante_df["Género"] = postulante_df["Género"].replace(generos)
    adherente_df["Tipo de documento(ADHERENTE)"] = adherente_df[
        "Tipo de documento(ADHERENTE)"
    ].replace(ids)

    # arreglo parentescos
    adherente_df["Parentesco(ADHERENTE)"] = adherente_df["Parentesco(ADHERENTE)"].apply(
        lambda x: (
            "3"
            if isinstance(x, str) and x.startswith("H")
            else (
                "2"
                if isinstance(x, str) and x.startswith("C") or x.startswith("E")
                else "3"
            )
        )
    )
    log.write(f"Arreglando...{item}Celdas nulas y vacias")

    def limpiar_columna(df, columna, reemplazo):
        df[columna] = (
            df[columna]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .replace("", reemplazo)
        )
        if columna not in ["Matrícula Cooperativa", "Domicilio Fiscal - Sector"]:
            df[columna] = df[columna].str[:5]

    def limpiar_celdas(postulante_df):
        columnas_a_limpiar = {
            "Domicilio Fiscal - Código Postal": "0",
            "Domicilio Fiscal - Número": "0",
            "Matrícula Cooperativa": "",
            "Domicilio Fiscal - Sector": "",
            "Domicilio Fiscal - Manzana": "",
            "Domicilio Fiscal - Departamento": "",
            "Domicilio Fiscal - Piso": "",
            "Domicilio Fiscal - Torre": "",
        }

        for columna, reemplazo in columnas_a_limpiar.items():
            limpiar_columna(postulante_df, columna, reemplazo)

    # Llamada a la función para limpiar las celdas
    limpiar_celdas(postulante_df)

    ################# LIMPIEZA DE DUPLICADOS Y DNI ERRONEOS ############################
    log.write(f"Arreglando...{item}Duplicados y DNI erroneos")
    # Identificar y guardar duplicados
    duplicados = postulante_df[postulante_df.duplicated(subset="CUIT", keep=False)]

    # Filtrar para quedarse solo con la fila más reciente
    postulante_df = postulante_df.sort_values(
        by=["CUIT", "Fecha de caratulación EE"], ascending=[True, False]
    ).drop_duplicates(subset="CUIT")

    # Crear el informe de borrados por duplicados
    informe_borrados_duplicados = duplicados[
        ~duplicados["Número de EE"].isin(postulante_df["Número de EE"])
    ].copy()

    if not informe_borrados_duplicados.empty:
        informe_borrados_duplicados.loc[:, "Motivo de Borrado"] = "Duplicado"
    else:
        # Manejar la situación cuando el DataFrame está vacío
        log.write("No hubo duplicados que armar.")

    # Identificar y guardar inconsistencias CUIT-DNI
    def tiene_inconsistencia(row):
        cuit = str(row["CUIT"])
        dni = str(row["Nº Documento"])
        return not (cuit[2:-1] == dni)

    inconsistencias = postulante_df[postulante_df.apply(tiene_inconsistencia, axis=1)]

    # Crear el informe de borrados por inconsistencia
    informe_borrados_inconsistencia = postulante_df.loc[inconsistencias.index].copy()
    informe_borrados_inconsistencia["Motivo de Borrado"] = "Inconsistencia CUIT-DNI"

    # Borrar las líneas con inconsistencias en postulante_df
    postulante_df = postulante_df.drop(inconsistencias.index)

    # Unir ambos informes
    informe_borrados = pd.concat(
        [informe_borrados_duplicados, informe_borrados_inconsistencia]
    )
    log.write(f"Guardando...{item}Informe_borrados.xlsx")
    # Guardar informe_borrados como un archivo Excel
    informe_borrados.to_excel("SOMOSOTAD\\informe_borrados.xlsx", index=False)

    # Filtrar el df adherente_df eliminando las filas con "Número de EE" en común con el informe_borrados
    adherente_df = adherente_df[
        ~adherente_df["Número de EE"].isin(informe_borrados["Número de EE"])
    ]
    # Ordena el DataFrame por 'fecha' de forma descendente dentro de cada grupo de 'DNI'
    adherente_df = adherente_df.sort_values(
        by=["Número de Documento(ADHERENTE)", "Fecha de caratulación EE"],
        ascending=[True, False],
    )

    # Elimina duplicados basados en 'DNI', conservando solo la fila con la fecha más reciente
    adherente_df = adherente_df.drop_duplicates(subset="Número de Documento(ADHERENTE)")

    # Reinicia los índices después de la manipulación
    adherente_df = adherente_df.reset_index(drop=True)
    ####################################################################################

    # Actualizar la columna "Obra social elegida" en postulante_df según la condición en "¿Es jubilado?"
    postulante_df.loc[postulante_df["¿Es jubilado?"] == "SI", "Obra social elegida"] = (
        "500807"
    )
    ################## LIMPIEZA DE DATOS MAL CARGADOS ##########################
    log.write(f"Guardando...{item}Csvs y zips")

    try:
        # Verificar si el subdirectorio SOMOSOTAD existe, si no, crearlo
        subdirectory = "SOMOSOTAD"
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)

        # Guardar el nuevo DataFrame como CSV
        adherente_df.to_csv("SOMOSOTAD\\adherentes.csv", sep="|", index=False)
        postulante_df.to_csv("SOMOSOTAD\\postulantes.csv", sep=",", index=False)

        # Definir los nombres de los archivos CSV y el nombre del archivo ZIP
        if adherente_df.shape[0] != 0:
            csv_files = ["SOMOSOTAD/postulantes.csv", "SOMOSOTAD/adherentes.csv"]
        else:
            csv_files = ["SOMOSOTAD/postulantes.csv"]
        zip_file = "SOMOSOTAD/postulantes_TAD.zip"

        # Crear un archivo ZIP y agregar los archivos CSV
        with zipfile.ZipFile(zip_file, "w") as zipf:
            for csv_file in csv_files:
                zipf.write(csv_file, arcname=csv_file.split("/")[-1])

        # armamos el envio a webservice
        postulante_df["CUIT"].to_csv(
            "SOMOSOTAD\\para_webservice.csv", index=False, header=False, sep="\t"
        )
        log.write(f"Archivos {csv_files} comprimidos en {zip_file}")
    except Exception as e:
        log.write(
            f"{e} \n {error}Hay problemas en la creacion de archivos.\n"
        )
        return 0

    # Obtener la fecha y hora actual
    conteo = postulante_df["Tipo de Trámite"].value_counts()
    altas = conteo[0]
    try:
        mod = int(conteo[1])
    except:
        mod = 0
    adh = adherente_df.shape[0]
    bajas = informe_borrados.shape[0]
    lineas = altas + bajas + adh + mod
    fecha_actual = datetime.datetime.now()
    fecha_formateada = fecha_actual.strftime("%Y-%m-%d %H:%M:%S")
    postulante_df['Fecha de caratulación EE'] = pd.to_datetime(postulante_df['Fecha de caratulación EE'])
    fecha_min = postulante_df['Fecha de caratulación EE'].min()
    fecha_max = postulante_df['Fecha de caratulación EE'].max()
    fecha_entre = f"{fecha_min.strftime('%m/%d')}-{fecha_max.strftime('%m/%d')}"
    with open("paquetelog.txt", "a") as archivo:
        # Escribir la nueva línea en el archivo
        archivo.write(f"\nTADI|{fecha_formateada}|{fecha_entre}|{altas}|{bajas}|{mod}|{adh}|{lineas}")

    log.write(f"{success}Proceso terminado con exito.\n")
    return 0