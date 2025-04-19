map_df = df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
st.map(map_df[["latitude", "longitude"]], zoom=1)
st.map(df[["Latitude", "Longitude"]], zoom=1)
