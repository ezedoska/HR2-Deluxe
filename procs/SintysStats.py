from procs import Prov, Evaluar, SintysFile
from procs.DictsAndLists1x import lista

# from procs.DictsAndLists2x import lista
import pandas as pd
import timeit
from datetime import datetime
from procs.formats import title, success, warning, error, item, subtitle,fnum


def run(log,version,jubi,eval,datos):
    # Timear el proceso
    ticg = timeit.default_timer()
    # Inicializamos la consola de rich
    # console = Console(log_path=False)

    # Tiulo
    log.write(f"{title}SINTyS STATS")
    log.write(f"Pandas: V{pd.__version__}")
    log.write(f"{version=}")
    log.write(f"{jubi=}")
    log.write(f"{eval=}")
    log.write(f"{datos=}\n")

    if version:
        ver = 1
    else:
        ver = 0

    engine = ["c", "pyarrow", "python"]
    backend = ["numpy_nullable", "pyarrow"]


    # Leemos el p30.
    paquete30 = SintysFile.lectura("SINTYS.tar.gz", engine[ver], backend[ver],log,version)
    # paquete30 = P30.lectura("SINTYS.tar.gz", engine[ver])

    # Juntamos las variables para usar del dict.
    # Si por alguna razon no existe el dataframe, lo rellena de uno vacio pero con
    # las mismas columnas para evitar errores.
    # fmt: off
    # for k,v in paquete30:
    #     log.write(v.shape[0])
    
    log.write("Transformando y limpiando datos...")
    tic = timeit.default_timer()
    var = paquete30.get("B00", pd.DataFrame(columns=lista[0]["dtype"].keys())) # type: ignore
    dat = paquete30.get("DATOS", pd.DataFrame(columns=lista[1]["dtype"].keys())) # type: ignore
    bar = paquete30.get("EMBARCACIONES", pd.DataFrame(columns=lista[2]["dtype"].keys()))# type: ignore
    avi = paquete30.get("AERONAVES", pd.DataFrame(columns=lista[3]["dtype"].keys())) # type: ignore 
    dep = paquete30.get("EMPLEO_DEPENDIENTE", pd.DataFrame(columns=lista[4]["dtype"].keys())) # type: ignore
    ind = paquete30.get("EMPLEO_INDEPENDIENTE", pd.DataFrame(columns=lista[5]["dtype"].keys()))# type: ignore
    fal = paquete30.get("FALLECIDOS", pd.DataFrame(columns=lista[6]["dtype"].keys())) # type: ignore
    inm = paquete30.get("INMUEBLES", pd.DataFrame(columns=lista[7]["dtype"].keys()))# type: ignore
    jub = paquete30.get("JUBILACIONES_PENSIONES", pd.DataFrame(columns=lista[8]["dtype"].keys())) # type: ignore
    aut = paquete30.get("PADRON_AUTOMOTORES", pd.DataFrame(columns=lista[9]["dtype"].keys())) # type: ignore
    jur = paquete30.get("PERSONAS_JURIDICAS", pd.DataFrame(columns=lista[10]["dtype"].keys()))# type: ignore
    pnc = paquete30.get("PNC", pd.DataFrame(columns=lista[11]["dtype"].keys())) # type: ignore
    rub = paquete30.get("RUBPS", pd.DataFrame(columns=lista[12]["dtype"].keys()))# type: ignore
    asg = paquete30.get("ASIGNACIONES", pd.DataFrame(columns=lista[13]["dtype"].keys()))# type: ignore

    # Convertir la columna 'fnac' a tipo datetime
    dat['fnac'] = pd.to_datetime(dat['fnac'], format='%d/%m/%Y')
    
    # Arreglamos el sexo :cool:
    dat['sexo'].fillna('1', inplace=True)

    # Calcular la fecha actual
    fecha_actual = datetime.now()

    # Definir una función para determinar si es jubilable
    def es_jubilable(fecha_nacimiento, sexo):
        edad = (fecha_actual - fecha_nacimiento).days // 365  # Calcular edad en años
        if sexo == 2:  # Mujer (sexo = 2)
            if edad >= 60:
                return 'Si'
            else:
                return 'No'
        elif sexo == 1:  # Hombre (sexo = 1)
            if edad >= 65:
                return 'Si'
            else:
                return 'No'
        else:
            return 'No'  # Otros casos (sexo distinto de 1 o 2)

    # Aplicar la función para crear la columna 'jubilable?'
    dat['jubilable?'] = dat.apply(lambda row: es_jubilable(row['fnac'], row['sexo']), axis=1)
    log.write(f"{var.shape[0]=}")
    # Agregamos CUIT a cada df
    bar['cuit'] = dat['cuit']
    avi['cuit'] = dat['cuit']
    dep['cuit'] = dat['cuit']
    ind['cuit'] = dat['cuit']
    fal['cuit'] = dat['cuit']
    inm['cuit'] = dat['cuit']
    jub['cuit'] = dat['cuit']
    jub["ndoc"] = dat["ndoc"]
    aut['cuit'] = dat['cuit']
    jur['cuit'] = dat['cuit']
    pnc['cuit'] = dat['cuit']
    rub['cuit'] = dat['cuit']
    asg['cuit'] = dat['cuit']

    # Pasamos columnas a float
    jub['MONTO'] = jub['MONTO'].astype(float)
    dep['MONTO'] = dep['MONTO'].astype(float)

    # Entramos el Minimo VItal y Movil
    mvym = 190141.60

    # Agregamos la diferencia de dependiente y minimo vital y movil
    dep['diferencia mvym $'] = dep['MONTO'] - mvym
    jub['diferencia mvym $'] = jub['MONTO'] - mvym
    log.write(f"{item}HECHO en {tic - timeit.default_timer()}\n")

    # Stats
    # prov_stats = Prov.stats(dat, pnc, var, jub, dep, asg, fal, jur, rub)

    # Armamos excel de jubilados
    if jubi:
        log.write("Exportando Excel jubilados...")
        tic = timeit.default_timer()
        log.write(f"{jub.shape[0]=}")
        jub.to_excel("Jubilados.xlsx", engine="openpyxl")
        log.write(f"{item}HECHO en {tic - timeit.default_timer()}\n")

    # Armamos las tabs del excel y lo exportamos.
    if eval:
        # Evaluamos.
        eval_stats = Evaluar.stats(dat, jub, dep, jur, fal, aut, inm, mvym,log,)
        log.write("Exportando Excel evaluaciones...")
        tic = timeit.default_timer()
        writer = pd.ExcelWriter("Evaluacion_P30.xlsx", engine="openpyxl")
        # stats_prov.to_excel(writer, sheet_name="Stats globales")
        eval_stats[0].to_excel(writer, sheet_name="Efectores fuera del marco legal")  # type: ignore
        eval_stats[1].to_excel(writer, sheet_name="Detalle Muebles")  # type: ignore
        eval_stats[2].to_excel(writer, sheet_name="Detalle Inmuebles")  # type: ignore
        ev_dep = pd.merge(eval_stats[0], dep, left_index=True, right_index=True)
        ev_dep.to_excel(writer, sheet_name="Detalle Dependientes")  # type: ignore
        ev_ind = pd.merge(eval_stats[0], ind, left_index=True, right_index=True)
        ev_ind.to_excel(writer, sheet_name="Detalle Independientes")  # type: ignore
        ev_jub = pd.merge(eval_stats[0], jub, left_index=True, right_index=True)
        ev_jub.to_excel(writer, sheet_name="Detalle Jubilados")  # type: ignore
        log.write(f"{ev_dep.shape[0]=}")
        log.write(f"{ev_ind.shape[0]=}")
        log.write(f"{ev_jub.shape[0]=}")
        writer.close()
        log.write(f"{item}HECHO en {tic - timeit.default_timer()}\n")

    if datos:
        log.write("Exportando Excel datos...")
        if var.shape[0] < 1048575: 
            # Armamos un excel con todos los datos para su emjor lectura
            tic = timeit.default_timer()
            writerF = pd.ExcelWriter("Datos_P30.xlsx", engine="openpyxl")
            var.to_excel(writerF, sheet_name="varios")
            dat.to_excel(writerF, sheet_name="datos")
            bar.to_excel(writerF, sheet_name="barcos")
            avi.to_excel(writerF, sheet_name="aviones")
            dep.to_excel(writerF, sheet_name="dependientes")
            ind.to_excel(writerF, sheet_name="independientes")
            fal.to_excel(writerF, sheet_name="fallecidos")
            inm.to_excel(writerF, sheet_name="inmuebles")
            jub.to_excel(writerF, sheet_name="jubilados")
            aut.to_excel(writerF, sheet_name="automotores")
            jur.to_excel(writerF, sheet_name="juridicos")
            pnc.to_excel(writerF, sheet_name="pensiones no contrib")
            rub.to_excel(writerF, sheet_name="programas sociales")
            asg.to_excel(writerF, sheet_name="asignaciones familiares")
            log.write(f"{var.shape[0]=}")
            log.write(f"{dat.shape[0]=}")
            log.write(f"{bar.shape[0]=}")
            log.write(f"{avi.shape[0]=}")
            log.write(f"{dep.shape[0]=}")
            log.write(f"{ind.shape[0]=}")
            log.write(f"{fal.shape[0]=}")
            log.write(f"{inm.shape[0]=}")
            log.write(f"{jub.shape[0]=}")
            log.write(f"{aut.shape[0]=}")
            log.write(f"{jur.shape[0]=}")
            log.write(f"{pnc.shape[0]=}")
            log.write(f"{rub.shape[0]=}")
            log.write(f"{asg.shape[0]=}")
            writerF.close()
            log.write(f"{item}HECHO en {tic - timeit.default_timer()}\n")
        else:
            log.write(f"{warning}El archivo es muy grande para pasar a un excel.Cancelado.\n")

    # fmt: on
    log.write(f"{success}PROCESO COMPLETADO en {ticg - timeit.default_timer()}\n")

