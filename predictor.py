import flask
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import urllib
import requests
from bs4 import BeautifulSoup
import re

# set the project root directory as the static folder, you can set others.
app = flask.Flask(__name__, static_url_path='')

@app.route("/")
def viz_page():
    with open("house.html", 'r') as viz_file:
        return viz_file.read()
# def root():
#     return app.send_static_file('house.html')

# def send_js():
#     return flask.send_from_directory('static', 'script.js')

# def viz_page():
#     with open("house.html", 'r') as viz_file:
#         return viz_file.read()

@app.route("/predict", methods=["POST"])
def predict():

	data = flask.request.json
	x = data["features"]
	d ={}    

	c1 = [u'Bayview', u'Central Richmond', u'Central Sunset', u'Crocker Amazon',
	       u'Daly City', u'Diamond Heights', u'Excelsior', u'Forest Hill',
	       u'Forest Hill Extension', u'Golden Gate Heights', u'Ingleside',
	       u'Ingleside Heights', u'Ingleside Terrace', u'Inner Parkside',
	       u'Inner Richmond', u'Inner Sunset', u'Lakeshore', u'Lakeside',
	       u'Little Hollywood', u'Merced Heights', u'Midtown Terrace',
	       u'Miraloma Park', u'Mission Terrace', u'Mount Davidson Manor',
	       u'Oceanview', u'Outer Mission', u'Outer Parkside', u'Outer Richmond',
	       u'Outer Sunset', u'Parkside', u'Portola', u'Silver Terrace',
	       u'St. Francis Wood', u'Sunnyside', u'Twin Peaks', u'Visitacion Valley',
	       u'West Portal', u'Western Addition', u'Westwood Highlands',
	       u'Westwood Park']
	c2 = [u'Buena Vista Park', u'Central Waterfront - Dogpatch',
	       u'Corona Heights', u'Cow Hollow', u'Downtown', u'Glen Park',
	       u'Haight-Ashbury', u'Hayes Valley', u'Lake', u'Lone Mountain',
	       u'Lower Pacific Heights', u'Marina', u'Nob Hill', u'North Beach',
	       u'North Panhandle', u'North Waterfront', u'Parnassus - Ashbury',
	       u'Potrero Hill', u'Presidio Heights', u'Russian Hill', u'Sea Cliff',
	       u'Telegraph Hill', u'Van Ness - Civic Center', u'Yerba Buena']
	c3 = [u'Bernal Heights', u'Eureka Valley - Dolores Heights - Castro',
	       u'Mission', u'Noe Valley', u'Pacific Heights', u'South Beach',
	       u'South of Market']

	if x[-2] in c1:
	    d['group1'] = 1
	    d['group2'] = 0
	    d['group3'] = 0
	elif x[-2] in c2:
	    d['group1'] = 0
	    d['group2'] = 1
	    d['group3'] = 0
	else:
	    d['group1'] = 0
	    d['group2'] = 0
	    d['group3'] = 1

	d['bedrooms'] = x[3]
	d['bathrooms'] = x[4]
	d['totalrooms'] = x[5]
	d['finishedsqft'] = x[0]
	d['lot_sqft'] = x[1]
	d['history'] = 2016 - x[2]
	d['finishedsqft_rooms'] = d['finishedsqft']/float(x[5])
	d['bed_bath'] = d['bedrooms']/d['bathrooms']
	d['bathbed'] = d['bedrooms']*d['bathrooms']
	d['lot_finish'] = d['lot_sqft'] / d['finishedsqft']
	D = pd.DataFrame(d,index=[0])

	df = pd.read_csv("final_data.csv")

	if x[-1] == "SingleFamily":
	    df_sf = df[df.usecode == 'singlefamily.csv']
	    X = df_sf[['bathrooms','bedrooms','finishedsqft','totalrooms','finishedsqft_rooms','bed_bath','history','lot_sqft','lot_finish'
	             ]]
	    Y = df_sf['adjusted_price_m']
	    n = pd.get_dummies(df_sf.group)
	    X = pd.concat([X, n], axis=1)
	    
	    rf = RandomForestRegressor(n_estimators=40, max_depth=5)
	    model_rf = rf.fit(X, Y)
	    
	    D_sf = D[['bathrooms','bedrooms','finishedsqft','totalrooms','finishedsqft_rooms','bed_bath','history','lot_sqft','lot_finish',
	          'group1','group2','group3']]
	    pred = model_rf.predict(D_sf)
	else:
	    df_condo = df[df.usecode == 'condo.csv']
	    X = df_condo[['bathrooms','bedrooms','finishedsqft','finishedsqft_rooms','bathbed','history','lot_finish','finishedsqftrooms'
	          ]]
	    Y = df_condo['adjusted_price_m']
	    n = pd.get_dummies(df_condo.group)
	    X = pd.concat([X, n], axis=1)

	    rf = RandomForestRegressor(n_estimators=40, max_depth=5)
	    model_rf = rf.fit(X, Y)
	    
	    D_condo = D[['bathrooms','bedrooms','finishedsqft','finishedsqft_rooms','bathbed','history','lot_finish','finishedsqftrooms',
	          'group1','group2','group3']]
	    pred = model_rf.predict(D_condo)
	    
	estimation = round(pred,2)

	df = df[df.finishedsqft >= 0.8*x[0]]
	df = df[df.finishedsqft <= 1.2*x[0]]
	df = df[df.bedrooms==x[3]]
	df = df[df.bathrooms==x[4]]
	df = df[df.neighborhood==x[6]]
	df = df[df.totalrooms ==x[5]]
	df.sort(columns='date')

	est_low = round(min(df.adjusted_price/1000000.0),2)

	est_high = round(max(df.adjusted_price/1000000.0),2)

	address1 = df.iloc[0,1]
	address2 = df.iloc[1,1]
	address3 = df.iloc[2,1]
	address = [address1, address2, address3]

	price1 = 'Last sold price: '+str(df.iloc[0,23]/1000000.0)+' million'
	price2 = 'Last sold price: '+str(df.iloc[1,23]/1000000.0)+' million'
	price3 = 'Last sold price: '+str(df.iloc[2,23]/1000000.0)+' million'
	price = [price1,price2,price3]

	date1 = 'Last sold date: '+df.iloc[0,19]
	date2 = 'Last sold date: '+df.iloc[1,19]
	date3 = 'Last sold date: '+df.iloc[2,19]
	date = [date1,date2,date3]

	#get house id by address from api
	pic_url = []
	for e in address:
	    x = re.findall(r'Address: (.+)', e)[0]
	    address_url = urllib.quote(x)
	    url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?zws-id=X1-ZWz19t5ocjlyiz_2doog&address=' + address_url + '&citystatezip=San%20Francisco%2C+CA'
	    response = requests.get(url)
	    text = response.text
	    soup = BeautifulSoup(text)
	    
	    house_url = soup.find_all('homedetails')[0].text
	    response2 = requests.get(house_url)
	    text2 = response2.text
	    soup2 = BeautifulSoup(text2)
	    try:
	    	pic_url += [soup2.find_all('img', {'class':'hip-photo'})[0]['src']]
	    except IndexError:
	    	pic_url += ['https://www.drphillipscenter.org/resources/images/default.jpg']

	estimation_s = str(estimation)+' million'
	est_range = str(est_low) + ' million'+' to '+str(est_high)+' million'
	results = {"estimation": estimation_s, "address": address, 'pic': pic_url, 'estimated_range':est_range, 'price': price,'date':date, 'words':'Previously sold houses in neighborhood'}
	return flask.jsonify(results)

app.run()