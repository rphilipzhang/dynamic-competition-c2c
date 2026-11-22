function [yaG1, ybG1, pfta1G, pftb1G] = FindGeneral_exo(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma, lamS, lamN)
%  Inputs
    alpha_a1 = 1/2 + beta*(pb1 - pa1);
    alpha_b1 = 1 - alpha_a1;
    alpha_a2 = 1/2 + beta*(pb2 - pa2);
    alpha_b2 = 1 - alpha_a2;
    
    gamma_a2 = gamma*(lamS + lamN*alpha_a2);
    gamma_b2 = gamma*(lamS + lamN*alpha_b2);

    gammaC_a2 = gamma*lamN*alpha_a2;
    gammaC_b2 = gamma*lamN*alpha_b2;
% find za zb
    fa = 1 - ca/( pa1 + gamma_a2*(pa2-ca) );
    zaG1 = mu - sigma + 2*sigma*fa;
    fb = 1 - ( cb - gammaC_b2*theta*(pb2-cb)*ca/(pa1 + gamma_a2*(pa2-ca)) )/( pb1 + (gamma_b2 - gammaC_b2*theta)*(pb2-cb) );
    zbG1 = mu - sigma + 2*sigma*fb;
    
    % find ya1 and yb1
    yaG1 = (alpha_a1+theta*alpha_b1)*zaG1 - theta*alpha_b1*zbG1;
    ybG1 = alpha_b1*zbG1;
    
    % find lefta1 and leftb1
    leftaG1 = 1/(2*sigma)*( (alpha_a1 + theta*alpha_b1)*zaG1 - theta*alpha_b1*zbG1 )*(zbG1 - mu + sigma)...
           - (1/(2*sigma))*(alpha_a1/2)*(zbG1^2 - (mu - sigma)^2) + 1/(2*sigma)*(alpha_a1 + theta*alpha_b1)*zaG1*(zaG1 - zbG1)...
           - 1/(2*sigma)*(alpha_a1 + theta*alpha_b1)/2*(zaG1^2 - zbG1^2);
       
    leftbG1 = alpha_b1/2*(1/(2*sigma))*(zbG1 - mu + sigma)^2;
    
    % find 2nd-period profits
    zaG2 = mu - sigma + 2*sigma*(1 - ca/pa2);
    zbG2 = mu - sigma + 2*sigma*(1 - cb/pb2);
   
    yaG2 = (alpha_a2 + theta*alpha_b2)*zaG2 - theta*alpha_b2*zbG2;
    ybG2 = alpha_b2*zbG2;
   
    leftaG2 = 1/(2*sigma)*( (alpha_a2 + theta*alpha_b2)*zaG2 - theta*alpha_b2*zbG2 )*(zbG2 - mu + sigma)...
       - (1/(2*sigma))*(alpha_a2/2)*(zbG2^2 - (mu - sigma)^2) + 1/(2*sigma)*(alpha_a2 + theta*alpha_b2)*zaG2*(zaG2 - zbG2)...
       - 1/(2*sigma)*(alpha_a2 + theta*alpha_b2)/2*(zaG2^2 - zbG2^2);
    leftbG2 = alpha_b2/2*(1/(2*sigma))*(zbG2 - mu + sigma)^2;
   
    pfta2G = (pa2-ca)*yaG2 - pa2*leftaG2;
    pftb2G = (pb2-cb)*ybG2 - pb2*leftbG2;
    
    % find profits
    pfta1G = (pa1-ca + gamma_a2*(pa2-ca))*yaG1 - (pa1+gamma_a2*(pa2-ca))*leftaG1 + gammaC_a2*(pa2-ca)*ybG1 - gammaC_a2*(pa2-ca)*leftbG1 + pfta2G;
    pftb1G = (pb1-cb + gamma_b2*(pb2-cb))*ybG1 - (pb1+gamma_b2*(pb2-cb))*leftbG1 + gammaC_b2*(pb2-cb)*yaG1 - gammaC_b2*(pb2-cb)*leftaG1 + pftb2G;
    
end

