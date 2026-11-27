"""Cross-chapter regression checks in units c=1 where applicable."""
from fractions import Fraction as F
from math import isclose, sqrt

# Same-order attractive potential: finite positive centrifugal term is
# insufficient when a > J^2/(2m).
m, J, a = F(2), F(2), F(3, 2)
for r in (F(1, 10), F(1, 100)):
    assert (-a/r**2 + J**2/(2*m*r**2)) * r**2 == F(-1, 2)
assert J**2/(2*m) - 1 == 0

# Equal beam/target masses m=1; compare invariant S at the same threshold
# and at the same kinetic-energy budget. Fixed target uses p_a^2=E_a^2-1.
def fixed_target(K):
    E = 1 + K
    return (E + 1)**2 - (E**2 - 1)

def collider(K):
    return (2 + K)**2

assert fixed_target(6) == collider(2) == 16
assert fixed_target(2) == 8 < collider(2)
# An exothermic mass sum of 1 can be realized as two particles of mass
# 1/2 at sqrt(S)=2; a single particle of mass 1 cannot carry that invariant.
assert fixed_target(0) == 4 != 1
assert isclose(2 * sqrt(F(1, 4) + F(3, 4)), 2)

# Relativistic kinetic Hamiltonian with identical kinetic momentum in
# both models; use rationalized expression to avoid small subtraction.
p = 0.02
kinetic = p**2 / (sqrt(1 + p**2) + 1)
assert abs(kinetic - (p**2 / 2 - p**4 / 8)) < 5e-12

# Equal-mass, equal-length double pendulum: independently evaluate the
# exact equations at theta=0 and verify the predicted eigenpairs.
for root, slope in ((2-sqrt(2), sqrt(2)), (2+sqrt(2), -sqrt(2))):
    assert isclose(2, root * (2+slope))
    assert isclose(slope, root * (1+slope))
print("5 cross-chapter checks passed")
