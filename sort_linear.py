import itertools
from sys import stdout
from mip import Model, xsum, BINARY, INTEGER, CBC, Var, minimize, maximize
import conflict

# timestamps = 14
# timestamps = 12
timestamps = 11
# timestamps = 11
timestamps+=1
number_registers = 3
swap = 1
total_registers = number_registers + swap
# all permutations of 1,2,3
permutations = list(itertools.permutations(range(1,number_registers+1)))
permutation_count = len(permutations)


m = Model()
# m = Model(solver_name=CBC)
M = 10 # an upper bound for the integer variables/expressions

def coupleBinary(b2, b0, b1):
    global m, M
    m += (b2 <= b0)
    m += (b2 <= b1)
    m += (b2 >= b0 + b1 - 1)
    # return couple(b2, b0, b1)

def couple(i2, b, i1):
    """Couples i2 to b*i1 (or if b then i1 else 0)
    (might work with expressions but not tested/thought about)

    Args:
        i2 (Var): The output variable to be coupled
        b (Var): A binary variable
        i1 (Var): An integer variable
    """
    global m, M
    # TODO: maybe simplify if i1 is binary
    # maybe name constraints
    m += (i2 <= i1)
    m += (i2 >= i1-(1-b)*M)
    m += (i2 <= b*M)
    
def comparisons(i1, i2):
    """Generates two binary decision variables cl and cg such that
    cl = 1 iff i1 < i2
    cg = 1 iff i1 > i2
    The formulas are non-optimal if only cl or cg is needed, but not both.
    
    Args:
        i1 (Var): An integer variable
        i2 (Var): An integer variable
    
    Returns:
        (Var, Var): The two binary decision variables (cl, cg)
    """
    global m, M
    # maybe name constraints
    c_gt = m.add_var(var_type=BINARY)
    c_lt = m.add_var(var_type=BINARY)
    m += (i1-i2 >= 1-M*(1-c_gt))
    m += (i2-i1 >= 1-M*(1-c_lt))
    m += (c_gt+c_lt <= 1)
    m += (i2-i1 >= -M*c_gt)
    m += (i1-i2 >= -M*c_lt)
    return c_lt, c_gt


# Set up the variables

v = {}
fgt = {}
flt = {}

# c_noop = {}
c_cmp   = {}
c_mov   = {}
c_cmovg = {}
c_cmovl = {}

# commands
for i in range(timestamps):
    c_cmp[i] = {}
    c_mov[i] = {}
    c_cmovg[i] = {}
    c_cmovl[i] = {}
    for a in range(total_registers):
        c_cmp[i][a] = {}
        c_mov[i][a] = {}
        c_cmovg[i][a] = {}
        c_cmovl[i][a] = {}
        for b in range(total_registers):
            if a == b:
                continue
            c_cmovg[i][a][b] = m.add_var(name="c_cmovg[%d][%d][%d]" % (i,a,b), var_type=BINARY)
            c_cmovl[i][a][b] = m.add_var(name="c_cmovl[%d][%d][%d]" % (i,a,b), var_type=BINARY)
            if a < b:
                c_cmp[i][a][b] = m.add_var(name="c_cmp[%d][%d][%d]" % (i,a,b), var_type=BINARY)
            c_mov[i][a][b] = m.add_var(name="c_mov[%d][%d][%d]" % (i,a,b), var_type=BINARY)

# registers and flags
for i in range(timestamps):
    v[i] = {}
    fgt[i] = {}
    flt[i] = {}
    for k in range(permutation_count):
        v[i][k] = {}
        fgt[i][k] = m.add_var(name="fgt[%d][%d]" % (i,k), var_type=BINARY)
        flt[i][k] = m.add_var(name="flt[%d][%d]" % (i,k), var_type=BINARY)
        for a in range(total_registers):
            v[i][k][a] = m.add_var(name="v[%d][%d][%d]" % (i,k,a), var_type=INTEGER)

# auxiliary variables
# for comparisons
is_gt = {}
is_lt = {}
for i in range(timestamps):
    is_gt[i] = {}
    is_lt[i] = {}
    for k in range(permutation_count):
        is_gt[i][k] = {}
        is_lt[i][k] = {}
        for a in range(total_registers):
            is_gt[i][k][a] = {}
            is_lt[i][k][a] = {}
            for b in range(total_registers):
                if a < b:
                    c_lt, c_gt = comparisons(v[i][k][a], v[i][k][b])
                    is_lt[i][k][a][b] = c_lt
                    is_gt[i][k][a][b] = c_gt

