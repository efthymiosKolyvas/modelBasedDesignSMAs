function theta = simTemp(deformation, duty, initialCondition, tss)

noACoils = 7.5;       pitch = deformation/noACoils;
rho = 0.45; % Ohm (individual actuator)
R_leaking = 1.25; % Ohm (resistivity from wires and connectors)
Vo =  3.3; % Volt (power supply for PWM)
vrms = Vo*sqrt((1023-duty)/1023);        irms = vrms/(rho+R_leaking);
cv = 0.1155;     % J/K
% % "pxy" parameters represent the approximation of heat convection coefficient (h) 
% % as a function of the spring's pitch and steady state temperature (value in h*1e3):
p00 =  1.484;      p10 =     0.04956;      p01 =      0.4973;
p20 =   -0.000294;      p11 =     0.01563;      p02 =      0.2379;
x = initialCondition;        y = pitch;
h = p00 + p10*x + p01*y + p20*x^2 + p11*x*y + p02*y^2;
h = h*1e-3;
qq= rho/cv;  qp = h/cv;
bz = qq/qp*(1- exp(-qp*tss));
az = -exp(-qp*tss);
theta = bz*(irms^2) - az*initialCondition;
