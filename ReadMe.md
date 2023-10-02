
We want to use integer programming (IP) to synthesize programs.
Common subproblems are ILP and MIP.
Good libraries are Python-MIP which in turn can employ solvers like CBC or Gurobi.

The encoding is non-trivial and requires some thought.
Especially, we want to represent complex non-linear interaction 
only using linear constraints and integer variables.

## Greater

One subproblem for comparing registers is to check if one is greater than the other.
In the end, we want a binary decision variable that is $1$ if $a>b$ and $0$ otherwise.

A constraint like $b+c\cdot a\geq a$ would force $c$ to be $1$ if $a>b$.
However, this constraint is quadratic and thus not allowed in MIP.

Instead, we use additional variables, an upper bound, and multiple one-sided constraints:
- $a-b \geq 1-M\cdot(1-c_>)$
- $b-a \geq 1-M\cdot(1-c_<)$
- $c_>+c_<\leq 1$
- $a-b\geq -M\cdot c_<$
- $b-a\geq -M\cdot c_>$

$M$ is a bound large enough to consume $a$ and $b$.
The last two constraints prevent the $c_<=c_>=0$ case when $a\neq b$.
Without them, $a=b$ would force $c_<=c_>=0$ but $a>b$ and $a<b$ would have two solutions:
The intended one and $c_<=c_>=0$.

## Sorting

We want to synthesize a sorting algorithm with the conditional move and compare instructions.
We therefore have the commands `noop`, `cmovg a b` (16), `cmovl a b` (16), `cmp a b` (3-16).

We encode the state of the registers (three and one swap) as integers.
The flags (greater, less) are represented as binary variables.
We simultanously encode all possible permutations to represent a general sorting indepedent of inputs.

Futhermore, we have binary variable for every possible command.

Additionally, for every (interesting) pair of registers in one permutation and timestamp, we add comparison decisions that encode which register contains a greater value.

For the first timestamp, we initialize the register $i$ with $i$, the swap register with $0$, and the flags with $0$.

## Links
- [Python-MIP](https://docs.python-mip.com/en/latest/examples.html)
- [Complete MIP Docs](https://buildmedia.readthedocs.org/media/pdf/python-mip/latest/python-mip.pdf#page=8&zoom=100,96,96)


https://pypi.org/project/qpsolvers/
MIQP
