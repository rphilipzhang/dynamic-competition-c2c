"""Independent general identities for exogenous comparative statics using uniform-law lost sales."""
import sympy as sp

a,b,q,C,v,r,t,mu,sig=sp.symbols("a b q C v r t mu sig", positive=True)
D=v+(1-t)*r
H=C-(v+r)*q
qB=q+H/D
RA=a*mu-sig*a*q**2+t*b*sig*(qB**2-q**2)
RB=b*(mu-sig*qB**2)
deriv_total=sig*b*H*((2*q*v+H)*v+r*(1-t)*(2*q*v-H))/D**3
assert sp.cancel(sp.diff(RA+RB,t)-deriv_total)==0
# C=c_B, v=p_B1, r=gamma*alpha_B2*(p_B2-c_B). q=q_A is constant in theta.
yB=b*(mu+sig-2*sig*qB)
profitB=v*RB-C*yB+r*(RA+RB)
slope=sig*b*r*(C**2-((v+r)*q)**2)/D**2
assert sp.cancel(sp.diff(profitB,t)-slope)==0
print("Exact total sales and B-profit slope identities verified; H=c_B-(v+r)*q_A>0.")
print("P4 numerator/H is v*(2*q_A*v+H)+r*(1-theta)*(2*q_A*v-H).")
print("P6 slope = sigma*alpha_B1*r*[c_B^2-((v+r)*q_A)^2]/D^2.")
print("P3 derivative uses E R_A=a*mu-a*sigma*q_A^2+theta*b*sigma*(q_B^2-q_A^2), with q_B=q_A+H/D.")
