import numpy as np
import pandas as pd
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

#FUNCTIONS=====================================================================

def download_stocks(stocks, start, end):
    '''
    Function that downloads stocks from yahoo finance.
    Inputs:
      stocks: list of quote or symbol (stock abbreviation)
      start: starting date in string format like: 'YYYY-MM-DD'
      end: ending date in string format like: 'YYYY-MM-DD'
    '''
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


def graph(stock,n):
    plt.ion()
#    n=20
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


def montecarlo(stocks, start, end, riskFreeRate, n=50000, graph=True):
    data = process_stocks(stocks, start, end)
    data = data.iloc[:,(~data.isna().any()).values]
    stocks = list(data.columns)
    #data.to_csv('summary.csv')
    returns_daily = data.pct_change()
    returns_annual = (returns_daily.mean()+1) ** 250 -1
    sd = returns_daily.std()
    sharpe = (returns_daily-((1+riskFreeRate/100)**(1/250)-1)).mean()/(returns_daily-((1+riskFreeRate/100)**(1/250)-1)).std()
    #http://onlyvix.blogspot.com/2010/08/simple-trick-to-convert-volatility.html
    cov_daily = returns_daily.cov()
    cov_annual = cov_daily * np.sqrt(250)
    #cov_annual = cov_daily * 250
    summary=pd.DataFrame()
    summary['sd']=sd
    summary['sharpe']=sharpe
    summary['daily_return']=returns_daily.mean()
    summary.to_csv('summary.csv')

    # empty lists to store returns, volatility and weights of imiginary portfolios
    port_returns = []
    port_volatility = []
    stock_weights = []
    sharpe_ratio = []

    # set the number of combinations for imaginary portfolios
    num_assets = data.shape[1]
#    num_portfolios = 50000

    # populate the empty lists with each portfolios returns,risk and weights
    for single_portfolio in range(n):
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        returns = np.dot(weights, returns_annual)
        volatility = np.sqrt(np.dot(weights.T, np.dot(cov_annual, weights)))
        sharpe = returns / volatility
        sharpe_ratio.append(sharpe)
        port_returns.append(returns)
        port_volatility.append(volatility)
        stock_weights.append(weights)

    # a dictionary for Returns and Risk values of each portfolio
    portfolio = {'Returns': port_returns,
                 'Volatility': port_volatility,
                 'Sharpe Ratio': sharpe_ratio}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter,symbol in enumerate(stocks):
        portfolio[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio)

    # get better labels for desired arrangement of columns
    column_order = ['Returns', 'Volatility', 'Sharpe Ratio'] + [stock+' Weight' for stock in stocks]

    # reorder dataframe columns
    df = df[column_order]

    # plot the efficient frontier with a scatter plot
    #plt.style.use('seaborn')
    #df.plot.scatter(x='Volatility', y='Returns', figsize=(10, 8), grid=True)
    #plt.xlabel('Volatility (Std. Deviation)')
    #plt.ylabel('Expected Returns')
    #plt.title('Efficient Frontier')
    #plt.show()


    min_volatility = df['Volatility'].min()
    max_sharpe = df['Sharpe Ratio'].max()
    sharpe_portfolio = df.loc[df['Sharpe Ratio'] == max_sharpe]
    min_variance_port = df.loc[df['Volatility'] == min_volatility]

    if graph:
        plt.style.use('seaborn')
        df.plot.scatter(x='Volatility', y='Returns', c='Sharpe Ratio',
                        cmap=plt.cm.binary, edgecolors='black',figsize=(10, 8), grid=True)
#        plt.scatter(x=sharpe_portfolio['Volatility'], y=sharpe_portfolio['Returns'], c='black', marker='D', s=100)
#        plt.scatter(x=min_variance_port['Volatility'], y=min_variance_port['Returns'], c='black', marker='D', s=100 )
#        plt.yticks(np.arange(-.3, 1.2, step=0.1))
#        plt.xticks(np.arange(0.025, .13, step=0.025))
        plt.xlabel('Volatility')
        plt.ylabel('Expected Yearly Returns')
        plt.title('Montecarlo Simulation of '+ str(n) + " Random Weights")
        plt.show()

    return sharpe_portfolio, min_variance_port











db='stock.db'
start = '2015-01-01'
end = '2019-12-31'
riskFreeRate = 1.75/100 #10 year treasury bond

#stocks = ['RSG','DUK','NEE','AEP','DTE']    #min volatility 2018-2019
#stocks = ['NEE','BLL','CMG','KEYS','ETR']  #max sharpe
#stocks = ['AMD','CMG','KEYS','EW','TDG']   #max return
#stocks = ['NEE','BLL','CMG','KEYS','TDG','TDG'] #most repeated ones

p_sharpe, min_variance_port= montecarlo(stocks, start, end, riskFreeRate, 50000, True)

stocks = ['AMZN','MSFT','AAPL']  #EXAMPLE


with open('symbols.csv','r') as f:
    stocks = f.read().splitlines()
    stocks = stocks[1:]
data=process_stocks(stocks, start, end) #list of stocks, start and end dates
data = data.iloc[:,(~data.isna().any()).values]
stocks=list(data.columns)


p_sharpe2, min_variance_port2= montecarlo(stocks, start, end, riskFreeRate, 500000, False)












scrape(stocks_to_track,10,'stock.db')
portfolio = ['AAPL']
graph(['AAPL'])



