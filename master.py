#db='stock.db'
start = '2015-01-01'
end = '2019-12-31'
riskFreeRate = 1.75/100 #10 year treasury bond

#LOAD ALL S&P 500
#with open('symbols.csv','r') as f:
#    stocks = f.read().splitlines()
#    stocks = stocks[1:]

#stocks = ['RSG','DUK','NEE','AEP','DTE']    #min volatility 2018-2019
stocks = ['NEE','BLL','CMG','KEYS','ETR']  #max sharpe
#stocks = ['AMD','CMG','KEYS','EW','TDG']   #max return
#stocks = ['NEE','BLL','CMG','KEYS','TDG','TDG'] #most repeated ones
#stocks = ['AMZN','MSFT','AAPL']  #EXAMPLE

p_sharpe, min_variance_port = portfolio.montecarlo(stocks, start, end, riskFreeRate, 50000, True)
p_sharpe2, min_variance_port2 = portfolio.montecarlo(stocks, start, end, riskFreeRate, 500000, False)

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




#CREAR DICCIONARIO CON MY_PORTFOLIO QUE TENGA
	#SYMBOL / STATUS / WEIGHT / INCREASE TODAY / 4 WEEKS / 6 MONTHS / 1 YEAR

#CREAR DICCIONARIO DE ACCIONES A DAR SEGUIMIENTO
	#SYMBOL / STATUS / INCREASE TODAY / 4 WEEKS / 6 MONTHS / 1 YEAR

#CHECAR PRETTY PRINT DE MI LIBRO

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
print('\x1b[6;30;42m' + 'Success!' + '\x1b[0m')
