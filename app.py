import streamlit as st
import pandas.io.sql as sqlio
import altair as alt
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd
import datetime

from db import conn_str

st.title("Seattle Events")

# Load event data from the database
df = sqlio.read_sql_query("SELECT * FROM events", conn_str)

# Convert 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Dropdown for selecting a category
category_filter = st.selectbox("Select a category", ['All'] + list(df['category'].unique()))

# Date range selector for event date
start_date, end_date = st.date_input("Select date range", [])

# Location filter
location_filter = st.selectbox("Select a location", ['All'] + list(df['location'].unique()))

# Weather filter (optional)
# You might want to include specific weather conditions or a boolean filter for 'Good' vs 'Bad' weather

# Applying filters to the dataframe
if category_filter != 'All':
    df = df[df['category'] == category_filter]

if start_date and end_date:
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

if location_filter != 'All':
    df = df[df['location'] == location_filter]

# 1. Chart: Event Counts by Category
st.altair_chart(
    alt.Chart(df).mark_bar().encode(
        x=alt.X("count()", title="Number of Events"),
        y=alt.Y("category:N", sort='-x', title="Category")
    ).properties(title="Event Counts by Category").interactive(),
    use_container_width=True
)

# 2. Chart: Events by Month
df['month'] = df['date'].dt.month_name()
st.altair_chart(
    alt.Chart(df).mark_bar().encode(
        x=alt.X("count()", title="Number of Events"),
        y=alt.Y("month:N", sort='-x', title="Month")
    ).properties(title="Events by Month").interactive(),
    use_container_width=True
)

# 3. Chart: Events by Day of the Week
df['day_of_week'] = df['date'].dt.day_name()
st.altair_chart(
    alt.Chart(df).mark_bar().encode(
        x=alt.X("count()", title="Number of Events"),
        y=alt.Y("day_of_week:N", sort='-x', title="Day of the Week")
    ).properties(title="Events by Day of the Week").interactive(),
    use_container_width=True
)

# 4. Chart: Events by Location
# Assuming 'location' is a suitable column for this chart. You may need to adjust based on your data structure.
st.altair_chart(
    alt.Chart(df).mark_bar().encode(
        x=alt.X("count()", title="Number of Events"),
        y=alt.Y("location:N", sort='-x', title="Location")
    ).properties(title="Events by Location").interactive(),
    use_container_width=True
)

# Map Visualization
# Initialize a map centered around Seattle
m = folium.Map(location=[47.6062, -122.3321], zoom_start=12)

# Geolocator for converting locations to coordinates
geolocator = Nominatim(user_agent="seattle_events")

# Add markers for events
for _, event in df.iterrows():
    # Attempt to geolocate the venue/location
    location = geolocator.geocode(event['venue'] + ', Seattle, WA')
    if location:
        folium.Marker(
            location=[location.latitude, location.longitude],
            popup=event['title'],
            tooltip=event['venue']
        ).add_to(m)

# Display the map with event markers
st_folium(m, width=730, height=500)

# Show filtered dataframe
st.write(df)
