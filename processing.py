import pandas as pd
import unicodedata
import jellyfish
import streamlit as st
from rapidfuzz import fuzz
from helpers import transformar_cadena
from joblib import Parallel, delayed

def calcular_puntuacion(fila):
    puntuacion = 0
    if fila['Validado por el RENIEC'] == 1:
        puntuacion += 8
    if pd.notnull(fila['Integrante del Hogar']):
        puntuacion += 4
    if pd.notnull(fila['Nro. Documento']):
        puntuacion += 2
    no_vacios = fila.count() - 1
    total_columnas = len(fila) - 1
    puntuacion += no_vacios / total_columnas
    return puntuacion

def seleccionar_columana(nombre,columnas):
    # Calcula las similitudes y almacena en una lista de tuplas (nombre_columna, similitud)
    similitudes = [(nombre_columna, fuzz.token_sort_ratio(nombre_columna, nombre)) for nombre_columna in columnas]
    
    # Encuentra la tupla con la similitud máxima
    nombre_columna_max_similitud, _ = max(similitudes, key=lambda x: x[1])

    return nombre_columna_max_similitud

def encontrar_mejor_coincidencia(personas_df, nombre, itera, umbral):

    nombre = transformar_cadena(nombre)

    def custom_similarity(palabra, x_palabra):
        if len(palabra) <= 3 and len(x_palabra) <= 3:
            return fuzz.partial_token_sort_ratio(palabra, x_palabra)
        else:
            return 100 * jellyfish.jaro_winkler_similarity(palabra, x_palabra)
    

    def calcular_similitud(nombreFuente):
        # nombreFuente
        nombreFuente = transformar_cadena(nombreFuente)
        nombreF_palabras = nombreFuente.split()
        nombre_palabras = nombre.split()
        # palabra_similitudes = [max([100 * jellyfish.jaro_winkler_similarity(palabra, x_palabra) for x_palabra in nombreF_palabras]) for palabra in nombre_palabras]
        palabra_similitudes = [
        max([custom_similarity(palabra, x_palabra) for x_palabra in nombreF_palabras]) 
        for palabra in nombre_palabras
        ]
        palabra_similitudes.sort(reverse=True)
        # print(palabra_similitudes)
        min_len = max(3, min(len(nombre_palabras), len(nombreF_palabras)))
        palabra_similitudes = palabra_similitudes[:min_len]
        promedio_palabra_similitud = sum(palabra_similitudes) / len(palabra_similitudes)
        errores_ortograficos1 = 100 * jellyfish.jaro_winkler_similarity(nombre, nombreFuente)
        if promedio_palabra_similitud - errores_ortograficos1 > 7:
            # errores_ortograficos1 = max(fuzz.token_sort_ratio(nombre, nombreFuente),fuzz.partial_token_sort_ratio(nombre, nombreFuente))
            errores_ortograficos1 = max(errores_ortograficos1,fuzz.token_sort_ratio(nombre, nombreFuente),fuzz.partial_token_sort_ratio(nombre, nombreFuente))
        penalizacion = (100 - errores_ortograficos1) / 4
        puntuacion_final = promedio_palabra_similitud - penalizacion
        return puntuacion_final
    # return calcular_similitud('Aliaga Marin Pilar Rosa')
    personas_df['similitud'] = Parallel(n_jobs=-1)(delayed(calcular_similitud)(nombre) for nombre in personas_df['Nombre Completo'])
    # personas_df['similitud'] = personas_df['Nombre Completo'].apply(calcular_similitud)
    personas_coincidentes = personas_df[personas_df['similitud'] >= umbral].sort_values(by='similitud', ascending=False)

    if not personas_coincidentes.empty and itera < 2:
        new_umbral=personas_coincidentes.iloc[0]['similitud']
        if new_umbral <90:
            new_umbral=90
        new_umbral=new_umbral-new_umbral*7.5/100
        new_personas_coincidentes = personas_coincidentes[personas_coincidentes['similitud'] >=new_umbral].sort_values(by='similitud', ascending=False)
        new_personas_coincidentes['tamaño'] = new_personas_coincidentes['Nombre Completo'].apply(len)
        sorted_personas = new_personas_coincidentes.sort_values(by='tamaño', ascending=False)
        if not sorted_personas.empty  and sorted_personas.iloc[0]['tamaño'] > len(nombre):
            personas_coincidentes = encontrar_mejor_coincidencia(personas_df, sorted_personas.iloc[0]['Nombre Completo'], 2, umbral + 2.5)
        else:
            personas_coincidentes = personas_df[personas_df['similitud'] >=umbral+2.5].sort_values(by='similitud', ascending=False)

    return personas_coincidentes

def seleccionar_mejor_opcion(df, nombre,similitud):
    coincidencias_cache = {}
    if nombre in coincidencias_cache:
        return coincidencias_cache[nombre]

    coincidencia = encontrar_mejor_coincidencia(df, nombre, 1, umbral=similitud)
    if coincidencia.empty:
        resultado = {"ID": None, "Nro. Documento": None, "Nombre Elegido": nombre, "Cantidad de repetidos": 0, "Resultado": "Nuevo"}
    else:
        coincidencia = coincidencia.sort_values(by='puntuacion', ascending=False)
        mejor_fila =  coincidencia.iloc[0]
        segunda_mejor_fila = coincidencia.iloc[1] if len(coincidencia) > 1 else None

        if segunda_mejor_fila is not None:
            if mejor_fila['puntuacion'] >= 8 and segunda_mejor_fila['puntuacion'] >= 8:
                resultado = {"ID": None, "Nro. Documento": None, "Nombre Elegido": nombre, "Cantidad de repetidos": len(coincidencia), "Resultado": "Muchos válidos por RENIEC"}
                coincidencias_cache[nombre] = resultado
                return resultado
            elif mejor_fila['puntuacion'] >= 4 and segunda_mejor_fila['puntuacion'] >= 4:
                resultado1 = "Muchos con Familia"
            elif mejor_fila['puntuacion'] >= 2 and segunda_mejor_fila['puntuacion'] >= 2:
                resultado1 = "Muchos con DNI"
            elif abs(mejor_fila['puntuacion'] - segunda_mejor_fila['puntuacion']) < 0.10:
                resultado = {"ID": None, "Nro. Documento": None, "Nombre Elegido": nombre, "Cantidad de repetidos": len(coincidencia), "Resultado": "Muy poca Diferencia"}
                coincidencias_cache[nombre] = resultado
                return resultado
            else:
                resultado1 = "Por menos vacíos"
        else:
            resultado1 = "Bien"

        resultado = {
            "ID": mejor_fila['ID'],
            "Nro. Documento": mejor_fila['Nro. Documento'],
            "Nombre Elegido": mejor_fila['Nombre Completo'],
            "Cantidad de repetidos": len(coincidencia),
            "Resultado": resultado1
        }

    coincidencias_cache[nombre] = resultado
    return resultado

def grabar(df_resultado, quejas_df):
    mes_df = pd.concat([df_resultado, quejas_df], axis=1)
    csv = mes_df.to_csv(index=False)

    st.download_button(label="Descargar datos como CSV", data=csv, file_name='nombreArchivoQueja.csv', mime='text/csv')
