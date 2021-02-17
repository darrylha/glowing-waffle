#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  9 16:21:21 2021

@author: darrylha
"""
import requests
import numpy as np
import pandas as pd
#import pandas_datareader.data as web
#import datetime





#plt.title('Intraday Times Series for the MSFT stock (1 min)')


token = 'pk_c2eac995db9e4ed68c8b347474dc2a47'


#Company
sym='TSLA'

#inputs
cagr = 1
discount_rate = .1
LTGrowth = .02

financials = requests.get(f'https://cloud.iexapis.com/stable/stock/{sym}/financials?token={token}&period=annual').json()
cashflow = requests.get(f'https://cloud.iexapis.com/stable/stock/{sym}/cash-flow?token={token}&period=annual').json()
income = requests.get(f'https://cloud.iexapis.com/stable/stock/{sym}/income?token={token}&period=annual').json()
fundamentals = requests.get(f'https://cloud.iexapis.com/stable/stock/{sym}/fundamentals?token={token}&period=annual').json()
quote = requests.get(f'https://cloud.iexapis.com/stable/stock/{sym}/quote?token={token}').json()


cashflow_historical = requests.get(f'https://cloud.iexapis.com/stable/stock/{sym}/cash-flow?token={token}&period=annual&last=4').json()['cashflow']

cfh = np.empty(len(cashflow_historical))

for i in range(len(cashflow_historical)):
    cfh[i] = cashflow_historical[i]["cashFlow"] + cashflow_historical[i]["capitalExpenditures"]
    
cfh = np.flip(cfh)    

historical_cagr = np.average(np.diff(cfh)/cfh[1:])

cagr = historical_cagr if historical_cagr > 0 else cagr

fcf = cashflow['cashflow'][0]['cashFlow'] + cashflow['cashflow'][0]['capitalExpenditures']


# next 5 years net income projection
def fcfProjected(cagr):
    a = np.arange(6)
    temp = np.empty(len(a), dtype = int)
    temp[0] =  financials['financials'][0]['netIncome']
    fcf_projected = (1 + cagr * np.arange(6)) * fcf
    return fcf_projected 
    
#fcfProjected(1)
#fcf_projected_pd = pd.DataFrame(
#    {
#     "fcf_projected": fcf_projected
#     }
#    )

#pd.options.display.float_format = '{:,.0f}'.format

#print(fcf_projected_pd)



discount_rate = .08 
LTGrowth = .02

    
def target_price(fcf_projected,discount_rate, LTGrowth):
    npv = np.npv(discount_rate,fcf_projected)
    
    
    Terminal_value = (fcf_projected[5] * (1+ LTGrowth)) /(discount_rate  - LTGrowth)
    
    Terminal_value_Discounted = Terminal_value/(1+discount_rate)**4

    target_equity_value = Terminal_value_Discounted + npv
    debt = fundamentals['fundamentals'][0]['debtFinancial']
    target_value = target_equity_value - debt
    num_of_shares = fundamentals['fundamentals'][0]['sharesIssued']
    
    target_price_per_share = target_value/num_of_shares
    return target_price_per_share

fcf_projected = fcfProjected(cagr)
target_price_per_share = target_price(fcf_projected,discount_rate,LTGrowth)
latest_price = quote["latestPrice"]

print(sym + ' forecasted price per stock is ' + str(target_price_per_share) )
print(f'the forecast is based on the following assumptions: revenue growth: {cagr} and Cost of Capital: {discount_rate}' )
print(f'perpetuity growth: {LTGrowth}')
print(f"Latest Price is {latest_price}")



iterations = 10000

    
    # Create probability distributions
fcf_growth_dist = np.random.normal(loc=cagr, scale=0.01, size=iterations)
fcf_growth_dist[2]

# Calculate DCF value for each set of random inputs
output_distribution = []
for i in range(iterations):
    fcf_temp = fcfProjected(fcf_growth_dist[i])
    target_price_temp = target_price(fcf_temp,discount_rate,LTGrowth)    
    # DCF valuation
    output_distribution.append(target_price_temp)
    

pd.Series(output_distribution).plot.hist(grid=True, bins=20, rwidth=0.9,
                   color='#607c8e')
