import glob
import gnupg
import os
import shutil
import glob
import tarfile
import zipfile
from procs.formats import title,success,warning,error,item

def runEncrypt(log):
    log.write(f"{title}ENCRIPTADOR")
    paquetes2 = (
        glob.glob("*Paquete2*.txt")
        + glob.glob("*Hijos*.txt")
        + glob.glob("*Efectores*.txt")
    )
    if len(paquetes2)==0:
        log.write(f"{warning}No se encontraron paquetes para encriptar.\n")
        return 0
    log.write("Paquetes encontrados:")
    log.write(paquetes2)
    for file in paquetes2:
        log.write(f"Encriptando: {item}{file}")
        encrypt_files(file,log)
    log.write(f"{success}Paquetes encriptados con exito!\n")

def encrypt_files(file,log):
    gpg = gnupg.GPG(options={"--allow-weak-key-signatures": None})
    with open(file, "rb") as f:
        status = gpg.encrypt_file(
            f,
            recipients=["bases@sintys.gov.ar", "emore@desarrollosocial.gob.ar"],
            output=f"out/{file}.gpg",
        )
    if status.ok:
        log.write(f"{success}OK")
        shutil.move(file, f"in/{file}")
    else:
        log.write(f"{error}{status.stderr}")

def runDecrypt(log):
    log.write(f"{title}DESENCRIPTADOR")
    paquetes2 = glob.glob("*.pgp")
    if len(paquetes2)==0:
        log.write(f"{warning}No se encontraron paquetes para desencriptar.\n")
        return 0
    log.write("Paquetes encontrados:")
    log.write(paquetes2)
    file_extensions = [".txt", ".csv"]
    for file in paquetes2:
        log.write(f"Desencriptando: {item}{file}")
        tar = os.path.splitext(file)[0]
        # log.write(tar)
        decrypt_file(file,log)
        # Extract the files from the source archive to the temporary folder
        with tarfile.open(f"out/{tar}", "r:gz") as tar:
            # Get a list of all the members (files/folders) in the tar file
            members = tar.getmembers()

            # Create a new zip file to store the extracted archives
            with zipfile.ZipFile(
                f"out/{file}_resultado.zip", "w", compression=zipfile.ZIP_DEFLATED
            ) as zip:
                # Loop through all members in the tar file
                for member in members:
                    # Check if the member is a file and located in the desired subfolder
                    if member.isfile() and "expediente/resultado" in member.name:
                        # Extract the file to a temporary location
                        tar.extract(member, path="temp/")

                        # Add the extracted file to the zip file without the subfolder structure
                        zip.write(
                            os.path.join("temp", member.name),
                            arcname=os.path.basename(member.name),
                        )

                        # Delete the extracted file from the temporary location
                        os.remove(os.path.join("temp", member.name))
                        shutil.rmtree("temp/")
    log.write(f"{success}Paquetes desencriptados con exito!\n")

def decrypt_file(file,log):
    gpg = gnupg.GPG()
    filename = os.path.splitext(file)[0]
    with open(file, "rb") as f:
        status = gpg.decrypt_file(f, passphrase="Eze2kftw!", output=f"out/{filename}")

    if status.ok:
        log.write(f"{success}OK")
        shutil.move(file, f"in/{filename}")
    else:
        log.write(f"{error}{status.stderr}")
