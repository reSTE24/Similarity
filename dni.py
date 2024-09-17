from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from processing import calcular_similitud

def buscar_datos_por_dni(dni):
    url = "https://eldni.com/pe/buscar-datos-por-dni"
    # Configurar opciones de Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Añadir un User-Agent aleatorio
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Configurar el servicio de ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Inicializar el navegador
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navegar a la URL
        driver.get(url)

        # Esperar a que el elemento del token esté presente
        wait = WebDriverWait(driver, 10)
        token_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="_token"]')))

        # Obtener el valor del token
        token = token_element.get_attribute('value')

        # Encontrar el campo de DNI y el botón de envío
        dni_input = driver.find_element(By.NAME, 'dni')
        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')

        # Introducir el DNI
        dni_input.send_keys(dni)

        # Hacer clic en el botón de envío
        submit_button.click()

        # Esperar a que aparezca el resultado
        result_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'samp.inline-block')))

        # Obtener el texto del resultado
        result = result_element.text

        return result
    except Exception as e:
        return f"Error al buscar datos: {str(e)}"
    finally:
        # Cerrar el navegador
        driver.quit()

def verificar_dni(df):
    df['Correcto'] = 0
    df['NOMBRERENIEC'] = ""
    umbral = 92
     # Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        dni = row['Nro. Documento']
        nombre =row["Nombre Completo"]
        
        # Obtener los datos de la función buscar_datos_por_dni
        datos_dni = buscar_datos_por_dni(dni)
        
        # Calcular la similitud
        similitud = calcular_similitud(nombre, datos_dni, 1)  # Asumiendo que '1' es algún parámetro relevante
        
        # Actualizar la columna 'Correcto' basándonos en la similitud
        if similitud >= umbral:
            df.at[index, 'Correcto'] = 1
        
        # Guardar los datos obtenidos en 'NOMBRERENIEC'
        df.at[index, 'NOMBRERENIEC'] = datos_dni
    return df


# Ejemplo de uso

# dni = "20052783"
# resultado = buscar_datos_por_dni(dni)
# print(f"El resultado de la búsqueda es: {resultado}")