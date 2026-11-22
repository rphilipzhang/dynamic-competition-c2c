function result = SpftaT1(pa1, pb1, pa2, pb2, theta, ca, cb, beta, mu, sigma, gamma)
% Total profit conditional on a fixed continuation price pair.
% The main solver verifies this continuation over all feasible sales states.

   % The sales-dependent part is included with period 1 below.
   [pfta2S, ~] = period2_profit(pa2, pb2, theta, ca, cb, beta, mu, sigma, 'S', gamma, 0, 0);

   % 1st Period
   alpha1 = 1/2 + beta*(pb1-pa1);
   
   if pa1 >= ca/cb*pb1 + gamma/cb*( ca*(pb2 - cb) - cb*(pa2-ca) )
       
       zaS1 = mu - sigma + 2*sigma*( 1 - ca/( pa1 + gamma*(pa2 - ca) ) );
       zbS1 = mu - sigma + 2*sigma*( 1 - cb/( pb1 + gamma*(pb2 - cb) ) );

       ya1S = (alpha1 + theta*(1 - alpha1))*zaS1 - theta*(1 - alpha1)*zbS1;
       yb1S = (1 - alpha1)*zbS1;
 
       lefta1S = 1/(2*sigma)*( (alpha1 + theta*(1 - alpha1))*zaS1 - theta*(1 - alpha1)*zbS1 )*(zbS1 - mu + sigma)...
           - (1/(2*sigma))*(alpha1/2)*(zbS1^2 - (mu - sigma)^2) + 1/(2*sigma)*(alpha1 + theta*(1 - alpha1))*zaS1*(zaS1 - zbS1)...
           - 1/(2*sigma)*(alpha1 + theta*(1 - alpha1))/2*(zaS1^2 - zbS1^2);
       leftb1S = (1 - alpha1)/2*(1/(2*sigma))*(zbS1 - mu + sigma)^2;

   else
       
       zaS1 = mu - sigma + 2*sigma*( 1 - ca/( pa1 + gamma*(pa2 - ca) ) );
       zbS1 = mu - sigma + 2*sigma*( 1 - cb/( pb1 + gamma*(pb2 - cb) ) );

       ya1S = alpha1*zaS1;
       yb1S = (1 - alpha1 + theta*alpha1)*zbS1 - theta*alpha1*zaS1;
       
       lefta1S = alpha1/2*(1/(2*sigma))*(zaS1 - mu + sigma)^2;
       leftb1S = 1/(2*sigma)*( (1 - alpha1 + alpha1*theta)*zbS1 - alpha1*theta*zaS1 )*(zaS1 - mu + sigma)...
           - (1/(2*sigma))*((1-alpha1)/2)*(zaS1^2 - (mu - sigma)^2) + 1/(2*sigma)*( 1 - alpha1 + alpha1*theta )*zbS1*(zbS1 - zaS1)...
           - 1/(2*sigma)*( 1 - alpha1 + alpha1*theta )/2*(zbS1^2 - zaS1^2);
       
   end
   pfta1S = (pa1-ca + gamma*(pa2-ca))*ya1S - (pa1+gamma*(pa2-ca))*lefta1S + pfta2S;

   result = pfta1S;
end
