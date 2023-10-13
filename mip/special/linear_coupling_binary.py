from mip import Model, xsum, BINARY, INTEGER, OptimizationStatus, CBC
import itertools

for b0v, b1v in itertools.product([0,1],[0,1]):
    model = Model(solver_name=CBC)
    model.verbose = 0
    
    b1 = model.add_var("b1", var_type=BINARY)
    b0 = model.add_var("b0", var_type=BINARY)
    
    model += (b1==b1v)
    model += (b0==b0v)
    
    b2 = model.add_var("b2", var_type=BINARY)
    
    model += (b2 <= b0)
    model += (b2 <= b1)
    model += (b2 >= b0 + b1 - 1)
    # M = 10
    # model += (i2 <= i1)
    # model += (i2 >= i1-(1-b)*M)
    # model += (i2 <= b*M)
    
    print("Solving for "+((b0.name)+"="+str(b0v))+", "+((b1.name)+"="+str(b1v)))
    
    # print all solutions
    while True:
        status = model.optimize()
        # print("Number of solutions: %d" % model.num_solutions)
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            for v in model.vars:
                print('%s: %g' % (v.name, v.x))
        else:
            break
        model += xsum([1-v if v.x else v for v in [b2]]) >= 1
        # break
        print()
    
    print()
        