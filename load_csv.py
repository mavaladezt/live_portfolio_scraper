from time import sleep
import wget
import numpy as np
import pandas as pd
from random import sample
import sqlite3
from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt
import datetime

#DATABASE CONNECTIONS ==========================================================================================================================

db = 'stock.db'

def execute_query(db,queries):
    try:
        
        conn = sqlite3.connect(db)
        print("Connected to SQLITE Database stocks.db")
    except:
        print("Error connecting to stocks.db database.")
    for query in queries:
        conn.execute(query)
        conn.commit()
    conn.close()

def get_query(db,query):
    try:
        conn = sqlite3.connect(db)
#        print("Connected to SQLITE Database stocks.db")
    except:
        print("Error connecting to stocks.db database.")
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result


#LOAD HISTORY ==========================================================================================================================

def download_history(start,end):
    with open('symbols.csv','r') as f:
       symbols= f.read().splitlines()

    file_path = './Download/'

    n=len(symbols)

    for symbol in symbols:
        print("\nDownloading:",symbol)
        url = "http://quotes.wsj.com/" + symbol + "/historical-prices/download?MOD_VIEW=page&num_rows=6299&startDate=" + start + "&endDate=" + end
        file_name = file_path + symbol + ".csv"
        wget.download(url, file_name)
        sleep(0.003)

        i=1
        file_to_open = file_path + symbol + '.csv'
        content_list=[]
        with open(file_to_open,'r') as f:
            line = f.readline()
            while line:
                content_list.append(line.replace(",", "").split())
                line = f.readline()
        content_list = content_list[1:]
        queries=[]
        for line in content_list:
            query = "INSERT INTO history VALUES ('" + '20' + line[0][6:9] + "-" + line[0][0:2] + "-" + line[0][3:5] + "'," + line[1] + "," + line[2] + "," + line[3]+ "," + line[4] + "," + line[5] + ",'" + symbol + "'," + str(float(line[4])/float(line[1])-1) + ");"
            queries.append(query)
        execute_query(db,queries)
        print('Status:', round(100*i/n,2),"%")
        i+=1

    pass



def upload_history():
    with open('symbols.csv','r') as f:
       symbols= f.read().splitlines()

    file_path = './Download/'

#    n=len(symbols)

    for symbol in symbols:
        i=1
        file_to_open = file_path + symbol + '.csv'
        content_list=[]
        with open(file_to_open,'r') as f:
            line = f.readline()
            while line:
                content_list.append(line.replace(",", "").split())
                line = f.readline()
        content_list = content_list[1:]
        queries=[]
        for line in content_list:
            query = "INSERT INTO history VALUES ('" + '20' + line[0][6:9] + "-" + line[0][0:2] + "-" + line[0][3:5] + "'," + line[1] + "," + line[2] + "," + line[3]+ "," + line[4] + "," + line[5] + ",'" + symbol + "'," + str(float(line[4])/float(line[1])-1) + ");"
            queries.append(query)
        execute_query(db,queries)
        print('Status:', round(100*i/n,2),"%")
        i+=1

    pass



#EVALUATE PORTFOLIO===================================================================================================================




query = "SELECT date, symbol, growth FROM history WHERE date>'2019-09-30';"

test = get_query(db,query)

#test=test[test.index>'2019-09-30']

test=test.pivot(index='date', columns='symbol')['growth']

test=test[test.columns[np.sum(pd.isna(test),axis=0)==0]]


test.shape
n,c=test.shape

variance=[]
for i in test.columns:
    variance.append(np.std(test[i])**2)

variance=np.array(variance)




covariances=np.cov(test,rowvar=False,ddof=0)
np.fill_diagonal(covariances, variance)


weights = np.sum(np.linalg.inv(covariances),axis=0)/np.sum(np.sum(np.linalg.inv(covariances),axis=0))



rendimiento=np.sum(np.mean(test,axis=0)*weights)               #in percent
rendimiento_anualizado=(1+rendimiento)**(252-1)-1              #in percent
if np.sum(np.linalg.inv(covariances))<0:
    volatilidad=0
else:
    volatilidad = 100*(1/np.sum(np.linalg.inv(covariances)))**.5   #in percent
#np.sum(covariances,axis=0)


#columnas I want to keep
#np.sum(pd.isna(test),axis=0)==0


#len(test.columns)
#sample(list(range(1,11)),3)


#SCRAPING =========================================================================================================


def scrape(stocks,times):

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    for i in range(times):
        t = datetime.datetime.now()
        t_string = str(t.year) + "-" + str(t.month) + "-" + str(t.day) + " " + str(t.hour) + ":" + str(t.minute)+ ":" + str(t.second)
        for stock in stocks:
            url='https://finance.yahoo.com/quote/'+ stock
            response = requests.get(url,headers=headers)
            text = BeautifulSoup(response.text, 'html.parser')
            TitleTags = text.find_all('span',{'class':"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
            x = float(TitleTags[0].string)
            query_list=[]
#            query = "INSERT INTO live VALUES (datetime('now','localtime'),"        + str(x) + ",'" + stock + "');"
            query = "INSERT INTO live VALUES (datetime('" + t_string + "'),"  + str(x) + ",'" + stock + "');"
            query_list.append(query)
            execute_query(db,query_list)
            sleep(1)
        #sleep(0.5)

#'2007-01-01 10:00:00'
#yyyy-MM-dd HH:mm:ss




#LIVE GRAPH =========================================================================================================




def graph(portfolio,weights=0):
    plt.ion()
    n=20
    if len(portfolio)==1:
        for i in range(n):
            df = get_query(db,"Select * from live where symbol in ('" + str(one_stock[0]) + "');")
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            y = df.loc[df.symbol=='AAPL']['open']
            plt.clf()
            plt.plot(y)
            plt.draw()
            plt.pause(1)







#RUNNING FUNCTIONS =========================================================================================================

start = '10/19/2019'
end= '10/22/2019'
#download_history(start,end)
#upload_history()
#DELETE FROM history WHERE date>'2019-10-18';

#DELETE FROM live WHERE date>'2019-01-01';
stocks=['AAPL','MSFT']
times=2

scrape(stocks,times)

df = get_query(db,"Select * from live where symbol in ('" + str(one_stock[0]) + "');")
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')
y = df.loc[df.symbol=='AAPL']['open']



portfolio = ['AAPL','MSFT']
one_stock = ['AAPL']
graph(one_stock)



#aqui me quede, esta funcion hay que cargarla en la de graph() despues ver la forma de multiplicarlo por el weight

text= "'" + portfolio[0] + "','"
for i in range(1,len(portfolio)):
    text =  text + portfolio[i] + "',"
    print(text)
text=text[:-1]




