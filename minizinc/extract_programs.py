import os
import sys
import typing

# file = "sort_sol_11_chuffed_a.txt"
file = "result/sort_sol_11_chuffed_a_order.txt"
# file = "result/sort_sol_11_chuffed_a.txt"
output = "output"
if not os.path.exists(output):
    os.makedirs(output)
length = 11
n = 3
s = 1

programs = []
current_program = []
inProgram = True

with open(file,"r") as f:
    content = f.readlines()

sep = "----------"
if content[0].startswith("Program:"):
    sep = "Program:"
    
for l in content:
    l = l.strip()
    if l.startswith(sep):
        inProgram = True
        current_program = []
    elif inProgram:
        current_program.append(l)
        if len(current_program) == length:
            programs.append(current_program)
            inProgram = False
    
seenPrograms = set()
new_programs = []
for p in programs:
    sp = "\n".join(p)
    if sp in seenPrograms:
        continue
    seenPrograms.add(sp)
    new_programs.append(p)

# print(len(programs))
programs = new_programs
print(len(programs))

# sort by count of 1*mov + 2*cmp + 3*cmov

# type command = tuple[str,int,int]

def getCommand(line:str) -> tuple[str,int,int]:
    line = line.lower().strip()
    # parts = line.split(" ")
    # if len(parts)<3:
    #     print(parts)
    instr,a,b = line.split(" ")
    a = int(a)
    b = int(b)
    return instr,a,b

def score(instr:str):
    if instr=="mov":
        return 1
    elif instr=="cmp":
        return 2
    else:
        return 4
    
def parseProgram(program:list[str]):
    return [getCommand(s) for s in program]

def programScore(program:list[tuple[str,int,int]]):
    instrs = [i for i,_,_ in program]
    program_score = sum([score(i) for i in instrs])
    return program_score

def printProgram(program:list[tuple[str,int,int]]):
    for i,a,b in program:
        print(f"{i} {a} {b}")
        
def programToString(program:list[tuple[str,int,int]]):
    return "\n".join([f"{i} {a} {b}" for i,a,b in program])

programs = [parseProgram(p) for p in programs]
best = min(programs, key=programScore)
# printProgram(best)
    
movs = sum([1 for i,_,_ in best if i=="mov"])
cmps = sum([1 for i,_,_ in best if i=="cmp"])
cmovs = sum([1 for i,_,_ in best if i.startswith("cmov")])
print(f"{movs} Move instructions, {cmps} Compare instructions, {cmovs} Conditional Move instructions")


original_programs = programs
programs = sorted(programs, key=programScore)
# get all programs with the minimal score
best_score = programScore(programs[0])
best = [p for p in programs if programScore(p)==best_score]
print(f"There are {len(best)} programs with the best score of {best_score}")

less_flag = n+s
greater_flag = n+s+1
flags = [less_flag, greater_flag]

def getReads(command:tuple[str,int,int]) -> list[int]:
    i,a,b = command
    if i == "cmp":
        return [a,b]
    elif i.startswith("cmov"):
        return [b]+flags
    elif i == "mov":
        return [b]
    else:
        assert False, f"Unknown instruction {i}"

def getWrites(command:tuple[str,int,int]) -> list[int]:
    i,a,b = command
    if i == "cmp":
        return flags
    elif i.startswith("cmov"):
        return [a]
    elif i == "mov":
        return [a]
    else:
        assert False, f"Unknown instruction {i}"
        
def hasDependency(cmd1, cmd2, raw=True, waw=False, war=False):
    # raw: read after write
    # waw: write after write
    # war: write after read
    if raw:
        reads1 = getReads(cmd1)
        writes2 = getWrites(cmd2)
        if any(r in writes2 for r in reads1):
            return True
    if waw:
        writes1 = getWrites(cmd1)
        writes2 = getWrites(cmd2)
        if any(w in writes2 for w in writes1):
            return True
    if war:
        writes1 = getWrites(cmd1)
        reads2 = getReads(cmd2)
        if any(w in reads2 for w in writes1):
            return True
    return False

def depGraph(program, *args, **kwargs):
    graph = []
    for i,cmd1 in enumerate(program):
        graph.append([])
        for j,cmd2 in enumerate(program):
            if j<=i:
                continue
            if hasDependency(cmd1, cmd2, *args, **kwargs):
                graph[i].append(j)
    return graph

def criticalPath(depGraph):
    n = len(depGraph)
    visited = [False]*n
    dp = [0]*n
    
    def dfs(u):
        if visited[u]:
            return dp[u]
        visited[u] = True
        for v in depGraph[u]:
            dp[u] = max(dp[u], dfs(v)+1)
        return dp[u]
    
    for u in range(n):
        dfs(u)
    
    return max(dp)

raw = True
# waw = False
# war = False
waw = True
war = True
best = [(p, criticalPath(depGraph(p, raw=raw, war=war, waw=waw))) for p in best]
best = sorted(best, key=lambda x: x[1])
print(f"The best program has a critical path of {best[0][1]}")
print(f"The worst best program has a critical path of {best[-1][1]}")

best_path = best[0][1]
best = [p for p,s in best if s==best_path]
print("There are", len(best), "programs with the best critical path of length", best_path)

print("The best program is:")
printProgram(best[0])

# print("The worst best program is:")
# printProgram(best[-1][0])


count = {}
for p in original_programs:
    pscore = programScore(p)
    code = programToString(p)
    path = criticalPath(depGraph(p, raw=raw, war=war, waw=waw))
    if pscore not in count:
        count[pscore] = {}
    if path not in count[pscore]:
        count[pscore][path] = 0
    count[pscore][path] += 1
    outputPath = os.path.join(output, str(pscore), str(path), str(count[pscore][path])+".txt")
    os.makedirs(os.path.dirname(outputPath), exist_ok=True)
    with open(outputPath, "w") as f:
        f.write(code)
        