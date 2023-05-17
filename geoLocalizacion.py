from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_folium import st_folium
from datetime import datetime
from st_aggrid import AgGrid
import streamlit as st
import pandas as pd
import requests
import folium
import io

from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_folium import st_folium
from datetime import datetime
from st_aggrid import AgGrid

# buffer to use for excel writer
buffer = io.BytesIO()
geocode_e = pd.DataFrame()

#Fecha
fecha = datetime.now()

# Personalizamos titulos
st.title('Geolocalizacion de Colaboradores')

# Create the sidebar
sidebar = st.sidebar

# Customize the title in sidebar
sidebar.title("Herramientas")
#st.header('Fecha '+ fecha.strftime("%m/%d/%Y, %H:%M:%S"))

# Save sesion Stage
if 'Empleados_Map' not in st.session_state:
    st.session_state['Empleados_Map'] = pd.DataFrame()

if 'Activar_btn' not in st.session_state:
    st.session_state['Activar_btn'] = 0

if 'grid_Options' not in st.session_state:
    st.session_state['grid_Options'] = GridOptionsBuilder

# Abre el menu para la carga de archivos
uploaded_file = sidebar.file_uploader('Seleccionar el archivo de excel de colaboradores', type="xlsx") 

if uploaded_file is not None:
    empleados = pd.read_excel(uploaded_file, sheet_name='Hoja2')  
    geocode_e = empleados 
    shape = empleados.shape

    if sidebar.button("Procesar Archivo"):
        st.session_state['Activar_btn'] = 0
        # Insertar nuevas columnas
        geocode_e.insert(shape[1], 'Latitud', None)
        geocode_e.insert(shape[1] + 1, 'Longitud', None)

        # Progress bar
        progress_text = "Calculado Latitud y Longitud. Porfavor espere."
        my_bar = st.progress(0, text=progress_text)

        api_key = 'AIzaSyCIN_vAVJiIoLcFGHSE6PG89rWQnuFV8D8'

        err = 0
        reg = 0
        total = geocode_e['Empleado'].count()

        for index, row in geocode_e.iterrows():
            try:
                print('Combinacion Calle, Municipio, Estado CP')
                address = row['Calle'] + ', ' + row['Municipio'] + ', ' + row['Estado'] + ', ' + str(row['C.P.'])
                url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
                response = requests.get(url)
                json_data = response.json()
                lat = json_data['results'][0]['geometry']['location']['lat']
                lng = json_data['results'][0]['geometry']['location']['lng']
                geocode_e.loc[index, 'Latitud'] = lat
                geocode_e.loc[index, 'Longitud'] = lng
                print(address ,f'Latitud: {lat}, Longitud: {lng}')
                reg += 1
            except:
                print('Combinacion CP Municipio, Estado')
                try:
                    address = str(row['C.P.']) + ' ' + row['Municipio'] + ', ' + row['Estado']
                    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}'
                    response = requests.get(url)
                    json_data = response.json()
                    lat = json_data['results'][0]['geometry']['location']['lat']
                    lng = json_data['results'][0]['geometry']['location']['lng']
                    geocode_e.loc[index, 'Latitud'] = lat
                    geocode_e.loc[index, 'Longitud'] = lng
                    print(address ,f'Latitud: {lat}, Longitud: {lng}')
                    reg += 1
                except:
                    err += 1

            porc =  ((err+reg)/total)*100
            info_bar = 'Registros correctos: ' + str(reg) + ' Errores: ' + str(err) + ' Porcentaje: ' + str(round(porc, 2)) + '%'
            my_bar.progress(((err+reg)/total), text=info_bar)
            status = 1

        st.session_state['Empleados_Map'] = geocode_e  
        st.session_state['Activar_btn'] = 1

        gb = GridOptionsBuilder.from_dataframe(geocode_e)
        gb.configure_pagination(enabled=True, paginationPageSize=10)
        gb.configure_selection(selection_mode='single', use_checkbox=True)
        st.session_state['grid_Options'] = gb.build()

if st.session_state['Activar_btn'] == 1:     
    # Descarga del Dataframe GeoCode xlsx
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        st.session_state['Empleados_Map'].to_excel(writer, sheet_name='Empleados', index=False)
        # Close the Pandas Excel writer and output the Excel file to the buffer
        writer.save()

    # Boton de descargar
    download2 = st.download_button(label="Descargar Geolocalización", data=buffer, file_name='Geolocalizacion Empleados.xlsx', mime='application/vnd.ms-excel')
    #st.dataframe(geocode_e) 

    grid_response = AgGrid(st.session_state['Empleados_Map'], gridOptions =  st.session_state['grid_Options'])
    
    #grid_response['selected_rows']
    rows_selection = grid_response['selected_rows']
    if len(rows_selection) > 0:
        df_emp = pd.DataFrame(rows_selection)[['Empleado', 'Nombre','Latitud', 'Longitud', 'Calle', 'Municipio', 'Estado', 'C.P.']] 
        coordenadas = df_emp['Latitud'], df_emp['Longitud']

        map = folium.Map(coordenadas, zoom_start=16)
        folium.Marker(
            coordenadas,
            popup="Empleado",
            tooltip=df_emp[['Nombre']]
        ).add_to(map)

        st_data = st_folium(map, width=750, height=350)