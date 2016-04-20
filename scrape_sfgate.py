import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import *

import requests
import pprint
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

def loadPage(url):

    page = QWebPage()
    loop = QEventLoop() 
    page.mainFrame().loadFinished.connect(loop.quit)
    page.mainFrame().load(QUrl(url))
    loop.exec_() 
    return page.mainFrame().toHtml()

app = QApplication(sys.argv)

for i in range(1,13): 
    #url = """http://www.sfgate.com/webdb/homesales/?appSession=62394121042939095974604243804125972115667225306241842463756579389539619617572902719647069617948654518042925562712294167607160157&RecordID=&PageID=2&PrevPageID=1&cpipage=""" +str(i)+'&CPISortType=&CPIorderBy='
    #url = 'http://www.sfgate.com/webdb/homesales/?appSession=95321263662334992584489562332295501542748135578959443742621858893452432463029521137221863603304156826975461352994264703512194626&RecordID=&PageID=2&PrevPageID=1&cpipage='+str(i)+'&CPISortType=&CPIorderBy='
    url = 'http://www.sfgate.com/webdb/homesales/?appSession=64329322129873111204574554973483280103329065656847042053181216317168570306162401356813312547725230111651362605283184354571771674&RecordID=&PageID=2&PrevPageID=1&cpipage='+str(i)+'&CPISortType=&CPIorderBy='

    html = loadPage(url)
    soup = BeautifulSoup(str(html.toAscii()))
    info = soup.find_all('font', {'face':"verdana"})

    print i, len(info)
    #c = 0
    df = pd.DataFrame()
    for e in info:
        time.sleep(1.0)
        #print c
        #c += 1
        data = {}
        house = e.text.split(',')
        #print house
        data['address'] = house[0]
        data['house_info'] = house[1]
        
        df = df.append(data, ignore_index=True)

    df.to_csv('sfdata.csv', mode='a+', header=False)

app.exit()

