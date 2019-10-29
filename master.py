from time import sleep

FUNCTIONS
download_stocks(stocks, start, end) #downloads data to df.csv
execute_query(db,queries) #executes queries in list form
get_query(db,query) #query as string, get back data frame
delete_history_sql(stocks, start, end)  #deletes all stocks in that range of dates
history_to_sql(db) #read df.csv and uploads data to sql history table
scrape(stocks,times,db) # stocks in list form, saves it in sql (live and status)
graph(stock, n)   #graph that want to display updated every n seconds
process_stocks(stocks_to_track, start, end) #list of stocks, start and end dates
montecarlo(stocks, start, end, riskFreeRate, n=50000, graph=True)
monitor(stocks_to_track,my_portfolio,my_weights,n)


#DOWNLOAD HISTORY==============================================================================================
#db='stock.db'
start = '2019-10-25'
end = '2019-10-25'

with open('symbols.csv','r') as f:
    stocks = f.read().splitlines()
    stocks = stocks[1:]

portfolio.download_stocks(stocks, start, end)
portfolio.delete_history_sql(stocks, '2019-10-25', '2019-10-28')
portfolio.history_to_sql()


#DOWNLOAD HISTORY==============================================================================================


riskFreeRate = 1.75/100 #10 year treasury bond


#stocks = ['RSG','DUK','NEE','AEP','DTE']    #min volatility 2018-2019
stocks = ['NEE','BLL','CMG','KEYS','ETR']  #max sharpe
#stocks = ['AMD','CMG','KEYS','EW','TDG']   #max return
#stocks = ['NEE','BLL','CMG','KEYS','TDG','TDG'] #most repeated ones
#stocks = ['AMZN','MSFT','AAPL']  #EXAMPLE
stocks = ['CHTR', 'ETR', 'MLM', 'CPRT', 'MAA']  #optimal

start = '2019-01-01'
end = '2019-10-30'

p_sharpe, min_variance_port = portfolio.montecarlo(stocks, start, end, riskFreeRate, 50000, True)
#p_sharpe2, min_variance_port2 = portfolio.montecarlo(stocks, start, end, riskFreeRate, 50000, False)

#GRAPH A SPECIFIC STOCK
portfolio.graph(['AAPL'],5)

#LOAD DATA
#data = portfolio.process_stocks(stocks, start, end)
#data = data.iloc[:,(~data.isna().any()).values]
#stocks = list(data.columns)

#SCRAPE SELECTED STOCKS
stocks_to_track = ['NEE','BLL','CMG','KEYS','ETR','AMZN','AAPL','MSFT']
my_portfolio = ['NEE','BLL','CMG','KEYS','ETR']
my_weights = [0.61,0.14,0.02,0.21,0.02]

portfolio.scrape(stocks_to_track,10,'stock.db')

portfolio.monitor(stocks_to_track,my_portfolio,my_weights,15)




#===========================================================================================================


