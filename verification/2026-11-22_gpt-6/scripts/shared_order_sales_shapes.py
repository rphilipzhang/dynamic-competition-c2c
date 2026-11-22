"""Symbolic checks for the order/sales crossings and polynomial degrees."""
import sympy as sp

t, g = sp.symbols("theta gamma", nonnegative=True)
a, b, u, v, m, n, A, B, x, z, s, h, r, q, U = sp.symbols(
    "a b u v m n A B x z sigma H r q U", positive=True
)
# x,z are second-period shares of A,B; a,b are first-period shares.
D = v + r * (1 - t)
tail_b = q + h / D
order_theta_part = 2 * s * b * t * (tail_b - q)
assert sp.cancel(sp.diff(order_theta_part, t, 2) - 4*s*b*h*r*(v+r)/D**3) == 0
f = tail_b**2 - q**2
assert sp.cancel(sp.diff(t*f, t, 2) - (2*sp.diff(f, t) + t*sp.diff(f, t, 2))) == 0
print("Order curvature 4*s*b*H*r*(v+r)/D^3; sales curvature s*b*(2*f' + theta*f'').")

# At theta=1 the denominators clear without assuming costs or prices distinct.
S, T, K = u+g*m, v+g*n, u+g*x*m
sA, sB = A/S, B/T
qA, qB = A/K, (B-g*z*n*A/K)/v
# theta=1: with a+b=1 the A order is aU-2sigma(q_A-b*q_B);
# expected A sales are a*mu-sigma*(q_A**2-b*q_B**2).
y_num = sp.cancel(v*S*T*K*((sA-qA)+b*(qB-sB))/g)
er_num = sp.cancel(v**2*S**2*T**2*K**2*((qA**2-sA**2)+b*(sB**2-qB**2))/g)
J = B*x*m - A*z*n
assert sp.cancel(sp.diff(y_num, g, 2)-2*b*m*n*J) == 0
assert sp.cancel(sp.diff(er_num, g, 5)+sp.factorial(5)*b*m**2*n**2*J**2) == 0
print("P1 quadratic second derivative = 2*b*m*n*J.")
print("P3 quintic fifth derivative = -120*b*m^2*n^2*J^2; J=B*x*m-A*z*n>0.")

# Test the claimed unqualified quartic degree in P5 at its vanishing-leading-coefficient market.
# p_A1=p_B1=p_A2=p_B2=4; A=1,B=5/2; mu=10,sigma=1; both shares=1/2, theta=1.
a0 = b0 = sp.Rational(1, 2)
A0, B0 = sp.Integer(1), sp.Rational(5, 2)
m0, n0 = 4-A0, 4-B0
S0, T0, K0 = 4+g*m0, 4+g*n0, 4+g*a0*m0
def profit_a(own, other, within):
    ra = a0*10-own**2+b0*other**2
    rb = b0*(10-other**2)
    ya = a0*11-2*(own-b0*other)
    return 4*ra-A0*ya+g*m0*(ra if within else a0*(ra+rb))

profit_S = profit_a(A0/S0, B0/T0, True)
profit_N = profit_a(A0/K0, (B0-g*b0*n0*A0/K0)/4, False)
h_A = sp.factor((profit_S-profit_N)*S0*T0**2*K0**2*4**2/g)
print("Boundary market h_A(1,gamma) =",h_A, "; degree =",sp.degree(h_A, g))
assert sp.degree(h_A, g) == 3
