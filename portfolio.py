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
from pandas.plotting import register_matplotlib_converters
from datetime import date
from termcolor import colored
import os
register_matplotlib_converters()


#FUNCTIONS=====================================================================


def download_stocks(stocks, start, end):
    '''
    Function that downloads stocks from yahoo finance.
    Inputs:
      stocks: list of quote or symbol (stock abbreviation)
      start: starting date in string format like: 'YYYY-MM-DD'
      end: ending date in string format like: 'YYYY-MM-DD'
    Output:
      Saves all downloaded stock information to file named df.csv 
    '''
    data = pd.DataFrame()
    df = pd.DataFrame()
    i = 1
    for stock in stocks:
        print( i ,"out of:",len(stocks),"(",stock,")")
        if i == 1:
            df = pd.DataFrame(web.DataReader(stock, data_source='yahoo', start=start, end=end))
            df['symbol']=stock
        else:
            temp = pd.DataFrame(web.DataReader(stock, data_source='yahoo', start=start, end=end))
            temp['symbol'] = stock
            df = df.append(temp)
        i += 1
        sleep(0.01)
    df.to_csv('df.csv', encoding = 'utf-8')
    pass

def execute_query(db,queries):
    '''
    Function for executing sql queries to local sql database.
    Inputs:
      db: local database name as string
      queries: list of query strings the connection will execute
    Output:
      No output: executes queries directly to database and commit changes
    '''
    try:        
        conn = sqlite3.connect(db)
#        print("Connected to SQLITE Database stock.db")
    except:
        print("Error connecting to stock.db database.")
    for query in queries:
        conn.execute(query)
        conn.commit()
    conn.close()

def get_query(db,query):
    '''
    Function for executing sql query and returning results in pandas dataframe format
    Inputs:
      db: local database name as string
      query: string with select statement
    Output:
      Return dataframe with resulting query
    '''
    try:
        conn = sqlite3.connect(db)
    except:
        print("Error connecting to stock.db database.")
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

def delete_history_sql(stocks, start, end):
    '''
    Function that deletes information from sql database to avoid having duplicates. Done before adding new information.
    Inputs:
      stocks: stock symbols/quotes in list form that will be deleted
      start: starting date of rows that will be deleted
      end: ending date of rows that will be deleted
    Output:
      No output: executes queries directly to database and commit changes
    '''
    query=[]
    query.append("DELETE FROM history WHERE symbol in ("+ str(stocks)[1:-1] + ") and date between '" + start + "' and '" + end + "';")
    print('Removing duplicates from database...')
    execute_query('stock.db',query)
    pass

def history_to_sql():
    '''
    Function that uploads stock information saved in df.csv (generated by download_stocks function.
    Inputs:
      No inputs: reads df.csv by default
    Output:
      No output: executes queries directly to database and commit changes
    '''
    with open('df.csv') as f: 
        reader = csv.reader(f)
        lines = list(reader)    
#    queries_duplicates=[]
    queries=[]
    for line in lines[1:]:
#        queries_duplicates.append("DELETE FROM history WHERE date='" + line[0] + "' and symbol = '" + line[7] + "';")
        queries.append("INSERT INTO history VALUES ('" + line[0] + "',"   + line[1] + ","   + line[2] + "," + line[3] + "," + line[4] + "," + line[5] + "," + line[6] + ",'" + line[7] + "');")
#    print('Removing duplicates from database...')
#    execute_query(db,queries_duplicates)
    print('Inserting items to database...')
    execute_query('stock.db',queries)
    pass

