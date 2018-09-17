function sumForces = equilibr4CommonNode(dx, theta, previousData, vertexPoints, activSpringId)

[Q, P, LoParaphernalia] = deal(vertexPoints{:});

%% 1. given a new dx, corresponding to the thermally actuated spring ('active' actuator), 
%% 2. calc new position for P
QjP = P - Q(activSpringId, :);          QjP_unit = QjP/norm(QjP);
dx_vec = dx*QjP_unit;
Pn = P - dx_vec;

%% 3. calc new deltas for the new point Pn
delta = zeros(1, 3);   QjPn = zeros(3, 2);     QjPn_unit = zeros(3, 2);
for jj =1: length(Q)
    QjPn(jj, :) = Pn - Q(jj, :);     QjPn_unit(jj, :) = QjPn(jj, :)/norm(QjPn(jj, :));
    delta(jj) = norm(QjPn(jj, :)) - LoParaphernalia(jj);
end
%% 4. calculate new individual forces by using the model
force = zeros(1, length(Q));    region = zeros(1, length(Q));
for springNo = 1: length(Q)
    [force(springNo), region(springNo)] = simForce(delta(springNo), theta(springNo), previousData{springNo});
end

%% 5. calculate vector sum of forces and its direction with respect to the active spring
sumForces = zeros(1, 2);
for jj = 1:length(Q)
    sumForces = force(jj)*QjPn_unit(jj, :) + sumForces;
end
%% optimization cost-variable: sumForces
% fzero looks for zero crossings of the minimization variable (requires sign for the optimization variable)
sumForces = sign(dot(sumForces, -QjPn_unit(activSpringId, :)))*norm(sumForces);

