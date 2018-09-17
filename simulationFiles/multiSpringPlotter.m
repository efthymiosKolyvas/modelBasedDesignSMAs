function multiSpringPlotter(vertexPoints, parameterValues, figureHandles, force_delta, referencePoints)

[Q, P] = deal(vertexPoints{:});
[h1, hs] = deal(figureHandles{:});
% cartesian plane plot
figure(h1), clf, hold on
plot(Q(:, 1), Q(:, 2), 'k.', 'MarkerSize', 16),
plot(P(1), P(2), 'go', 'LineWidth', 2)
plot(referencePoints(:, 1), referencePoints(:, 2), 'mx', 'LineWidth', 2)
for springNo=1:length(hs)
    text(Q(springNo,1)-3, Q(springNo,2)-1, strcat('spring #', string(springNo)));
end
% individual plots
positionss = [[1020 430 320 250]; [20 130 320 250]; [1020 40 320 250]]; %  set for display with dimensions: 1366x768
for springNo=1:length(hs)
    operatorPlot(hs(springNo), parameterValues{springNo}, force_delta(springNo, :), positionss(springNo, :))
    title(gca(hs(springNo)), strcat('spring #', string(springNo)));
end