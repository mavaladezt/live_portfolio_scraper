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

portfolio.download_stocks(['MSFT'], start, end)
portfolio.delete_history_sql(stocks, '2019-10-25', '2019-10-28')
portfolio.history_to_sql()


#DOWNLOAD HISTORY==============================================================================================


riskFreeRate = 1.75/100 #10 year treasury bond


#stocks = ['RSG','DUK','NEE','AEP','DTE']    #min volatility 2018-2019
stocks = ['NEE','BLL','CMG','KEYS','ETR']  #max sharpe
#stocks = ['AMD','CMG','KEYS','EW','TDG']   #max return
#stocks = ['NEE','BLL','CMG','KEYS','TDG','TDG'] #most repeated ones
#stocks = ['AMZN','MSFT','AAPL']  #EXAMPLE

start = '2019-01-01'
end = '2019-12-31'

p_sharpe, min_variance_port = portfolio.montecarlo(stocks, start, end, riskFreeRate, 50000, True)
#p_sharpe2, min_variance_port2 = portfolio.montecarlo(stocks, start, end, riskFreeRate, 50000, False)

#GRAPH A SPECIFIC STOCK
portfolio.graph(['AAPL'],5)

#LOAD DATA
#data = portfolio.process_stocks(stocks, start, end)
#data = data.iloc[:,(~data.isna().any()).values]
#stocks = list(data.columns)

#SCRAPE SELECTED STOCKS
stocks_to_track = ['BLL','CMG','AEP','DTE','TDG','EW','DUK','AMZN','KEYS','AAPL','BA','MSFT','ETR','RSG','AMD','NEE']
my_portfolio = ['NEE','BLL','CMG','KEYS','ETR']
my_weights = [0.61,0.14,0.02,0.21,0.02]

portfolio.monitor(stocks_to_track,my_portfolio,my_weights,15)

portfolio.scrape(stocks_to_track,10,'stock.db')













































































#stocks_to_track_dict = {}
#for stock in stocks_to_track:
#  stocks_to_track_dict[stock] = [0,0,0,0,0,0,0]
#str(stocks_to_track)[1:-1]

def monitor(stocks_to_track,my_portfolio,my_weights,n):
    for i in n:
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

        #(summary.loc[stock]['now']/summary.loc[stock]['opening'] -1)

        print('My Portfolio\n')
        for stock in my_portfolio:
            if summary.loc[stock]['recommendation']=='BUY':
                status = '\x1b[6;30;42m' + 'BUY ' + '\x1b[0m'
            else:
                status = '\x1b[6;37;41m' + summary.loc[stock]['recommendation'] + '\x1b[0m'

            if (summary.loc[stock]['now']/summary.loc[stock]['opening'] -1)>=0:
                increase = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),1)) + "%"),'green')
            else:
                increase = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),1)) + "%"),'red')

            if (summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1)>=0:
                increase_month = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),1)) + "%"),'green')
            else:
                increase_month = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),1)) + "%"),'red')


            if (summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1)>=0:
                increase_year = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),1)) + "%"),'green')
            else:
                increase_year = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),1)) + "%"),'red')
            #print(stock,"\t Status:",status,'\t','Price:',round(float(summary.loc[stock]['now']),1)," ",  increase, '\t', increase_month, '\t', increase_year)
            print("{:<8} {:<5} {:<10} {:<6} {:<8} {:<12} {:<12} {:<12}".format(stock,'Status:',status,'Price:',round(float(summary.loc[stock]['now']),1),increase,increase_month,increase_year))


        print('-'*(13+13+16+9+len(date_updated)))
        print('Other Stocks\n')

        rest=set(stocks_to_track).difference(set(my_portfolio))

        for stock in rest:
            if summary.loc[stock]['recommendation']=='BUY':
                status = '\x1b[6;30;42m' + 'BUY ' + '\x1b[0m'
            else:
                status = '\x1b[6;37;41m' + summary.loc[stock]['recommendation'] + '\x1b[0m'

            if (summary.loc[stock]['now']/summary.loc[stock]['opening'] -1)>=0:
                increase = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),1)) + "%"),'green')
            else:
                increase = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['opening'] -1),1)) + "%"),'red')

            if (summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1)>=0:
                increase_month = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),1)) + "%"),'green')
            else:
                increase_month = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['month_ago'] -1),1)) + "%"),'red')


            if (summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1)>=0:
                increase_year = colored((" " + str(round((summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),1)) + "%"),'green')
            else:
                increase_year = colored((" " + str(round(-(summary.loc[stock]['now']/summary.loc[stock]['start_of_year'] -1),1)) + "%"),'red')
            #print(stock,"\t Status:",status,'\t','Price:',round(float(summary.loc[stock]['now']),1)," ",  increase, '\t', increase_month, '\t', increase_year)
            print("{:<8} {:<5} {:<10} {:<6} {:<8} {:<12} {:<12} {:<12}".format(stock,'Status:',status,'Price:',round(float(summary.loc[stock]['now']),1),increase,increase_month,increase_year))
        sleep(1)

#a=colored('hello', 'red')
#print (a, colored('world', 'green'))








#temp2 = temp2.set_index('symbol')

#PONER DATE AND TIME UPDATED

#print("{:<8} {:<15} {:<10}".format('Key','Label','Number'))

#for k, v in d.iteritems():
#    label, num = v
#    print "{:<8} {:<15} {:<10}".format(k, label, num)

#import shutil
#shutil.get_terminal_size().columns
#shutil.get_terminal_size().lines

#from termcolor import colored
#print (colored('hello', 'red'), colored('world', 'green'))
#print('\x1b[6;30;42m' + 'BUY' + '\x1b[0m')

