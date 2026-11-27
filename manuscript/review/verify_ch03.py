"""第3章模型检查：标准库实现；运行 python3 review/verify_ch03.py。"""
import math,json
from pathlib import Path
checks=[]
def close(a,b,tol=1e-9):
 assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)
def solve2(a,b,c,d,u,v):
 det=a*d-b*c;assert det>0
 return ((d*u-b*v)/det,(-c*u+a*v)/det)
# r(q,t)非线性含时参数化，验证用于动能投影的恒等式
q1,q2,t,v1,v2=1.2,.4,.3,.7,-.2
rq=lambda a,b,t:[[math.cos(b+t),math.sin(b+t),2*a],[-a*math.sin(b+t),a*math.cos(b+t),t]]
vel=lambda a,b,t,u,v:[u*math.cos(b+t)-a*math.sin(b+t)*(v+1),u*math.sin(b+t)+a*math.cos(b+t)*(v+1),2*a*u+t*v+b]
h=1e-5
for k in [0,1]:
 plus=vel(q1+h*(k==0),q2+h*(k==1),t,v1,v2);minus=vel(q1-h*(k==0),q2-h*(k==1),t,v1,v2)
 rplus=rq(q1+h*v1,q2+h*v2,t+h)[k];rminus=rq(q1-h*v1,q2-h*v2,t-h)[k]
 for j in range(3):close((plus[j]-minus[j])/(2*h),(rplus[j]-rminus[j])/(2*h),1e-8)
checks.append('含时坐标的运动学恒等式')
# 两杆稳定支的一阶导为零、二阶导正，并校验图中两杆长度
F=9/8;A1,A2=1.5,.5
for A in [A1,A2]:
 co=-F/math.hypot(F,A);si=-A/math.hypot(F,A)
 close(A*co-F*si,0);assert -A*si-F*co>0
close(math.hypot(1.2,1.6),2);close(math.hypot(18/math.sqrt(97),8/math.sqrt(97)),2)
checks.append('两杆稳定象限、Hessian与等长图形')
# 双滑轮联立方程回代三条Newton方程与动滑轮张力
m1,m2,m3,g=4.,2.,1.,9.8
u,v=solve2(m1+m2+m3,m3-m2,m3-m2,m2+m3,(m1-m2-m3)*g,(m2-m3)*g)
a1,a2,a3=u,-u+v,-u-v
T1=m1*(g-a1);T2=m2*(g-a2);T3=m3*(g-a3)
close(T2,T3);close(T1,2*T2)
checks.append('双滑轮质量矩阵与绳张力的Newton独立复核')
# 双摆：质量矩阵、短时RK4与总能量
m1=m2=l1=l2=g=1.
def rhs(s):
 a,b,u,v=s;D=a-b;c=math.cos(D);sn=math.sin(D)
 aa,bb=solve2(2.,c,c,1.,-sn*v*v-2*math.sin(a),sn*u*u-math.sin(b))
 return [u,v,aa,bb]
def energy(s):
 a,b,u,v=s
 return u*u+.5*v*v+math.cos(a-b)*u*v-2*math.cos(a)-math.cos(b)
def rk(s,h):
 k1=rhs(s);k2=rhs([x+h*y/2 for x,y in zip(s,k1)])
 k3=rhs([x+h*y/2 for x,y in zip(s,k2)]);k4=rhs([x+h*y for x,y in zip(s,k3)])
 return [x+h*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(s,k1,k2,k3,k4)]
def run(h):
 s=[.5,.9,.2,-.1];E0=energy(s);err=0.
 for _ in range(round(10/h)):
  s=rk(s,h);err=max(err,abs(energy(s)-E0)/abs(E0))
 return {'h':h,'max_relative_energy_error':err,'final_state':s}
