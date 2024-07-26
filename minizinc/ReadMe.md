- [MiniZinc Problem Collection](http://www.hakank.org/minizinc/index.html)
- [FlatZinc to SMT](https://github.com/MiniZinc/libminizinc/issues/161)
- [FlatZinc Flattening](https://www.minizinc.org/doc-2.7.6/en/flattening.html)
- [MiniZinc User Manual](https://www.minizinc.org/doc-2.7.6/en/part_3_user_manual.html)
- [MiniZinc Python](https://minizinc-python.readthedocs.io/en/latest/)
- [Advanced Python Usage](https://minizinc-python.readthedocs.io/en/latest/advanced_usage.html)
- [Discussion about MiniZinc](https://news.ycombinator.com/item?id=16194112)
- [Builtin Predicates](https://www.minizinc.org/doc-2.4.3/en/lib-builtins.html)
- [Global Predicates](https://www.minizinc.org/doc-2.7.6/en/predicates.html)
- [Tips](https://www.minizinc.org/doc-2.7.6/en/efficient.html)


Run with `minizinc --solver Chuffed sort_syn.mzn sort_data.dzn` for fastest solving.
Use `-a` to print all solutions (or intermediate solutions if solve satisfiable).

`time minizinc --solver Chuffed -a sort_syn.mzn sort_data.dzn | tee -a sort_sol_11_chuffed_a_order.txt`

To try:
- [ ] systematic other solvers
- [ ] `O0` ... `O5` (`O5` does not seem to improve optimizing query)
- [x] enforce output 123 (30s-1min -> 5s)
- [ ] compute critical path for solutions (dependency DAG)


With consistent renaming, every permutation should be possible as output
=> We can restrict the search space to 1/6.
(One could think that the compare restriction might violate this assumption but the enumeration of all programs validates it.)

All programs:
- With output order:
  - all: 5602
  - max mov, cmp: 2520
  - time: 13m
  - minimal raw: 680
  - minimal raw+war+waw: 576
- Without output order:
  - all: 33612
  - max mov, cmp: 15120
  - time: 154m


How to extract:









time minizinc --solver Chuffed sort_syn_v2_org_change.mzn sort_data3.dzn

time minizinc --solver Chuffed sort_syn_mixed.mzn sort_data3.dzn



Available solver configurations:
  Chuffed 0.12.1 (org.chuffed.chuffed, cp, lcg, int)
  COIN-BC 2.10.10/1.17.8 (org.minizinc.mip.coin-bc, mip, float, api, osicbc, coinbc, cbc)
  Couenne 0.5.8 (org.coin-or.couenne)
  CPLEX <unknown version> (org.minizinc.mip.cplex, mip, float, api)
  findMUS 0.7.0 (org.minizinc.findmus)
  Gecode 6.3.0 (org.gecode.gecode, default solver, cp, int, float, set, restart)
  Gecode Gist 6.3.0 (org.gecode.gist, cp, int, float, set, restart)
  Globalizer 0.1.7.2 (org.minizinc.globalizer, experimental, tool)
  Gurobi 10.0.3 (org.minizinc.mip.gurobi, mip, float, api)
  HiGHS 1.5.1 (org.minizinc.mip.highs, mip, float, api, highs)
  SCIP <unknown version> (org.minizinc.mip.scip, mip, float, api)
  Xpress <unknown version> (org.minizinc.mip.xpress, mip, float, api)
Search path for solver configurations:
  /opt/minizinc-ide/share/minizinc/solvers
  /usr/local/share/minizinc/solvers
  /usr/share/minizinc/solvers



Available solver configurations:
  Chuffed 0.12.1 (org.chuffed.chuffed, cp, lcg, int)
  COIN-BC 2.10.10/1.17.8 (org.minizinc.mip.coin-bc, mip, float, api, osicbc, coinbc, cbc)
  Couenne 0.5.8 (org.coin-or.couenne)
  CPLEX <unknown version> (org.minizinc.mip.cplex, mip, float, api)
  findMUS 0.7.0 (org.minizinc.findmus)
  Gecode 6.3.0 (org.gecode.gecode, default solver, cp, int, float, set, restart)
  Gecode Gist 6.3.0 (org.gecode.gist, cp, int, float, set, restart)
  Globalizer 0.1.7.2 (org.minizinc.globalizer, experimental, tool)
  Gurobi 10.0.3 (org.minizinc.mip.gurobi, mip, float, api)
  HiGHS 1.5.1 (org.minizinc.mip.highs, mip, float, api, highs)
  OR Tools CP-SAT 9.8.9999 (com.google.ortools.sat, cpsatlp, cp, lcg, int)
  SCIP <unknown version> (org.minizinc.mip.scip, mip, float, api)
  Xpress <unknown version> (org.minizinc.mip.xpress, mip, float, api)



gecode >950min?
gurobi >166min
ortools >72min


com.google.ortools.sat =58min