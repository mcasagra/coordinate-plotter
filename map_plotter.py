import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Coordinate Plotter", layout="wide")
st.title("📍 Coordinate Plotter")

st.markdown("Upload a CSV file or paste coordinates, and plot them on a map.")

# Sample CSV download
sample_csv = """col1,col2,col3,Site Name,col5,col6,col7,col8,col9,Latitude,Longitude
1,A,X,San Francisco,?,?,?,?,?,37.7749,-122.4194
2,B,Y,Los Angeles,?,?,?,?,?,34.0522,-118.2437
"""
st.download_button("📥 Download Sample CSV", sample_csv, file_name="sample_coordinates.csv", mime="text/csv")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

data = None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 CSV Preview")
        st.dataframe(df.head())
        
        # Ensure there are enough columns
        if df.shape[1] >= 11:
            site_names = df.iloc[:, 3].astype(str).str.strip()
            latitudes = pd.to_numeric(df.iloc[:, 9], errors="coerce")
            longitudes = pd.to_numeric(df.iloc[:, 10], errors="coerce")
            
            data = pd.DataFrame({
                "Site Name": site_names,
                "Latitude": latitudes,
                "Longitude": longitudes
            }).dropna().drop_duplicates()
        else:
            st.error("CSV does not have enough columns. Must have Site Name in 4th column, Latitude in 10th, Longitude in 11th.")
    except Exception as e:
        st.error(f"Error reading CSV: {e}")

# Manual input
manual_input = st.text_area("Or paste coordinates here (Site Name, Latitude, Longitude):")

if manual_input.strip():
    try:
        manual_lines = [line.split(",") for line in manual_input.strip().split("\n")]
        manual_df = pd.DataFrame(manual_lines, columns=["Site Name", "Latitude", "Longitude"])
        manual_df["Latitude"] = pd.to_numeric(manual_df["Latitude"], errors="coerce")
        manual_df["Longitude"] = pd.to_numeric(manual_df["Longitude"], errors="coerce")
        manual_df = manual_df.dropna().drop_duplicates()
        
        if data is not None:
            data = pd.concat([data, manual_df], ignore_index=True).drop_duplicates()
        else:
            data = manual_df
    except Exception as e:
        st.error(f"Error parsing manual input: {e}")

# Plot map
if data is not None and not data.empty:
    st.subheader("🗺 Map")
    m = folium.Map(location=[data["Latitude"].mean(), data["Longitude"].mean()], zoom_start=5)
    for _, row in data.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=row["Site Name"]
        ).add_to(m)
    st_folium(m, width=800, height=500)
    
    # Download cleaned CSV
    csv_download = data.to_csv(index=False)
    st.download_button("💾 Download Cleaned CSV", csv_download, "cleaned_coordinates.csv", "text/csv")
else:
    st.info("Upload a CSV or paste coordinates to plot them.")