# for quadratic/cubic constraints
c_acmovg = {}
c_acmovl = {}
v_aval_g = {}
v_aval_l = {}
v_aval_m = {}
for i in range(timestamps):
    c_acmovg[i] = {}
    c_acmovl[i] = {}
    v_aval_g[i] = {}
    v_aval_l[i] = {}
    v_aval_m[i] = {}
    for k in range(permutation_count):
        c_acmovg[i][k] = {}
        c_acmovl[i][k] = {}
        v_aval_g[i][k] = {}
        v_aval_l[i][k] = {}
        v_aval_m[i][k] = {}
        for a in range(total_registers):
            c_acmovg[i][k][a] = {}
            c_acmovl[i][k][a] = {}
            v_aval_g[i][k][a] = {}
            v_aval_l[i][k][a] = {}
            v_aval_m[i][k][a] = {}
            for b in range(total_registers):
                if a == b:
                    continue
                c_acmovg[i][k][a][b] = m.add_var(name="c_acmovg[%d][%d][%d][%d]" % (i,k,a,b), var_type=BINARY)
                c_acmovl[i][k][a][b] = m.add_var(name="c_acmovl[%d][%d][%d][%d]" % (i,k,a,b), var_type=BINARY)
                coupleBinary(c_acmovg[i][k][a][b], c_cmovg[i][a][b], fgt[i][k])
                coupleBinary(c_acmovl[i][k][a][b], c_cmovl[i][a][b], flt[i][k])
                
                v_aval_g[i][k][a][b] = m.add_var(name="v_aval_g[%d][%d][%d][%d]" % (i,k,a,b), var_type=INTEGER)
                v_aval_l[i][k][a][b] = m.add_var(name="v_aval_l[%d][%d][%d][%d]" % (i,k,a,b), var_type=INTEGER)
                v_aval_m[i][k][a][b] = m.add_var(name="v_aval_m[%d][%d][%d][%d]" % (i,k,a,b), var_type=INTEGER)
                couple(v_aval_g[i][k][a][b], c_acmovg[i][k][a][b], v[i][k][b])
                couple(v_aval_l[i][k][a][b], c_acmovl[i][k][a][b], v[i][k][b])
                
                couple(v_aval_m[i][k][a][b], c_mov[i][a][b], v[i][k][b])
                
                
                

# debug
# for t in range(timestamps-1):
#     for k in range(permutation_count):
#         permutation = permutations[k]
#         for a in range(number_registers):
#             m += (v[t][k][a] == permutation[a]), "v_init[%d][%d]" % (k,a)
# m += (c_cmp[0][0][1] == 1), "c_cmp_init"
# m += (c_cmovg[1][2][1] == 1), "c_cmovg_init"

# if True:
#     A = 0
#     B = 1
#     C = 2
#     S = 3
#     def swap(i, X, Y):
#         global m
#         m += c_cmp[i][X][Y] == 1
#         m += c_cmovg[i+1][S][X] == 1
#         m += c_cmovg[i+2][X][Y] == 1
#         m += c_cmovg[i+3][Y][S] == 1
#     swap(0, A, B)
#     swap(4, B, C)
#     swap(8, A, B)

if True:
    X = 0
    Y = 1
    Z = 2
    S = 3
    
    # ("mov"  , S, Y),
    # ("cmp"  , Z, Y), 
    # ("cmovl", S, Z),
    # ("cmovg", Y, Z),
    # m +=   c_mov[0][S][Y] == 1
    # m +=   c_cmp[1][Y][Z] == 1
    # m += c_cmovg[2][S][Z] == 1
    # m += c_cmovl[3][Y][Z] == 1
    
    # ("mov"  , Z, X),
    # ("cmp"  , Y, X), 
    # ("cmovl", Z, Y),
    # ("cmovl", Y, X),
    # m +=   c_mov[4][Z][X] == 1
    # m +=   c_cmp[5][X][Y] == 1
    # m += c_cmovg[6][Z][Y] == 1
    # m += c_cmovg[7][Y][X] == 1
    
    # ("cmp"  , S, Z),
    # ("cmovl", X, S),
    # ("cmovg", Z, S), 
    # m +=   c_cmp[8][Z][S] == 1
    # m += c_cmovg[9][X][S] == 1
    # m += c_cmovl[10][Z][S] == 1


# init values
for k in range(permutation_count):
    permutation = permutations[k]
    m += (fgt[0][k] == 0), "fgt_init[%d]" % k
    m += (flt[0][k] == 0), "flt_init[%d]" % k
    for a in range(number_registers):
        m += (v[0][k][a] == permutation[a]), "v_init[%d][%d]" % (k,a)
    for a in range(number_registers, total_registers):
        m += (v[0][k][a] == 0), "v_init[%d][%d]" % (k,a)
        
        
