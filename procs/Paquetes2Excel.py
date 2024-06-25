from io import StringIO
import pandas as pd
import glob
import shutil
from procs.formats import title, success, warning, error, item, subtitle, fnum


def p02xlsx(log):
    log.write(f"{title}F1252 a EXCEL")

    file_name = glob.glob("F01252.cuit.30707046399*.txt")
    if len(file_name) == 0:
        log.write(f"{warning}No se encontro archivo que procesar.\n")
        return 0
    # dicts
    dict02 = {
        "TipoDeRegistro": 2,
        "Id MDS (Clave REDLES)": 15,
        "Tipo Documento": 2,
        "Nº Documento": 10,
        "Sexo": 1,
        "Fecha de Nacimiento": 8,
        "Apellido": 50,
        "Nombre": 50,
        "Código de País de Origen": 3,
        "País de Origen": 30,
        "Código de Actividad": 6,
        "Domicilio Fiscal - Calle": 40,
        "Domicilio Fiscal - Número": 6,
        "Domicilio Fiscal - Piso": 5,
        "Domicilio Fiscal - Departamento": 5,
        "Domicilio Fiscal - Manzana": 5,
        "Domicilio Fiscal - Sector": 5,
        "Domicilio Fiscal - Torre": 5,
        "Domicilio Fiscal - Tipo Dato Adicional": 2,
        "Domicilio Fiscal - Dato Adicional": 20,
        "Domicilio Fiscal - Código de Provincia": 2,
        "Domicilio Fiscal - Código Postal": 8,
        "Domicilio Fiscal - Localidad": 15,
        "Coincide Domicilio Fiscal con Legal": 1,
        "Domicilio Legal - Calle": 40,
        "Domicilio Legal - Número": 6,
        "Domicilio Legal - Piso": 5,
        "Domicilio Legal - Departamento": 5,
        "Domicilio Legal - Manzana": 5,
        "Domicilio Legal - Sector": 5,
        "Domicilio Legal - Torre": 5,
        "Domicilio Legal - Tipo Dato Adicional": 2,
        "Domicilio Legal - Dato Adicional": 20,
        "Domicilio Legal - Código de Provincia": 2,
        "Domicilio Legal - Código Postal": 8,
        "Domicilio Legal - Localidad": 15,
        "Vencimiento del CERMI": 8,
        "CUIT; CUIL o CDI": 11,
        "Tipo Residencia": 1,
        "Email": 60,
        "Tipo de mail": 2,
    }
    with open(file_name[0], mode="r", encoding="ANSI") as f:
        content = f.read()
    # convierto el las variables en DF
    df = pd.read_fwf(
        StringIO(content),
        widths=dict02.values(),
        names=dict02.keys(),
    )
    # preparamos el excel
    archivo = f"out/Paquete0.xlsx"
    writer = pd.ExcelWriter(
        archivo, engine="openpyxl"
    )  # pylint: disable=abstract-class-instantiated

    # Anexamos paginar por pagina en el mismo excel
    df.to_excel(writer, sheet_name="1252 envio", engine="openpyxl")

    # generamos el excel
    writer.close()

    # Archivamos la copia en la carpeta del lote correspondiente
    shutil.move(file_name[0], f"in/{file_name[0]}")
    log.write(f"{success}{archivo} exitosamente creado.\n")


def p12xlsx(log):
    log.write(f"{title}F1252v a EXCEL")

    file_name = glob.glob("Lote_*_AFIP_MDS_F01252.*.txt")
    if len(file_name) == 0:
        log.write(f"{warning}No se encontro archivo que procesar.\n")
        return 0
    nameslist = [
        "Numero de lote",
        "Id MDS (Clave REDLES)",
        "CUIT",
        "Condicion Art. 33",
        "Empleador  Monto total de la nomina",
        "Empleador  Periodo",
        "DependiZente",
        "CUIT Sociedad que compone",
        "CUIT Sociedad que compone - Relacion",
        "CUIT Sociedad que compone - Cargo",
        "CUIT Sociedad que compone - Desde",
        "CUIT Sociedad que compone - Estado",
        "CUIT Asociado del Efector",
        "CUIT Asociado - Desde",
        "Error",
    ]
    df = pd.read_csv(file_name[0], delimiter=";", names=nameslist)
    df.to_excel(r"out/Paquete1.xlsx", index=False, engine="openpyxl")
    shutil.move(file_name[0], f"in/{file_name[0]}")
    log.write(f"{success}Paquete1.xlsx exitosamente creado.\n")


