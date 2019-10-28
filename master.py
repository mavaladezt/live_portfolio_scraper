from datetime import date
from termcolor import colored
#db='stock.db'
start = '2015-01-01'
end = '2019-12-31'
riskFreeRate = 1.75/100 #10 year treasury bond

#LOAD ALL S&P 500
#with open('symbols.csv','r') as f:
#    stocks = f.read().splitlines()
#    stocks = stocks[1:]

#stocks = ['RSG','DUK','NEE','AEP','DTE']    #min volatility 2018-2019
#stocks = ['NEE','BLL','CMG','KEYS','ETR']  #max sharpe
#stocks = ['AMD','CMG','KEYS','EW','TDG']   #max return
#stocks = ['NEE','BLL','CMG','KEYS','TDG','TDG'] #most repeated ones
#stocks = ['AMZN','MSFT','AAPL']  #EXAMPLE

p_sharpe, min_variance_port = portfolio.montecarlo(stocks, start, end, riskFreeRate, 50000, True)
p_sharpe2, min_variance_port2 = portfolio.montecarlo(stocks, start, end, riskFreeRate, 50000, False)

#LOAD DATA
#data = portfolio.process_stocks(stocks, start, end)
#data = data.iloc[:,(~data.isna().any()).values]
#stocks = list(data.columns)

#SCRAPE SELECTED STOCKS
stocks_to_track = ['BLL','CMG','AEP','DTE','TDG','EW','DUK','AMZN','KEYS','AAPL','BA','FORD','MSFT','ETR','RSG','AMD','NEE']
my_portfolio = ['NEE','BLL','CMG','KEYS','ETR']
my_weights = [0.61,0.14,0.02,0.21,0.02]

portfolio.scrape(stocks_to_track,10,'stock.db')

#GRAPH A SPECIFIC STOCK
portfolio.graph(['AAPL'],5)





#stocks_to_track_dict = {}
#for stock in stocks_to_track:
#  stocks_to_track_dict[stock] = [0,0,0,0,0,0,0]
#str(stocks_to_track)[1:-1]

current_year = date.today().year
query = "select date from history where date>= '" + str(current_year) + "-01-01' order by date limit 1;"
first_day_year = portfolio.get_query('stock.db',query)
first_day_year=first_day_year.iloc[0,0]

query = "select max(date) from history;"
latest_date = portfolio.get_query('stock.db',query)
latest_date = latest_date.iloc[0,0]

query = "select distinct(date) from history where date < '" + str(latest_date) + "' order by date desc limit 1 offset 20;"
month_date = portfolio.get_query('stock.db',query)
month_date = month_date.iloc[0,0]


#query = 'select symbol, adjclose as ytd from history where symbol in ('+str(stocks_to_track)[1:-1]+') and date = (select max(date) from history);'
#temp = portfolio.get_query('stock.db',query)

query = 'select symbol, volume, adjclose as opening from history where symbol in ('+str(stocks_to_track)[1:-1]+') and date = (select max(date) from history);'
summary = portfolio.get_query('stock.db',query)
summary = summary.set_index('symbol')

query = "select symbol, adjclose as start_of_year from history where symbol in ("+str(stocks_to_track)[1:-1]+") and date = '"+str(first_day_year)+"';"
temp1 = portfolio.get_query('stock.db',query)
temp1 = temp1.set_index('symbol')

query = "select symbol, adjclose as month_ago from history where symbol in ("+str(stocks_to_track)[1:-1]+") and date = '"+str(month_date)+"';"
temp2 = portfolio.get_query('stock.db',query)
temp2 = temp2.set_index('symbol')

query = "select symbol, recommendation from status where symbol in ("+str(stocks_to_track)[1:-1]+");"
temp3 = portfolio.get_query('stock.db',query)
temp3 = temp3.set_index('symbol')

query = "select symbol, open as now, date from live where (symbol, date) in (select symbol, max(date) from live group by symbol) and symbol in (" + str(stocks_to_track)[1:-1] + ");"
temp4 = portfolio.get_query('stock.db',query)
temp4 = temp4.set_index('symbol')

summary = summary.merge(temp1, how='left', left_index=True, right_index=True)
summary = summary.merge(temp2, how='left', left_index=True, right_index=True)
summary = summary.merge(temp3, how='left', left_index=True, right_index=True)
summary = summary.merge(temp4, how='left', left_index=True, right_index=True)

summary['weights']=''

for stock, weight in zip(my_portfolio,my_weights):
    summary.at[stock, 'weights'] = weight

query = "select max(date) as date from live;"
date_updated = portfolio.get_query('stock.db',query)
date_updated = str(date_updated.iloc[0,0])

#===========================================================

print('STOCK MONITOR','\t'*4,'Updated: ',date_updated)
print('-'*(13+13+16+9+len(date_updated)))

print('My Portfolio\n')
for stock in my_portfolio:
    if summary.loc[stock]['recommendation']=='BUY':
        status = '\x1b[6;30;42m' + 'BUY' + '\x1b[0m'
    else:
        status = '\x1b[6;30;42m' + summary.loc[stock]['recommendation'] + '\x1b[0m'
    print(stock,"\t Status:",status,'\t','Price:',round(float(summary.loc[stock]['now']),2),  (1+(summary.loc[stock]['now']/summary.loc[stock]['opening'] -1)**250-1             ))

#    print("{:<8} {:<15} {:<10}".format('Symbol','Price','Number'))


print (colored('hello', 'red'), colored('world', 'green'))








temp2 = temp2.set_index('symbol')

#PONER DATE AND TIME UPDATED

print("{:<8} {:<15} {:<10}".format('Key','Label','Number'))

for k, v in d.iteritems():
    label, num = v
    print "{:<8} {:<15} {:<10}".format(k, label, num)

import shutil
shutil.get_terminal_size().columns
shutil.get_terminal_size().lines

from termcolor import colored
print (colored('hello', 'red'), colored('world', 'green'))
print('\x1b[6;30;42m' + 'BUY' + '\x1b[0m')

