import pandas as pd
import tarfile

# from pandasql import sqldf
import timeit
from procs.formats import title, success, warning, error, item, subtitle,fnum
# Inicializamos la consola de rich
# console = Console(log_path=False)


def lectura(paquete, engine, backend,log,version):
    pd.options.future.infer_string = True
    
    log.write(f"Leyendo P30...")
    if version:
        from procs.DictsAndLists2x import lista, listaTCA,listaB00
    else:
        from procs.DictsAndLists1x import lista, listaTCA,listaB00
    tic = timeit.default_timer()
    # Abrimos el GZ en python para manosearlo por dentro.
    try:
        TarP3 = tarfile.open(paquete, "r:gz")
    except Exception as e:
        log.write(f"Hubo un error leyendo el archivo de vuelta:{e}.")
        return 0
    log.write(f"Encontrado: '{paquete}'")
    p30 = {}
    # Buscamos los archivos dentro del GZ.
    log.write("Leyendo vuelta SyNTIS.")
    log.write(f"Leyendo DATOS:")
    # print(name for name in TarP3.getnames())
    # Empezamos con el dict "lista"
    for file in lista:
        try:
            filename = [name for name in TarP3.getnames() if file["Nombre"] in name]
            # print(filename)
            txt = TarP3.extractfile(filename[0])
            # log.write(f"{file['Nombre']}")
            df = pd.read_csv(
                txt,  # type: ignore
                sep="\t",
                encoding="ansi",
                dtype=file["dtype"],
                names=file["dtype"].keys(),
                header=0,
                index_col=0,
                engine=engine,
                dtype_backend=backend,
            )
            # log.write(df.index.dtype)
            # # Para saber las columnas que suelen venir con nulls
            # columns_with_nulls = df.columns[df.isnull().any()]
            # print("Columnas con valores nulos:")
            # print(columns_with_nulls)
            p30[file["Nombre"]] = df
            log.write(f"{item}{file['Nombre']}")
        except IndexError as E:
            log.write(f"{error}{file['Nombre']}")
        except pd.errors.ParserError as E:
            if file['Nombre']=='B00':
                df = pd.read_csv(
                    txt,  # type: ignore
                    sep="\t",
                    encoding="ansi",
                    dtype=listaB00["dtype"],
                    names=listaB00["dtype"].keys(),
                    header=0,
                    index_col=0,
                    engine=engine,
                    dtype_backend=backend,
                )
            # # Para saber las columnas que suelen venir con nulls
            # columns_with_nulls = df.columns[df.isnull().any()]
            # print("Columnas con valores nulos:")
            # print(columns_with_nulls)
            p30[file["Nombre"]] = df
            log.write(f"{item}{file['Nombre']}")
    log.write(f"\n")

    # Continuamos con el dict "listaTCA" 
    log.write(f"Leyendo CODIGOS:")
    for file in listaTCA:
        try:
            filename = [name for name in TarP3.getnames() if file["Nombre"] in name]
            txt = TarP3.extractfile(filename[0])
            df = pd.read_csv(
                txt,  # type: ignore
                sep="\t",
                encoding="ansi",
                dtype=file["dtype"],
                names=file["dtype"].keys(),
                skiprows=1,
                engine=engine,
                dtype_backend=backend,
            )
            df.set_index(df.columns[0], inplace=True)
            log.write(f"{item}{file['Nombre']}")
            df.insert(loc=0, column="tabla", value=file["Nombre"])
            p30[file["Nombre"]] = df
        except IndexError as E:
            log.write(f"{error}{file['Nombre']}")
            continue
    log.write("\n")
    log.write(f"{item}HECHO en {tic - timeit.default_timer()}\n")
    # Cerramos el GZ para que no haya error al moverlo.
    TarP3.close()
    return p30