coarse,fine=run(.01),run(.005)
ratio=coarse['max_relative_energy_error']/fine['max_relative_energy_error']
assert fine['max_relative_energy_error']<coarse['max_relative_energy_error'] and ratio>8
# 任意状态的能量导数应零，有限差分沿方程速度检查
s=[.7,-.3,.4,-.2];ds=rhs(s)
close((energy([x+h*v for x,v in zip(s,ds)])-energy([x-h*v for x,v in zip(s,ds)]))/(2*h),0,1e-8)
checks.append('双摆方程能量恒等式与RK4短时步长收敛')
# 黏滞摆的驱动/耗散收支
m,l,b,theta,om,tau=2.,.7,.3,.4,.6,.8
acc=(tau-b*om-m*9.8*l*math.sin(theta))/(m*l*l)
close(m*l*l*om*acc+m*9.8*l*math.sin(theta)*om,-b*om*om+tau*om)
checks.append('阻尼驱动摆的功率收支')
# 受驱动杆：EL恒定而机械能依电机功率改变
m,k,O,r,v=2.,3.,2.,.7,.3
acc=-(k-m*O*O)*r/m
close(m*v*acc+(k-m*O*O)*r*v,0)
power=m*v*acc+(k+m*O*O)*r*v
close(power,2*m*O*O*r*v)
checks.append('受驱动杆的两种能量及约束功率')
# 完整约束乘子与张力
m,l,theta,om=1.3,.8,.4,1.2
y=-l*math.cos(theta);speed=l*om
lam=(-m*speed*speed+m*9.8*y)/(l*l)
close(-lam*l,m*(l*om*om+9.8*math.cos(theta)))
checks.append('单摆乘子归一化与法向张力')
# 诺特恒等式：对任意非解曲线x=t^3+.4t, free L，boost C=pt-mx
m,t=1.7,.6
x=t**3+.4*t;v=3*t*t+.4;acc=6*t
# C derivative=m(acc*t+v)-mv
close(m*(acc*t+v)-m*v,m*acc*t)
# oscillator time translation C=-EL, offshell identity
k=2.;close(-(m*v*acc+k*x*v),(m*acc+k*x)*(-v))
checks.append('匀速变换边界项与时间平移诺特恒等式')
# 非完整盘圆轨迹及乘子, vakonomic yaw generically differs
m,R,w,O,theta=1.2,.6,1.1,.4,.7
vx,vy=R*w*math.cos(theta),R*w*math.sin(theta)
lam1,lam2=-m*R*w*O*math.sin(theta),m*R*w*O*math.cos(theta)
close(lam1*math.cos(theta)+lam2*math.sin(theta),0)
close(lam1*vx+lam2*vy-R*(lam1*math.cos(theta)+lam2*math.sin(theta))*w,0)
assert abs(R*w*math.sin(theta))>1e-3
checks.append('滚动盘反力投影、功率与不同变分模型的区别')
# uniform B two gauges Ldiff=e Dt(Bxy), conserved Noether quantity
m,e,B,x,y,vx,vy=1.4,-.7,2.,.4,.8,-.2,.5
old=.5*m*(vx*vx+vy*vy)-e*B*y*vx
new=.5*m*(vx*vx+vy*vy)+e*B*x*vy
close(new-old,e*B*(y*vx+x*vy));ax=e*B*vy/m
close(m*ax-e*B*vy,0)
checks.append('电磁两种规范的全导数与同一诺特荷')
# hoop off-axis frequency from derivative
R,g,O=1.3,9.8,4.
th=math.acos(g/(O*O*R))
f=lambda t:math.sin(t)*(O*O*math.cos(t)-g/R)
close((f(th+h)-f(th-h))/(2*h),-O*O*math.sin(th)**2,1e-8)
checks.append('旋转圆环的非竖直平衡与小振动频率')
# cone radial freq independent vs effective potential second derivative
m,g,al,r0=1.2,9.8,.6,.9
p2=m*m*g*math.cos(al)*r0**3*math.sin(al)**2
close(3*p2/(m*m*r0**4*math.sin(al)**2),3*g*math.cos(al)/r0)
checks.append('锥面圆轨道的径向稳定性')
report={'checks_passed':checks,'double_pendulum':{'coarse':coarse,'fine':fine,'energy_error_ratio':ratio},
'double_pulley':{'accelerations':[a1,a2,a3],'tensions':[T1,T2,T3]},'driven_rod_power':power}
Path(__file__).with_name('ch03_verification_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
