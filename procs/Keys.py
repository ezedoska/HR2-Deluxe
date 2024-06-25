import subprocess
import gnupg
from procs.formats import title,success,warning,error,item
def run(log):
    """instalar python-gnupg, no gnupg a secas, y si existe, desinstalarlo"""
    log.write(f"{title}INSTALACION DE LLAVES SINTYS")
    log.write(f"{warning}Recordar instalar GNUP4WIN antes de correr esto.")
    log.write("Buscando llaves")
    
    keys = [
        "keys/sintys pub.asc",
        "keys/eze key.asc",
        "keys/eze key secret.asc",
        "keys/sintys pub.asc",
    ]
    passphrases = ["Eze2kftw!", "Eze2kftw!", "Eze2kftw!", "Eze2kftw!"]

    # Inicializa una instancia de GPG
    try:
        gpg = gnupg.GPG()
    except:
        gpg = gnupg.GPG(gnupghome=r'C:\Program Files (x86)\GnuPG')

    log.write("Importando llaves")
    for key_file, passphrase in zip(keys, passphrases):
        with open(key_file, 'rb') as f:
            imported_key = gpg.import_keys(f.read(), passphrase=passphrase)
            if imported_key.count:
                log.write(f"{item}Llave {key_file} importada con éxito.")
            elif gpg.list_keys():
                if imported_key.fingerprints[0] == gpg.list_keys()[0]['fingerprint']:
                    log.write(f"{warning}Llave {key_file} ya estaba instalada.")
                else:
                    log.write(f"{error}Error al importar la llave {key_file}.")
            else:
                log.write(f"{warning}Llave {key_file} ya estaba instalada.(?)")
    log.write("Instalando llaves")

    # Obtiene las huellas digitales de las llaves importadas
    fingerprints = [key['fingerprint'] for key in gpg.list_keys()]

    log.write("Firmando llaves")
    # Firma las llaves con confianza máxima
    for fingerprint in fingerprints:
        gpg.trust_keys(fingerprint, "TRUST_ULTIMATE")

    log.write(f"{success}Llaves de encriptación instaladas.\n")