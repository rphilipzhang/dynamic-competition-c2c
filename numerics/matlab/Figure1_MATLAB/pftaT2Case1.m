function result = pftaT2Case1(pa2, pb2, theta, ca, cb, beta, mu, sigma)
% Original single-branch expression for the firm with the higher stockout threshold.
% Use period2_profit for both stockout orderings and the full sales-state payoff.

    numerator = ...
        ca^2 * pb2^2 * (1 + 2*pa2*beta*(-1+theta) - 2*pb2*beta*(-1+theta) + theta) * sigma + ...
        pa2^2 * (2*pb2^3*beta*mu + pb2^2*(mu - 2*pa2*beta*mu) - 2*cb^2*pb2*beta*theta*sigma + cb^2*(1+2*pa2*beta)*theta*sigma) + ...
        ca*pa2*pb2 * (pb2*(-1+2*pa2*beta)*mu - 2*cb*(1+2*pa2*beta)*theta*sigma + pb2*(-1+2*pa2*beta+4*cb*beta*theta)*sigma - 2*pb2^2*beta*(mu+sigma));
    
    denominator = 2 * pa2 * pb2^2;
    
    result = numerator / denominator;
end
