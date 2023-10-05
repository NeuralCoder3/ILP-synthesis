
import numpy as np
import gurobipy as gp
from gurobipy import GRB

import itertools


# Improvements:
# SOS1 for commands (only 1 is non-zero)
# quadratic -> linear
#   flag
#   acmov[gl]
#   new value
# Heuristcs:
#  initial cmp (cmov without flag useless)
#  no cmp after cmp
#  




timestamps = 14
# timestamps = 12
# timestamps = 11 # no sol found for 123
# timestamps = 9 # no sol found for 123
# timestamps = 3
number_registers = 3
swap = 1
total_registers = number_registers + swap
# all permutations of 1,2,3
permutations = list(itertools.permutations(range(1,number_registers+1)))
permutation_count = len(permutations)

m = gp.Model("sort")
# m.setParam('PRESOLVE', 0)
# m.setParam(GRB.Param.SolutionNumber, sol)
# m.Params.LogToConsole = 0

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
            if a == b:
                continue
            c_cmovg[i][a][b] = m.addVar(name="c_cmovg[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
            c_cmovl[i][a][b] = m.addVar(name="c_cmovl[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
            for k in range(permutation_count):
                c_acmovg[i][k][a][b] = m.addVar(name="c_acmovg[%d][%d][%d][%d]" % (i,k,a,b), vtype=GRB.BINARY)
                c_acmovl[i][k][a][b] = m.addVar(name="c_acmovl[%d][%d][%d][%d]" % (i,k,a,b), vtype=GRB.BINARY)
            if a < b:
                c_cmp[i][a][b] = m.addVar(name="c_cmp[%d][%d][%d]" % (i,a,b), vtype=GRB.BINARY)
                
# unnecessary helper constraints
# for i in range(timestamps):
#     for k in range(permutation_count):
#         for a in range(total_registers):
#             m.addConstr(v[i][k][a] >= 0, name="v_nonneg[%d][%d][%d]" % (i,k,a))
#             m.addConstr(v[i][k][a] <= number_registers, name="v_ub[%d][%d][%d]" % (i,k,a))
            
            
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
M = 10 # upper bound
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
                    m.addLConstr(va - vb >= 1-M*(1-c_gt), name=name+"_cg1")
                    m.addLConstr(vb - va >= 1-M*(1-c_lt), name=name+"_cl1")
                    m.addLConstr(c_lt + c_gt <= 1, name=name+"_c")
                    m.addLConstr(vb - va >= -M*c_gt, name=name+"_cg2")
                    m.addLConstr(va - vb >= -M*c_lt, name=name+"_cl2")


# per step constraints (system evolution -- command semantics)
for i in range(timestamps-1):
    # describe process i -> i+1 (how does i+1 changes depending on i)
    
    # there is exactly one command
    cmps = []
    cmovgs = []
    cmovls = []
    all_commands = c_noop[i]
    no_cmp = 1
    for a in c_cmp[i]:
        for b in c_cmp[i][a]:
            cmps.append(c_cmp[i][a][b])
            all_commands += c_cmp[i][a][b]
            no_cmp -= c_cmp[i][a][b]
    for a in c_cmovg[i]:    
        for b in c_cmovg[i][a]:
            cmovgs.append(c_cmovg[i][a][b])
            all_commands += c_cmovg[i][a][b]
    for a in c_cmovl[i]:
        for b in c_cmovl[i][a]:
            cmovls.append(c_cmovl[i][a][b])
            all_commands += c_cmovl[i][a][b]
    # print("cmp: ",len(cmps))
    # all_commands = \
    #     c_noop[i] + \
    #     sum(cmps) + \
    #     sum(cmovgs) + \
    #     sum(cmovls)
    m.addConstr(all_commands == 1, name="one_command[%d]" % i)
    
    # no_cmp = 1 - sum(cmps)
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
            # not fired (no flag) is still an issued command
            # if not fired (e.g. wrong command or no flag) -> keep old value
            # no_change = 1 - sum(c_acmovg[i][k][a].values()) - sum(c_acmovl[i][k][a].values())
            no_change = 1
            for b in c_cmovg[i][a]:
                no_change -= c_acmovg[i][k][a][b]
            for b in c_cmovl[i][a]:
                no_change -= c_acmovl[i][k][a][b]
            
            no_change_var=m.addVar(name="no_change[%d][%d][%d]" % (i,k,a), vtype=GRB.BINARY)
            m.addConstr(no_change_var == no_change, name="no_change[%d][%d][%d]_set" % (i,k,a))
            # v_new = no_change * v[i][k][a]
            v_new = no_change_var * v[i][k][a]
            for b in c_cmovg[i][a]:
                v_new += c_acmovg[i][k][a][b] * v[i][k][b]
            for b in c_cmovl[i][a]:
                v_new += c_acmovl[i][k][a][b] * v[i][k][b]
            m.addConstr(v[i+1][k][a] == v_new, name="v_update[%d][%d][%d]" % (i+1,k,a))
                
    
# commands in final step are ignored
        
# debug testing
# m.addConstr(c_cmp[0][0][1] == 1)
# m.addConstr(c_cmovg[1][0][1] == 1)
# m.addConstr(c_cmovl[1][1][2] == 1)


# goal
# all sorted i => i
for k in range(permutation_count):
    for a in range(number_registers):
        m.addConstr(v[timestamps-1][k][a] == a+1)

# same across all permutations
for a in range(number_registers):
    for k in range(permutation_count-1):
        # m.addConstr(v[timestamps-1][k][a] == v[timestamps-1][k+1][a])
        for k2 in range(permutation_count):
            m.addConstr(v[timestamps-1][k][a] == v[timestamps-1][k2][a], name="v_same_reg[%d][%d][%d]" % (k,k2,a))
            
for k in range(permutation_count):
    for a in range(number_registers):
        # m.addConstr(v[timestamps-1][k][a] != 0)
        # m.addConstr(v[timestamps-1][k][a] > 0)
        m.addConstr(v[timestamps-1][k][a] >= 1, name="v_value_bound[%d][%d]" % (k,a))
        for b in range(number_registers):
            if a < b:
                m.addConstr(is_gt[timestamps-1][k][a][b] + is_lt[timestamps-1][k][a][b] == 1, name="v_diff_perm[%d][%d][%d]" % (k,a,b))
            # if a != b:
                # m.addConstr(v[timestamps-1][k][a] != v[timestamps-1][k][b])
                # pass



        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
# noops = 0
# for i in range(timestamps):
#     noops += c_noop[i]
# for i in range(timestamps):
#     m.addConstr(c_noop[i]==0, name="no_noop[%d]" % i)

# m.setObjective(noops, GRB.MAXIMIZE)
        
# m.Params.LogToConsole = 0
m.write("sort_raw.lp")
m.optimize()
# m.write("sort_opt.lp")

print("Found %d solutions" % m.SolCount)
if m.SolCount == 0:
    exit(1)

constraint_violation = m.getAttr(GRB.Attr.ConstrVio)
print("Constraint violation: %f" % constraint_violation)
if constraint_violation > 0.1:
    pass
    # exit(1)
    # list all violated constraints
    # for c in m.getConstrs():
    #     if (c.slack)>=0.1:
    #         print(c.constrName)
    #         print(c.slack)
    #         print(c.RHS)
        # print(dir(c))
        # 'CBasis', 'CDualNorm', 'CTag', 'ConstrName', 'DStart', 'FarkasDual', 'IISConstr', 'IISConstrForce', 'Lazy', 'Pi', 'RHS', 'SARHSLow', 'SARHSUp', 'ScenNRHS', 'Sense', 'Slack',
        # if c.violation > 0.1:
        #     print(c.constrName, c.violation)

commands = []
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
    if c_noop[i].X >= 0.5:
        command+="noop"
        # print(c_noop[i].X)
    for a in c_cmp[i]:
        for b in c_cmp[i][a]:
            if c_cmp[i][a][b].X >= 0.5:
                command+="cmp r%d r%d" % (a,b)
                # print(c_cmp[i][a][b].X)
    for a in c_cmovg[i]:    
        for b in c_cmovg[i][a]:
            if c_cmovg[i][a][b].X >= 0.5:
                command+="cmovg r%d r%d" % (a,b)
                # print(c_cmovg[i][a][b].X)
    for a in c_cmovl[i]:
        for b in c_cmovl[i][a]:
            if c_cmovl[i][a][b].X >= 0.5:
                command+="cmovl r%d r%d" % (a,b)
                # print(c_cmovl[i][a][b].X)

    print("Execute command: %s" % command)
    commands.append(command)
    print()
    
print("Commands: ")
print("\n".join(commands))

def val(x):
    num_val = int(x.x+0.5)
    if x.vtype == GRB.BINARY:
        return "■" if num_val == 1 else "□"
    else:
        return str(num_val)

with open("sort_log.txt", "w") as f:
    # print("All variables:")
    # m.cbGetSolution(m.getVars())
    for var in m.getVars():
        print(var.varName, val(var), var.x, file=f)
        
with open("sort_log_ordered.txt", "w") as f:
    # val = lambda x: str(int(x.x+0.5))
    for i in range(timestamps):
        print("Timestamp %s" % i, file=f)
        print("  Commands", file=f)
        print("    noop: %s" % val(c_noop[i]), file=f)
        for a in c_cmp[i]:
            for b in c_cmp[i][a]:
                print("    cmp r%d r%d: %s" % (a,b,val(c_cmp[i][a][b])), file=f)
        for a in c_cmovg[i]:
            for b in c_cmovg[i][a]:
                print("    cmovg r%d r%d: %s" % (a,b,val(c_cmovg[i][a][b])), file=f)
        for a in c_cmovl[i]:
            for b in c_cmovl[i][a]:
                print("    cmovl r%d r%d: %s" % (a,b,val(c_cmovl[i][a][b])), file=f)
        print("  Activated CMov", file=f)
        for k in c_acmovg[i]:
            for a in c_acmovg[i][k]:
                for b in c_acmovg[i][k][a]:
                    print("    acmovg[%d] r%d r%d: %s" % (k,a,b,val(c_acmovg[i][k][a][b])), file=f)
        for k in c_acmovl[i]:
            for a in c_acmovl[i][k]:
                for b in c_acmovl[i][k][a]:
                    print("    acmovl[%d] r%d r%d: %s" % (k,a,b,val(c_acmovl[i][k][a][b])), file=f)
        print("  Flags", file=f)
        for k in range(permutation_count):
            print("    fgt[%d]: %s" % (k,val(fgt[i][k])), file=f)
            print("    flt[%d]: %s" % (k,val(flt[i][k])), file=f)
        print("  Registers", file=f)
        for k in range(permutation_count):
            registers = v[i][k].items()
            registers = sorted(registers, key=lambda x: x[0])
            flag_str = ("<" if flt[i][k].X else "") + (">" if fgt[i][k].X else "")
            flag_str = "[" + flag_str + "]"
            # print("    %s" % ", ".join(val(v) for _,v in registers), file=f)
            print("    ", end="", file=f)
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
                print(val(r_v), end=cmp_str, file=f)
            print("  " + flag_str, file=f)
        
with open("sort_constraints.txt","w") as f:
    for c in m.getConstrs():
        print(c.constrName, c.sense, c.RHS, file=f)
        
        
if constraint_violation > 0.1:
    print(f"There were {constraint_violation} constraint violations")