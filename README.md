pip install beautifulsoup4
pip install psycopg2
pip install folium

## Reflection
This week I learned how to embed an weather API with my database. One of the challenged task was that my data does not sucessfully insert into the database. Thus, I treid to trouble shoot the issues and it ends up that my code cannot insert the pulled data to the database, becuase some of the content from the table are empty. Thus, I added a condition that if the data is empty, input 'None' as an value. This allows my scraper.py sucessfull insert the data into my Postgres Database.