## Getting Started
1. pip install beautifulsoup4
2. pip install psycopg2
3. pip install folium
4. python run scraper.py
5. streamlit run app.py

## Lessons Learned
- Learned how to connect my Postgres database to the Azure and my environment
- Learned how to do the data visualization for an streamlit app
- Enhanced my knowledge in virtual environment

## Questions
- How to imporve the visual of the charts and incorporate user interation for this app?

## Reflection
This week I learned how to embed an weather API with my database. One of the challenged task was that my data does not sucessfully insert into the database. Thus, I treid to trouble shoot the issues and it ends up that my code cannot insert the pulled data to the database, becuase some of the content from the table are empty. Thus, I added a condition that if the data is empty, input 'None' as an value. This allows my scraper.py sucessfull insert the data into my Postgres Database.

Also it is important to check the typo for my postgres database connection
