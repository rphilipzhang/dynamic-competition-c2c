function panels = Figure1_reproduce(makePlot)
% Figure1_reproduce draws Figure 1 and reports the profit crossings.
% panels = Figure1_reproduce(false) returns the same numbers without graphics.
% Columns of panels(k).profits are the total profits in S and N, respectively.
if nargin < 1
    makePlot = true;
end

theta = [0.01, 0.1:0.1:0.9, 0.99]';
% Columns are panel, A's unit cost, interaction strength, and retailer index.
spec = {'(a)', 0.10, 0.7, 1; '(b)', 0.10, 2, 1; ...
        '(c)', 0.95, 0.7, 2; '(d)', 0.95, 2, 2};
retailers = 'AB';
ylimits = [51.8, 53.4; 60, 85; 36.52, 36.55; 40, 65];
if makePlot
    figure('Name', 'Figure 1 - equilibrium profits', 'Color', 'w');
end
for k = 1:size(spec, 1)
    label = spec{k,1};
    ca = spec{k,2};
    gamma = spec{k,3};
    firm = spec{k,4};
    profits = zeros(numel(theta), 2);
    pricesS = zeros(numel(theta), 4);
    pricesN = zeros(numel(theta), 4);
    for h = 1:numel(theta)
        [~, profits(h,:), pricesS(h,:), pricesN(h,:)] = panel_gap(theta(h), ca, gamma, firm);
    end
    % Use the model profit difference, not interpolation of plotted nodes.
    % Both moderate-gamma panels have one sign change; the others have none.
    gap = profits(:,2) - profits(:,1);
    changes = find(gap(1:end-1).*gap(2:end) < 0);
    crossings = theta(gap == 0);
    for h = 1:numel(changes)
        j = changes(h);
        root = fzero(@(x) panel_gap(x, ca, gamma, firm), [theta(j), theta(j+1)]);
        crossings(end+1,1) = root; %#ok<AGROW>
    end
    panels(k).label = label; %#ok<AGROW>
    panels(k).retailer = retailers(firm);
    panels(k).ca = ca;
    panels(k).gamma = gamma;
    panels(k).theta = theta;
    panels(k).profits = profits;
    % Price columns are [A1, B1, A2, B2] for each scenario.
    panels(k).pricesS = pricesS;
    panels(k).pricesN = pricesN;
    panels(k).crossings = sort(crossings);
    if isempty(crossings)
        fprintf('%s Retailer %c, gamma = %g: no profit crossing on the plotted grid.\n', label, retailers(firm), gamma);
    else
        fprintf('%s Retailer %c, gamma = %g: profit crossing theta =', label, retailers(firm), gamma);
        fprintf(' %.9f', sort(crossings));
        fprintf('\n');
    end
    if makePlot
        subplot(2, 2, k);
        plot(theta, profits(:,1), 'r--', theta, profits(:,2), 'b-', 'LineWidth', 1.4);
        xlim([0, 1]);
        ylim(ylimits(k,:));
        xlabel('Substitution rate \theta');
        ylabel(sprintf('Retailer %c profit', retailers(firm)));
        title(sprintf('%s Retailer %c, \\gamma = %g', label, retailers(firm), gamma));
        legend('Scenario S', 'Scenario N', 'Location', 'northwest');
    end
end
end

function [gap, profits, pricesS, pricesN] = panel_gap(theta, ca, gamma, firm)
S = pricing_equilibrium('S', [2,4], theta, ca, 1, 0.1, 10, 5, gamma);
N = pricing_equilibrium('N', [2,4], theta, ca, 1, 0.1, 10, 5, gamma);
if size(S.totalProfits,1) ~= 1 || size(N.totalProfits,1) ~= 1
    error('pricing:FigureEquilibrium', 'The panel requires one pure first-period equilibrium in each scenario at theta=%g.', theta);
end
profits = [S.totalProfits(1,firm), N.totalProfits(1,firm)];
gap = profits(2) - profits(1);
pricesS = [S.period1Prices, S.period2Prices];
pricesN = [N.period1Prices, N.period2Prices];
end
