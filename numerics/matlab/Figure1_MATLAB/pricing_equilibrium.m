function result = pricing_equilibrium(scenario, prices, theta, ca, cb, beta, mu, sigma, gamma)
% Pure price equilibria for a finite price menu and uniform seed demand.
% The original first-period inventory formulas apply when the same second-
% period prices are a pure equilibrium at every realized sales state.
% This is tested before the formulas are used. All first-period pure
% equilibria for the certified continuation are returned in separate rows.

prices = prices(:);
if isempty(prices) || ~isreal(prices) || any(~isfinite(prices)) || ...
        numel(unique(prices)) ~= numel(prices) || any(prices <= max(ca, cb))
    error('pricing:PriceMenu', 'Use distinct finite prices above both unit costs.');
end
if any(~isfinite([theta, ca, cb, beta, mu, sigma, gamma])) || ...
        theta < 0 || theta > 1 || min(ca, cb) <= 0 || sigma <= 0 || ...
        mu < sigma || gamma < 0 || beta < 0 || beta*(max(prices) - min(prices)) >= 0.5
    error('pricing:Parameters', 'Check costs, positive demand shares, and the uniform-demand and C2C parameters.');
end

% Feasible sales satisfy RA >= 0, RB >= 0, RA+RB <= mu+sigma. In S, each
% payoff is affine in own sales; in N it is affine in total sales. Use the
% endpoints to test every deviation at every state inside this bound.
upperDemand = mu + sigma;
n = numel(prices);
baseA = zeros(n);
baseB = zeros(n);
upperA = zeros(n);
upperB = zeros(n);
for i = 1:n
    for j = 1:n
        args = {prices(i), prices(j), theta, ca, cb, beta, mu, sigma, scenario, gamma};
        [baseA(i,j), baseB(i,j)] = period2_profit(args{:}, 0, 0);
        [upperA(i,j), ~] = period2_profit(args{:}, upperDemand, 0);
        [~, upperB(i,j)] = period2_profit(args{:}, 0, upperDemand);
    end
end
tolA = 64 * eps(max([1; abs(baseA(:)); abs(upperA(:))]));
tolB = 64 * eps(max([1; abs(baseB(:)); abs(upperB(:))]));
commonEquilibria = false(n);
possibleEquilibria = false(n);
for i = 1:n
    for j = 1:n
        a = best_response_interval(baseA(i,j)-baseA(:,j), upperA(i,j)-upperA(:,j), tolA);
        b = best_response_interval(baseB(i,j)-baseB(i,:), upperB(i,j)-upperB(i,:), tolB);
        commonEquilibria(i,j) = a(1)==0 && a(2)==1 && b(1)==0 && b(2)==1;
        if strcmp(scenario, 'S')
            possibleEquilibria(i,j) = a(1)<=a(2) && b(1)<=b(2) && a(1)+b(1)<=1;
        else
            possibleEquilibria(i,j) = max(a(1), b(1)) <= min(a(2), b(2));
        end
    end
end

[a2, b2] = find(commonEquilibria);
if isempty(a2)
    error('pricing:StateDependentContinuation', ...
        ['No constant pure continuation was certified over the sales triangle in scenario %s. ' ...
         'A sales-dependent continuation analysis is needed for these parameters.'], scenario);
elseif numel(a2) > 1
    error('pricing:MultipleContinuations', ...
        ['Several price pairs are equilibria at every sales state in scenario %s: %s. ' ...
         'Specify a continuation selection to evaluate period 1.'], scenario, mat2str([prices(a2), prices(b2)]));
end
pa2 = prices(a2);
pb2 = prices(b2);
[otherA, otherB] = find(possibleEquilibria & ~commonEquilibria);
result.otherPeriod2Prices = [reshape(prices(otherA), [], 1), reshape(prices(otherB), [], 1)];
if ~isempty(otherA)
    warning('pricing:OtherContinuations', ...
        ['Using the constant continuation %s in scenario %s. Other pure price pairs ' ...
         'are supported at some sales states within the bound: %s.'], ...
        mat2str([pa2, pb2]), scenario, mat2str(result.otherPeriod2Prices));
end

% Every first-period price deviation gets its own inventory equilibrium.
if strcmp(scenario, 'S')
    profitA1 = @SpftaT1;
    profitB1 = @SpftbT1;
else
    profitA1 = @NpftaT1;
    profitB1 = @NpftbT1;
end
payoffA = zeros(n);
payoffB = zeros(n);
for i = 1:n
    for j = 1:n
        payoffA(i,j) = profitA1(prices(i), prices(j), pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma);
        payoffB(i,j) = profitB1(prices(i), prices(j), pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma);
    end
end
[a1, b1] = find(pure_equilibria(payoffA, payoffB));
eq = sub2ind([n, n], a1, b1);
result.period2Prices = [pa2, pb2];
result.period1Prices = [reshape(prices(a1), [], 1), reshape(prices(b1), [], 1)];
result.totalProfits = [reshape(payoffA(eq), [], 1), reshape(payoffB(eq), [], 1)];
result.payoffA = payoffA;
result.payoffB = payoffB;
end

function interval = best_response_interval(gainAtZero, gainAtUpper, tolerance)
% Intersect g0 + (g1-g0)*x >= 0 across all unilateral deviations; x is
% own sales (S) or aggregate sales (N), divided by the upper demand bound.
left = gainAtZero(:) + tolerance;
right = gainAtUpper(:) + tolerance;
if any(left < 0 & right < 0)
    interval = [Inf, -Inf];
    return
end
starts = left < 0;
ends = right < 0;
lower = max([0; -left(starts) ./ (right(starts) - left(starts))]);
upper = min([1; left(ends) ./ (left(ends) - right(ends))]);
interval = [lower, upper];
end

function mask = pure_equilibria(payoffA, payoffB)
% Rows are A's prices and columns are B's prices. Keep ties for either firm.
if any(~isfinite(payoffA(:))) || any(~isfinite(payoffB(:)))
    error('pricing:NonfinitePayoff', 'A price profile produced a nonfinite payoff.');
end
tolA = 64 * eps(max(1, max(abs(payoffA(:)))));
tolB = 64 * eps(max(1, max(abs(payoffB(:)))));
bestA = bsxfun(@ge, payoffA, max(payoffA, [], 1) - tolA);
bestB = bsxfun(@ge, payoffB, max(payoffB, [], 2) - tolB);
mask = bestA & bestB;
end