def p52xlsx(log):
    log.write(f"{title}F1253v a EXCEL")
    file_name = glob.glob("Cuitificacion Efectores - Lote nro*")
    if len(file_name) == 0:
        log.write(f"{warning}No se encontro archivo que procesar.\n")
        return 0
    with open(file_name[0]) as f:
        lines = f.readlines()

    # listas
    reg02 = []
    reg03 = []
    reg04 = []
    reg05 = []
    # dicts
    dict02 = {
        "TipoDeRegistro": 2,
        "CUIT": 11,
        "Estado del CUIT": 1,
        "Caracterizacion": 3,
        "Caracterizacion - Fecha": 8,
        "Categoria - Impuesto": 4,
        "Estado de la Categoria": 2,
        "Categoria - Periodo": 6,
        "C.U.R. Calculado": 12,
        "CUIT Sociedad que compone": 11,
        "CUIT Sociedad que compone - Relacion": 2,
        "CUIT Sociedad que compone - Cargo": 2,
        "CUIT Sociedad que compone - Desde": 8,
        "CUIT Sociedad que compone - Estado": 1,
        "CUIT Asociado del Efector": 11,
        "CUIT Asociado - Desde": 8,
        "CUIT Asociado - Estado": 0,
        # "Reg":0,
        "Codigo de error": 2,
        "Descripcion Error": 50,
    }
    dict03 = {
        "TipoDeRegistro": 2,
        "CUIT": 11,
        "Categoria de Pago": 4,
        "Periodo Categoria": 6,
    }
    dict04 = {
        "TipoDeRegistro": 2,
        "CUIT Cooperativa a Caracterizar": 11,
        "Fecha de Inicio de Caracterizacion": 8,
        "Reg": 1,
        "Codigo de error": 2,
        "Descripcion Error": 30,
    }
    dict05 = {
        "TipoDeRegistro": 2,
        "CUIT Cooperativa": 11,
        "CUIT Efector": 11,
        "Fecha": 8,
        "Tipo de Movimiento": 1,
        "Reg": 0,
        "Código de error": 2,
        "Descripcion Error": 64,
    }

    # separo las lineas por reg
    for ln in lines:
        if ln.startswith("02"):
            X_ln = ln[0:]
            reg02.append(X_ln)
        if ln.startswith("03"):
            X_ln = ln[0:]
            reg03.append(X_ln)
        if ln.startswith("04"):
            X_ln = ln[0:]
            reg04.append(X_ln)
        if ln.startswith("05"):
            X_ln = ln[0:]
            reg05.append(X_ln)

    # convierto la listas en string
    reg02f = "".join(str(x) for x in reg02)
    reg03f = "".join(str(x) for x in reg03)
    reg04f = "".join(str(x) for x in reg04)
    reg05f = "".join(str(x) for x in reg05)

    # convierto el las variables en DF
    df02 = pd.read_fwf(
        StringIO(reg02f),
        widths=dict02.values(),
        names=dict02.keys(),
    )
    df03 = pd.read_fwf(
        StringIO(reg03f),
        widths=dict03.values(),
        names=dict03.keys(),
    )
    df04 = pd.read_fwf(
        StringIO(reg04f),
        widths=dict04.values(),
        names=dict04.keys(),
    )
    df05 = pd.read_fwf(
        StringIO(reg05f),
        widths=dict05.values(),
        names=dict05.keys(),
    )

    # preparamos el excel
    archivo = f"out/Paquete5.xlsx"
    writer = pd.ExcelWriter(
        archivo, engine="openpyxl"
    )  # pylint: disable=abstract-class-instantiated

    # Anexamos paginar por pagina en el mismo excel
    df02.to_excel(writer, sheet_name="Info altas", engine="openpyxl")
    df03.to_excel(writer, sheet_name="Categorizados", engine="openpyxl")
    df04.to_excel(writer, sheet_name="Alta coop", engine="openpyxl")
    df05.to_excel(writer, sheet_name="Alta asoc-coop", engine="openpyxl")

    # generamos el excel
    writer.close()

    # Archivamos la copia en la carpeta del lote correspondiente
    shutil.move(file_name[0], f"in/{file_name[0]}")
    log.write(f"{success}{archivo} exitosamente creado.\n")


