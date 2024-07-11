import streamlit as st
import pandas as pd
from processing import (
    calcular_puntuacion,
    seleccionar_columana,
    encontrar_mejor_coincidencia,
    seleccionar_mejor_opcion,
    grabar
)
from helpers import transformar_cadena

# Navbar V2
st.sidebar.title("Navegación V2")
opcion_v2 = st.sidebar.radio("Ir a", ["Subir archivo y procesar quejas V2", 
                                      "Subir archivo y buscar coincidencias V2",
                                      "Comprobar quejas V2"])

if opcion_v2 == "Subir archivo y buscar coincidencias V2":
    st.title('Subir archivo CSV y buscar coincidencias V2')
    st.write('Sube un archivo CSV y ajusta la sensibilidad para buscar coincidencias.')

    # Parámetros y columnas del CSV
    id_col_personas = 'ID'
    dni_col = 'Nro. Documento'
    nombre_col_personas = 'Nombre Completo'
    
    uploaded_file = st.file_uploader("Elige un archivo CSV", type="csv")
    sensibilidad = st.slider('Sensibilidad', 0, 100, 90, 1)
    busqueda = st.text_input('Buscar...')

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        df['puntuacion'] = df.apply(calcular_puntuacion, axis=1)
        df = df[[id_col_personas, dni_col, 'puntuacion', nombre_col_personas]]
        df[nombre_col_personas] = df[nombre_col_personas].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.strip()

        if busqueda:
            resultados = encontrar_mejor_coincidencia(df, busqueda, 1, umbral=sensibilidad)
            st.write('Resultados de la búsqueda:')
            st.dataframe(resultados)
        else:
            st.write(f'Archivo cargado exitosamente, sensibilidad: {sensibilidad}%')

elif opcion_v2 == "Subir archivo y procesar quejas V2":
    st.title('Subir archivo CSV de personas y sus quejas y reclamos V2')
    st.write('Sube un archivo CSV de personas y un Excel de quejas y reclamos.')

    uploaded_file = st.file_uploader("Elige un archivo CSV", type="csv")
    quejas = st.file_uploader("Elige un archivo Hoja de cálculo", type="xlsx")

    if uploaded_file is not None and quejas is not None:
        df = pd.read_csv(uploaded_file)
        df['puntuacion'] = df.apply(calcular_puntuacion, axis=1)
        df = df[['ID', 'Nro. Documento', 'puntuacion', 'Nombre Completo']]
        df['Nombre Completo'] = df['Nombre Completo'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.strip()
        st.write('Archivo cargado exitosamente')
        
        quejas_df = pd.read_excel(quejas)
        nombre_col_quejas =   seleccionar_columana('Nombre Titular',quejas_df.columns)
        
        resultados = [seleccionar_mejor_opcion(df, nombre) for nombre in quejas_df[nombre_col_quejas]]
        df_resultados = pd.DataFrame(resultados)
        
        grabar(df_resultados, quejas_df)

elif opcion_v2 == "Comprobar quejas V2":
    st.title('Subir archivo CSV de personas y sus quejas y reclamos V2')
    st.write('Sube un archivo CSV de personas y un CSV de quejas y reclamos.')

    uploaded_file = st.file_uploader("Elige un archivo CSV", type="csv")
    quejas = st.file_uploader("Elige un archivo Hoja de cálculo", type="csv")

    if uploaded_file is not None and quejas is not None:
        df = pd.read_csv(uploaded_file)
        df['puntuacion'] = df.apply(calcular_puntuacion, axis=1)
        df = df[['ID', 'Nro. Documento', 'puntuacion', 'Nombre Completo']]
        st.write('Archivo cargado exitosamente')

        quejas_df = pd.read_csv(quejas)
        nombre_col_quejas = 'Personas'
        
        resultados = [seleccionar_mejor_opcion(df, nombre) for nombre in quejas_df[nombre_col_quejas]]
        df_resultados = pd.DataFrame(resultados)
        
        csv = df_resultados.to_csv(index=False)
        st.download_button(label="Descargar datos como CSV", data=csv, file_name='nombreArchivoQueja.csv', mime='text/csv')

# Guardar el código en un archivo llamado app.py y ejecutarlo con:
# streamlit run app.py
