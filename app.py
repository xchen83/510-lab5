import streamlit as st
import datetime
import pandas.io.sql as sqlio
import altair as alt
import pandas as pd
import folium
from streamlit_folium import st_folium

from db import conn_str

# Function to generate map based on DataFrame
def generate_map(df):
    m = folium.Map(location=[47.6062, -122.3321], zoom_start=12)
    for index, row in df.iterrows():
        if pd.notnull(row['latitude']) and pd.notnull(row['longitude']):
            folium.Marker([row['latitude'], row['longitude']], popup=row['venue']).add_to(m)
        else:
            print(f"Skipping row {index} due to missing coordinates")
    return m


st.title("Seattle Events")

df = sqlio.read_sql_query("SELECT * FROM events", conn_str)

# Chart for the most common event categories
categories_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('count()', title='Number of Events'),
    y=alt.Y('category:N', sort='-x', title='Event Category')
).properties(title='Most Common Event Categories in Seattle').interactive()

st.altair_chart(categories_chart, use_container_width=True)


# Chart 1 for the month with the most events
df['month'] = df['date'].dt.strftime('%B')  # Converts datetime to month name

# Chart 2 for the month with the most events
month_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('count()', title='Number of Events'),
    y=alt.Y('month:N', sort='-x', title='Month')
).properties(title='Months with Most Events in Seattle').interactive()

st.altair_chart(month_chart, use_container_width=True)

# Chart 3 for most popular day of the week
df['day_of_week'] = df['date'].dt.day_name()  # Converts datetime to day of the week name

# Chart for the most popular day of the week
day_of_week_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('count()', title='Number of Events'),
    y=alt.Y('day_of_week:N', sort='-x', title='Day of the Week')
).properties(title='Most Popular Days of the Week for Events in Seattle').interactive()

st.altair_chart(day_of_week_chart, use_container_width=True)


# Controls
filtered_df = df.copy()

# Filter category
category = st.selectbox("Select a category", filtered_df['category'].unique())
filtered_df = filtered_df[filtered_df['category'] == category]

# Filter date
min_date = df['date'].min().date()
max_date = df['date'].max().date()
selected_date_range = st.date_input("Select date range", value=[min_date, max_date], min_value=min_date, max_value=max_date)
filtered_df = filtered_df[(filtered_df['date'].dt.date >= selected_date_range[0]) & (filtered_df['date'].dt.date <= selected_date_range[1])]

# Filter location
locations = ['All'] + list(df['location'].unique())
selected_location = st.selectbox("Select a location", options=locations)

if selected_location != 'All':
    filtered_df = filtered_df[filtered_df['location'] == selected_location]

# Filter weather condition
weather_conditions = ['All'] + list(df['short_forecast'].unique())
selected_weather_condition = st.selectbox("Select a weather condition", options=weather_conditions)

if selected_weather_condition != 'All':
    filtered_df = filtered_df[filtered_df['short_forecast'] == selected_weather_condition]

# Display filtered data
st.write(filtered_df)

# Update map based on filtered data
st.subheader("Event Locations")
st_folium(generate_map(filtered_df), width=1200, height=600)