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
- systematic other solvers
- `O0` ... `O5` (`O5` does not seem to improve optimizing query)
- [x] enforce output 123 (30s-1min -> 5s)


With consistent renaming, every permutation should be possible as output
=> We can restrict the search space to 1/6.
(One could think that the compare restriction might violate this assumption but the enumeration of all programs validates it.)

All programs:
- With output order:
  - all: 5602
  - max mov, cmp: 2520
  - time: 13m
- Without output order:
  - all: 33612
  - max mov, cmp: 15120
  - time: 154m
