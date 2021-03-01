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
enterprise_value_data = requests.get(f'https://financialmodelingprep.com/api/v3/enterprise-values/{company}?apikey={demo}').json()
enterprise_value_date = next(item for item in enterprise_value_data if item["date"] == "2019-12-31")

#inputs
revenue_growth_rate = .4
terminal_year_growth_rate = .0175
steady_state_growth_rate_years = 5
revenues = company_income_fund_date["revenue"]
interest_expense = company_income_fund_date["interestExpense"]
ebit = company_income_fund_date["operatingIncome"]
sales_to_capital_ratio_initial = 2
sales_to_capital_ratio_end = sales_to_capital_ratio_initial * .65

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
target_ebit_margin = .1025
ebit_margin_rate_years = pd.to_numeric(pd.Series(range(1,speed_of_convergence + 1)), downcast='float')
ebit_margin_rate_convergence = target_ebit_margin - (target_ebit_margin - ebit_margin)/speed_of_convergence * (speed_of_convergence - ebit_margin_rate_years)
ebit_margin_rate_proj[0] = ebit_margin 
ebit_margin_rate_proj[1:len(ebit_margin_rate_years) + 1] = ebit_margin_rate_convergence
ebit_margin_rate_proj[len(ebit_margin_rate_years) + 1:] = target_ebit_margin
ebit_proj = ebit_margin_rate_proj * revenues_proj
ebit_post_tax_proj = ebit_proj * (1 - tax_rate)
ebit_post_tax_proj[ebit_post_tax_proj < 0] = 0



#Sales to Capital Ratio
sales_to_capital_series = copy.deepcopy(years_proj)
sales_to_capital_series[1:6] = sales_to_capital_ratio_initial
sales_to_capital_series[6:] = sales_to_capital_ratio_end


#fcff
capex_proj = revenues_proj.diff() / sales_to_capital_series
fcff_proj = (ebit_post_tax_proj - capex_proj).dropna()


#Discount Factor
cum_discount_factor_proj = copy.deepcopy(years_proj)
risk_free_rate = .0175
initial_cost_of_capital = .0886
mature_cost_of_capital = .074
cost_of_capital_vec = pd.Series(range(0,num_years_to_project), dtype = 'float64')
cost_of_capital_vec[1:6] = initial_cost_of_capital
cost_of_capital_vec[6:] = mature_cost_of_capital - (mature_cost_of_capital - initial_cost_of_capital)/speed_of_convergence * (speed_of_convergence - pd.Series(range(1,6), dtype = 'float64'))

cum_discount_factor_proj = (1/(1 + cost_of_capital_vec)).cumprod()

pv_fcff = cum_discount_factor_proj[:-1].reset_index(drop=True) * fcff_proj[:-1].reset_index(drop=True)


terminal_cash_flow = fcff_proj.iloc[-1]
terminal_cost_of_capital = cost_of_capital_vec.iloc[-1]
terminal_growth_rate = revenue_growth_rate_series.iloc[-1] - 1
terminal_value = terminal_cash_flow/(terminal_cost_of_capital - terminal_growth_rate)
pv_terminal_value = terminal_value * cum_discount_factor_proj.iloc[-1]
pv_cf_sum = sum(pv_fcff)
pv_sum = pv_cf_sum + pv_terminal_value
failure_prob = .1
fair_value_weight = .5
proceeds_of_failure = pv_sum * fair_value_weight
operating_asset_value = pv_sum * (1 - failure_prob) + proceeds_of_failure * failure_prob
cash = company_balance_fund_date["cashAndCashEquivalents"]
debt = company_balance_fund_date["totalDebt"]
equity_value = operating_asset_value + cash - debt
outstanding_shares = enterprise_value_date["numberOfShares"]
equity_value
print(f"{equity_value:,}")
