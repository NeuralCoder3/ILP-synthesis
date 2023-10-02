
import numpy as np
import gurobipy as gp
from gurobipy import GRB

import itertools

# timestamps = 14
timestamps = 1
number_registers = 3
swap = 1
total_registers = number_registers + swap
# all permutations of 1,2,3
permutations = list(itertools.permutations(range(1,number_registers+1)))
permutation_count = len(permutations)

m = gp.Model("sort")

v = {}
is_gt = {}
is_lt = {}
fgt = {}
flt = {}
c_noop = {}
c_cmp = {}
c_cmovg = {}
c_cmovl = {}
# set up variables
for i in range(timestamps):
    v[i] = {}
    is_gt[i] = {}
    is_lt[i] = {}
    fgt[i] = {}
    flt[i] = {}
    c_noop[i] = m.addVar(name="c_noop[%d]" % i, vtype=GRB.BINARY)
    c_cmp[i] = {}
    c_cmovg[i] = {}
    c_cmovl[i] = {}
    for k in range(permutation_count):
        v[i][k] = {}
        is_gt[i][k] = {}
        is_lt[i][k] = {}
        fgt[i][k] = m.addVar(name="fgt[%d][%d]" % (i,k), vtype=GRB.BINARY)
        flt[i][k] = m.addVar(name="flt[%d][%d]" % (i,k), vtype=GRB.BINARY)
        for a in range(total_registers):
            v[i][k][a] = m.addVar(name="v[%d][%d][%d]" % (i,k,a), vtype=GRB.INTEGER)
            is_gt[i][k][a] = {}
            is_lt[i][k][a] = {}
            for b in range(total_registers):
                if a < b:
                    is_gt[i][k][a][b] = m.addVar(name="is_gt[%d][%d][%d][%d]" % (i,k,a,b), vtype=GRB.BINARY)
                    is_lt[i][k][a][b] = m.addVar(name="is_lt[%d][%d][%d][%d]" % (i,k,a,b), vtype=GRB.BINARY)
    for a in range(total_registers):
        c_cmp[i][a] = {}
        c_cmovg[i][a] = {}
        c_cmovl[i][a] = {}
        for b in range(total_registers):
            c_cmovg[i][a][b] = m.addVar(name="c_cmovg[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
            c_cmovl[i][a][b] = m.addVar(name="c_cmovl[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
            if a < b:
                c_cmp[i][a][b] = m.addVar(name="c_cmp[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
            
            
# initialize variables
for k in range(permutation_count):
    permutation = permutations[k]
    m.addConstr(fgt[0][k] == 0, name="initFgt[%d]" % k)
    m.addConstr(flt[0][k] == 0, name="initFlt[%d]" % k)
    for a in range(number_registers):
        m.addConstr(v[0][k][a] == permutation[a], name="initV[%d][%d]" % (k,a))
    for b in range(swap):
        m.addConstr(v[0][k][number_registers+b] == 0, name="initVS[%d][%d]" % (k,number_registers+b))
        
# set up comparison constraints
M = 1000 # upper bound
for i in range(timestamps):
    for k in range(permutation_count):
        for a in range(total_registers):
            for b in range(total_registers):
                if a < b:
                    # is_gt[i][k][a][b] => whether v[i][k][a] > v[i][k][b]
                    # is_lt[i][k][a][b] => whether v[i][k][a] < v[i][k][b]
                    va = v[i][k][a]
                    vb = v[i][k][b]
                    c_gt = is_gt[i][k][a][b]
                    c_lt = is_lt[i][k][a][b]
                    name = "is_cmp[%d][%d][%d][%d]" % (i,k,a,b)
                    # m.addConstr(va - vb >= 1-M*(1-c_gt), name=name+"_cg1")
                    # m.addConstr(vb - va >= 1-M*(1-c_lt), name=name+"_cl1")
                    # m.addConstr(c_lt + c_gt <= 1, name=name+"_c")
                    # m.addConstr(vb - va >= -c_gt, name=name+"_cg2")
                    # m.addConstr(va - vb >= -c_lt, name=name+"_cl2")
                    # m.addConstr(c_gt == -0, name=name+"_cg2")
                    
                    

    
        
        
# m.Params.LogToConsole = 0
m.optimize()

for i in range(timestamps):
    print("Timestamp %d" % i)
    for k in range(permutation_count):
        registers = v[i][k].items()
        registers = sorted(registers, key=lambda x: x[0])
        flag_str = ("<" if flt[i][k].X else "") + (">" if fgt[i][k].X else "")
        print(", ".join(str(int(v.X)) for _,v in registers), flag_str)
        print("  r0 < r1: %d" % is_lt[i][k][0][1].X)
        print("  r0 > r1: %d" % is_gt[i][k][0][1].X)