def p72xlsx(log):
    log.write(f"{title}F1257 a EXCEL")

    file_name = glob.glob("F01257*.txt")
    if len(file_name) == 0:
        log.write(f"{warning}No se encontro archivo que procesar.\n")
        return 0
    fwidths = [
        2,
        160,
        11,
        11,
        5,
        4,
        8,
        40,
        6,
        5,
        5,
        5,
        5,
        5,
        2,
        20,
        2,
        8,
        60,
        1,
        40,
        6,
        5,
        5,
        5,
        5,
        5,
        2,
        20,
        2,
        8,
        60,
        60,
        2,
        3,
        1,
        4,
        15,
        3,
    ]
    with open(file_name[0], mode="r", encoding="ANSI") as f:
        content = f.read()
    df = pd.read_fwf(
        StringIO(content),
        widths=fwidths,
        names=[
            "Tipo Registro",
            "Denominacion",
            "CUIT A.R.",
            "Nro Clave Proyecto",
            "Resolucion - Numero",
            "Resolucion - Ano",
            "Resolucion - Fecha de emision",
            "Domicilio Fiscal - Calle",
            "Domicilio Fiscal - Numero",
            "Domicilio Fiscal - Piso",
            "Domicilio Fiscal - Departamento",
            "Domicilio Fiscal - Manzana",
            "Domicilio Fiscal - Sector",
            "Domicilio Fiscal - Torre",
            "Domicilio Fiscal - Tipo Dato Adicional",
            "Domicilio Fiscal - Dato Adicional",
            "Domicilio Fiscal - Codigo de Provincia",
            "Domicilio Fiscal - Codigo Postal",
            "Domicilio Fiscal - Localidad",
            "Coincide Domicilio Fiscal con Legal",
            "Domicilio Legal - Calle",
            "Domicilio Legal - Numero",
            "Domicilio Legal - Piso",
            "Domicilio Legal - Departamento",
            "Domicilio Legal - Manzana",
            "Domicilio Legal - Sector",
            "Domicilio Legal - Torre",
            "Domicilio Legal - Tipo Dato Adicional",
            "Domicilio Legal - Dato Adicional",
            "Domicilio Legal - Codigo de Provincia",
            "Domicilio Legal - Codigo Postal",
            "Domicilio Legal - Localidad",
            "EMail - Direccion",
            "EMail - Tipo",
            "Telefono - Tipo Telefono",
            "Tipo Linea Telefonica",
            "Telefono - Codigo de Area",
            "Telefono - Numero",
            "Telefono - Compania",
        ],
    )

    df.to_excel(r"out/p7.xlsx", index=False, engine="openpyxl")
    shutil.move(file_name[0], f"in/{file_name[0]}")
    log.write(f"{success}p7.xlsx exitosamente creado.")


def p82xlsx(log):
    log.write(f"{title}F1258 a EXCEL")
    file_name = glob.glob("*F1258*")
    if len(file_name) == 0:
        log.write(f"{warning}No se encontro archivo que procesar.\n")
        return 0
    with open(file_name[0]) as f:
        lines = f.readlines()

    # listas
    reg02 = []
    reg03 = []
    # dicts
    dict02 = {
        "TipoDeRegistro": 2,
        "Nro Redles": 11,
        "CUIT": 11,
        "Caracterizacion": 2,
        "Fecha nueva vigencia": 6,
    }
    dict03 = {
        "TipoDeRegistro": 2,
        "Nro Redles": 11,
        "CUIT": 11,
        "Fecha de baja": 6,
    }

    # separo las lineas por reg
    for ln in lines:
        if ln.startswith("02"):
            X_ln = ln[0:]
            reg02.append(X_ln)
        if ln.startswith("03"):
            X_ln = ln[0:]
            reg03.append(X_ln)

    # convierto la listas en string
    reg02f = "".join(str(x) for x in reg02)
    reg03f = "".join(str(x) for x in reg03)

    # convierto el las variables en DF
    df02 = pd.read_fwf(
        StringIO(reg02f), widths=dict02.values(), names=dict02.keys(), dtype=str
    )
    df03 = pd.read_fwf(
        StringIO(reg03f), widths=dict03.values(), names=dict03.keys(), dtype=str
    )

    # preparamos el excel
    archivo = f"out/Paquete8.xlsx"
    writer = pd.ExcelWriter(
        archivo, engine="openpyxl"
    )  # pylint: disable=abstract-class-instantiated

    # Anexamos paginar por pagina en el mismo excel
    df02.to_excel(writer, sheet_name="Modificaciones", engine="openpyxl")
    df03.to_excel(writer, sheet_name="Bajas", engine="openpyxl")

    # generamos el excel
    writer.close()

    # Archivamos la copia en la carpeta del lote correspondiente
    shutil.copy(file_name[0], f"in/{file_name[0]}")
    log.write(f"{success}p8.xlsx exitosamente creado.\n")


