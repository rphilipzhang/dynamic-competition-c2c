"""Endpoint certificates for the equal-share, fixed-market profit comparisons.
The pen-and-paper evaluation uses the upper-tail variables of the uniform law.
At theta=0 the two independent stock optimizations have optimal-value term
sigma*c_i**2/(p_i1+gamma*m_i) times own share.  In N add the profit from
the other firm's expected sales.  At theta=1 total lost sales in N are
sigma*qA**2, and the first-period B tail converges to H/v.  Both squared
order tails in S are O(gamma^-2). All limits here hold at a fixed market.
"""
import sympy as sp
a,b,A,B,u,v,m,n,mu,s=sp.symbols("a b A B u v m n mu s", positive=True)
# A,B are costs; m,n are second-period unit margins. H>0 follows from A11.
H=B-b*n*A/(a*m)
yB=H/v
dA1=s*b*yB*(2*A-u*yB)
dB1=s*b*(v*yB**2-2*B*yB)
assert sp.cancel(dB1+s*b*(B**2-(b*n*A/(a*m))**2)/v)==0
# Coefficient of the gap at theta=0 after multiplying it by gamma:
limA0=s*a*(A**2/m-A**2/(a*m)+m*B**2/(b*n**2))
limB0=s*b*(B**2/n-B**2/(b*n)+n*A**2/(a*m**2))
assert sp.cancel((limA0-s*a*(m*B**2/(b*n**2)-b*A**2/(a*m))).subs(b,1-a))==0
assert sp.cancel((limB0-s*b*(n*A**2/(a*m**2)-a*B**2/(b*n))).subs(b,1-a))==0
pa2,pb2=sp.symbols('pa2 pb2',positive=True)
# P5's threshold is linear in B after replacing the second-period margins.
K=-2*a*A**2*v+b*A*u*pb2+2*a*A*pa2*v-B*u*(a*pa2-(2*a-1)*A)
assert sp.factor((a*m*v*(2*A-u*yB)-K).subs({m:pa2-A,n:pb2-B,b:1-a}))==0
print("At theta=1 the unscaled S-N profit limits are")
print("A: sigma*b*(H/v)*(2*cA-u*H/v); B: -sigma*b*(cB^2-(b*mB*cA/(a*mA))^2)/v.")
print("The former has exactly the sign of the printed cutoff numerator; the latter is strictly negative.")
print("At theta=0 the gamma-scaled limits agree with the closed-form leading coefficients.")
print("A's is positive since cB*mA>=cA*mB and a>b^2; B's is positive in a neighborhood of equal costs (A11 forces a,b toward 1/2 there).")
