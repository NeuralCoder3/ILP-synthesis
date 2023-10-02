Everything except registers (v_*) is a decision variable (0,1)
In step i we execute a command to change the state from i to i+1


Variables
=========

State k at timestep i:
    register: v_i_k_a
    for 0 <= a < 3+1 (swap)
    flag: f_gt_i_k, f_lt_i_k

Command Vars:
    c_cmd_i_a_b
    for cmd in {cmp, cmovg, cmovl}
    c_noop_i

Aux Vars:
    is_gt_i_k_a_b
    





Constraints
===========

Initializer:
    v_0_k_0 = 1
    v_0_k_1 = 2
    v_0_k_2 = 3
    v_0_k_3 = 0
    f_gt_i_k = 0
    f_lt_i_k = 0

Per Step i -> i+1:
    only one instruction:
        c_noop_i + sum c_cmd_i_a_b = 1
    values: 
        v_(i+1)_k_a = 
            (sum_b c_cmovg_i_a_b * f_gt_i_k * v_i_k_b) + 
            (sum_b c_cmovl_i_a_b * f_lt_i_k * v_i_k_b) + 
            noop_i_a * v_i_k_a
    flags:
        f_gt_(i+1)_k = no_cmp_i*f_gt_i_k + sum_a sum_b c_cmp_i_a_b * is_gt_i_k_a_b
        f_lt_(i+1)_k = no_cmp_i*f_lt_i_k + sum_a sum_b c_cmp_i_a_b * is_lt_i_k_a_b
    auxiliary:
        is_gt_i_k_a_b = ??? (see greater formulation)
        
aliases:
    no_cmp_i = 1-some_compare_i
    some_compare_i = sum c_cmp_i_a_b
    noop_i_a = 1-(sum_b c_cmovg_i_a_b + sum_b c_cmovl_i_a_b)
        cmp or any cmov without a in front
        1 - all cmovg/l with a in front
        
