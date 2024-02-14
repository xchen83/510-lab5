import requests
import re
import json
import html
import datetime
from zoneinfo import ZoneInfo
import psycopg2

URL = 'https://visitseattle.org/events/page/'
URL_LIST_FILE = './data/links.json'
URL_DETAIL_FILE = './data/data.json'

def get_weather_data(location_query):
    location_query = f'{location_query}, Seattle'
    location_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_query,
        'format': 'json',
    }
    response = requests.get(location_url, params=params, headers={'User-Agent': 'Mozilla/5.0'})
    location_data = response.json()

    if location_data:
        latitude = location_data[0]['lat']
        longitude = location_data[0]['lon']

        # Use latitude and longitude to query weather API
        weather_api_url = f"https://api.weather.gov/points/{latitude},{longitude}"
        weather_response = requests.get(weather_api_url, headers={'User-Agent': 'Mozilla/5.0'})
        weather_data = weather_response.json()

        forecast_url = weather_data['properties']['forecast']
        detailed_forecast_url = weather_data['properties']['forecastGridData']
        res = requests.get(forecast_url, headers={'User-Agent': 'Mozilla/5.0'})
        weather_forecast_data = res.json()

        # Extracting short forecast
        short_forecast = weather_forecast_data.get('properties', {}).get('periods', [{}])[0].get('shortForecast', '')

        # Fetch more detailed forecast data to get min, max temperature, and wind chill
        grid_res = requests.get(detailed_forecast_url, headers={'User-Agent': 'Mozilla/5.0'})
        grid_data = grid_res.json()
        min_temperature = grid_data.get('properties', {}).get('minTemperature', {}).get('values', [{}])[0].get('value', '')
        max_temperature = grid_data.get('properties', {}).get('maxTemperature', {}).get('values', [{}])[-1].get('value', '')
        wind_chill = grid_data.get('properties', {}).get('windChill', {}).get('values', [{}])[0].get('value', '')

        return short_forecast, min_temperature, max_temperature, wind_chill, latitude, longitude

    return None, None, None, None, None, None

def list_links():
    res = requests.get(URL + '1/', headers={'User-Agent': 'Mozilla/5.0'})
    last_page_no = int(re.findall(r'bpn-last-page-link"><a href=".+?/page/(\d+?)/.+" title="Navigate to last page">', res.text)[0])

    links = []
    for page_no in range(1, last_page_no + 1):
        res = requests.get(URL + str(page_no) + '/', headers={'User-Agent': 'Mozilla/5.0'})
        links.extend(re.findall(r'<h3 class="event-title"><a href="(https://visitseattle.org/events/.+?/)" title=".+?">.+?</a></h3>', res.text))

    with open(URL_LIST_FILE, 'w') as file:
        json.dump(links, file)

def get_detail_page():
    with open(URL_LIST_FILE, 'r') as file:
        links = json.load(file)

    data = []
    for link in links:
        try:
            res = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (YourAppName)'})
            row = {
                'title': html.unescape(re.findall(r'<h1 class="page-title" itemprop="headline">(.+?)</h1>', res.text)[0]),
                'date': datetime.datetime.strptime(re.findall(r'<h4><span>.*?(\d{1,2}/\d{1,2}/\d{4})</span>', res.text)[0], '%m/%d/%Y').replace(tzinfo=ZoneInfo('America/Los_Angeles')).isoformat(),
                'venue': re.findall(r'<h4><span>.*?\d{1,2}/\d{1,2}/\d{4}</span> \| <span>(.+?)</span></h4>', res.text)[0].strip(),
                'category': html.unescape(re.findall(r'<a href=".+?" class="button big medium black category">(.+?)</a>', res.text)[0]),
                'location': "Region Not Available"  # Default value, in case the next line fails
            }
            metas = re.findall(r'<a href=".+?" class="button big medium black category">(.+?)</a>', res.text)
            if len(metas) > 1:
                row['location'] = metas[1]

            weather_info = get_weather_data(row['venue'])
            if weather_info[0]:  # Checks if short_forecast is not None
                row['weather'] = {
                    'short_forecast': weather_info[0],
                    'min_temperature': weather_info[1],
                    'max_temperature': weather_info[2],
                    'wind_chill': weather_info[3],
                    'latitude': weather_info[4],
                    'longitude': weather_info[5]
                }

            data.append(row)
        except Exception as e:
            print(f'Error processing link {link}: {e}')

    with open(URL_DETAIL_FILE, 'w') as file:
        json.dump(data, file)

def insert_to_pg():
    urls = json.load(open(URL_LIST_FILE, 'r'))
    data = json.load(open(URL_DETAIL_FILE, 'r'))
    
    conn = psycopg2.connect(DB_CONNECTION_STRING)
    cur = conn.cursor()

    for url, row in zip(urls, data):
        try:
            cur.execute(
                """
                INSERT INTO events (url, title, date, venue, category, location)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING;
                """,
                (url, row['title'], row['date'], row['venue'], row['category'], row['location'])
            )
        except psycopg2.Error as e:
            print(f"Error inserting data for URL: {url}")
            print(e)

    conn.commit()
    cur.close()
    conn.close()


def scrape_events_data():
    list_links()
    get_detail_page()
    insert_to_pg()

if __name__ == '__main__':
    scrape_events_data()
