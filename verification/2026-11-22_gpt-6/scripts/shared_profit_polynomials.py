"""Reconstruct the numerators in P5(c2) and P6(c2) at fixed markets by exact interpolation and independent sales integration."""
from fractions import Fraction as F
from math import comb
from itertools import product

def diff(f,x,n):
    return sum((-1)**(n-j)*comb(n,j)*f(x+j) for j in range(n+1))
def check(u,v,A,B,ca,cb,beta):
    a=F(1,2)+beta*(B-A); b=1-a
    mu=F(10); sig=F(5); m=A-ca; n=B-cb
    assert a==F(1,2)+beta*(v-u) and 0<b<=a<1 and ca*v<=cb*u and ca*B<=cb*A
    def h(t,g,i):
        money=[]
        for w in (False, True):  # S, then N
            q=ca/(u+g*m*(a if w else 1))
            z=(cb-t*b*g*n*q)/(v+(1-t)*b*g*n) if w else cb/(v+g*n)
            ra=a*(mu-sig*q*q)+t*b*sig*(z*z-q*q)
            rb=b*(mu-sig*z*z)
            ya=a*(mu+sig-2*sig*q)+2*t*b*sig*(z-q)
            yb=b*(mu+sig-2*sig*z)
            if i=="A":
                money.append(u*ra-ca*ya+g*m*(a*(ra+rb) if w else ra))
            else:
                money.append(v*rb-cb*yb+g*n*(b*(ra+rb) if w else rb))
        d=(money[0]-money[1])/g
        if i=="A":
            return d*(u+g*m)*(v+g*n)**2*(u+a*g*m)**2*(v+b*g*(1-t)*n)**2
        return d*(v+g*n)*(u+a*g*m)**2*(v+b*g*(1-t)*n)/n
    g=F(7,3)
    def tdiff(i,n):return diff(lambda k:h(F(k,7),g,i),0,n)*7**n
    assert tdiff('A',4)==0 and tdiff('B',2)==0
    assert tdiff('A',3)==6*b**3*g*sig*n**2*(u+a*g*m)**2*(cb*(u+g*A)-ca*(v+g*B))**2
    leadA=diff(lambda x:h(1,F(x),'A'),1,4)
    signexpr=-2*a*ca**2*v+b*ca*u*B+2*a*ca*A*v-cb*u*(a*A-(2*a-1)*ca)
    assert diff(lambda x:h(1,F(x),'A'),1,5)==0 and leadA*signexpr>=0 and (leadA==0)==(signexpr==0)
    for theta,expected in [(0,a*b*sig*(-2*cb**2*m**2*a**2+2*ca**2*n**2*b)),(1,2*b*sig*((b*ca*n)**2-(a*cb*m)**2))]:
        assert diff(lambda x:h(theta,F(x),'B'),1,3)==0
        assert diff(lambda x:h(theta,F(x),'B'),1,2)==expected
    return (signexpr>0)-(signexpr<0)

signs=[]
for u,A,spread,ca,cb in product([3,6],[4,7],[0,F(1,4)],[F(1,4),F(9,10)],[1,2]):
    signs.append(check(F(u),F(u)+spread,F(A),F(A)+spread,ca,F(cb),F(1,8)))
print(len(signs),"fixed equal-share markets; exact theta degrees and highest derivatives agree.")
print("P5 theta=1 quartic leading signs represented:", sorted(set(signs)))
print("P6 second derivatives at both endpoints agree exactly.")
