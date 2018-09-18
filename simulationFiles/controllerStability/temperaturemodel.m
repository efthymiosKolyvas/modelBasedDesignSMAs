%% temperature model data::
rho = 0.55;         cv = 0.1255;     % J/K
% % parameters to approximate the relationship:
% % heatConvectionCoefficient = f(springPitch,theta_{ss}) % (values in scaling of 1e3)
p00 =  1 +  1.984;      p10 =     0.04956;
p01 =      0.4973;      p20 =   -0.000294;
p11 =     0.01563;      p02 =      0.2379;
%% the variation in the value of 'h' is considered as an uncertainty, in terms
% % of examining the system stability. The uncertainty bounds are
% calculated as (remember, requires scaling by 1e3):
[x_min, x_max] = deal(0, 120);      
[y_min, y_max] = deal(0.1, 3);
h_max = p00 + p10*x_max + p01*y_max + ...
    p20*x_max^2 + p11*x_max*y_max + ...
    p02*y_max^2;
h_min = p00 + p10*x_min + p01*y_min + ...
    p20*x_min^2 + p11*x_min*y_min + ...
    p02*y_min^2;
h_min = 1e-3*h_min;     h_max = 1e-3*h_max;
h_mean = mean([h_min, h_max]);
%% temperature models
go = tf(rho/cv, [1 h_mean/cv]);
p = 9;      i = 1e-4;   piC = tf([p i], [1 0]);
mmu = 0.3;  % slope of the backlash model
%% loop transformation
gs = piC*go;     gp = piC*tf(rho/cv, [1 (h_max)/cv]); 
wl1 = gp/gs -1;      % weight function
[nm, dd] = tfdata(gs, 'v');     [a, b, c, d] = tf2ss(nm, dd);
% matrix form of the loop transformed system
atilde = [a, zeros(length(a), 1); c 0];         
btilde = [b; d+1/mmu];
cq1 = [c 0];        cq2 = [zeros(size(c)) 1];
% dqp = [d + 1/mmu];
%% gs: model w/ the controller in series
[aqp, bqp, cqp, dqp] = tf2ss(nm, dd);
[nw, dw] = tfdata(wl1, 'v');        
[aqw, bqw, cqw, dqw] = tf2ss(nw, dw);

