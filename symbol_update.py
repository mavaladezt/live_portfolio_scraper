from time import sleep
import wget
import numpy as np
import pandas as pd
from random import sample
import sqlite3
from bs4 import BeautifulSoup
import requests
import re

with open('symbols.csv','r') as f:
   symbols= f.read().splitlines()

#print(symbols)

n=len(symbols)

def download_history(start,end,symbols):
    for symbol in symbols:
        print("Downloading:",symbol)
        url = "http://quotes.wsj.com/" + symbol + "/historical-prices/download?MOD_VIEW=page&num_rows=6299&startDate=" + start_date + "&endDate=" + end_date
        file_name = "./Download/" + symbol + ".csv"
        wget.download(url, file_name)
        sleep(0.5)
    pass

#Download all files
start = '10/20/2019'
end= '10/20/2019'
download_history(start,end,symbols)

#Read files and load it to database





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

db = 'stock.db'

#queries=["INSERT INTO history VALUES ('1/1/2019', 1, 2,3,4,5000,'APPL',0.30);","INSERT INTO history VALUES ('1/1/2019', 1, 2,3,4,5000,'APPL',0.40);"]

#execute_query(db,queries)

#check available tables
#res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
#for name in res:
#    print (name[0])

#results=conn.execute("SELECT * FROM history;")



file_path = './Download/'
n=len(symbols)
i=1
for symbol in symbols:
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
#        query = "INSERT INTO history VALUES ('" + line[0] + "'," + line[1] + "," + line[2] + "," + line[3]+ "," + line[4] + "," + line[5] + ",'" + symbol + "'," + str(float(line[4])/float(line[1])-1) + ");"
        query = "INSERT INTO history VALUES ('" + '20' + line[0][6:9] + "-" + line[0][0:2] + "-" + line[0][3:5] + "'," + line[1] + "," + line[2] + "," + line[3]+ "," + line[4] + "," + line[5] + ",'" + symbol + "'," + str(float(line[4])/float(line[1])-1) + ");"
#        print(query)
        queries.append(query)
    execute_query(db,queries)
    print('Status:', round(100*i/n,2),"%")
    i+=1



#Get data query

def get_query(db,query):
    try:
        conn = sqlite3.connect(db)
        print("Connected to SQLITE Database stocks.db")
    except:
        print("Error connecting to stocks.db database.")
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

db = 'stock.db'
#query = "SELECT date, symbol, growth FROM history ORDER BY date, symbol;"
#query = "SELECT date, symbol, growth FROM history WHERE symbol IN ('MSFT','AAPL','AMZN');"
#query = "SELECT date, symbol, growth FROM history WHERE date>'2019-09-30' AND symbol IN ('MSFT','AAPL','AMZN');"
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
#print(variance)
variance=np.array(variance)
#output_matrix=variance*np.eye(c)



covariances=np.cov(test,rowvar=False,ddof=0)
np.fill_diagonal(covariances, variance)

#weights=np.linalg.inv(np.fill_diagonal(covariances, variance))
weights = np.sum(np.linalg.inv(covariances),axis=0)/np.sum(np.sum(np.linalg.inv(covariances),axis=0))

#np.sum(covariances,axis=0)

rendimiento=np.sum(np.mean(test,axis=0)*weights)               #in percent
rendimiento_anualizado=(1+rendimiento)**(252-1)-1              #in percent
if np.sum(np.linalg.inv(covariances))<0:
    volatilidad=0
else:
    volatilidad = 100*(1/np.sum(np.linalg.inv(covariances)))**.5   #in percent
#np.sum(covariances,axis=0)


#columnas I want to keep
#np.sum(pd.isna(test),axis=0)==0


len(test.columns)
sample(list(range(1,11)),3)


#====================================================================





headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

stocks=['AAPL','MSFT']

for stock in stocks:
    url='https://finance.yahoo.com/quote/'+ stock
    response = requests.get(url,headers=headers)
    text = BeautifulSoup(response.text, 'html.parser')
    TitleTags = text.find_all('span',{'class':"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
    x = float(TitleTags[0].string)
    query_list=[]
    query = "INSERT INTO live VALUES (datetime('now','localtime'),"+ str(x) + ",'" + stock + "');"
    query_list.append(query)
    execute_query(db,query_list)
    sleep(2)

test2 = get_query(db,"Select * from live;")
test2

