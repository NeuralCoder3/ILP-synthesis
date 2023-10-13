from minizinc import Instance, Model, Solver

# Load n-Queens model from file
nqueens = Model("./nqueens.mzn")
# Find the MiniZinc solver configuration for Gecode
solver = Solver.lookup("gecode")
# solver = Solver.lookup("mip")
# solver = Solver.lookup("gurobi")
# Create an Instance of the n-Queens model for Gecode
instance = Instance(solver, nqueens)
# Assign 4 to n
instance["n"] = 4

# normal
result = instance.solve()
print(result["q"])

# intermediate_solutions / all solutions (not supported by Gurobi)
# result = instance.solve(intermediate_solutions=True)
# result = instance.solve(all_solutions=True)
# for i in range(len(result)):
#     print(result[i, "q"])
