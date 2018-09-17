%% simulation of three antagonistic SMA springs
run  initializationFile

h1 = figure(1);     h2 = figure(2);
h3 = figure(3);     h4 = figure(4);
figureHandles = {h1, [h2, h3, h4]};

discret_ts = .1;    tfinal = 900;   initialGuess = 0;
time = linspace(0, tfinal, floor(tfinal/discret_ts));
duties = repmat([1023, 1023, 1023], size(time,2), 1);
referenceReached = false; rindx = 0;

%%
thetaRec = tinf*ones(length(time), noSprings);        deltaRec = zeros(length(time), noSprings);    
forceRec = zeros(length(time), noSprings);

theta = tinf*ones(1,noSprings);    delta = zeros(1,noSprings);        
initialCondition = tinf*ones(1,noSprings);     thetaChanged = zeros(1,noSprings);
error = zeros(1,noSprings);    force = zeros(1,noSprings);

previousData = {[0, 0], [0, 0], [0, 0],};
parameterValues = {{zeros(1,5)}, {zeros(1,4)}, {zeros(1,4)}};

for instantIterator = 2:length(time)
    if all (error < 0.1)
        referenceReached = true;
    end
    if referenceReached
        rindx = rindx + 1;
        try
            reference = referencePoints(rindx, :);
        catch ME
            if (strcmp(ME.identifier,'MATLAB:badsubscript'))
                disp(':: loop complete, exiting..')
                lastIndx = instantIterator;
            end
            break
        end
        disp('changing reference point')
        referenceReached = false;
    end
    
    % check for thermal actuation
    for springNo = 1: noSprings
        % control action
        error(springNo) = norm(Q(springNo,:) - P) - norm(Q(springNo,:) - reference); % signed error
        if max(0, error(springNo))
            duties(instantIterator, springNo) = 0;
        end
        
        delta(springNo) = norm(P - Q(springNo, :)) - (Lo+paraphernalia(springNo));
        theta(springNo) = simTemp(delta(springNo), duties(instantIterator, springNo), ...
            initialCondition(springNo) - tinf, discret_ts)  + tinf;
        initialCondition(springNo) = theta(springNo);  thetaRec(instantIterator, springNo) = theta(springNo);
        
        parameterValues{springNo} = operatorParameters(theta(springNo));
        [force(springNo), ~] = simForce(delta(springNo), theta(springNo), previousData{springNo});
        previousData{springNo} = [delta(springNo), force(springNo)];        forceRec(instantIterator, springNo) = force(springNo);
        thetaChanged(springNo) = diff(thetaRec(instantIterator-1:instantIterator, springNo));
    end
    % check for mechanical actuation
    for springNo = 1: noSprings
        if thetaChanged(springNo)
            vertexPoints = {Q, P, Lo+ paraphernalia};      activSpringId = springNo;
            dx = fzero(@ (dx) equilibr4CommonNode(dx, theta, previousData, vertexPoints, activSpringId), initialGuess);
            QjP = P - Q(activSpringId, :);          QjP_unit = QjP/norm(QjP);
            dx_vec = dx*QjP_unit;
            P = P - dx_vec;
            
            for jj = 1:noSprings  % correct constitutive quantities for all antagonists, for the new P
                delta(jj) = norm(P - Q(jj, :)) - (Lo+paraphernalia(jj));
                [force(jj), ~] = simForce(delta(jj), theta(jj), previousData{jj});
                previousData{jj} = [delta(jj), force(jj)];
            end
        end
        deltaRec(instantIterator, springNo) = delta(springNo);
        forceRec(instantIterator, springNo) = force(springNo); 
    end
    multiSpringPlotter({Q, P}, parameterValues, figureHandles, [force(:), delta(:)], referencePoints)
    pause(0.01)
end

close all
%%
thetaRec(lastIndx:end,:) =[]; deltaRec(lastIndx:end,:) =[]; forceRec(lastIndx:end,:) =[]; time(lastIndx:end) =[];
thetaRec(1,:) =[]; deltaRec(1,:) =[]; forceRec(1,:) =[]; time(1) =[];
%%
figure(1), plot(time, thetaRec), ylabel('temperatures  ($^oC$)', 'Interpreter', 'Latex'), xlabel('time (s)', 'Interpreter', 'Latex')
figure(2), plot(time, deltaRec), ylabel('deformations ($mm$)', 'Interpreter', 'Latex'), xlabel('time (s)', 'Interpreter', 'Latex')
figure(3), plot(time, forceRec), ylabel('forces  ($gr-f$)', 'Interpreter', 'Latex'), xlabel('time (s)', 'Interpreter', 'Latex')
pause, close all
