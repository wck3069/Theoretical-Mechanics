"""本轮新增模型的数值抽查：python3 review/verify_examples.py。非全书形式证明。"""
import math, random
random.seed(6)
for _ in range(100):
    beta=random.uniform(-.9,.9); t=random.uniform(1,3); x=random.uniform(-2,2)
    g=1/math.sqrt(1-beta*beta); tp=g*(t-beta*x); xp=g*(x-beta*t)
    assert math.isclose(tp*tp-xp*xp,t*t-x*x,abs_tol=1e-12)
    q=random.uniform(-2,2); p=random.uniform(-2,2); h=.1
    pn=p-h*q; qn=q+h*pn
    inv=lambda q,p:(q*q+p*p-h*q*p)/2
    assert math.isclose(inv(qn,pn),inv(q,p),abs_tol=1e-12)
    u=random.uniform(0,.99); gamma=1/math.sqrt(1-u*u)
    assert math.isclose(gamma*gamma-(gamma*u)**2,1,abs_tol=1e-12)
# 无量纲稳恒进动：I1=2,I3=1,omega3=10,mgl=1,cos(theta)=.5
for root in ((10-math.sqrt(96))/2,(10+math.sqrt(96))/2):
    assert abs(root*root-10*root+1)<1e-12
# 反作用轮：Ib=9,Iw=1,nu=10
omega=-1; nu=10
assert 9*omega+(omega+nu)==0
assert .5*9*omega**2+.5*(omega+nu)**2==45
print('通过：100组间隔/质量壳/辛欧拉不变量，进动二根，反作用轮动量与能量。')
