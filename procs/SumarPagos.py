import pandas as pd
import glob
import locale
from io import StringIO
import re
from procs.formats import title, success, item, subtitle, fnum

def log_and_clip(log, clip, message):
    log.write(message)
    return clip + message + '\n'

def format_currency(value):
    return locale.currency(value, grouping=True)

def mostrar_suma(log, datos, clip):
    locale.setlocale(locale.LC_ALL, "es_AR")
    entries = {
        "PAGADO POR CUIT": format_currency(datos['monto']),
        "PAGADO TOTAL": format_currency(datos['subsidioTotal']),
        "TITULARES": f"{datos['cantTitulares']:n}",
        "TITULARES PAGADO": format_currency(datos['subsidioTitulares']),
        "ADH": f"{datos['cantAdh']:n}",
        "ADH PAGADO": format_currency(datos['subsidioAdh']),
        "ADH + TITULARES": format_currency(datos['subsidioComparadoTotal']),
        "META": f"{datos['meta']:n}"
    }
    for key, value in entries.items():
        message = f"{key}: {value}"
        clip = log_and_clip(log, clip, message)
    clip += '\n'
    return clip

def procesar_archivo(log, clip, df, config):
    title, monto_col, adh_col = config["title"], config["monto_col"], config["adh_col"]
    clip = log_and_clip(log, clip, f"{subtitle}{title}:")
    clip = log_and_clip(log, clip, f"Procesando archivo: {item}{config['file']}")

    datos = {
        'monto': df[monto_col].min(),
        'subsidioTotal': df[monto_col].sum(),
        'cantTitulares': df.shape[0],
        'cantAdh': df[adh_col].sum() if adh_col else 0,
        'subsidioTitulares': lambda d: d['cantTitulares'] * d['monto'],
        'subsidioAdh': lambda d: d['subsidioTotal'] - d['subsidioTitulares'],
        'subsidioComparadoTotal': lambda d: d['subsidioTitulares'] + d['subsidioAdh'],
        'meta': lambda d: d['cantAdh'] + d['cantTitulares']
    }

    for key in ['subsidioTitulares', 'subsidioAdh', 'subsidioComparadoTotal', 'meta']:
        datos[key] = datos[key](datos)
    
    if "periodo" in config:
        periodo_str = ', '.join(config['periodo'])
        clip = log_and_clip(log, clip, f"Periodo de pagos: {periodo_str}")
    
    return mostrar_suma(log, datos, clip)

def leer_archivo(file, encoding="ANSI", delimiter="|", decimal=",", colspecs=None, names=None, skiprows=1, skipfooter=1):
    if colspecs:
        with open(file, mode="r", encoding=encoding) as f:
            content = f.read()
        return pd.read_fwf(
            StringIO(content),
            colspecs=colspecs,
            names=names,
            dtype=str,
            skiprows=skiprows,
            skipfooter=skipfooter
        )
    return pd.read_csv(file, encoding=encoding, delimiter=delimiter, decimal=decimal)

def run(log):
    log.write(f"{title}SUMA ARCHIVOS DE PAGO")
    log.write("Buscando archivos de pago...")
    clip = ''
    files_config = {
        "mono_pt*": {
            "func": procesar_archivo,
            "config": {"title": "POTENCIAR TRABAJO", "monto_col": "importe", "adh_col": "adherentes"}
        },
        "mono_co*": {
            "func": procesar_archivo,
            "config": {"title": "CONAMI", "monto_col": "importe", "adh_col": "adherentes"}
        },
        "EFECTORES_SALIDA_*.txt": {
            "func": procesar_archivo,
            "config": {
                "title": "SUBSIDIO GENERAL",
                "monto_col": "importe",
                "adh_col": "adherentes",
                "colspecs": ((0, 99), (100, 111), (111, 117), (126, 132), (140, 147), (164, 168)),
                "names": ("etc", "cuit", "periodo", "OS", "importe", "adherentes")
            }
        },
        "Efectores_*.csv": {
            "func": procesar_archivo,
            "config": {"title": "OBRAS SOCIALES", "monto_col": "SUB", "adh_col": "ADHERENTES"}
        },
    }

    for pattern, settings in files_config.items():
        for file in glob.glob(pattern):
            config = settings["config"]
            config["file"] = file
            if "colspecs" in config:
                df = leer_archivo(file, colspecs=config["colspecs"], names=config["names"])
                df["importe"] = df["importe"].apply(lambda x: float(x[:-2] + "." + x[-2:]))
                df["adherentes"] = df["adherentes"].astype(int)
                config["periodo"] = df["periodo"].unique()
            else:
                df = leer_archivo(file)
            clip = settings["func"](log, clip, df, config)

    result = re.sub(r'\[.*?\]', '', clip)
    log.app.copy_to_clipboard(result)
    log.write(f"{success}Resultados copiados al clipboard.\n")
    return 0
