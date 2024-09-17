# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# import time
# import random
# from processing import calcular_similitud

import requests
from bs4 import BeautifulSoup
import random
import time
from processing import calcular_similitud

def buscar_datos_por_dni(dni):
    url = "https://eldni.com/pe/buscar-datos-por-dni"
    
    # Lista de User-Agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents)
    }
    
    try:
        # Hacer una solicitud GET inicial para obtener el token CSRF
        session = requests.Session()
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer el token CSRF
        token = soup.select_one('input[name="_token"]')['value']
        
        # Preparar los datos para la solicitud POST
        data = {
            '_token': token,
            'dni': dni
        }
        
        # Hacer la solicitud POST
        response = session.post(url, headers=headers, data=data)
        
        # Parsear la respuesta
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer el resultado
        result_element = soup.select_one('samp.inline-block')
        if result_element:
            return result_element.text.strip()
        else:
            return "No se encontraron resultados"
    
    except Exception as e:
        return f"Error al buscar datos: {str(e)}"

def verificar_dni(df):
    df['Correcto'] = 0
    df['NOMBRERENIEC'] = ""
    umbral = 92
    
    for index, row in df.iterrows():
        dni = row['Nro. Documento']
        nombre = row["Nombre Completo"]
        
        # Obtener los datos de la función buscar_datos_por_dni
        datos_dni = buscar_datos_por_dni(dni)
        
        # Calcular la similitud
        similitud = calcular_similitud(nombre, datos_dni, 1)
        
        # Actualizar la columna 'Correcto' basándonos en la similitud
        if similitud >= umbral:
            df.at[index, 'Correcto'] = 1
        
        # Guardar los datos obtenidos en 'NOMBRERENIEC'
        df.at[index, 'NOMBRERENIEC'] = datos_dni
        
        # Añadir un pequeño retraso para evitar sobrecargar el servidor
        time.sleep(random.uniform(1, 3))
    
    return df


# Ejemplo de uso

# dni = "20052783"
# resultado = buscar_datos_por_dni(dni)
# print(f"El resultado de la búsqueda es: {resultado}")