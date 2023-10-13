from mip import Model, xsum, BINARY, INTEGER, OptimizationStatus, CBC, minimize
import itertools

model = Model(solver_name=CBC)
model.verbose = 0

i1 = model.add_var("i1", var_type=INTEGER)
i2 = model.add_var("i2", var_type=INTEGER)

M = 10

model+= (i2 <= i1)
model+= (i2 >= 42)
model+= (i2 == i2)

# model.objective = minimize(i2)

status = model.optimize()
if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
    for v in model.vars: print('%s: %g' % (v.name, v.x))
else:
    print("No solution found")
print()
