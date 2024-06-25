import pandas as pd
import random
from datetime import datetime
from procs.PaquetesSINTyS import encrypt_files
from procs.formats import title,success,warning,error,item

def run(log):
    log.write(f"{title}NO MS")
    # Step 1: Read the initial Excel file
    try:
        main_df = pd.read_excel("noms.xlsx")
        log.write(f"Archivo encontrado")
    except FileNotFoundError:
        log.write(f"{warning}No se encontro el archivo de NO MS\n")
        return 0
    
    # Step 2: Create the main_df dataframe with static columns
    static_info_dict = {
        "calle": "25 DE MAYO",
        "numero": "606",
        "piso": " ",
        "depto": " ",
        "manzana": " ",
        "sector": " ",
        "torre": " ",
        "TipodatoAdic": "03",
        "DatoAdicional": "Sin Datos",
        "CodProvincia": "0",
        "CPostal": "1002",
        "Localidad": "25 DE MAYO",
        "calleFiscal": "25 DE MAYO",
        "NroFiscal": "606",
        "PisoFiscal": " ",
        "DeptoFiscal": " ",
        "ManzanaFiscal": " ",
        "SectorFiscal": " ",
        "TorreFiscal": " ",
        "TipodatoAdicFiscal": "03",
        "DatoAdicionalFiscal": "Sin Datos",
        "CodProvinciaFiscal": "0",
        "CPostalFiscal": "1002",
        "LocalidadFiscal": "25 DE MAYO",
        "CUIT_declarada": " ",
        "Fechainfo": " ",
        "Paq_0_NroLote": "9901",
        "BLANCOS": " ",
        "UNLAM": " ",
        "Municipio": "CIUDAD DE BUENOS AIRES",
        "otro Municipio": "CIUDAD DE BUENOS AIRES",
        "Actividad": "202320",
        "Descripcion actividad": "FABRICACIÓN DE COSMÉTICOS, PERFUMES Y  PRODUCTOS D",
        "NroREDLES": "1000",
        "tipoRedles": "9",
        "CodDoc": "96",
        # 'NroDocumento': ' ',
        # 'PaisOrigen': ' ',
        # 'Apellido': ' ',
        # 'Nombre': ' ',
        # 'Sexo': ' ',
        # 'FechaNacimiento': ' '
    }

    for column, value in static_info_dict.items():
        main_df[column] = value

    # Step 3: Set the column widths based on the provided SQL script
    column_widths = {
        "NroREDLES": 8,
        "tipoRedles": 1,
        "CodDoc": 2,
        "NroDocumento": 10,
        "PaisOrigen": 30,
        "Apellido": 50,
        "Nombre": 50,
        "Sexo": 1,
        "FechaNacimiento": 8,
        "calle": 40,
        "numero": 6,
        "piso": 5,
        "depto": 5,
        "manzana": 5,
        "sector": 5,
        "torre": 5,
        "TipodatoAdic": 2,
        "DatoAdicional": 20,
        "CodProvincia": 2,
        "CPostal": 8,
        "Localidad": 30,
        "calleFiscal": 40,
        "NroFiscal": 6,
        "PisoFiscal": 5,
        "DeptoFiscal": 5,
        "ManzanaFiscal": 5,
        "SectorFiscal": 5,
        "TorreFiscal": 5,
        "TipodatoAdicFiscal": 2,
        "DatoAdicionalFiscal": 20,
        "CodProvinciaFiscal": 2,
        "CPostalFiscal": 8,
        "LocalidadFiscal": 30,
        "CUIT_declarada": 11,
        "Fechainfo": 8,
        "Paq_0_NroLote": 4,
        "BLANCOS": 58,
        "UNLAM": 5,
        "Municipio": 30,
        "otro Municipio": 30,
        "Actividad": 10,
        "Descripcion actividad": 50,
    }
    log.write(f"Formateando archivo de salida")
    main_df["FechaNacimiento"] = pd.to_datetime(
        main_df["FechaNacimiento"], errors="coerce"
    )
    main_df["FechaNacimiento"] = main_df["FechaNacimiento"].dt.strftime("%Y%m%d")
    main_df["NroREDLES"] = [
        str(random.randint(100000, 999999)) for _ in range(len(main_df))
    ]
    current_date = datetime.today().strftime("%Y%m%d")
    main_df["Fechainfo"] = current_date
    # Step 3: Convert the dataframe to a fixed-width string
    fixed_width_text = ""

    for _, row in main_df.iterrows():
        line = ""
        for col, width in column_widths.items():
            value = str(row[col])
            line += value[:width].ljust(width)
        fixed_width_text += line + "\n"

    file = f"Paquete22LoteEX{current_date}.txt"
    # Step 4: Save the fixed-width text to a file
    with open(file, "w") as f:
        f.write(fixed_width_text)
    log.write(f"Encriptando...")
    encrypt_files(file,log)
    log.write(f"{success}Proceso terminado con exito.\n")
    return 0
