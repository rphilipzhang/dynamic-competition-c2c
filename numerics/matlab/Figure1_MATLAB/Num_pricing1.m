% Single parameter point from the original script (Figure 1d at theta = 0.99).
% To draw the four panels, run Figure1_reproduce instead.
%% Inputs
ca = 0.95;
cb = 1;
gamma = 2;

theta = 0.99;

beta = 0.1;

mu = 10;
sigma = 5;

pl = 2;
pu = 4;


vc_price = [pl, pu]; 
n_price = length(vc_price);

% The complete state-dependent period-2 game is checked in each scenario.
% First-period equilibrium profits are printed in the original column order.
S = pricing_equilibrium('S', vc_price, theta, ca, cb, beta, mu, sigma, gamma);
N = pricing_equilibrium('N', vc_price, theta, ca, cb, beta, mu, sigma, gamma);

priceT2ES = S.period2Prices;
priceT2EN = N.period2Prices;
priceT1ES = S.period1Prices;
priceT1EN = N.period1Prices;
countT1ES = size(priceT1ES, 1);
countT1EN = size(priceT1EN, 1);
ASPfttotalE = S.totalProfits(:,1);
BSPfttotalE = S.totalProfits(:,2);
ANPfttotalE = N.totalProfits(:,1);
BNPfttotalE = N.totalProfits(:,2);

% Preserve the original common-equilibrium variables when the two agree.
priceT2E = intersect(priceT2ES, priceT2EN, 'rows');
countT2E = size(priceT2E, 1);
disp('Period 2 prices [A B], first row S, second row N')
disp([priceT2ES; priceT2EN])
if countT1ES == 1 && countT1EN == 1
    disp('Period 1 prices [A B], first row S, second row N')
    disp([priceT1ES; priceT1EN])
    disp('Total profits [A_S B_S A_N B_N]')
    disp([ASPfttotalE, BSPfttotalE, ANPfttotalE, BNPfttotalE])
else
    fprintf('Period 1 pure price equilibria: S = %d, N = %d.\n', countT1ES, countT1EN)
    disp('S: price A, price B, profit A, profit B')
    disp([priceT1ES, S.totalProfits])
    disp('N: price A, price B, profit A, profit B')
    disp([priceT1EN, N.totalProfits])
end
