function result = pftbT2Case1(pa2, pb2, cb, beta, mu, sigma)
% Original single-branch expression for the firm with the lower stockout threshold.
% Use period2_profit for both stockout orderings and the full sales-state payoff.

    numerator = -((cb - pb2) * (-1 - 2*pa2*beta + 2*pb2*beta) * ((-pb2)*mu + cb*sigma));
    denominator = 2 * pb2;
    
    result = numerator / denominator;

end
