import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

# Titles an header in streamlit
st.title('Aplicación web de Ciencia de Datos')
st.header('Alonso Hernandez Baca')

DATA_URL = 'Employees.csv'

# Load only 500 regs
@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    return data

# Call the function
empleados = load_data(500)

# Create the sidebar
sidebar = st.sidebar

# Customize the title in sidebar
sidebar.title("Uso de las herramientas streamlit")

# Separator
st.markdown("___")

# Display the content of the dataset if checkbox is true
st.header("Empleados Dataset")

agree = sidebar.checkbox("Mostrar el Dataset de Empleados? ")
if agree:
  st.dataframe(empleados)

st.markdown("___")

# Fuction for filter the Employee_ID
@st.cache_data
def filterdata(id_name):
    filtered_data_byname = empleados[empleados['Employee_ID'].str.upper().str.contains(id_name)]
    return filtered_data_byname

# Fuction for filter the Hometown and Unit
@st.cache_data
def load_data_byHometown(dataframe,param, Hometown):
    filtered_data_byhome = dataframe[ dataframe[param] == Hometown ]
    return filtered_data_byhome

#Container
optionals = sidebar.expander("Filtros de empleados", True)

# Textbox Employee_ID
myname = optionals.text_input('Buscar por Employee_ID:')

# SelectedBox Hometown
selected_H = optionals.selectbox('Buscar por Hometown', empleados['Hometown'].unique())

# SelectedBox Unit
selected_U = optionals.selectbox('Buscar por Hometown', empleados['Unit'].unique())

# Filter by Employee_ID, Hometown, Unit
if optionals.button('Filter'):
    filterbyname = filterdata(myname)
    filterbyh = load_data_byHometown(filterbyname, 'Hometown', selected_H )
    filterbyh2 = load_data_byHometown(filterbyh, 'Unit',selected_U )
    count_row = filterbyh2.shape[0]  # 0 - row, 1 -col
    st.write(f"Total names : {count_row}")
    st.dataframe(filterbyh2)

# Separator
st.markdown("___")

# Slider of Education Level
ed_level = optionals.slider( 
  "Selecciona el nivel educativo",
  min_value = float(empleados['Education_Level'].min()),
  max_value = float(empleados['Education_Level'].max())
)

subset_fare = empleados[(empleados['Education_Level'] >= ed_level)]
st.write(f"Numero de registros con el nivel educativo de: {ed_level}: {subset_fare.shape[0]}")
st.dataframe(subset_fare)

st.markdown("___")

# Filter by City
select_city = sidebar.selectbox('Filtrar por ciudad', empleados['Hometown'].unique())

# Filter by Employee_ID, Hometown, Unit
if sidebar.button('Filter City'):
    filterbycity = load_data_byHometown(empleados, 'Hometown', select_city )
    count_row = filterbycity.shape[0]  # 0 - row, 1 -col
    st.write(f"Total names : {count_row}")
    st.dataframe(filterbycity)

# Separator
st.markdown("___")

# Filter by Unit
select_unit = sidebar.selectbox('Filtrar por Unit', empleados['Unit'].unique())

# Filter by Employee_ID, Hometown, Unit
if sidebar.button('Filter by Unit'):
    filterbyunit = load_data_byHometown(empleados, 'Unit', select_unit )
    count_row = filterbyunit.shape[0]  # 0 - row, 1 -col
    st.write(f"Total names : {count_row}")
    st.dataframe(filterbyunit)

# Graphs
# Histogram by Age
fig, ax = plt.subplots()
ax.hist(empleados.Age)
st.header("Histograma edad de los empleados")
st.pyplot(fig)

# Histogram by Unit
st.markdown("___")
fig2, ax2 = plt.subplots()
ax2.hist(empleados["Unit"])
ax2.set_xlabel("Area de trabajo")
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90)
st.header("Histograma por area de trabajo")
st.pyplot(fig2)

# Graph Attrition by Hometown 
st.markdown("___")
# Group by Hometown save in a new DT
empleados_homet = empleados[['Hometown','Attrition_rate']].groupby('Hometown').sum()
fig3, ax3 = plt.subplots()
y_pos = empleados_homet.index
x_pos = empleados_homet['Attrition_rate']
ax3.barh(y_pos, x_pos)
ax3.set_ylabel("Ciudad")
ax3.set_xlabel("Tasa de desercion")
st.header('Grafica desercion por ciudad')
st.pyplot(fig3)

# Graph Attrition Rate by Age
st.markdown("___")
# Group by Age save in a new DT
empleados_age = empleados[['Age','Attrition_rate']].groupby('Age').sum()
fig4, ax4 = plt.subplots()
y_pos2 = empleados_age.index
x_pos2 = empleados_age['Attrition_rate']
ax4.barh(y_pos2, x_pos2)
ax4.set_ylabel("Edad")
ax4.set_xlabel("Tasa de desercion")
st.header('Grafica desercion por edad')
st.pyplot(fig4)


# Graph relation between Time of service and Attriton Rate
st.markdown("___")
fig5, ax5 = plt.subplots()
ax5.scatter(empleados["Time_of_service"], empleados["Attrition_rate"])
ax5.set_xlabel("Años en servicio")
ax5.set_ylabel("Tasas de desercion")
st.header("Grafica años en servicio vs tasa de desercion")
st.pyplot(fig5)