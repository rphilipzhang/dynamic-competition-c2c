"""Check the price derivatives in P7 and P8(b2) as symbolic identities."""
import sympy as sp
x,y,c,d,U,s,t=sp.symbols("x y c d U s t",positive=True)
# In the units 2*beta=mu=1, x is own and y the rival price.
share=(1+y-x)/2
own_z=1+s-2*c*s/x
rival_z=1+s-2*d*s/y
low=share*own_z
extra=t*(1-share)*(own_z-rival_z)
high=low+extra
def equals(a,b):assert sp.cancel(a-b)==0
equals(sp.diff(low,x),c*s*(1+y)/x**2-(1+s)/2)
equals(sp.diff(high,x),-(1+s)/2+c*s*(1+t+(1-t)*y)/x**2+d*t*s/y)
equals(sp.diff(high,y),(1+s-2*c*(1-t)*s/x)/2-d*t*s*(1+x)/y**2)
equals(sp.diff(low,y),(1+s-2*c*s/x)/2)
equals(extra.subs(x,c*y/d),0)
equals(sp.diff(extra,x).subs(x,c*y/d), (t*(1-share)*2*c*s/x**2).subs(x,c*y/d))
# Elementary bounds for the end of either price interval in the proof record.
equals(2/(U-1)-2*(1+U)/U**2,2/(U**2*(U-1)))
equals(1/(U-1)-4/U**2,(U-2)**2/((U-1)*U**2))
beta,h,K,L,nuB=sp.symbols("beta h K L nuB", positive=True)
shareB=sp.Rational(1,2)+beta*(x-y)
B=shareB*(h-2*s*K/(y+L*nuB))
equals(sp.diff(B,y),-beta*h+s*K*(1+2*beta*x+2*beta*L*nuB)/(y+L*nuB)**2)
print("Exact P7 derivatives on both sides of the critical-ratio tie; continuity and the own-price slope jump verified.")
print("Upper-bound identities U^2 >= 4(U-1) and (1+U)(U-1) < U^2 checked.")
print("P8(b2): formula (A.26) verified at constant L=gamma*(1-theta), including L=0.")