def somoso2xlsx(log):
    log.write(f"{title}SOMOSO a EXCEL")

    file_name = glob.glob("SOMOSO_*")
    if len(file_name) == 0:
        log.write(f"{warning}No se encontro archivo que procesar.\n")
        return 0
    namesList2 = [
        "IdSolicitud",
        "IdTipoSolicitud",
        "CUIL",
        "CUILViejo",
        "apeYnom",
        "Apellidos",
        "Nombres",
        "FechaNacimiento",
        "IdPaisNacimiento",
        "Sexo",
        "Edad",
        "Telefono",
        "Email",
        "FechaUltAct",
        "Dependencia",
        "IdPrograma",
        "IdTipoEfector",
        "NombreAgrupamiento",
        "Matricula",
        "IdActividad",
        "NumeroRenaf",
        "IdCentroEducativo",
        "IdNivelEducativo",
        "NivelFinalizado",
        "UltimoAnioAprobado",
        "IdCoberturaSalud",
        "IdAccesoSalud",
        "IdDificultadSalud",
        "IdObraSocial",
        "IdTrabajoSemanaAnterior",
        "TrabajoInformalSemanaAnterior",
        "BuscoTrabajoUltimos30Dias",
        "IdTiempoBuscaTrabajo",
        "TrabajoAlgunaVez",
        "IdTrabajoInformal",
        "NombreTrabajoInformal",
        "IdIngresosEfector",
        "Ingresos",
        "ComparteViviendaGrupoFamiliar",
        "IdTipoVivienda",
        "TipoViviendaOtro",
        "IdMaterialPisoVivienda",
        "IdMaterialTechoVivienda",
        "AmbientesVivienda",
        "IdAguaProvieneVivienda",
        "IdAguaLlegaVivienda",
        "IdBanioVivienda",
        "IdDesagueVivienda",
        "ZonaInundableVivienda",
        "BasuralesVivienda",
        "AlumbradoPublicoVivienda",
        "PavimentoVivienda",
        "RecoleccionResiduosVivienda",
        "TransportePublicoVivienda",
        "IdProvincia",
        "Provincia",
        "domLocalidad",
        "domCalle",
        "domCalleAltura",
        "domPiso",
        "domDto",
        "domMunicipio",
        "domCodigoPostal",
        "IdMotivoRenuncia",
        "FechaFallecimiento",
        "MotivoOtro",
        "ADH_CUIL",
        "ADH_apeyNom",
        "ADH_Apellidos",
        "ADH_Nombres",
        "ADH_AdhiereObraSocial",
        "ADH_DatosAdp",
        "ADH_FechaNacimiento",
        "ADH_Sexo",
        "ADH_Edad",
        "ADH_IdCentroEducativo",
        "ADH_IdNivelEducativo",
        "ADH_NivelFinalizado",
        "ADH_ultimoAnioAprobado",
        "ADH_IngresoUltimos30Dias",
        "ADH_Ingresos",
        "ADH_IdParentesco",
        "VersionModeloDatos",
        "TelefonoFijo",
        "TelefonoCelular",
        "IdGenero",
        "domDomTorre",
        "domDomBarrioParaje",
        "domManzana",
        "domDomCasa",
        "domDomDistritoDpto",
        "InicioActividades",
        "CantIntegrantes",
        "IdLugarActividad",
        "IdModalidadTrabajo",
        "IdMotivoInscripcion",
        "MotivoInscripcionOtros",
        "Discapacidad",
        "CursaEstudios",
    ]

    df = pd.read_csv(file_name[0], encoding="ANSI", delimiter="|", names=namesList2)
    df.to_excel(r"out/SOMOSO.xlsx", index=False, engine="openpyxl")
    shutil.copy(file_name[0], f"in/{file_name[0]}")
    log.write(f"{success}SOMOSO.xlsx exitosamente creado.\n")
