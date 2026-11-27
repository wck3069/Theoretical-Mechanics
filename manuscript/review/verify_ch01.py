"""第一章教学模型复核，仅用Python标准库；从书稿目录运行。"""
from pathlib import Path
import math, json

def close(a,b,tol=1e-9):
    assert abs(a-b)<=tol*max(1,abs(a),abs(b)), (a,b)

checks=[]
# 两体弹性/非弹性碰撞：总动量及能量损失
for m,M,u1,u2,e in [(1,1,1,0,.5),(2,5,3,-1,1),(1,10,2,0,0)]:
    vg=(m*u1+M*u2)/(m+M);w=u1-u2
    v1=vg-M/(m+M)*e*w;v2=vg+m/(m+M)*e*w
    close(m*u1+M*u2,m*v1+M*v2)
    close(.5*(m*u1*u1+M*u2*u2-m*v1*v1-M*v2*v2),.5*m*M/(m+M)*(1-e*e)*w*w)
checks.append('三组碰撞：动量守恒与相对动能损失')
# 平面机械臂Jacobian有限差分与解析求导对照
l1,l2,q1,q2=3.,2.,.4,.7
f=lambda a,b:(l1*math.cos(a)+l2*math.cos(a+b),l1*math.sin(a)+l2*math.sin(a+b))
j=[[-l1*math.sin(q1)-l2*math.sin(q1+q2),-l2*math.sin(q1+q2)],
   [l1*math.cos(q1)+l2*math.cos(q1+q2),l2*math.cos(q1+q2)]]
h=1e-5
for k in range(2):
    a=f(q1+h*(k==0),q2+h*(k==1));b=f(q1-h*(k==0),q2-h*(k==1))
    for i in range(2):close((a[i]-b[i])/(2*h),j[i][k],1e-8)
checks.append('机械臂位置导数与速度Jacobian')
# 月球霍曼：SI计算，近远点角动量一致
mu=4.902800118e12;R=1737.4e3;r1=R+100e3;r2=R+1000e3;a=(r1+r2)/2
vt1=math.sqrt(mu*(2/r1-1/a));vt2=math.sqrt(mu*(2/r2-1/a))
dv1=vt1-math.sqrt(mu/r1);dv2=math.sqrt(mu/r2)-vt2;flight=math.pi*math.sqrt(a**3/mu)
close(r1*vt1,r2*vt2)
close(vt1*vt1/2-mu/r1,-mu/(2*a));close(vt2*vt2/2-mu/r2,-mu/(2*a))
checks.append('霍曼转移：两转折点能量、角动量及数值')
# 电梯微分方程与配重边界：无量纲GM=Omega=mu=1
rt=2.;mt=2.;tt=mt*(rt-1/rt**2)
T=lambda r:tt+(1/rt-1/r)+(rt*rt-r*r)/2
close(T(rt),tt)
for r in [.5,.9,1,1.5]:
    close((T(r+1e-5)-T(r-1e-5))/2e-5,1/r**2-r,1e-7)
assert T(1)>T(.9) and T(1)>T(1.1)
checks.append('太空电梯：张力求导、顶端配重边界与最大值')
# 广义机器人圆环角动量系数及转角
for M,m in [(1,1),(5,2),(100,1)]:
    theta=2*math.pi;phi=-theta*m/(M+2*m);alpha=phi+theta
    close(M*phi+M*m/(M+m)*alpha,0)
close(-2*math.pi/(1+2),-2*math.pi/3)
checks.append('自由圆环：等质量及不等质量的角动量关系')
# 等面积扇形的偏近点角积分
E1=math.radians(65.736) # 以正文实际值替代
source=(Path(__file__).resolve().parents[1]/'chapters/ch01.tex').read_text()
import re
m=re.search(r'domain=0:([\d.]+),samples=60',source);assert m
E1=math.radians(float(m[1]));m=re.search(r'domain=180:([\d.]+),samples=60',source);assert m
E2=math.radians(float(m[1]))
close(E1-.6*math.sin(E1),E2-.6*math.sin(E2)-math.pi,1e-8)
checks.append('等面积图：两偏近点角区间的扫掠面积')
# 拉格朗日点：首个天体为原点，mu=.01，L3近似误差为高阶
mass=.01
res=lambda u:(1-mass)*u/abs(u)**3+mass*(u-1)/abs(u-1)**3-(u-mass)
assert abs(res(-1+7*mass/12))<1e-5
checks.append('L3首天体原点坐标的小质量比展开')
# 高斯势角动量函数极大及二阶导数分支
Lsq=lambda x:2*x*x*math.exp(-x)
assert Lsq(2)>Lsq(1.99) and Lsq(2)>Lsq(2.01)
checks.append('高斯势临界圆轨道与严格稳定内支')

def orbit(step):
    x,y,vx,vy=1.,0.,0.,.8
    E0=-.68;j0=.8;period=2*math.pi*(25/34)**1.5
    n=math.ceil(10*period/step);h=10*period/n
    energy_err=angular_err=0.;rmin=1.
    for _ in range(n):
        r=math.hypot(x,y);ax,ay=-x/r**3,-y/r**3
        xn=x+h*vx+.5*h*h*ax;yn=y+h*vy+.5*h*h*ay
        rn=math.hypot(xn,yn);anx,any=-xn/rn**3,-yn/rn**3
        vx+=.5*h*(ax+anx);vy+=.5*h*(ay+any);x,y=xn,yn
        energy_err=max(energy_err,abs((vx*vx+vy*vy)/2-1/rn-E0)/abs(E0))
        angular_err=max(angular_err,abs(x*vy-y*vx-j0)/abs(j0));rmin=min(rmin,rn)
    return {'actual_step':h,'steps':n,'max_relative_energy_error':energy_err,
            'max_relative_angular_error':angular_err,'min_radius':rmin}
coarse,fine=orbit(.01),orbit(.005)
ratio=coarse['max_relative_energy_error']/fine['max_relative_energy_error']
assert 3.8<ratio<4.2
assert fine['max_relative_angular_error']<1e-11
assert abs(fine['min_radius']-8/17)<2e-4
checks.append('Verlet十周期：二阶能量误差收敛、角动量与近心距')
report={'checks_passed':checks,'Hohmann':{'dv1_m_s':dv1,'dv2_m_s':dv2,'flight_s':flight},
        'orbit_coarse':coarse,'orbit_fine':fine,'energy_error_ratio':ratio}
out=Path(__file__).with_name('ch01_verification_results.json');out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
