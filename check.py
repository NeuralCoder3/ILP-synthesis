import itertools


number_registers = 3
swap = 1
total_registers = number_registers + swap
permutations = list(itertools.permutations(range(1,number_registers+1)))


states = []
for p in permutations:
    # state.append(list(p) + [0] * swap + [False,False])
    states.append({
        'registers': list(p) + [0] * swap,
        # 'swap': [0] * swap,
        'lt': False,
        'gt': False,
    })
    
# print(states)


def apply(stmt, state):
    instr, a, b = stmt
    va = state['registers'][a]
    vb = state['registers'][b]
    if instr == "mov":
        state['registers'][a] = vb
    elif instr == "cmp":
        state['lt'] = va < vb
        state['gt'] = va > vb
    elif instr == "cmovl":
        if state['lt']:
            state['registers'][a] = vb
    elif instr == "cmovg":
        if state['gt']:
            state['registers'][a] = vb
    else:
        raise Exception("Unknown instruction: " + instr)
        


X = 0
Y = 1
Z = 2
S = 3
program = [
    # XYZ = ABC
    # Swap
    
    ("mov"  , S, Y), # S = B
               
    ("cmp"  , Z, Y), 
    ("cmovl", S, Z), # S = max(Y,Z) = max(B,C)
    ("cmovg", Y, Z), # Y = min(Y,Z) = min(B,C)
               
               
    ("cmp"  , Y, X), 
    ("mov"  , Z, X), # Z = A
    ("cmovl", Z, Y), # Z = max(X,Y) = max(A,min(B,C))
    ("cmovl", Y, X), # Y = min(X,Y) = min(A,min(B,C)) => global min
               
    ("cmp"  , S, Z), # max(A,min(B,C)) ? max(B,C)
    ("cmovl", X, S), # 
    ("cmovg", Z, S), 
    # X = min
    # Y = max
    # Z = middle
]



program = [
    ("mov"  , S, Y),
    ("cmp"  , Z, Y), 
    ("cmovl", S, Z),
    ("cmovg", Y, Z),
               
    ("mov"  , Z, X),
    ("cmp"  , Y, X), 
    ("cmovl", Z, Y),
    ("cmovl", Y, X),
               
    ("cmp"  , S, Z),
    ("cmovl", X, S),
    ("cmovg", Z, S), 
]
# 11

def printState(state):
    print(", ".join(str(s) for s in state['registers']), 
          "<" if state['lt'] else "", ">" if state['gt'] else "")

for stmt in program:
    print("Statement: ", stmt)
    for state in states:
        apply(stmt, state)
    for state in states:
        printState(state)
        
    print("")
