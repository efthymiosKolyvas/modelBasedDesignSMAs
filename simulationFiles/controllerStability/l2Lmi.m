%% LMI stability conditions by the paper: T. Pare, J. How, "Robust Stability and Performance 
%% Analysis of Systems with Hysteresis Nonlinearities", ACC98
%% requires the cvx package by: http://cvxr.com/cvx/
run temperaturemodel
dzp = 0;    dzw = 0;
% interconnection w/ multipliers
A = [aqp, zeros(size(aqp,1), size(aqw, 2)); ...
    zeros(size(aqw, 1), size(aqp,2)),  aqw];
Bp = [bqp; zeros(size(aqw, 1), size(bqp, 2))];
Bw = [zeros(size(aqp, 1) -1, size(bqw, 2)); bqw];
Cq = [cqp, cqw];
Cz = [cqp, zeros(1, size(aqw,2))];
%% complete system (G^\tilde_s)
A_tilde = [A, zeros(size(A, 1), 1); ...
    Cq, zeros(size(Cq,1), 1)];
Bp_tilde = [Bp; dqp+1/mmu];Bw_tilde = [0; Bw; dqw];
Cq1_tilde = [Cq, 0];  Cq2_tilde = [zeros(size(Cq)), 1];
Cz_tilde = [Cz, 0];
Dqp_tilde = [dqp + 1/mmu];      Dqw_tilde = [dqw];
Dzp_tilde = [dzw];      Dzw_tilde = [dzw];

Gs = [A_tilde, Bp_tilde, Bw_tilde; ...
    Cq1_tilde + Cq2_tilde, Dqp_tilde, Dqw_tilde; ...
    Cz_tilde, Dzp_tilde, Dzw_tilde];    

%%
cvx_begin sdp
    variable P(size(A_tilde)) symmetric
    variables gammaSq lambda tau delta
    minimize(gammaSq)
    subject to
    [-A_tilde'*P-P*A_tilde-Cz_tilde'*Cz_tilde,...
      lambda*Cq1_tilde'+tau*Cq2_tilde'-...
      P*Bp_tilde-Cz_tilde'*Dzp_tilde,...
          -P*Bw_tilde-Cz_tilde'*Dzw_tilde; ...
    (lambda*Cq1_tilde'+tau*Cq2_tilde'-P*Bp_tilde-...
    Cz_tilde'*Dzp_tilde)',...
        lambda*(Dqp_tilde+Dqp_tilde')-2*delta*...
        eye(size(Dqp_tilde))-Dzp_tilde'*Dzp_tilde,...
             lambda*Dqw_tilde-Dzp_tilde'*Dzw_tilde; ...
                (-P*Bw_tilde-Cz_tilde'*Dzw_tilde)', ...
        (lambda*Dqw_tilde-Dzp_tilde'*Dzw_tilde)', ...
                gammaSq-Dzw_tilde'*Dzw_tilde ] >= 0;
    lambda >= 0;
    tau >= 0;
    delta >= 0;
    gammaSq >= 0;
    P >= 0;
cvx_end    

tau
lambda
delta
gammaSq
