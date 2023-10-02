
import numpy as np
import gurobipy as gp
from gurobipy import GRB


for av,bv in [(2,2),(2,3),(3,2)]:
    m = gp.Model("greater")
    m.Params.LogToConsole = 0

    a = m.addVar(vtype=GRB.INTEGER, name="a")
    b = m.addVar(vtype=GRB.INTEGER, name="b")

    c = m.addVar(vtype=GRB.BINARY, name="c")

    m.addConstr(a == av, name="a0")
    m.addConstr(b == bv, name="b0")
    m.addConstr(b + c * a >= a, name="c0")
    
    m.setParam(GRB.Param.PoolSearchMode, 2)
    m.optimize()
    
    nSolutions = m.SolCount
    print('Number of solutions found: ' + str(nSolutions))
    for sol in range(nSolutions):
        m.setParam(GRB.Param.SolutionNumber, sol)
        # print(m.ObjVal)
        # for station_idx in range(0, len(station_in_route)):

        #     m.cbGetSolution(m.getVars())
        print("a: ",a.Xn)
        print("b: ",b.Xn)
        print("c: ",c.Xn)
        print()

        ### Here I need to request the current solution from the model

        # If variable in solution is  > 0:
                # print(' Station %d' % station_idx, end='\n')
    print('')


