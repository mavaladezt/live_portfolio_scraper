import numpy as np
import pandas as pd 
#import scipy.optimize as sco
import pandas_datareader.data as web
from time import sleep
import wget
from random import sample
import sqlite3
from bs4 import BeautifulSoup
import requests
import re
import matplotlib.pyplot as plt
import datetime
import csv 


#==========REVIEWED CODE =============================================================


def download_stocks(stocks, start, end):
    data = pd.DataFrame()
    df = pd.DataFrame()
    i = 1
    for stock in stocks:
        print( i ,"out of:",len(stocks)+1,"(",stock,")")
        if i == 1:
            df = pd.DataFrame(web.DataReader(stock, data_source='yahoo', start=start, end=end))
            df['symbol']=stock
        else:
            temp = pd.DataFrame(web.DataReader(stock, data_source='yahoo', start=start, end=end))
            temp['symbol'] = stock
            df = df.append(temp)
        i += 1
        sleep(0.1)
    df.to_csv('df.csv', encoding = 'utf-8') 
#    return df
    pass


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


def history_to_sql(db):
    with open('df.csv') as f: 
        reader = csv.reader(f)
        lines = list(reader)    
    queries_duplicates=[]
    queries=[]
    for line in lines[1:]:
        queries_duplicates.append("DELETE FROM history WHERE date='" + line[0] + "' and symbol = '" + line[7] + "';")
        queries.append("INSERT INTO history VALUES ('" + line[0] + "',"   + line[1] + ","   + line[2] + "," + line[3] + "," + line[4] + "," + line[5] + "," + line[6] + ",'" + line[7] + "');")
    print('Removing duplicates from database...')
    execute_query(db,queries_duplicates)
    print('Inserting items to database...')
    execute_query(db,queries)
    pass


