function [profitA, profitB] = period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, scenario, gamma, salesA1, salesB1)
% Expected period-2 profits after the inventory subgame at realized sales.
% For zero previous sales these are the two seed-demand profits.

if ca / pa2 <= cb / pb2
    % B stocks out first (or simultaneously). A can serve spillover from B.
    baseA = pftaT2Case1(pa2, pb2, theta, ca, cb, beta, mu, sigma);
    baseB = pftbT2Case1(pa2, pb2, cb, beta, mu, sigma);
else
    % A stocks out first. Swap both prices and costs in the original functions.
    baseA = pftbT2Case1(pb2, pa2, ca, beta, mu, sigma);
    baseB = pftaT2Case1(pb2, pa2, theta, cb, ca, beta, mu, sigma);
end

switch scenario
    case 'S'
        extraDemandA = gamma * salesA1;
        extraDemandB = gamma * salesB1;
    case 'N'
        shareA = 0.5 + beta * (pb2 - pa2);
        expansion = gamma * (salesA1 + salesB1);
        extraDemandA = shareA * expansion;
        extraDemandB = (1 - shareA) * expansion;
    otherwise
        error('pricing:Scenario', 'Use S or N for the C2C scenario.');
end

profitA = baseA + (pa2 - ca) * extraDemandA;
profitB = baseB + (pb2 - cb) * extraDemandB;
end