# evolution of system (execute commands)
for i in range(timestamps):
    # execute one command
    # TODO: check that list comprehension works as intended
    cmps = xsum([c_cmp[i][a][b] for a in c_cmp[i] for b in c_cmp[i][a]])
    movs = xsum([c_mov[i][a][b] for a in c_mov[i] for b in c_mov[i][a]])
    cmovgs = xsum([c_cmovg[i][a][b] for a in c_cmovg[i] for b in c_cmovg[i][a]])
    cmovls = xsum([c_cmovl[i][a][b] for a in c_cmovl[i] for b in c_cmovl[i][a]])
    all_commands = cmps + movs + cmovgs + cmovls
    
    if i == timestamps-1:
        m += (all_commands == 0), "no_final_command"
        break
    
    m += (all_commands == 1), "all_commands[%d]" % i

    no_cmp = 1-cmps
    # TODO: maybe we can use the coupling directly
    no_cmp_var = m.add_var(name="no_cmp_var[%d]" % i, var_type=BINARY)
    m += (no_cmp_var == no_cmp), "no_cmp_var_def[%d]" % i
    
    # execute flags
    # update flags if comparison was executed
    # TODO: maybe couple above (at location of acmov)
    for k in range(permutation_count):
        act_prev_fgt = m.add_var(name="act_prev_fgt[%d][%d]" % (i,k), var_type=BINARY)
        act_prev_flt = m.add_var(name="act_prev_flt[%d][%d]" % (i,k), var_type=BINARY)
        coupleBinary(act_prev_fgt, no_cmp_var, fgt[i][k])
        coupleBinary(act_prev_flt, no_cmp_var, flt[i][k])
        f_gt_new = act_prev_fgt
        f_lt_new = act_prev_flt
        for a in c_cmp[i]:
            for b in c_cmp[i][a]:
                act_gt_cmp = m.add_var(name="act_gt_cmp[%d][%d][%d][%d]" % (i,k,a,b), var_type=BINARY)
                act_lt_cmp = m.add_var(name="act_lt_cmp[%d][%d][%d][%d]" % (i,k,a,b), var_type=BINARY)
                coupleBinary(act_gt_cmp, c_cmp[i][a][b], is_gt[i][k][a][b])
                coupleBinary(act_lt_cmp, c_cmp[i][a][b], is_lt[i][k][a][b])
                f_gt_new += act_gt_cmp
                f_lt_new += act_lt_cmp
        m += (fgt[i+1][k] == f_gt_new), "fgt_evo[%d][%d]" % (i,k)
        m += (flt[i+1][k] == f_lt_new), "flt_evo[%d][%d]" % (i,k)
        
    # execute moves
    for k in range(permutation_count):
        for a in range(total_registers):
            # m += (v[i+1][k][a] == v[i][k][a]), "v_evo[%d][%d][%d]" % (i,k,a)
    #         # no successfull mov with dest register a
            stay_same = 1-\
                xsum([c_acmovg[i][k][a][b] for b in c_cmovg[i][a]]) -\
                xsum([c_acmovl[i][k][a][b] for b in c_cmovl[i][a]]) -\
                xsum([c_mov[i][a][b] for b in c_mov[i][a]])
            stay_same_var = m.add_var(name="stay_same_var[%d][%d][%d]" % (i,k,a), var_type=BINARY)
            m += (stay_same_var == stay_same), "stay_same_var_def[%d][%d][%d]" % (i,k,a)
            act_prev_v = m.add_var(name="act_prev_v[%d][%d][%d]" % (i,k,a), var_type=INTEGER)
            couple(act_prev_v, stay_same_var, v[i][k][a])
            
            v_new_val = act_prev_v + \
                xsum([v_aval_g[i][k][a][b] for b in c_cmovg[i][a]]) + \
                xsum([v_aval_l[i][k][a][b] for b in c_cmovl[i][a]]) + \
                xsum([v_aval_m[i][k][a][b] for b in c_mov[i][a]])
            m += (v[i+1][k][a] == v_new_val), "v_evo[%d][%d][%d]" % (i,k,a)

# no command at last timestamp
# t = timestamps-1
# cmps = xsum([c_cmp[t][a][b] for a in c_cmp[t] for b in c_cmp[t][a]])
# cmovgs = xsum([c_cmovg[t][a][b] for a in c_cmovg[t] for b in c_cmovg[t][a]])
# cmovls = xsum([c_cmovl[t][a][b] for a in c_cmovl[t] for b in c_cmovl[t][a]])
# movs = xsum([c_mov[t][a][b] for a in c_mov[t] for b in c_mov[t][a]])
# all_commands = cmps + movs + cmovgs + cmovls
# m += (all_commands == 0), "all_commands[%d]" % t


# goal

