import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    file_path = 'output_combined_crosstab.xlsx'
    return pd.read_excel(file_path)

data = load_data()

# Tambahkan kolom gabungan untuk lokasi
data['Lokasi'] = 'Kota ' + data['Kota'] + ' - ' + 'Kecamatan ' + data['Kecamatan'] + ' - ' + 'Kelurahan ' + data['Kelurahan']

# Buat daftar unik untuk Kota, Kecamatan, dan Lokasi
kota_options = [f"Kota {kota}" for kota in data['Kota'].unique()]
kecamatan_options = data[['Kota', 'Kecamatan']].drop_duplicates().apply(
    lambda x: f"Kota {x['Kota']} - Kecamatan {x['Kecamatan']}", axis=1
).tolist()
kelurahan_options = data[['Kota', 'Kecamatan', 'Kelurahan']].drop_duplicates().apply(
    lambda x: f"Kota {x['Kota']} - Kecamatan {x['Kecamatan']} - Kelurahan {x['Kelurahan']}", axis=1
).tolist()

# Gabungkan semua opsi ke dalam scrollbar
location_options = kota_options + kecamatan_options + kelurahan_options

# Scrollbar Filter
st.title("Dashboard Investasi DKI Jakarta")
selected_location = st.selectbox(
    "Pilih Lokasi", options=location_options, index=0
)

# Filter data berdasarkan pilihan lokasi
if selected_location.startswith("Kota ") and " - Kecamatan" not in selected_location:
    # Pilihan tingkat Kota
    kota = selected_location.replace("Kota ", "")
    filtered_data = data[data['Kota'] == kota]
    level = 'Kota'
elif " - Kecamatan" in selected_location and " - Kelurahan" not in selected_location:
    # Pilihan tingkat Kecamatan
    kota, kecamatan = selected_location.replace("Kota ", "").split(" - Kecamatan ")
    filtered_data = data[(data['Kota'] == kota) & (data['Kecamatan'] == kecamatan)]
    level = 'Kecamatan'
else:
    # Pilihan tingkat Kelurahan
    kota, kecamatan, kelurahan = selected_location.replace("Kota ", "").replace(" - Kecamatan ", "|").replace(" - Kelurahan ", "|").split("|")
    filtered_data = data[(data['Kota'] == kota) & (data['Kecamatan'] == kecamatan) & (data['Kelurahan'] == kelurahan)]
    level = 'Kelurahan'

# Agregasikan data jika tingkat Kota atau Kecamatan dipilih
if level == 'Kota':
    aggregated_data = filtered_data.groupby('Kota').sum()
elif level == 'Kecamatan':
    aggregated_data = filtered_data.groupby('Kecamatan').sum()
else:
    aggregated_data = filtered_data  # Tidak perlu agregasi untuk Kelurahan

# KPI Section
st.subheader("Key Performance Indicators (KPI)")

# Menggunakan HTML untuk menampilkan KPI dengan font kecil
col1, col2 = st.columns(2)
col1.markdown(
    f"""
    <div style="font-size:18px;">
        <b>Total PMDN (Unit):</b> {aggregated_data['PMDN'].sum():,.2f}<br>
        <b>Total PMDN (Rp):</b> {aggregated_data['PMDN_y'].sum():,.2f}
    </div>
    """, unsafe_allow_html=True
)
col2.markdown(
    f"""
    <div style="font-size:18px;">
        <b>Total PMA (Unit):</b> {aggregated_data['PMA'].sum():,.2f}<br>
        <b>Total PMA (Rp):</b> {aggregated_data['PMA_y'].sum():,.2f}
    </div>
    """, unsafe_allow_html=True
)

st.markdown("---")

# Visualization: Perbandingan PMDN vs PMA berdasarkan lokasi

# Filtered data untuk chart
if level == 'Kota':
    chart_data = aggregated_data
elif level == 'Kecamatan':
    chart_data = filtered_data.groupby('Kecamatan').sum()
else:
    chart_data = filtered_data

# Menghitung persentase
chart_data['Total'] = chart_data['PMDN_y'] + chart_data['PMA_y']
chart_data['PMDN_y_pct'] = (chart_data['PMDN_y'] / chart_data['Total']) * 100
chart_data['PMA_y_pct'] = (chart_data['PMA_y'] / chart_data['Total']) * 100

# Membuat chart
fig2 = go.Figure()
fig2.add_trace(go.Bar(
    y=chart_data.index,
    x=chart_data['PMDN_y_pct'],  # Menggunakan persentase PMDN_y
    name='PMDN',
    orientation='h',
    text=chart_data['PMDN_y_pct'].apply(lambda x: f"{x:.2f}%"),  # Format persentase
    textposition='auto'
))
fig2.add_trace(go.Bar(
    y=chart_data.index,
    x=chart_data['PMA_y_pct'],  # Menggunakan persentase PMA_y
    name='PMA',
    orientation='h',
    text=chart_data['PMA_y_pct'].apply(lambda x: f"{x:.2f}%"),  # Format persentase
    textposition='auto'
))
fig2.update_layout(
    barmode='stack',
    title={
        'text': 'Perbandingan Nilai Investasi (%): PMDN vs PMA',
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    height=300,
    xaxis={
        'title': 'Persentase (%)',
        'showticklabels': True
    },
    yaxis={
        'title': 'Lokasi' if level == 'Kelurahan' else 'Kecamatan' if level == 'Kecamatan' else 'Kota'
    }
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")


# Helper function to create bar charts
def create_bar_chart(data, column_prefix, title, level):
    chart_data = data[[col for col in data.columns if col.startswith(column_prefix)]].sum()
    chart_data = chart_data.sort_values(ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=chart_data.values,
        y=chart_data.index,
        orientation='h',
        text=chart_data.values,
        textposition='auto'
    ))
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Total Investasi',
        yaxis_title=level,
        height=400
    )
    return fig

# Expanders for each section
with st.expander("Distribusi Investasi berdasarkan Jenis Usaha"):
    fig1 = create_bar_chart(filtered_data, "X", "Distribusi Investasi: Jenis Usaha", level)
    st.plotly_chart(fig1, use_container_width=True)

with st.expander("Distribusi Investasi berdasarkan Skala Usaha"):
    fig2 = create_bar_chart(filtered_data, "AR", "Distribusi Investasi: Skala Usaha", level)
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("Distribusi Investasi berdasarkan Tingkat Risiko Usaha"):
    fig3 = create_bar_chart(filtered_data, "AZ", "Distribusi Investasi: Tingkat Risiko Usaha", level)
    st.plotly_chart(fig3, use_container_width=True)

with st.expander("Distribusi Investasi berdasarkan xxx"):
    fig4 = create_bar_chart(filtered_data, "BJ", "Distribusi Investasi: xxx", level)
    st.plotly_chart(fig4, use_container_width=True)

with st.expander("Distribusi Investasi berdasarkan Sektor Pembina"):
    fig5 = create_bar_chart(filtered_data, "CM", "Distribusi Investasi: Sektor Pembina", level)
    st.plotly_chart(fig5, use_container_width=True)

with st.expander("Distribusi Investasi berdasarkan Bidang Izin"):
    fig6 = create_bar_chart(filtered_data, "DK", "Distribusi Investasi: Bidang Izin", level)
    st.plotly_chart(fig6, use_container_width=True)