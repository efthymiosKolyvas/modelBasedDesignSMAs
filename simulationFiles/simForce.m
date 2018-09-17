function [force, region] = simForce(deformation, theta, previousData)

[ep, sp] = deal(previousData(1), previousData(2));

%% parameters initialization
% units are: e (mm), s (gr), th (\circ C)
parameterValues = operatorParameters(theta);

[Es, ses, ees] = deal(parameterValues{:});  [Ei, Eii, Eiii, Eiv, ein] = deal(Es{:});
[~, sFxm, ~,  sFxa] = deal(ses{:});   [~, eFxm, ~,  eFxa] = deal(ees{:});
%% sim
e = deformation;

u = Eiii*(e - ep) + sp;     % the material elastic properties remain unchanged (this is dead-zone)
RiL = min(sFxm + Eii*(e - eFxm), max(sFxa + Eiv*(e - eFxa), u));
s = max(Eiii*(e - ein), max(0.0, min(Ei*e, RiL)));

force = s;
region = 0;
return
%% which region
rr = [];
[dummy, indx1] = max([u, sFxa + Eiv*(e - eFxa)]);       rr = de2bi(indx1, 2);
[dummy, indx2] = min([dummy, sFxm + Eii*(e - eFxm)]);     rr = [rr; de2bi(indx2, 2)];
[dummy, indx3] = min([dummy, Ei*e]);       rr = [rr; de2bi(indx3, 2)];

if all(rr(:, 1))  % and for vector elements
    region = 3;
elseif all(rr(3, :) == [0, 1])
    region = 1;
elseif all(rr(2 : 3, :) == [0, 1; 1, 0])
    region = 2;
elseif all(rr == [0, 1; 1, 0; 1, 0])
    region = 4;
else
    region = 0;
end

