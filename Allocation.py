# Simple Resource Allocation Model

import pyomo.environ as pyo
from pyomo.dae import *

def ResourceAllocation(A, R, Min, FC, BPS, C, U, B, K, L, sense=pyo.maximize):
    
    """ Create a simple resource allocation problem.

    Args:
        A (list of str) : set of media channels
        R (list of str) : set of resources
        Min (dict[a] of int) : minimum budget to be used for each media channel
        FC (dict[a] of int) : fixed cost for setting up the marketing for different media channels
        #TB (int) : The total budget allowed to spend on all the marketing channels
        BPS (list of int) : Break points index based on the budget limit for each media channel
        B (dict of dict of int):  breakpoints for the media channels
        C (dict of dict of float) : exposures per media channel
        U (dict[r][a] of floats) : utilizations
        K (dict[r] of floats) : capacities
        L (int) : Number of break points
        
        
    Returns:
        model (Pyomo ConcreteModel) : the instantiated model

    """

    BigM = max(B[i][a] for i in BPS for a in A) + 1
    
    model = pyo.ConcreteModel(name='ResourceAllocation')

    def bounds_rule(m,i, a):
        #print(B[i-1][a],B[i][a])
        
        return (0,B[i][a]-B[i-1][a])
    

    model.x = pyo.Var(BPS, A, within=pyo.NonNegativeReals, bounds=bounds_rule)

    model.b = pyo.Var(A, within= pyo.Binary)
    


    model.MaxProfit = pyo.Objective(expr=\
                                  sum(C[i][a]*model.x[i,a] for i in BPS for a in A), sense=sense)
 
    

    def Capacity_rule(m, r):

        return sum(U[r][a]*m.x[i,a] for i in BPS for a in A) + sum(FC[r][a]*m.b[a] for a in A) <= K[r]
    model.Capacity = pyo.Constraint(R, rule=Capacity_rule)


    def MinUsed_rule(m,a):
       
        return m.x[1,a] >= m.b[a]*Min[a]
    model.MinUsed = pyo.Constraint(A, rule=MinUsed_rule)

    def BDef_rule(m,a):
         return BigM*m.b[a] >= sum(m.x[i,a] for i in BPS)
    model.BDef = pyo.Constraint(A, rule=BDef_rule)
    
    return model
