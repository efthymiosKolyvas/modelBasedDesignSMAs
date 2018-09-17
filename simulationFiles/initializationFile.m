clc; clearvars; close all;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
tinf = 21; % ^oC
paraphernalia = 2*ones(3,1); % mm

%% setup domain
noSprings = 3;      atAngles = linspace(0, 360, noSprings+1);       atAngles(end) = [];        atAngles = atAngles+90;
Lo = 6;     % (mm)
lj = 36;    % (mm)
% vertices at distance lj
innerangle = (180*(noSprings-2)/noSprings);  % angles of the regular polygon
rho = (lj/2)/cosd(innerangle/2);
vertxX(:,1) = rho*cosd(atAngles);   vertxY(:,1) = rho*sind(atAngles);
vertxX = vertxX - vertxX(1);     vertxY = vertxY - vertxY(1);
Q= [vertxX, vertxY];

center = (lj*sqrt(3)/2)*(1-1/3);
P = [0, -center];

% % referencePoints
atAngles = atAngles+(360/3)/2;
rho = (lj/10);
vertxX(:,1) = rho*cosd(atAngles);   vertxY(:,1) = rho*sind(atAngles);
vertxX = vertxX + P(1);     vertxY = vertxY + P(2);
referencePoints= [vertxX, vertxY];

previousData = {[0, 0], [0, 0], [0, 0],};

