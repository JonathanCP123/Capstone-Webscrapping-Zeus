from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', class_='history-rates-data')
rows = table.find_all('tr')

row_length = len(rows)

temp = []  # Initiating a list to store the tuples

# Loop through each row
for i in range(1, row_length):
    # Get the rowrun
    row = table.find_all('tr')[i]
    
    # Get Date
    date_element = row.find('span', class_='nowrap')
    if date_element:
        date = date_element.text
    else:
        date = None  # Handle the case where the date is not found
    
    # Get Daily Price
    price_element = row.find('span', class_='w')
    if price_element:
        daily_price = price_element.text
    else:
        daily_price = None  # Handle the case where the price is not found
    
    # Append the tuple to the list
    temp.append((date, daily_price))


temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns= ('date', 'daily_price'))

#insert data wrangling here

# Convert the 'date' column to datetime format
data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d', errors='coerce')

# Clean and convert the 'daily_price' column to numeric format
data['daily_price'] = data['daily_price'].str.replace('1 USD = ', '').str.replace(',', '').str.replace(' IDR', '')
data['daily_price'] = pd.to_numeric(data['daily_price'], errors='coerce')

viz = data.pivot_table(
    index='date',         
    values='daily_price',  
    aggfunc='sum'  
)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{data["daily_price"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = viz.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)