def scrape(stocks,times):
    '''
    Function that scrapes yahoo finance and downloads recommendation and price to local sql database.
    Inputs:
      stocks: stock symbols/quotes in list form that will be scraped
      times: number of times each stock will be scraped every half second
      db: stock.db default local database
    Output:
      Recommendation and live stock price
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    for i in range(times):
        for stock in stocks:
            url='https://finance.yahoo.com/quote/'+ stock
            response = requests.get(url,headers=headers)
            text = BeautifulSoup(response.text, 'html.parser')
            TitleTags = text.find_all('span',{'class':"Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"})
            x = float((TitleTags[0].string).replace(",",""))
            try:
                recommendation = text.find_all('span',{'class':['Fz(14px) Fw(b) C($positiveColor)','Fz(14px) Fw(b) C($primaryColor)','Fz(14px) Fw(b) C($c-fuji-orange-a)']})
                recommendation = str(recommendation[0].string)
            except:
                recommendation='NA'
            query_list=[]
            query2="delete from status where symbol='" + stock + "';"
            query_list.append(query2)
            query3="insert into status values ('" + recommendation  + "','" + stock + "');"
            query_list.append(query3)
            query = "INSERT INTO live VALUES (datetime('now','localtime'),"        + str(x) + ",'" + stock + "');"
            query_list.append(query)
            execute_query('stock.db',query_list)
            sleep(.5)
    pass


#LIVE GRAPH =========================================================================================================


def graph(stock,n):
    '''
    Function that graphs one of the scraped stocks live. Each function executes one graph. For multiple graphs
      just run separate functions with different symbols/quotes.
    Inputs:
      stock: symbol/quote of selected stock
      n: number of times to update graph every 1 second
    Output:
      Graph is displayed in separate window.
    '''
    plt.ion()
    for i in range(n):
        df = get_query('stock.db',"Select * from live where symbol in ('" + str(stock[0]) + "');")
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        y = df.loc[df.symbol==stock[0]]['open']
        plt.clf()
        plt.plot(y)
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.title('Live '+ str(stock[0]) + " Data")
        plt.draw()
        plt.pause(1)
    pass


def process_stocks(stocks_to_track, start, end):
    '''
    Function that downloads to dataframe the quotes so that further analysis can be done.
    Inputs:
      stocks_to_track: list of symbols/quotes
      start: starting date
      end: ending date
    Output:
      Pandas dataframe with selected symbols in the particular range of dates.
    '''
    stocks = "', '".join(stocks_to_track)
    query = "select date, symbol, adjclose from history where symbol in ('" + stocks + "') and date between '" + start + "' and '" + end + "';"
    data = get_query('stock.db',query)
    data = data.set_index('date')
    data = data[['symbol','adjclose']].pivot(columns='symbol')['adjclose']
    return data[stocks_to_track]


def montecarlo(stocks, start, end, riskFreeRate, n=50000, graph=True):
    '''
    Function that runs random weight simulation for that range of stocks.
    Credit to #Bradford Lynch, 2015, Ann Arbor, MI
    Inputs:
      stocks: symbols/quotes of selected stocks
      start: starting date
      end: ending date
      riskFreeRate: annual rate of return of a risk free such as the 10 year treasury
      n: ammount of random simulations
      graph: if True, a graph with the simulations will be displayed
    Output:
      sharpe_portfolio: portfolio with best sharpe ratio from simulation
      min_variance_port: portfolio with minimum variance from simulation
    '''
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
    portfolio_dict = {'Returns': port_returns,
                 'Volatility': port_volatility,
                 'Sharpe Ratio': sharpe_ratio}

    # extend original dictionary to accomodate each ticker and weight in the portfolio
    for counter,symbol in enumerate(stocks):
        portfolio_dict[symbol+' Weight'] = [Weight[counter] for Weight in stock_weights]

    # make a nice dataframe of the extended dictionary
    df = pd.DataFrame(portfolio_dict)

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


def monitor(stocks_to_track,my_portfolio,my_weights,n,sleep_time=0.5):
    '''
    Function that monitors selected stocks in a simple dashboard.
    Inputs:
      my_portfolio: stocks that are part of portfolio
      my weights: weigts of portfolio. Sum has to be 1.
      n: times dashboard is going to be updated if time is activated at the end of the function.
      sleep_time: time it waits to refresh screen after downloading each stock indicators
    Output:
      Console dashboard.
    '''
    print("\n" * 100)

    for i in range(n):

        current_year = date.today().year
        query = "select date from history where date>= '" + str(current_year) + "-01-01' order by date limit 1;"
        first_day_year = get_query('stock.db',query)
        first_day_year=first_day_year.iloc[0,0]

        query = "select max(date) from history;"
        latest_date = get_query('stock.db',query)
        latest_date = latest_date.iloc[0,0]

        query = "select distinct(date) from history where date < '" + str(latest_date) + "' order by date desc limit 1 offset 20;"
        month_date = get_query('stock.db',query)
        month_date = month_date.iloc[0,0]

        query = 'select symbol, volume, adjclose as opening from history where symbol in ('+str(stocks_to_track)[1:-1]+') and date = (select max(date) from history);'
        summary = get_query('stock.db',query)
        summary = summary.set_index('symbol')

        query = "select symbol, adjclose as start_of_year from history where symbol in ("+str(stocks_to_track)[1:-1]+") and date = '"+str(first_day_year)+"';"
        temp1 = get_query('stock.db',query)
        temp1 = temp1.set_index('symbol')

        query = "select symbol, adjclose as month_ago from history where symbol in ("+str(stocks_to_track)[1:-1]+") and date = '"+str(month_date)+"';"
        temp2 = get_query('stock.db',query)
        temp2 = temp2.set_index('symbol')

        query = "select symbol, recommendation from status where symbol in ("+str(stocks_to_track)[1:-1]+");"
        temp3 = get_query('stock.db',query)
        temp3 = temp3.set_index('symbol')

        query = "select symbol, open as now, date from live where (symbol, date) in (select symbol, max(date) from live group by symbol) and symbol in (" + str(stocks_to_track)[1:-1] + ");"
        temp4 = get_query('stock.db',query)
        temp4 = temp4.set_index('symbol')

        summary = summary.merge(temp1, how='left', left_index=True, right_index=True)
        summary = summary.merge(temp2, how='left', left_index=True, right_index=True)
        summary = summary.merge(temp3, how='left', left_index=True, right_index=True)
        summary = summary.merge(temp4, how='left', left_index=True, right_index=True)

        summary['weights'] = ''

        for stock, weight in zip(my_portfolio,my_weights):
            summary.at[stock, 'weights'] = weight
        #    yearly_growth = 

        query = "select max(date) as date from live;"
        date_updated = get_query('stock.db',query)
        date_updated = str(date_updated.iloc[0,0])

        #===========================================================

        print('STOCK MONITOR','\t'*4,'Updated: ',date_updated)
        print('-'*(13+13+16+9+len(date_updated)))

#        print("\n" * 100)
        print('My Portfolio')
        print('\t\t\t\t\t','d     ','m   ','ytd')
#        data_to_print=''
        a=0
        i=0
        for stock in my_portfolio:
            if summary.loc[stock]['recommendation']=='BUY':
                status = '\x1b[6;30;42m' + 'BUY ' + '\x1b[0m'
            else:
                status = '\x1b[6;37;41m' + summary.loc[stock]['recommendation'] + '\x1b[0m'

            a += ((summary.loc[stock]['now']/summary.loc[stock]['opening'] -1))*my_weights[i]
            i+=1
            
            if (summary.loc[stock]['now']/summary.loc[stock]['opening'] -1)>=0:
                increase = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),2)) + "%"),'green')
            else:
                increase = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),2)) + "%"),'red')

            if (summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1)>=0:
                increase_month = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),2)) + "%"),'green')
            else:
                increase_month = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),2)) + "%"),'red')


            if (summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1)>=0:
                increase_year = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),2)) + "%"),'green')
            else:
                increase_year = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),2)) + "%"),'red')
            #print(stock,"\t Status:",status,'\t','Price:',round(float(summary.loc[stock]['now']),1)," ",  increase, '\t', increase_month, '\t', increase_year)
            print("{:<8} {:<5} {:<10} {:<6} {:<8} {:<12} {:<12} {:<12}".format(stock,'Status:',status,'Price:',round(float(summary.loc[stock]['now']),2),increase,increase_month,increase_year))

 #           data_to_print += "{:<8} {:<5} {:<10} {:<6} {:<8} {:<12} {:<12} {:<12}.format(" + stock + ", Status: ,"+ status + ", Price: ," + str(round(float(summary.loc[stock]['now']),1)) + "," + str(increase) + "," + str(increase_month) + "," + str(increase_year) + "\n"
#        print(repr(data_to_print))
        a=round((1+a)**250-1,3)
        if a>0:
            print("Today's Annualized Change:" + '\x1b[6;30;42m' + str(a) + "%" + '\x1b[0m')
        else:
            print("Today's Annualized Change:" + '\x1b[6;37;41m' + str(a) + "%" + '\x1b[0m')

#        print("Today's Annualized Change:", a,"%")

        print('-'*(13+13+16+9+len(date_updated)))
        print('Other Stocks\n')


        rest=set(stocks_to_track).difference(set(my_portfolio))

        for stock in rest:
            if summary.loc[stock]['recommendation']=='BUY':
                status = '\x1b[6;30;42m' + 'BUY ' + '\x1b[0m'
            else:
                status = '\x1b[6;37;41m' + summary.loc[stock]['recommendation'] + '\x1b[0m'

            if (summary.loc[stock]['now']/summary.loc[stock]['opening'] -1)>=0:
                increase = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),2)) + "%"),'green')
            else:
                increase = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),2)) + "%"),'red')

            if (summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1)>=0:
                increase_month = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),2)) + "%"),'green')
            else:
                increase_month = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),2)) + "%"),'red')


            if (summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1)>=0:
                increase_year = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),2)) + "%"),'green')
            else:
                increase_year = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),2)) + "%"),'red')
            #print(stock,"\t Status:",status,'\t','Price:',round(float(summary.loc[stock]['now']),1)," ",  increase, '\t', increase_month, '\t', increase_year)
            print("{:<8} {:<5} {:<10} {:<6} {:<8} {:<12} {:<12} {:<12}".format(stock,'Status:',status,'Price:',round(float(summary.loc[stock]['now']),2),increase,increase_month,increase_year))
        print('\n')
        scrape(stocks_to_track,1)

        sleep(sleep_time)



