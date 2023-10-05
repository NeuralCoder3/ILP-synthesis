import itertools
from sys import stdout
from mip import Model, xsum, BINARY, INTEGER, CBC, Var


timestamps = 14
# timestamps = 12
# timestamps = 11
number_registers = 3
swap = 1
total_registers = number_registers + swap
# all permutations of 1,2,3
permutations = list(itertools.permutations(range(1,number_registers+1)))
permutation_count = len(permutations)


m = Model()
# model = Model(solver_name=CBC)
M = 10 # an upper bound for the integer variables/expressions

def couple(i2, b, i1):
    """Couples i2 to b*i1 (or if b then i1 else 0)
    (might work with expressions but not tested/thought about)

    Args:
        i2 (Var): The output variable to be coupled
        b (Var): A binary variable
        i1 (Var): An integer variable
    """
    global m, M
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
c_cmp = {}
c_cmovg = {}
c_cmovl = {}

# commands
for i in range(timestamps):
    c_cmp[i] = {}
    c_cmovg[i] = {}
    c_cmovl[i] = {}
    for a in range(total_registers):
        c_cmp[i][a] = {}
        c_cmovg[i][a] = {}
        c_cmovl[i][a] = {}
        for b in range(total_registers):
            if a == b:
                continue
            c_cmovg[i][a][b] = m.add_var(name="c_cmovg[%d][%d][%d]" % (i,a,b), var_type=BINARY)
            c_cmovl[i][a][b] = m.add_var(name="c_cmovl[%d][%d][%d]" % (i,a,b), var_type=BINARY)
            if a < b:
                c_cmp[i][a][b] = m.add_var(name="c_cmp[%d][%d][%d]" % (i,a,b), var_type=BINARY)

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
for i in range(timestamps):
    c_acmovg[i] = {}
    c_acmovl[i] = {}
    for k in range(permutation_count):
        c_acmovg[i][k] = {}
        c_acmovl[i][k] = {}
        for a in range(total_registers):
            c_acmovg[i][k][a] = {}
            c_acmovl[i][k][a] = {}
            for b in range(total_registers):
                if a == b:
                    continue
                c_acmovg[i][k][a][b] = m.add_var(name="c_acmovg[%d][%d][%d][%d]" % (i,k,a,b), var_type=BINARY)
                c_acmovl[i][k][a][b] = m.add_var(name="c_acmovl[%d][%d][%d][%d]" % (i,k,a,b), var_type=BINARY)
                couple(c_acmovg[i][k][a][b], c_cmovg[i][a][b], fgt[i][k])
                couple(c_acmovl[i][k][a][b], c_cmovl[i][a][b], flt[i][k])
                




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
for i in range(timestamps-1):
    cmps = xsum([c_cmp[i][a][b] for b in c_cmp[i][a] for a in c_cmp[i]])
    cmovg = xsum([c_cmovg[i][a][b] for b in c_cmovg[i][a] for a in c_cmovg[i]])
    cmovl = xsum([c_cmovl[i][a][b] for b in c_cmovl[i][a] for a in c_cmovl[i]])
    all_commands = cmps + cmovg + cmovl
    m += (all_commands == 1), "all_commands[%d]" % i




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
                print(f"Add constraint v[{timestamps-1}][{k}][{a}] == v[{timestamps-1}][{k2}][{a}]")
            
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
                
m.optimize()

if not m.num_solutions:
    print("We have no solution!")
    exit(1)
    
def is_set(x: Var):
    return x.x >= 0.5
    
def val(x: Var):
    num_val = int(x.x+0.5)
    if x.var_type == BINARY:
        return "■" if num_val == 1 else "□"
    else:
        return str(num_val)
    
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