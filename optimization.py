import scipy.optimize as sco
import numpy as np


#LOAD DATA
data = portfolio.process_stocks(stocks, start, end)
data = data.iloc[:,(~data.isna().any()).values]
stocks = list(data.columns)

returns_daily = data.pct_change()
returns_annual = (returns_daily.mean()+1) ** 250 -1
sd = returns_daily.std()
sharpe = (returns_daily - ((1+riskFreeRate/100)**(1/250)-1)).mean()/(returns_daily-((1+riskFreeRate/100)**(1/250)-1)).std()
#http://onlyvix.blogspot.com/2010/08/simple-trick-to-convert-volatility.html
cov_daily = returns_daily.cov()
cov_annual = cov_daily * np.sqrt(250)

#stocks = ['NEE','BLL','CMG','KEYS','ETR']
#weights = [0.61,0.14,0.02,0.21,0.02]
#weights = [0.2,0.2,0.2,0.2,0.2]
#weights = [1.0,0.0,0.0,0.0,0.0]
#weights = [0.11467726, 0.15389129, 0.15102192, 0.07096601, 0.50944353]  #optimum

riskFreeRate_daily=((1+riskFreeRate/100)**(1/250)-1) 

portReturn, portStdDev = calcPortfolioPerf(np.array(weights), returns_daily.mean(), cov_daily)
print(portReturn)
print(portStdDev)

sharpe = negSharpeRatio(np.array(weights), returns_daily.mean(), cov_daily, riskFreeRate_daily)

opts = findMaxSharpeRatioPortfolio(returns_daily.mean(), cov_daily, riskFreeRate_daily)
data.columns[opts.x>0.06]



def calcPortfolioPerf(weights, meanReturns, covMatrix):
    '''
    Calculates the expected mean of returns and volatility for a portolio of 
    assets, each carrying the weight specified by weights
    
    INPUT
    weights: array specifying the weight of each asset in the portfolio
    meanReturns: mean values of each asset's returns
    covMatrix: covariance of each asset in the portfolio
    
    OUTPUT
    tuple containing the portfolio return and volatility
    '''    
    #Calculate return and variance
    portReturn = np.sum( meanReturns*weights )
    portStdDev = np.sqrt(np.dot(weights.T, np.dot(covMatrix, weights)))
    
    return portReturn, portStdDev



def negSharpeRatio(weights, meanReturns, covMatrix, riskFreeRate):
    '''
    Returns the negated Sharpe Ratio for the speicified portfolio of assets
    
    INPUT
    weights: array specifying the weight of each asset in the portfolio
    meanReturns: mean values of each asset's returns
    covMatrix: covariance of each asset in the portfolio
    riskFreeRate: time value of money
    '''
    p_ret, p_var = calcPortfolioPerf(weights, meanReturns, covMatrix)
    
    return -(p_ret - riskFreeRate) / p_var



def findMaxSharpeRatioPortfolio(meanReturns, covMatrix, riskFreeRate):
    '''
    Finds the portfolio of assets providing the maximum Sharpe Ratio
    
    INPUT
    meanReturns: mean values of each asset's returns
    covMatrix: covariance of each asset in the portfolio
    riskFreeRate: time value of money
    '''
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix, riskFreeRate)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple( (0,1) for asset in range(numAssets))
    
    opts = sco.minimize(negSharpeRatio, numAssets*[1./numAssets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    
    return opts
    
def findMinVariancePortfolio(meanReturns, covMatrix):
    '''
    Finds the portfolio of assets providing the lowest volatility
    
    INPUT
    meanReturns: mean values of each asset's returns
    covMatrix: covariance of each asset in the portfolio
    '''
    numAssets = len(meanReturns)
    args = (meanReturns, covMatrix)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple( (0,1) for asset in range(numAssets))
    
    opts = sco.minimize(getPortfolioVol, numAssets*[1./numAssets,], args=args, method='SLSQP', bounds=bounds, constraints=constraints)
    
    return opts
