#!/usr/bin/env python
# coding: utf-8

# In[11]:
from astropy.table import QTable, Table, Column
from astropy import units as u
import numpy as np
import pyomo.environ as pyo
from Allocation import ResourceAllocation
import csv

#Allocations are in thousands of dollars.

Activities = ["Print","TV","SEO","Mobile", "Facebook"]
Resources = ["AdminExpense", "DistributionExpense","ContentExpense"]
C = {1:{"Print":250,"TV":300,"SEO":100,"Mobile":200, "Facebook":200},
     2:{"Print":150,"TV":100,"SEO":50,"Mobile":100, "Facebook":100}}
K = {"AdminExpense": 4000, "DistributionExpense":3000, "ContentExpense":3500}
L = 2

U = {"AdminExpense": {"Print":0.10,"TV":0.10,"SEO":0.10,"Mobile":0.10, "Facebook":0.10},
    "DistributionExpense": {"Print":0.30,"TV":0.20,"SEO":0.10,"Mobile":0.20, "Facebook":0.05},
    "ContentExpense": {"Print":0.60,"TV":0.70,"SEO":0.80,"Mobile":0.70, "Facebook":0.85}
    }

Minimum = {"Print":40,"TV":20,"SEO":15,"Mobile":20, "Facebook":40}    

B = {0:{"Print":0,"TV":0,"SEO":0,"Mobile":0, "Facebook":0}, 
     1:{"Print":400,"TV":500,"SEO":600,"Mobile":500, "Facebook":400},
     2:{"Print":10000,"TV":10000,"SEO":10000,"Mobile":10000, "Facebook":10000}}

FixedCost = {"AdminExpense": {"Print":3,"TV":3,"SEO":1,"Mobile":2, "Facebook":1},
    "DistributionExpense": {"Print":9,"TV":8,"SEO":8,"Mobile":6, "Facebook":7},"ContentExpense": {"Print":80,"TV":60,"SEO":70,"Mobile":50, "Facebook":80}
    }

BPS = list(range(1,L+1))


model = ResourceAllocation(Activities,Resources,Minimum,FixedCost,BPS,
                           C,U,B,K,L,sense=pyo.maximize)

opt = pyo.SolverFactory('glpk')
results = opt.solve(model)  # solves and updates model
pyo.assert_optimal_termination(results)
#model.pprint()

print("\nOUTPUT:\n")

print("\033[0;32m" + "Maximum Exposures incurred based on Budget Allocation:" + " " + "\033[0;0m" + "\033[;1m" + str(pyo.value(model.MaxProfit)) + " " +"exposures" + "\033[0;0m" + "\n")
#print(pyo.value(model.MaxProfit))


with open("budget_allocations_input.csv", mode='w') as csv_file:
	c=1
	writer = csv.DictWriter(csv_file, fieldnames=['MediaChannel','Exposures_atCostLevel1','Exposures_atCostLevel2','MinimumBudget($)'])
	writer .writeheader()
	for p in Activities:
		writer.writerow({'MediaChannel': p,'Exposures_atCostLevel1':C[c][p], 'Exposures_atCostLevel2':C[c+1][p],'MinimumBudget($)':Minimum[p]})
	writer.writerow({})
	    
	writer1 = csv.DictWriter(csv_file, fieldnames=['MediaChannel', 'AdminExpense($)', 'DistributionExpense($)', 'ContentExpense($)'])
	writer1.writeheader()
	for p in Activities:
	
		writer1.writerow({'MediaChannel': p,'AdminExpense($)':U['AdminExpense'][p], 'DistributionExpense($)':U['DistributionExpense'][p], 'ContentExpense($)':U['ContentExpense'][p]})
	writer1.writerow({})
csv_file.close()

with open("budget_allocations_input.csv", mode='a') as csv_file_a:
	csv_file_a.seek(0)
	writer2 = csv.DictWriter(csv_file_a, fieldnames=['MediaChannel', 'AdminExpense($)', 'DistributionExpense($)', 'ContentExpense($)'])
	writer2.writerow({'MediaChannel':'MaximumBudgetLimit($)','AdminExpense($)': K['AdminExpense'], 'DistributionExpense($)': K['DistributionExpense'], 'ContentExpense($)':K['ContentExpense']})
csv_file_a.close()



with open("budget_allocations_output.csv", mode='w') as csv_file1:
	c=1	
	writer = csv.DictWriter(csv_file1, fieldnames=['MediaChannel','TotalBudgetAllocation($)', 'BudgetSpentonExposures($)', 'BudgetSpentonFixedCosts($)','BudgetAllocation_atCostLevel1($)','BudgetAllocation_atCostLevel2($)','Exposures_atCostLevel1','Exposures_atCostLevel2'])
	writer .writeheader()
	for p in Activities:
		FC_sum = 0
		for r in Resources:
			FC_sum += FixedCost[r][p]
		if(pyo.value(model.x[c,p]) == 0):
			FC_sum = 0
			Sum=0
		Sum = pyo.value(model.x[c,p]) + pyo.value(model.x[c+1,p])
		BA1 = pyo.value(model.x[c,p])
		BA2 = pyo.value(model.x[c+1,p])
		Exp1 = C[c][p]*pyo.value(model.x[c,p])
		Exp2 = C[c+1][p]*pyo.value(model.x[c+1,p])
		writer.writerow({'MediaChannel': p,'TotalBudgetAllocation($)': Sum, 'BudgetSpentonExposures($)': Sum-FC_sum,'BudgetSpentonFixedCosts($)': FC_sum, 'BudgetAllocation_atCostLevel1($)': BA1, 'BudgetAllocation_atCostLevel2($)': BA2,'Exposures_atCostLevel1':Exp1,'Exposures_atCostLevel2':Exp2})



