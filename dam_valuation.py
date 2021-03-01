#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 16:35:18 2021

@author: darrylha
"""
import requests
import numpy as np
import pandas as pd
import copy

#import pandas_datareader.data as web
#import datetime






#Company
company = 'TSLA'
demo = '8bd4d01f414e765a5939a67aa62e43e1'
income_data = requests.get(f'https://financialmodelingprep.com/api/v3/income-statement/{company}?apikey={demo}').json()

company_income_fund_date = next(item for item in income_data if item["date"] == "2019-12-31")

balance_data = requests.get(f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{company}?apikey={demo}').json()

company_balance_fund_date = next(item for item in balance_data if item["date"] == "2019-12-31")


#inputs
revenue_growth_rate = .4
terminal_year_growth_rate = .0175
steady_state_growth_rate_years = 5
revenues = company_income_fund_date["revenue"]
interest_expense = company_income_fund_date["interestExpense"]
ebit = company_income_fund_date["operatingIncome"]
sales_to_capital_ratio = 2


#Years Vector 
num_years_to_project = 11
years_proj = pd.Series(range(0,num_years_to_project + 1), dtype = 'float64')


#Revenue Projections
revenue_growth_rate_series = copy.deepcopy(years_proj)
revenue_growth_rate_series[0] = 1
revenue_growth_rate_series[1:(steady_state_growth_rate_years +1)] = 1 + revenue_growth_rate
temp = (pd.Series(range(1,len(years_proj) - steady_state_growth_rate_years - 1)))
revenue_growth_rate_series[(steady_state_growth_rate_years +1):len(revenue_growth_rate_series) - 1] = 1 + (revenue_growth_rate - ((revenue_growth_rate - terminal_year_growth_rate)/len(temp)) * temp)
revenue_growth_rate_series[len(revenue_growth_rate_series) - 1] = revenue_growth_rate_series.iloc[-2]
revenues_proj = revenue_growth_rate_series.cumprod() * revenues

#EBIT Projections

ebit_margin_rate_proj = copy.deepcopy(years_proj)
ebit_margin = ebit/revenues
ebit_margin = .016
tax_rate = .25
ebit_post_tax = ebit * ( 1 - tax_rate)
speed_of_convergence = 5
target_ebit_margin = .10
ebit_margin_rate_years = pd.to_numeric(pd.Series(range(1,speed_of_convergence + 1)), downcast='float')
ebit_margin_rate_convergence = target_ebit_margin - (target_ebit_margin - ebit_margin)/speed_of_convergence * (speed_of_convergence - ebit_margin_rate_years)
ebit_margin_rate_proj[0] = ebit_margin 
ebit_margin_rate_proj[1:len(ebit_margin_rate_years) + 1] = ebit_margin_rate_convergence
ebit_margin_rate_proj[len(ebit_margin_rate_years) + 1:] = target_ebit_margin

#Sales to Capital Ratio

copy.deepcopy(years_proj)







cagr = 1
discount_rate = .1
LTGrowth = .02

pd.DataFrame(np.random.randn(7, 2))

tax_rate = .25
ebit_post_tax = ebit * ( 1 - tax_rate)
sales_to_capital_ratio = 2
revenue_growth_rate = .4 

cost_of_capital = .08


a_list = [1, 3, 49, 23, 4, 23]
def condition(x): return x > 4
output = [idx for idx, element in enumerate(a_list) if condition(element)]
print(output)