# all sorted i => i
# for k in range(permutation_count):
#     for a in range(number_registers):
#         m += (v[timestamps-1][k][a] == a+1), "v_goal[%d][%d]" % (k,a)

# same across all permutations
for a in range(number_registers):
    for k in range(permutation_count):
        for k2 in range(permutation_count):
            # k == k2 holds theoretically but the IP has problems with it
            if k != k2:
                m += (v[timestamps-1][k][a] == v[timestamps-1][k2][a]), "v_goal_same_register[%d][%d][%d]" % (k,k2,a)
                # print(f"Add constraint v[{timestamps-1}][{k}][{a}] == v[{timestamps-1}][{k2}][{a}]")
            
# different between registers
for k in range(permutation_count):
    for a in range(number_registers):
        for b in range(number_registers):
            if a < b:
                # m += (v[timestamps-1][k][a] != v[timestamps-1][k][b]), "v_goal_different_registers[%d][%d][%d]" % (k,a,b)
                m += (is_gt[timestamps-1][k][a][b] + is_lt[timestamps-1][k][a][b] == 1), "v_goal_diff_perm[%d][%d][%d]" % (k,a,b)
                
# greater than zero
for k in range(permutation_count):
    for a in range(number_registers):
        m += (v[timestamps-1][k][a] >= 1), "v_goal_positive[%d][%d]" % (k,a)
                
                
# heuristics (noop-prevention)
# m += c_cmp[0][0][1] == 1
                
# no two cmp in a row
for i in range(timestamps-1):
    cmps = xsum([c_cmp[i][a][b] for a in c_cmp[i] for b in c_cmp[i][a]])
    cmps_next = xsum([c_cmp[i+1][a][b] for a in c_cmp[i+1] for b in c_cmp[i+1][a]])
    m += (cmps + cmps_next <= 1), "no_two_cmp_in_a_row[%d]" % i
                
# no noop in general (+use flags)
                
                
# print intermediate solutions

# alibi objective to guide and have a ranking
# cmp_sum = xsum([c_cmp[i][a][b] for i in range(timestamps) for a in c_cmp[i] for b in c_cmp[i][a]])
# m.objective = minimize(cmp_sum)
# m.objective = maximize(cmp_sum)

# at most one solution
m.max_solutions = 1
m.optimize(max_solutions=1)
                
                
# call with
# python sort_linear.py | tee sort_linear_$(date +%Y-%m-%d_%H-%M-%S).txt
                
                
                
    
def is_set(x: Var):
    return x.x >= 0.5
    
def val(x: Var):
    num_val = int(x.x+0.5)
    if x.var_type == BINARY:
        return "■" if num_val == 1 else "□"
    else:
        return str(num_val)
    
def printSol():
    commands = []
    for i in range(timestamps):
        print("Timestamp %d" % i)
        for k in range(permutation_count):
            registers = v[i][k].items()
            registers = sorted(registers, key=lambda x: x[0])
            flag_str = ("<" if is_set(flt[i][k]) else "") + (">" if is_set(fgt[i][k]) else "")
            flag_str = "[" + flag_str + "]"
            for a in range(total_registers):
                r_v = registers[a][1]
                cmp_str = ""
                if a < len(registers)-1:
                    r_is_lt = is_set(is_lt[i][k][a][a+1])
                    r_is_gt = is_set(is_gt[i][k][a][a+1])
                    cmp_str = ("<" if r_is_lt else "") + (">" if r_is_gt else "")
                    if not r_is_lt and not r_is_gt:
                        cmp_str = "="
                    cmp_str = " " + cmp_str + " "
                    # cmp_str = ", "
                print(val(r_v), end=cmp_str)
            print("  " + flag_str)

        command = ""
        # if c_noop[i].X >= 0.5:
        #     command+="noop"
        for a in c_cmp[i]:
            for b in c_cmp[i][a]:
                if is_set(c_cmp[i][a][b]):
                    command+="cmp r%d r%d" % (a,b)
        for a in c_cmovg[i]:    
            for b in c_cmovg[i][a]:
                if is_set(c_cmovg[i][a][b]):
                    command+="cmovg r%d r%d" % (a,b)
        for a in c_cmovl[i]:
            for b in c_cmovl[i][a]:
                if is_set(c_cmovl[i][a][b]):
                    command+="cmovl r%d r%d" % (a,b)

        print("Execute command: %s" % command)
        commands.append(command)
        print()
        
    print("Commands: ")
    print("\n".join(commands))

if not m.num_solutions:
    print("We have no solution!")
    
    cf = conflict.ConflictFinder(m)
    iis = cf.find_iis(method=conflict.IISFinderAlgorithm.DELETION_FILTER)
    for c in iis:
        print(c)
    
    exit(1)

printSol()
