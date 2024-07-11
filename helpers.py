import re
import unicodedata

def transformar_cadena(cadena):
    reglas = [
        (r'LL(?=[a-zA-Z]{2})', 'Y'),
        (r'QU(?=[a-zA-Z]{2})', 'K'),
        (r'll', 'y'),
        (r'i', 'y'),
        (r'v', 'b'),
        (r'j', 'h'),
        (r'qu', 'k')
    ]
    
    for patron, reemplazo in reglas:
        cadena = re.sub(patron, reemplazo, cadena)

    cadena = ' '.join(cadena.strip().split())
    cadena = cadena.upper()
    cadena = unicodedata.normalize('NFKD', cadena).encode('ascii', errors='ignore').decode('utf-8')
    return cadena
