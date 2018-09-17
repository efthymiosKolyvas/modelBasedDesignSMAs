function operatorPlot(figureHandle, parameterValues, force_delta, positionss)

[Es, ses, ees] = deal(parameterValues{:});  [Ei, Eii, Eiii, Eiv, ein] = deal(Es{:});
[sSxm, sFxm, sSxa,  sFxa] = deal(ses{:});   [eSxm, eFxm, eSxa,  eFxa] = deal(ees{:});


figure(figureHandle); clf, hold on

plot([eSxm, eFxm], [sSxm, sFxm], 'o', 'LineWidth', 3, 'MarkerSize', 3)
plot([eFxa, eSxa], [sFxa, sSxa], 'ro', 'LineWidth', 3, 'MarkerSize', 3)
xx = [eFxa :0.5: eSxa];
plot(xx, sFxa + Eiv*(xx - (eFxa)), 'k--')
xx = [eSxm :0.5: eFxm];
plot(xx, sFxm + Eii*(xx - (eFxm)), 'k--')
xx = [0 :0.5: eSxm];
plot(xx, Ei*xx, 'k--')
xx = [eSxa :0.5: eFxm];
plot(xx, Eiii*(xx - (ein)), 'k--')

plot(force_delta(2), force_delta(1), 'yo', 'LineWidth', 4)
ylim([0, 1200]), xlim([-5, 35])
set(figureHandle, 'Position', positionss) 
% h = figureHandle;
