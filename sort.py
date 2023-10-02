
import numpy as np
import gurobipy as gp
from gurobipy import GRB

import itertools

# timestamps = 14
timestamps = 3
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
# activator variables for flag*cmov to avoid cubic formulas
c_acmovg = {}
c_acmovl = {}
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
    c_acmovg[i] = {}
    c_acmovl[i] = {}
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
        for k in range(permutation_count):
            if k not in c_acmovg[i]:
                c_acmovg[i][k] = {}
                c_acmovl[i][k] = {}
            c_acmovg[i][k][a] = {}
            c_acmovl[i][k][a] = {}
        for b in range(total_registers):
            c_cmovg[i][a][b] = m.addVar(name="c_cmovg[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
            c_cmovl[i][a][b] = m.addVar(name="c_cmovl[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
            for k in range(permutation_count):
                c_acmovg[i][k][a][b] = m.addVar(name="c_acmovg[%d][%d][%d][%d]" % (i,k,a,b), vtype=GRB.BINARY)
                c_acmovl[i][k][a][b] = m.addVar(name="c_acmovl[%d][%d][%d][%d]" % (i,k,a,b), vtype=GRB.BINARY)
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
                    # TODO: use less constraints
                    # TODO: maybe use max/ub instead of M
                    m.addConstr(va - vb >= 1-M*(1-c_gt), name=name+"_cg1")
                    m.addConstr(vb - va >= 1-M*(1-c_lt), name=name+"_cl1")
                    m.addConstr(c_lt + c_gt <= 1, name=name+"_c")
                    m.addConstr(vb - va >= -M*c_gt, name=name+"_cg2")
                    m.addConstr(va - vb >= -M*c_lt, name=name+"_cl2")


# per step constraints (system evolution -- command semantics)
for i in range(timestamps-1):
    # describe process i -> i+1 (how does i+1 changes depending on i)
    
    # there is exactly one command
    cmps = []
    cmovgs = []
    cmovls = []
    for a in c_cmp[i]:
        for b in c_cmp[i][a]:
            cmps.append(c_cmp[i][a][b])
    for a in c_cmovg[i]:    
        for b in c_cmovg[i][a]:
            cmovgs.append(c_cmovg[i][a][b])
    for a in c_cmovl[i]:
        for b in c_cmovl[i][a]:
            cmovls.append(c_cmovl[i][a][b])
    print("cmp: ",len(cmps))
    all_commands = \
        c_noop[i] + \
        sum(cmps) + \
        sum(cmovgs) + \
        sum(cmovls)
    m.addConstr(all_commands == 1, name="one_command[%d]" % i)
    
    no_cmp = 1 - sum(cmps)
    # flags encoding
    for k in range(permutation_count):
        f_gt_new = no_cmp * fgt[i][k]
        f_lt_new = no_cmp * flt[i][k]
        for a in c_cmp[i]:
            for b in c_cmp[i][a]:
                f_gt_new += c_cmp[i][a][b] * is_gt[i][k][a][b]
                f_lt_new += c_cmp[i][a][b] * is_lt[i][k][a][b]
        m.addConstr(fgt[i+1][k] == f_gt_new, name="fgt_update[%d][%d]" % (i+1,k))
        m.addConstr(flt[i+1][k] == f_lt_new, name="flt_update[%d][%d]" % (i+1,k))
        
    for k in range(permutation_count):
        for a in c_cmovg[i]:    
            for b in c_cmovg[i][a]:
                m.addConstr(c_acmovg[i][k][a][b] == c_cmovg[i][a][b] * fgt[i][k], name="c_acmovg_act[%d][%d][%d][%d]" % (i,k,a,b))
        for a in c_cmovl[i]:
            for b in c_cmovl[i][a]:
                m.addConstr(c_acmovl[i][k][a][b] == c_cmovl[i][a][b] * flt[i][k], name="c_acmovl_act[%d][%d][%d][%d]" % (i,k,a,b))
            
    # mov command encoding => value changes
    for k in range(permutation_count):
        for a in range(total_registers):
            # no_change = 1 - sum(c_cmovg[i][a].values()) - sum(c_cmovl[i][a].values())
            no_change = 1 - sum(c_acmovg[i][k][a].values()) - sum(c_acmovl[i][k][a].values())
            v_new = no_change * v[i][k][a]
            for b in c_cmovg[i][a]:
                v_new += c_acmovg[i][k][a][b] * v[i][k][b]
            for b in c_cmovl[i][a]:
                v_new += c_acmovl[i][k][a][b] * v[i][k][b]
            m.addConstr(v[i+1][k][a] == v_new, name="v_update[%d][%d][%d]" % (i+1,k,a))
                
    
# commands in final step are ignored
        
# debug testing
m.addConstr(c_cmp[0][0][1] == 1)
# m.addConstr(c_cmovg[1][0][1] == 1)
m.addConstr(c_cmovl[1][1][2] == 1)
        
# m.Params.LogToConsole = 0
m.optimize()

for i in range(timestamps):
    print("Timestamp %d" % i)
    for k in range(permutation_count):
        registers = v[i][k].items()
        registers = sorted(registers, key=lambda x: x[0])
        flag_str = ("<" if flt[i][k].X else "") + (">" if fgt[i][k].X else "")
        # print(", ".join(str(int(v.X)) for _,v in registers), flag_str)
        # print("  r0 < r1: %d" % is_lt[i][k][0][1].X)
        # print("  r0 > r1: %d" % is_gt[i][k][0][1].X)
        for a in range(total_registers):
            r_v = registers[a][1]
            cmp_str = ""
            if a < len(registers)-1:
                r_is_lt = is_lt[i][k][a][a+1].X
                r_is_gt = is_gt[i][k][a][a+1].X
                cmp_str = ("<" if r_is_lt else "") + (">" if r_is_gt else "")
                if not r_is_lt and not r_is_gt:
                    cmp_str = "="
                cmp_str = " " + cmp_str + " "
                # cmp_str = ", "
            print(str(int(r_v.x)), end=cmp_str)
        print("  " + flag_str)

    command = ""
    if c_noop[i].X:
        command+="noop"
    for a in c_cmp[i]:
        for b in c_cmp[i][a]:
            if c_cmp[i][a][b].X:
                command+="cmp r%d r%d" % (a,b)
    for a in c_cmovg[i]:    
        for b in c_cmovg[i][a]:
            if c_cmovg[i][a][b].X:
                command+="cmovg r%d r%d" % (a,b)
    for a in c_cmovl[i]:
        for b in c_cmovl[i][a]:
            if c_cmovl[i][a][b].X:
                command+="cmovl r%d r%d" % (a,b)

    print("Execute command: %s" % command)
