from mip import Model, xsum, BINARY, INTEGER, OptimizationStatus, CBC
import itertools

for i1v, bv in itertools.product([0,1,2,3],[0,1]):
    model = Model(solver_name=CBC)
    model.verbose = 0
    
    i1 = model.add_var("i1", var_type=INTEGER)
    b = model.add_var("b", var_type=BINARY)
    
    model += (i1==i1v)
    model += (b==bv)
    
    i2 = model.add_var("i2", var_type=INTEGER)
    
    M = 10
    model += (i2 <= i1)
    model += (i2 >= i1-(1-b)*M)
    model += (i2 <= b*M)
    
    print("Solving for "+((i1.name)+"="+str(i1v))+", b="+str(bv))
    
    # print all solutions
    while True:
        status = model.optimize()
        # print("Number of solutions: %d" % model.num_solutions)
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            for v in model.vars:
                print('%s: %g' % (v.name, v.x))
        else:
            break
        # model += xsum([1-v if v.x else v for v in [cgt,clt]]) >= 1
        break
        print()
    
    print()
        