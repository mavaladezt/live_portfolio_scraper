import pandas as pd
import numpy as np
import pandas_datareader.data as web
import matplotlib.pyplot as plt

def get_stock_information(stocks, start, end):
    '''
    Function that downloads stocks from yahoo finance.
    Inputs:
      stocks: list of quote or symbol (stock abbreviation)
      start: starting date in string format like: 'YYYY-MM-DD'
      end: ending date in string format like: 'YYYY-MM-DD'
    Output:
      data: dataframe with date as index, Closing Price and stock. Each column represents a stock.
            Data is processed to simplify calculations.
    '''
    data = pd.DataFrame()
    temp = pd.DataFrame()
    for stock in stocks:
        temp = pd.DataFrame(web.DataReader(stock, data_source='yahoo', start=start, end=end))
        temp['symbol'] = stock
        data = data.append(temp)       
    data = data[['symbol','Adj Close']].pivot(columns='symbol')['Adj Close']
    data = data[stocks]
    mean_returns = data.pct_change().mean()  #.mean()
    covariance = data.pct_change().cov()
    return data, mean_returns, covariance

def calculate_portfolio(weights, mean_returns, covariance):
    '''
    Function that calculates the mean return and variance of a portfolio according to its weight vector.
    Inputs:
      weights: vector with weights (sum has to be 1)
      mean_returns: calculate mean returns by multiplying weights by mean returns
      end: ending date in string format like: 'YYYY-MM-DD'
    Output:
      expected_return: calculate annual returns by multiplying weights by daily mean returns
      standard_deviation: calculate annual sd of portfolio based on weights vector.
    '''    
    return (np.sum(weights*mean_returns)+1)**250-1, np.sqrt(weights.T@(covariance@weights))*250**(.5)


def negative_Sharpe(weights, mean_returns, covariance, riskFreeRate=0.0175):
    '''
    Function that calculates the negative sharpe ratio. It is negative so I can minimize this function later
    Inputs:
      weights: vector with weights (sum has to be 1)
      mean_returns: calculated mean returns by multiplying weights by mean returns
      covariance: covariance matrix
      riskFreeRate = 10 year treasury bond annual rate
    Output:
      negative sharpe ratio.
    '''
    expected_return, standard_deviation = calculate_portfolio(weights, mean_returns, covariance)
    
    return -(expected_return - riskFreeRate) / standard_deviation


def optimize_sharpe(mean_returns, covariance, riskFreeRate):
    '''
    Finds the portfolio of assets providing the maximum Sharpe Ratio
    INPUT
    meanReturns: mean values of each asset's returns
    covMatrix: covariance of each asset in the portfolio
    riskFreeRate: time value of money
    '''
    numAssets = mean_returns.shape[0] 
    args = (mean_returns, covariance, riskFreeRate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple( (0,1) for asset in range(numAssets))
    
#    opts = sco.minimize(negative_Sharpe, numAssets*[1./numAssets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    opts = sco.minimize(negative_Sharpe, numAssets*[1./numAssets,], args=args, bounds=bounds, constraints=constraints)
    
    return opts


#stocks = ['NEE','BLL','CMG','KEYS','ETR','AMZN','AAPL','MSFT','TSLA','FORD']

#stocks = ['RSG','DUK','NEE','AEP']    #min volatility 2018-2019
#stocks = ['NEE','BLL','CMG','KEYS']  #max sharpe
stocks = ['AMD','CMG','KEYS','EW']   #max return

#stocks = ['NEE','BLL','CMG','KEYS','TDG'] #most repeated ones in top 5
stocks = ['AMZN','MSFT','AAPL']  #EXAMPLE
#stocks = ['CHTR', 'ETR', 'MLM', 'CPRT', 'MAA']  #optimal
#stocks = ['AMZN','AAPL','MSFT','NEE','RSG','AMD','TDG','KEYS','DTE','ETR','MLM','TSLA','EW','AEP','DUK']
start = '2019-01-01'
end = '2019-10-30'

with open('symbols.csv','r') as f:
    stocks = f.read().splitlines()
    stocks = stocks[1:51]


data, mean_returns, covariance = get_stock_information(stocks, start, end)

#data_full=data
#mean_returns_full=mean_returns
#covariance_full=covariance

#weights=np.array([.1,.1,.1,.1,.1,.1,.1,.1,.1,.1])
expected_return, standard_deviation = calculate_portfolio(weights, mean_returns, covariance)


riskFreeRate = 1.75/100
assets = data.shape[1]
x=[]
y=[]
#w=[]
max_sharpe={'sharpe':0,'return':0,'sd':0,'weights':[]}
min_variance={'sharpe':0,'return':0,'sd':np.inf,'weights':[]}
#sharpe=0
for i in range(50000):
    weights = np.random.random(assets)
    weights /= np.sum(weights)
    expected_return, standard_deviation = calculate_portfolio(weights, mean_returns, covariance)
    y.append(expected_return), x.append(standard_deviation)
#    w.append(weights)
    sharpe = (expected_return - riskFreeRate) / standard_deviation
    if sharpe>max_sharpe['sharpe']:
        max_sharpe['sharpe']=sharpe
        max_sharpe['return']=expected_return
        max_sharpe['sd']=standard_deviation
        max_sharpe['weights']=weights
    if standard_deviation<min_variance['sd']:
        min_variance['sharpe']=sharpe
        min_variance['return']=expected_return
        min_variance['sd']=standard_deviation
        min_variance['weights']=weights
#title = "Simulation of " + str(len(stocks)) + " with 50k Random Weights"
#title="4 Lowest Volatility Stocks"
title="4 Best Return Stocks"
#title="4 Best Sharpe Ratio Stocks"
plt.clf()
plt.scatter(x, y)
plt.title(title)
plt.xlabel('Standard Deviation')
plt.ylabel('Expected Annual Return')
plt.xlim(.05, .50)
plt.ylim(0, 1.5)
plt.scatter(min_variance['sd'], min_variance['return'], c='red')
plt.scatter(max_sharpe['sd'], max_sharpe['return'], c='red')
plt.scatter(standard_deviation_opt, expected_return_opt, c='black')
plt.show()


#    p_ret, p_var = (weights, meanReturns, covMatrix)   
#    return -(p_ret - riskFreeRate) / p_var


#    np.random.random(assets)




riskFreeRate_daily=((1+riskFreeRate/100)**(1/250)-1)

returns_daily = data.pct_change()
returns_annual = (returns_daily.mean()+1) ** 250 -1
sd = returns_daily.std()
sharpe = (returns_daily - ((1+riskFreeRate/100)**(1/250)-1)).mean()/(returns_daily-((1+riskFreeRate/100)**(1/250)-1)).std()
#http://onlyvix.blogspot.com/2010/08/simple-trick-to-convert-volatility.html
cov_daily = returns_daily.cov()
cov_annual = cov_daily * np.sqrt(250)


expected_return_opt, standard_deviation_opt = calculate_portfolio(opts.x, mean_returns, covariance)



opts = optimize_sharpe(mean_returns, covariance, riskFreeRate)