def scrape(stocks,times,db):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    for i in range(times):

        for stock in stocks:
            t = datetime.datetime.now()
            t_string = str(t.year) + "-" + str(t.month) + "-" + str(t.day) + " " + str(t.hour) + ":" + str(t.minute)+ ":" + str(t.second)
            url='https://finance.yahoo.com/quote/'+ stock
            response = requests.get(url,headers=headers)
            text = BeautifulSoup(response.text, 'html.parser')
            TitleTags = text.find_all('span',{'class':"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
            x = float((TitleTags[0].string).replace(",",""))

            try:
                recommendation = text.find_all('span',{'class':['Fz(14px) Fw(b) C($positiveColor)','Fz(14px) Fw(b) C($primaryColor)','Fz(14px) Fw(b) C($c-fuji-orange-a)']})
                recommendation = str(recommendation[0].string)
                print(recommendation)
            except:
                recommendation='NA'
            query_list=[]
            query2="delete from status where symbol='" + stock + "';"
            query_list.append(query2)
            query3="insert into status values ('" + recommendation  + "','" + stock + "');"
            query_list.append(query3)
            query = "INSERT INTO live VALUES (datetime('now','localtime'),"        + str(x) + ",'" + stock + "');"
#            query = "INSERT INTO live VALUES (datetime('" + t_string + "'),"  + str(x) + ",'" + stock + "');"
#            query = "INSERT INTO live VALUES (datetime('" + t_string + "'),"  + str(x) + ",'" + stock + "');"
            query_list.append(query)
            execute_query(db,query_list)
            sleep(1)
    pass


#LIVE GRAPH =========================================================================================================


def graph(stock):
    plt.ion()
    n=20
#    if len(port)==1:
    for i in range(n):
        df = get_query(db,"Select * from live where symbol in ('" + str(portfolio[0]) + "');")
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        #print(stock)
        y = df.loc[df.symbol==stock[0]]['open']
        plt.clf()
        plt.plot(y)
        plt.draw()
        plt.pause(1)
    pass

def process_stocks(stocks_to_track, start, end):
    stocks = "', '".join(stocks_to_track)
    query = "select date, symbol, adjclose from history where symbol in ('" + stocks + "') and date between '" + start + "' and '" + end + "';"
    data = get_query(db,query)
    data = data.set_index('date')
    data = data[['symbol','adjclose']].pivot(columns='symbol')['adjclose']
    return data[stocks_to_track]


#UPDATE DATABASE ==================================================================================
#DOWNLOAD ALL STOCKS
db='stock.db'
with open('symbols.csv','r') as f:
    stocks = f.read().splitlines()
    stocks = stocks[1:]
#start = '2019-01-01'
#end = '2019-12-31'

stocks_to_track=['AAPL','AMZN','MSFT','KLAC']

#weights = [0.5,0.5]
#download_stocks(stocks, start, end)
#history_to_sql()


data=process_stocks(stocks, '2019-01-01', '2019-10-24')



scrape(stocks_to_track,10,'stock.db')
portfolio = ['AAPL']

graph(['AAPL'])




data = data.iloc[:,(~data.isna().any()).values]  



#=======================REVISAR TODOS ESTOS CALCULOS


#stock_returns = (data - data.shift(1)) / data
#stock_returns = stock_returns.iloc[1:,]
#covMatrix = np.cov(stock_returns,rowvar=False,ddof=0)

returns_daily = data.pct_change()
returns_annual = (returns_daily.mean()+1) ** 250 -1
sd = (returns_daily.std())

riskFreeRate = 1.75/100 #10 year treasury bond

sharpe = (returns_daily.mean()-(riskFreeRate)*(1/250))/(returns_daily.std())


#http://onlyvix.blogspot.com/2010/08/simple-trick-to-convert-volatility.html
cov_daily = returns_daily.cov()
#cov_annual = cov_daily * np.sqrt(250)
cov_annual = cov_daily * 250

summary=pd.DataFrame()

summary['sd']=sd
summary['sharpe']=sharpe
#summary['daily_return']=returns_daily
summary['daily_return']=returns_daily.mean()
summary.sort_values(by=['sharpe'], ascending=False, inplace=True)
summary.to_csv('summary.csv')































stocks=['MSFT','MAA','KLAC','AAPL']
data[stocks]
returns_daily = data[stocks].pct_change()
returns_annual = (returns_daily.mean()+1) ** 250 -1

cov_daily = returns_daily.cov()
#cov_annual = cov_daily * np.sqrt(250)
cov_annual = cov_daily * 250



# empty lists to store returns, volatility and weights of imiginary portfolios
port_returns = []
port_volatility = []
stock_weights = []

# set the number of combinations for imaginary portfolios
num_assets = len(stocks)
num_portfolios = 50000

# populate the empty lists with each portfolios returns,risk and weights
for single_portfolio in range(num_portfolios):
    weights = np.random.random(num_assets)
    weights /= np.sum(weights)
    returns = np.dot(weights, returns_annual)
    volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
    port_returns.append(returns)
    port_volatility.append(volatility)
    stock_weights.append(weights)

# a dictionary for Returns and Risk values of each portfolio
portfolio = {'Returns': port_returns,
             'Volatility': port_volatility}

# extend original dictionary to accomodate each ticker and weight in the portfolio
for counter,symbol in enumerate(stocks):
    portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]

# make a nice dataframe of the extended dictionary
df = pd.DataFrame(portfolio)

# get better labels for desired arrangement of columns
column_order = ['Returns', 'Volatility'] + [stock+' Weight' for stock in stocks]

# reorder dataframe columns
df = df[column_order]

# plot the efficient frontier with a scatter plot
plt.style.use('seaborn')
df.plot.scatter(x='Volatility', y='Returns', figsize=(10, 8), grid=True)
plt.xlabel('Volatility (Std. Deviation)')
plt.ylabel('Expected Returns')
plt.title('Efficient Frontier')
plt.show()










































































def graph(portfolio,weights):
    weights=np.array(weights)
    plt.ion()
    n=20
#    if len(portfolio)==1:
        for i in range(n):
            stocks = "', '".join(portfolio)
            df = get_query(db,"Select * from live where symbol in ('" + str(one_stock[0]) + "');")
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            y = df.loc[df.symbol=='AAPL']['open']
            plt.clf()
            plt.plot(y)
            plt.draw()
            plt.pause(1)











def evaluate_portfolio(weights, stock_returns, covMatrix, riskFreeRate=0.01):
#In finance, the Sharpe ratio measures the performance of an investment
# compared to a risk-free asset, after adjusting for its risk. It is defined
# as the difference between the returns of the investment and the risk-free
# return, divided by the standard deviation of the investment. Wikipedia
#A negative Sharpe ratio means that the performance of a manager or portfolio
# is below the risk-free rate. For financial assets, negative Sharpe ratios
# won't persist for indefinite periods of time.
    portReturn = np.sum( stock_returns*weights )
#    portStdDev = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights)))
#    portStdDev = np.sqrt((weights.T@(covMatrix@weights)))
    portStdDev = (1/np.sum(np.linalg.inv(covMatrix)))**.5
#    sharpe_ratio = (portReturn-riskFreeRate)/portStdDev
    return portReturn, portStdDev


riskFreeRate = 1.75/100 #10 year treasury bond

