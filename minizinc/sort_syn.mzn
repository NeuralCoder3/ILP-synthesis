int: s; % The number of timesteps.
int: perm_count;
int: n; % number of registers
int: swap;
array [1..perm_count, 1..n] of int: init_perm;

include "globals.mzn";
% include "chuffed.mzn"; % makes it slower

enum Inst = { Cmp, Mov, CMovG, CMovL};
int: reg = n+swap;

array [1..s] of var Inst: cmd;
array [1..s] of var 1..reg: a;
array [1..s] of var 1..reg: b;

array [1..s,1..perm_count,1..reg] of var 0..n: state;
array [1..s,1..perm_count,1..2] of var bool: flags;

constraint %% state[0,..] = init_perm
    forall (k in 1..perm_count, r in 1..n) (
        state[1,k,r] = init_perm[k,r]
    );

constraint %% state[0,..,swap] = 0
    forall (k in 1..perm_count, r in 1..swap) (
        state[1,k,n+r] = 0
    );

constraint %% init flags are false
    forall (k in 1..perm_count) (
        flags[1,k,1] = false /\ flags[1,k,2] = false
    );

constraint %% don't operate with yourself
    forall (t in 1..s) (
        a[t] != b[t]
    );



%% evolution of state (executing commands)

constraint %% change flags (execute compare)
    forall (t in 1..(s-1)) (
        (cmd[t] = Cmp -> 
            forall (k in 1..perm_count) (
                flags[t+1,k,1] = (state[t,k,a[t]] < state[t,k,b[t]]) /\
                flags[t+1,k,2] = (state[t,k,a[t]] > state[t,k,b[t]])
            )) /\
        (cmd[t] != Cmp ->
            forall (k in 1..perm_count) (
                flags[t+1,k,1] = flags[t,k,1] /\
                flags[t+1,k,2] = flags[t,k,2]
            ))
    );

constraint %% change values (execute (c)mov)
    forall (t in 1..(s-1)) (
        % all non-a stay the same
        forall (k in 1..perm_count, r in 1..reg) (
            if r != a[t] then
                state[t+1,k,r] = state[t,k,r]
            endif
        ) /\
        (cmd[t] = Mov -> 
            forall (k in 1..perm_count) (
                state[t+1,k,a[t]] = state[t,k,b[t]]
            )) /\
        (cmd[t] = CMovL -> 
            forall (k in 1..perm_count) (
                if flags[t,k,1] then
                    state[t+1,k,a[t]] = state[t,k,b[t]]
                else
                    state[t+1,k,a[t]] = state[t,k,a[t]]
                endif
            )) /\
        (cmd[t] = CMovG -> 
            forall (k in 1..perm_count) (
                if flags[t,k,2] then
                    state[t+1,k,a[t]] = state[t,k,b[t]]
                else
                    state[t+1,k,a[t]] = state[t,k,a[t]]
                endif
            )) /\
        (cmd[t] = Cmp ->
            forall (k in 1..perm_count) (
                state[t+1,k,a[t]] = state[t,k,a[t]]
            ))
    );








%% Goal definition

constraint %% 1..n in last step
    forall (k in 1..perm_count) (
        %% different numbers in registers
        alldifferent([state[s,k,r] | r in 1..n]) /\
        %% all numbers in registers (1..n)
        forall (r in 1..n) (
            state[s,k,r] >= 1 /\ state[s,k,r] <= n
        )
    );

constraint %% same numbers across permutations in last step
    forall (r in 1..n) (
        forall (k in 1..perm_count) (
            state[s,k,r] = state[s,1,r]
        )
    );






%% heuristics (useful but not necessary)
%% https://www.minizinc.org/doc-2.7.6/en/efficient.html#redundant-constraints
%% might want to use redundant_constraint()
constraint %% only compare with larger registers
    forall (t in 1..s) (
        cmd[t] = Cmp -> a[t] < b[t]
    );

constraint %% no two compares in a row
    forall (t in 1..(s-1)) (
        cmd[t] != Cmp \/ cmd[t+1] != Cmp
    );


% Test Examples 
% constraint 
%     state[s,1,1] = 0;

% constraint 
%     cmd[1] = Cmp /\
%     a[1] = 1 /\
%     b[1] = 2;
% constraint 
%     cmd[2] = CMovL /\
%     a[1] = 1 /\
%     b[1] = 2;
% constraint 
%     cmd[2] = Mov /\
%     a[1] = 4 /\
%     b[1] = 2;

% constraint
%     %% set all flags
%     forall (t in 1..s, k in 1..perm_count) (
%         flags[t,k,1] = true /\ flags[t,k,2] = true
%     );


%% how to print

%% print all commands in the form "cmd a b"
output ["\(cmd[t]) \(a[t]) \(b[t])\n" | t in 1..(s-1)];

output ["\n"];

%% print each state as 
%% "Step: t"
%% "state[t,1,1] state[t,1,2] ... state[t,1,n]"
%% "state[t,2,1] state[t,2,2] ... state[t,2,n]"
%% ...
% output ["Step: \(t)\n" ++ "" | t in 1..s]
        % ["\(state[t,k,r]) " | r in 1..n] ++
        % ["\n" | k in 1..perm_count] | t in 1..s];

output ["Step: \(t)\n" ++ 
    concat([
        concat(["\(state[t,k,r]) " | r in 1..reg]) ++ 
            % showFlag(flags[t,k,1]) ++ show(flags[t,k,2]) ++
            if fix(flags[t,k,1]) then "<" else " " endif ++ 
            if fix(flags[t,k,2]) then ">" else " " endif ++
            "\n"
         | k in 1..perm_count]) ++ 
    if t<s then "Run : \(cmd[t]) \(a[t]) \(b[t])\n" else "" endif ++
    "\n"
    | t in 1..s]



