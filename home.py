import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache
def load_data():
    file_path = 'output_combined_crosstab.xlsx'
    return pd.read_excel(file_path)

data = load_data()

# Sidebar Filters
st.sidebar.header("Filter Data")
selected_kota = st.sidebar.multiselect(
    "Pilih Kota", options=data['Kota'].unique(), default=data['Kota'].unique()
)
selected_kecamatan = st.sidebar.multiselect(
    "Pilih Kecamatan", options=data['Kecamatan'].unique(), default=data['Kecamatan'].unique()
)
selected_kelurahan = st.sidebar.multiselect(
    "Pilih Kelurahan", options=data['Kelurahan'].unique(), default=data['Kelurahan'].unique()
)

# Filter data
filtered_data = data[
    (data['Kota'].isin(selected_kota)) &
    (data['Kecamatan'].isin(selected_kecamatan)) &
    (data['Kelurahan'].isin(selected_kelurahan))
]

# KPI Section
st.title("Dashboard Investasi DKI Jakarta")
total_pma = filtered_data['PMA_y'].sum()
total_pmdn = filtered_data['PMDN_y'].sum()
st.subheader("Key Performance Indicators (KPI)")
col1, col2 = st.columns(2)
col1.metric("Total PMA (Rp)", f"{total_pma:,.2f}")
col2.metric("Total PMDN (Rp)", f"{total_pmdn:,.2f}")

# Visualization
st.subheader("Distribusi Investasi Berdasarkan Sektor")
sector_columns = [col for col in data.columns if col not in ['Kota', 'Kecamatan', 'Kelurahan', 'PMA', 'PMDN', 'PMA_y', 'PMDN_y']]
sector_totals = filtered_data[sector_columns].sum().sort_values(ascending=False)
fig = px.bar(sector_totals, x=sector_totals.index, y=sector_totals.values, labels={'x': 'Sektor', 'y': 'Total Investasi (Rp)'})
st.plotly_chart(fig)

# Interactive Map (if location data is available)
if 'Latitude' in data.columns and 'Longitude' in data.columns:
    st.subheader("Peta Investasi")
    map_data = filtered_data[['Latitude', 'Longitude', 'PMA_y', 'PMDN_y']].dropna()
    map_data['Total Investasi'] = map_data['PMA_y'] + map_data['PMDN_y']
    st.map(map_data)

# Data Table
st.subheader("Tabel Data")
st.dataframe(filtered_data)
"""

# Save the script to a Python file for the user
script_path = "/mnt/data/dashboard_streamlit.py"
with open(script_path, "w") as script_file:
    script_file.write(streamlit_code)

script_path