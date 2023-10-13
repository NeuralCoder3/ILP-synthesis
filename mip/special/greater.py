from sys import stdout
from mip import Model, xsum, BINARY, INTEGER, OptimizationStatus


for av,bv in [(2,2),(2,3),(3,2)]:
    model = Model()
    model.verbose = 0

    a = model.add_var("a", var_type=INTEGER)
    b = model.add_var("b", var_type=INTEGER)
    cgt = model.add_var("cgt", var_type=BINARY)
    clt = model.add_var("clt", var_type=BINARY)
    
    
    # reset the model
    # model.reset()
    
    model += (a==av)
    model += (b==bv)
    
    # model += (b + c * a >= a)
    # model += (a-b >= 1-c)
    # model += (a-b <= (a-b).ub*c)
    # M = max(a.ub,b.ub)
    # model += a-b-M*(1-c) <= 0
    # model += a-b >= 1-(a-b).ub()*(1-c)
    # model += a-b <= M*c
    # model += a-b >= 1-M*(1-c)
    # M = max(a.ub,b.ub)+1
    M = 1000
    # model += a-b - M * (1-c) >= -M
    model += a-b >= 1-M*(1-cgt)
    model += b-a >= 1-M*(1-clt)
    model += cgt+clt <= 1 
    # remove c0=c1=0 case if a!=b
    model += (a-b) >= -clt
    model += (b-a) >= -cgt
    # model += c0+c1 == 1 
    # model += c0+c1 >= 1 
    
    print("Solving for a=%d, b=%d" % (av,bv))
    
    # print all solutions
    while True:
        status = model.optimize()
        # print("Number of solutions: %d" % model.num_solutions)
        if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
            print('a: %g' % a.x)
            print('b: %g' % b.x)
            print('cgt: %g' % cgt.x)
            print('clt: %g' % clt.x)
        else:
            break
        # exit(0)
        # model+= (1-c if c.x else c) >= 1
        model += xsum([1-v if v.x else v for v in [cgt,clt]]) >= 1
        print()
    
    print()
        
        # remove the current solution
        # model += (abs(c - c.x) > 0)
    # if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
    #     stdout.write('\n')
    #     stdout.write('c: %g\n' % c.x)
    #     stdout.write('a: %g\n' % a.x)
    #     stdout.write('b: %g\n' % b.x)
    # for v in model.vars:
    #     stdout.write('%s: %g\n' % (v.name, v.x))
        
    # exit(0)

# model+= (a==3)
# model+= (b==1)

# # c means "a is greater than b"
# # model+= (c==1) >> (a>b)

# model.optimize()
# if model.num_solutions:
#     stdout.write('\n')
#     stdout.write('c: %g\n' % c.x)
#     stdout.write('a: %g\n' % a.x)
#     stdout.write('b: %g\n' % b.x)
