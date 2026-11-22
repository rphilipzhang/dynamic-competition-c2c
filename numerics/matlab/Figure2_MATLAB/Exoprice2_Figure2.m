function panels = Exoprice2_Figure2(makePlot)
% Reproduce Figure B.1 of paper/OnlineAppendix.pdf.
% panels = Exoprice2_Figure2() draws and saves Figure2_from_MATLAB.pdf.
% panels = Exoprice2_Figure2(false) returns the same values without graphics.
% Each column of panels(k).values corresponds to panels(k).scenarios.
if nargin == 0
    makePlot = true;
end

% Fixed prices and uniform seed demand from the caption to Figure B.1.
pa1 = 2;
pb1 = 2;
pa2 = 2;
pb2 = 2;
cb = 1;
beta = 0.1;
mu = 10;
sigma = 5;
theta = (0:0.1:1).';

% Rows are GS, GN and the benchmark. Columns are gamma, lambda_S, lambda_N.
scenarioNames = {'GS', 'GN', '0'};
scenarioInputs = [2, 0.8, 0.2; 2, 0.2, 0.8; 0, 0.8, 0.2];
costsA = [0.50, 0.10, 0.92];
solutions = cell(numel(costsA), numel(scenarioNames));
for iCost = 1:numel(costsA)
    for s = 1:numel(scenarioNames)
        gamma = scenarioInputs(s, 1);
        lamS = scenarioInputs(s, 2);
        lamN = scenarioInputs(s, 3);
        rows = zeros(numel(theta), 4);
        for i = 1:numel(theta)
            [ya1, yb1, profitA, profitB] = FindGeneral_exo( ...
                pa1, pb1, pa2, pb2, theta(i), costsA(iCost), cb, ...
                beta, mu, sigma, gamma, lamS, lamN);
            rows(i, :) = [ya1, yb1, profitA, profitB];
        end
        solutions{iCost, s} = rows;
    end
end

% Panel order follows the four outputs of FindGeneral_exo.
costIndex = [1, 1, 2, 3];
scenarioCount = [2, 3, 2, 2];
letters = {'a', 'b', 'c', 'd'};
retailers = {'A', 'B', 'A', 'B'};
metrics = {'First-period order quantity', 'First-period order quantity', ...
           'Two-period expected profit', 'Two-period expected profit'};
panels = struct([]);
for k = 1:4
    panels(k).label = letters{k};
    panels(k).retailer = retailers{k};
    panels(k).metric = metrics{k};
    panels(k).ca = costsA(costIndex(k));
    panels(k).theta = theta;
    panels(k).scenarios = scenarioNames(1:scenarioCount(k));
    values = zeros(numel(theta), scenarioCount(k));
    for s = 1:scenarioCount(k)
        values(:, s) = solutions{costIndex(k), s}(:, k);
    end
    panels(k).values = values;
end

if ~makePlot
    return
end
styles = {'r--', 'b-', 'k-.'};
legendNames = {'Scenario GS', 'Scenario GN', 'Scenario 0'};
yLimits = [6.6 8.2; 4.5 6.7; 36.5 40; 16.86 16.95];
yTicks = {6.6:0.2:8.2, 4.6:0.2:6.6, 36.5:0.5:40, 16.86:0.01:16.95};
fig = figure('Name', 'Appendix Figure 2', 'NumberTitle', 'off', ...
             'Color', 'w', 'Units', 'inches', 'Position', [0.5 0.5 10 7.2]);
for k = 1:4
    ax = subplot(2, 2, k);
    hold(ax, 'on');
    for s = 1:scenarioCount(k)
        plot(ax, theta, panels(k).values(:, s), styles{s}, 'LineWidth', 1.7);
    end
    set(ax, 'Box', 'on', 'TickDir', 'out', 'FontSize', 10, ...
        'XLim', [0 1], 'XTick', 0:0.1:1, 'YLim', yLimits(k, :), 'YTick', yTicks{k});
    xlabel(ax, 'Substitution rate \theta');
    ylabel(ax, metrics{k});
    title(ax, sprintf('(%s) Retailer %s,  c_A = %.2g', ...
                      letters{k}, retailers{k}, panels(k).ca));
    legend(ax, legendNames(1:scenarioCount(k)), 'Location', 'northwest', 'Box', 'off');
end
set(fig, 'PaperUnits', 'inches', 'PaperSize', [10 7.2], ...
         'PaperPosition', [0 0 10 7.2]);
print(fig, fullfile(pwd, 'Figure2_from_MATLAB.pdf'), '-dpdf', '-painters');
end
