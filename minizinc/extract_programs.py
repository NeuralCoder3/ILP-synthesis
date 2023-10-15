import os
import sys
import typing

file = "sort_sol_11_chuffed_a.txt"
# file = "sort_sol_11_chuffed_a_order.txt"
length = 11

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

programs = [parseProgram(p) for p in programs]
best = min(programs, key=programScore)
for i, a, b in best:
    print(f"{i} {a} {b}")
    
movs = sum([1 for i,_,_ in best if i=="mov"])
cmps = sum([1 for i,_,_ in best if i=="cmp"])
cmovs = sum([1 for i,_,_ in best if i.startswith("cmov")])
print(f"{movs} Move instructions, {cmps} Compare instructions, {cmovs} Conditional Move instructions")


programs = sorted(programs, key=programScore)
# get all programs with the minimal score
best_score = programScore(programs[0])
best = [p for p in programs if programScore(p)==best_score]
print(f"There are {len(best)} programs with the best score of {best_score}")