int: s; % The number of timesteps.
int: perm_count;
int: n; % number of registers
int: swap;
array [1..perm_count, 1..n] of 0..n: init_perm;

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
% constraint %% same numbers across permutations in last step
%     forall (r in 1..n) (
%         forall (k in 1..perm_count) (
%             state[s,k,r] = state[s,1,r]
%         )
%     );

%% ascending order in last step
constraint %% 1..n in last step
    forall (k in 1..perm_count) (
        forall (r in 1..(n-1)) (
            state[s,k,r] <= state[s,k,r+1]
        )
    );


%% permutation of initial state in last step
constraint %% 1..n in last step
    forall (k in 1..perm_count) (
        sum([init_perm[k,r] = 0 | r in 1..n]) = sum([state[s,k,r] = 0 | r in 1..n])
        /\ sum([init_perm[k,r] = 1 | r in 1..n]) = sum([state[s,k,r] = 1 | r in 1..n])
        % sum([init_perm[k,r] = 1 | r in 1..n]) = sum([state[s,k,r] = 1 | r in 1..n])
        /\ sum([init_perm[k,r] = 2 | r in 1..n]) = sum([state[s,k,r] = 2 | r in 1..n])
        /\ sum([init_perm[k,r] = 3 | r in 1..n]) = sum([state[s,k,r] = 3 | r in 1..n]) 
        % /\ sum([init_perm[k,r] = 4 | r in 1..n]) = sum([state[s,k,r] = 4 | r in 1..n]) 

        % forall (r in 1..n) (
        %     % count of init[r] is the same as count of state[s,k,r]
        %     sum([init_perm[k,r] = state[s,k,i] | i in 1..n]) =
        %     sum([init_perm[k,r] = init_perm[k,i] | i in 1..n])
        % )
    );

%% we could mark these two as redundant constraints
% constraint %% 1..n in last step
%     forall (k in 1..perm_count) (
%         %% different numbers in registers
%         alldifferent([state[s,k,r] | r in 1..n]) /\
%         %% all numbers in registers (1..n)
%         forall (r in 1..n) (
%             state[s,k,r] >= 1 /\ state[s,k,r] <= n
%         )
%     );

%% possible with consistent renaming => 1/6 search space
% constraint %% 1..n in this order in last step
%     forall (k in 1..perm_count) (
%         forall (r in 1..n) (
%             state[s,k,r] = r
%         )
%     );



%% optimize mov and cmp count
% solve minimize sum([cmd[t] != Mov /\ cmd[t] != Cmp | t in 1..(s-1)]);





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

% cmp 1 2 or mov 4 2 are good starting points
% constraint cmd[1] = Cmp;
% constraint cmd[1] = Cmp /\ a[1] = 1 /\ b[1] = 2;


% reads decremental order
constraint 
    forall (t in 1..(s-1)) (
        % first read 3 before read 2
        b[t] = 2 -> exists (t2 in 1..t-1) (
            b[t2] = 3
        ) /\ 
        % first read 2 before read 1
        b[t] = 1 -> exists (t2 in 1..t-1) (
            b[t2] = 2
        ) 
        % first read 3 before read 4
        %
        % b[t] = 4 -> exists (t2 in 1..t-1) (
        %     b[t2] = 3
        % ) 
        % b[t] = 4 -> exists (t2 in 1..t-1) (
        %     a[t2] = 4
        % )
    );

% do not read if content is zero
% constraint 
%     forall (t in 1..(s-1), k in 1..perm_count) (
%         state[t,k,b[t]] != 0
%     );


%% in each step, each number at least once
% constraint 
%     forall (k in 1..perm_count, t in 1..s) (
%            sum([state[t,k,r] = 1 | r in 1..reg]) >= 1
%         /\ sum([state[t,k,r] = 2 | r in 1..reg]) >= 1
%         /\ sum([state[t,k,r] = 3 | r in 1..reg]) >= 1
%     );
% constraint 
%     forall (k in 1..perm_count) (
%            sum([state[5,k,r] = 1 | r in 1..reg]) >= 1
%         /\ sum([state[5,k,r] = 2 | r in 1..reg]) >= 1
%         /\ sum([state[5,k,r] = 3 | r in 1..reg]) >= 1
%     );
% constraint 
%     forall (k in 1..perm_count, t in 1..s) (
%            exists([state[t,k,r] = 1 | r in 1..reg])
%         /\ exists([state[t,k,r] = 2 | r in 1..reg])
%         /\ exists([state[t,k,r] = 3 | r in 1..reg])
%     );

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
    if t<s then "Run: \(cmd[t]) \(a[t]) \(b[t])\n" else "" endif ++
    "\n"
    | t in 1..s];


output ["\n"];


%% print all commands in the form "cmd a b"
output ["Program:\n"];
output ["\(cmd[t]) \(a[t]) \(b[t])\n" | t in 1..(s-1)];