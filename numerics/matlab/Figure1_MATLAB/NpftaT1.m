function result = NpftaT1(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma)
% Total profit conditional on a fixed continuation price pair.
% The main solver verifies this continuation over all feasible sales states.

   % The sales-dependent part is included with period 1 below.
   [pfta2N, ~] = period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, 'N', gamma, 0, 0);
   alpha2 = 1/2 + beta*(pb2 - pa2);

   % 1st Period
   alpha1 = 1/2 + beta*(pb1-pa1);
   
   if pa1 >= ca/cb*pb1 + gamma/cb*( (1-alpha2)*ca*(pb2 - cb) - alpha2*cb*(pa2-ca) )
       zaN1 = mu - sigma + 2*sigma*( 1 - ca/( pa1 + alpha2*gamma*(pa2 - ca) ) );
       zbN1 = mu - sigma + 2*sigma*( 1 - ( cb - (1 - alpha2)*(pb2 - cb)*gamma*theta*ca/(pa1 + alpha2*gamma*(pa2 - ca)) )/(pb1 + gamma*(1 - alpha2)*(pb2 - cb)*(1 - theta)) );


       ya1N = (alpha1 + theta*(1 - alpha1))*zaN1 - theta*(1 - alpha1)*zbN1;
       yb1N = (1 - alpha1)*zbN1;


       lefta1N = 1/(2*sigma)*( (alpha1 + theta*(1 - alpha1))*zaN1 - theta*(1 - alpha1)*zbN1 )*(zbN1 - mu + sigma)...
           - (1/(2*sigma))*(alpha1/2)*(zbN1^2 - (mu - sigma)^2) + 1/(2*sigma)*(alpha1 + theta*(1 - alpha1))*zaN1*(zaN1 - zbN1)...
           - 1/(2*sigma)*(alpha1 + theta*(1 - alpha1))/2*(zaN1^2 - zbN1^2);
       leftb1N = (1 - alpha1)/2*(1/(2*sigma))*(zbN1 - mu + sigma)^2;
       
   else
       % Here A stocks out first. Its continuation margin uses its own cost ca.
       zaN1 = mu - sigma + 2*sigma*( 1 - ( ca - alpha2*(pa2 - ca)*gamma*theta*cb/(pb1 + (1-alpha2)*gamma*(pb2 - cb)) )/(pa1 + gamma*alpha2*(pa2 - ca)*(1 - theta)) );
       zbN1 = mu - sigma + 2*sigma*( 1 - cb/( pb1 + (1-alpha2)*gamma*(pb2 - cb) ) );
       
       ya1N = alpha1*zaN1;
       yb1N = ( 1 - alpha1 + theta*alpha1)*zbN1 - theta*alpha1*zaN1;
       
       lefta1N = alpha1/2*(1/(2*sigma))*(zaN1 - mu + sigma)^2;
       leftb1N = 1/(2*sigma)*( (1 - alpha1 + alpha1*theta )*zbN1 - alpha1*theta*zaN1 )*(zaN1 - mu + sigma)...
           - (1/(2*sigma))*((1-alpha1)/2)*(zaN1^2 - (mu - sigma)^2) + 1/(2*sigma)*( 1 - alpha1 + alpha1*theta )*zbN1*(zbN1 - zaN1)...
           - 1/(2*sigma)*( 1 - alpha1 + alpha1*theta )/2*(zbN1^2 - zaN1^2);
       
   end
   
   pfta1N = (pa1-ca + gamma*alpha2*(pa2-ca))*ya1N - (pa1+gamma*alpha2*(pa2-ca))*lefta1N + gamma*alpha2*(pa2-ca)*yb1N - gamma*alpha2*(pa2-ca)*leftb1N + pfta2N;

   result = pfta1N;
end
