"""Exact coefficient certificate for the derivative in Proposition 2(c)."""
import sympy as sp

g,L,M,d0,d1,d2,d3=sp.symbols("g L M d0 d1 d2 d3", positive=True)
u,v,k,n,m,t,C,B=sp.symbols("u v k n m t C B", positive=True)
# u and v are the first-period prices A and B; C and B their costs.
# k=alpha_A2*(p_A2-C), n=alpha_B2*(p_B2-B), m=p_B2-B, t=theta.
w=(1-t)*n
tail_n=(B*(u+k*g)-t*n*C*g)/((u+k*g)*(v+w*g))
tail_s=B/(v+m*g)
D=(u+k*g)*(v+w*g)*(v+m*g)
lead=B*u*(m-w)-t*n*C*v
second=B*k*(m-w)-t*n*C*m
assert sp.cancel((tail_n-tail_s)*D-g*(lead+second*g))==0
assert sp.expand(lead-(B*u*(m-n)+t*n*(B*u-C*v)))==0
assert sp.expand(second-((1-t)*B*k*(m-n)+t*m*(B*k-n*C)))==0
den=d0+d1*g+d2*g**2+d3*g**3
coeffs=sp.Poly(sp.cancel(sp.diff((L*g+M*g**2)/den,g)*den**2),g).all_coeffs()
assert coeffs==[-M*d3,-2*L*d3,M*d1-L*d2,2*M*d0,L*d0]
print("Derivative coefficients (descending):", coeffs)
print("For 0 <= theta < 1 all d_i,L,M are positive under A11: m>n, B*u>=C*v, B*k>=C*n.")
print("Exactly one positive zero by Descartes and the opposite endpoint signs; gap tends to zero at each end.")
