"""第6章代表性核查与矢量图数据生成；仅用标准库。"""
import math,json
from pathlib import Path
checks=[];results={}
def close(a,b,tol=1e-8):
    assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)
def diff(f,x,h=1e-5):return (f(x+h)-f(x-h))/(2*h)
def simpson(f,a,b,N=2000):
    h=(b-a)/N
    return h/3*(f(a)+f(b)+sum((4 if j%2 else 2)*f(a+j*h) for j in range(1,N)))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def mv(A,v):return [dot(r,v) for r in A]
def mm(A,B):return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def tr(A):return list(map(list,zip(*A)))
def checkmat(A,B,tol=1e-9):
    for r,s in zip(A,B):
        for x,y in zip(r,s):close(x,y,tol)
def omega(n):return [[int(i<n and j==i+n)-int(i>=n and j==i-n) for j in range(2*n)] for i in range(2*n)]

# 1 非齐次、含时L的勒让德恒等式，用独立偏导核验。
M=lambda q:1+q*q
avec=lambda q,t:q*t+.2*q*q
V=lambda q,t:.3*q*q+.4*t*q
L=lambda q,v,t:.5*M(q)*v*v+avec(q,t)*v-V(q,t)
H=lambda q,p,t:.5*(p-avec(q,t))**2/M(q)+V(q,t)
q,p,t=.4,.8,.6;v=(p-avec(q,t))/M(q)
close(diff(lambda p:H(q,p,t),p),v)
close(diff(lambda q:H(q,p,t),q),-diff(lambda q:L(q,v,t),q))
close(diff(lambda t:H(q,p,t),t),-diff(lambda t:L(q,v,t),t))
checks.append('勒让德变换在使用运动方程前的偏导恒等式')

# 2 四次速度的三个局部分支，Hp用隐式Newton反解独立计算。
def branch(p,u):
    for j in range(12):u-=(u*u*u-u-p)/(3*u*u-1)
    return u
def branchH(p,u):
    v=branch(p,u);return .75*v**4-.5*v*v
for u in [0.,1.,-1.]:
    close(diff(lambda p:branchH(p,u),0),u)
    close(branchH(0,u),0 if u==0 else .25)
checks.append('非凸速度模型多分支、局部反解与H对动量导数')

# 3 罗斯函数对固定动量求导；角度重构与径向Newton式。
m,ell=1.7,.8;rad=.9;vel=.2
V=lambda r:-.7/r
R=lambda r,v,ell:.5*m*v*v-V(r)-ell*ell/(2*m*r*r)
close(diff(lambda r:R(r,vel,ell),rad),-.7/rad**2+ell**2/(m*rad**3))
close(-diff(lambda ell:R(rad,vel,ell),ell),ell/(m*rad*rad))
checks.append('与第5章同号的罗斯约化和离心项/重构')

# 4 相空间变分的边界形式：独立q,p变分，内部抵消后核验端点。
T=.8
for fixed in [False,True]:
    eta=lambda t:t*(T-t) if fixed else t*t+.3
    etad=lambda t:T-2*t if fixed else 2*t
    zeta=lambda t:math.cos(2*t)
    integrand=lambda t:zeta(t)*(-math.sin(t))+(-math.sin(t))*etad(t)-math.cos(t)*eta(t)-(-math.sin(t))*zeta(t)
    close(simpson(integrand,0,T),-math.sin(T)*eta(T),1e-10)
checks.append('相空间作用量独立变分与构型端点边界项')

# 5 规范变换用新旧势独立计算H，核验物理机械动量不变。
m,e,B=1.3,.7,.9;x,y,t=.4,-.3,.5;mom=[.8,.2]
chi=lambda x,y,t:.3*t*x*y
A=[0,B*x];grad=[.3*t*y,.3*t*x];ph=.2*x
pp=[mom[i]+e*grad[i] for i in range(2)];Ap=[A[i]+grad[i] for i in range(2)];php=ph-.3*x*y
oldH=sum((mom[i]-e*A[i])**2 for i in range(2))/(2*m)+e*ph
newH=sum((pp[i]-e*Ap[i])**2 for i in range(2))/(2*m)+e*php
close(newH,oldH-e*.3*x*y)
for i in range(2):close(pp[i]-e*Ap[i],mom[i]-e*A[i])
checks.append('电磁规范的含时生成函数、H变化与机械动量不变')

# 6 Liouville自由剪切、非静态高斯密度连续性及协方差行列式。
sq,sp,m=.6,.8,1.2;q,p,t=.4,-.2,.7
rho=lambda q,p,t:math.exp(-.5*((q-p*t/m)/sq)**2-.5*(p/sp)**2)
close(diff(lambda t:rho(q,p,t),t)+(p/m)*diff(lambda q:rho(q,p,t),q),0,1e-9)
varq=sq*sq+t*t*sp*sp/m**2;cov=t*sp*sp/m
close(varq*sp*sp-cov*cov,sq*sq*sp*sp)
pts=[(.5,.5),(1.5,.5),(1.5,1.5),(.5,1.5)]
area=lambda a:abs(sum(a[j][0]*a[(j+1)%len(a)][1]-a[(j+1)%len(a)][0]*a[j][1] for j in range(len(a))))/2
close(area(pts),area([(q+p,p) for q,p in pts]))
checks.append('自由流准确面积、非静态密度和协方差测度')

# 7 用多项式字典独立执行泊松代数，避免仅在一个数值点检查Jacobi。
NV=7 # x,y,z,px,py,pz,t
zero=(0,)*NV
def var(i):
    a=list(zero);a[i]=1;return {tuple(a):1.}
def plus(*polys):
    d={}
    for p in polys:
        for a,c in p.items():d[a]=d.get(a,0)+c
    return {a:c for a,c in d.items() if c!=0}
def scale(c,p):return {a:c*b for a,b in p.items() if c*b!=0}
def mul(p,q):
    d={}
    for a,c in p.items():
        for b,e in q.items():
            ab=tuple(x+y for x,y in zip(a,b));d[ab]=d.get(ab,0)+c*e
    return {a:c for a,c in d.items() if c!=0}
def deriv(p,j):
    d={}
    for a,c in p.items():
        if a[j]:
            b=list(a);b[j]-=1;d[tuple(b)]=c*a[j]
    return d
def PB(p,q):return plus(*[plus(mul(deriv(p,i),deriv(q,i+3)),scale(-1,mul(deriv(p,i+3),deriv(q,i)))) for i in range(3)])
x,y,z,px,py,pz,tt=[var(i) for i in range(NV)]
f=plus(mul(mul(x,x),py),mul(y,px));g=plus(mul(mul(px,px),y),mul(x,mul(py,py)));hh=mul(mul(x,px),y)
assert not plus(PB(f,PB(g,hh)),PB(g,PB(hh,f)),PB(hh,PB(f,g)))
Jx=plus(mul(y,pz),scale(-1,mul(z,py)));Jy=plus(mul(z,px),scale(-1,mul(x,pz)));Jz=plus(mul(x,py),scale(-1,mul(y,px)))
assert PB(Jx,Jy)==Jz
Hfree=scale(.5,plus(mul(px,px),mul(py,py),mul(pz,pz)));boost=plus(mul(tt,px),scale(-1,x))
assert not plus(deriv(boost,6),PB(boost,Hfree))
checks.append('多项式Jacobi恒等式、角动量代数及显时守恒量')

# 8 磁机械动量括号来自同一正则运算。
e,B=.7,.9
pix=px;piy=plus(py,scale(-e*B,x))
assert PB(pix,piy)=={zero:e*B}
assert PB(x,pix)=={zero:1.}
checks.append('机械动量磁括号与完整正则条件的区别')

# 9 4D体积反例和真正的互逆缩放。
Om=omega(2);bad=[[2,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,.5]]
new=mm(mm(bad,Om),tr(bad));close(new[0][2],2);close(new[1][3],.5)
good=[[2,0,0,0],[0,3,0,0],[0,0,.5,0],[0,0,0,1/3]]
checkmat(mm(mm(tr(good),Om),good),Om)
checks.append('四维单位体积非辛反例与正则缩放矩阵')

# 10 含时缩放生成函数，独立对变换后的q,p求全导数。
m,w,lam,t,q,p=1.4,.8,.3,.7,.2,-.4
Q=math.exp(lam*t)*q;P=math.exp(-lam*t)*p
K=lambda Q,P:math.exp(2*lam*t)*P*P/(2*m)+.5*m*w*w*math.exp(-2*lam*t)*Q*Q+lam*Q*P
Qdot=lam*Q+math.exp(lam*t)*p/m
Pdot=-lam*P-math.exp(-lam*t)*m*w*w*q
close(diff(lambda P:K(Q,P),P),Qdot);close(-diff(lambda Q:K(Q,P),Q),Pdot)
checks.append('含时正则缩放的新Hamilton量与全导数项')

# 11 HJ常力完全积分和重构；用偏导数直接代原PDE。
m,F,alpha,x,t=1.3,.6,.4,.7,.8
S=lambda x,a,t:(a+F*t)*x-a*a*t/(2*m)-a*F*t*t/(2*m)-F*F*t**3/(6*m)
pS=diff(lambda x:S(x,alpha,t),x);St=diff(lambda t:S(x,alpha,t),t)
close(St+pS*pS/(2*m)-F*x,0)
beta=diff(lambda a:S(x,a,t),alpha);close(x,beta+alpha*t/m+F*t*t/(2*m))
# 谐振子W正支的独立有限差分；避开转折点与反正弦切口。
m,w,E,q=1.2,.9,1.4,.3
W=lambda q,E:.5*q*math.sqrt(2*m*E-m*m*w*w*q*q)+E/w*math.asin(q/math.sqrt(2*E/(m*w*w)))
pW=diff(lambda q:W(q,E),q);close(pW*pW/(2*m)+.5*m*w*w*q*q,E)
close(diff(lambda E:W(q,E),E),math.asin(q/math.sqrt(2*E/(m*w*w)))/w)
checks.append('恒力与谐振子HJ残差、完全积分反解及局部分支')

# 12 谐振子作用积分与角度正则括号。
m,w,J=1.2,.9,.7
A=math.sqrt(2*J/(m*w));amp=math.sqrt(2*m*w*J)
close(simpson(lambda th:amp*math.cos(th)*A*math.cos(th),0,2*math.pi)/(2*math.pi),J)
q,p=.3,.7
angle=lambda q,p:math.atan2(m*w*q,p)
action=lambda q,p:(p*p+m*m*w*w*q*q)/(2*m*w)
bracket=diff(lambda q:angle(q,p),q)*diff(lambda p:action(q,p),p)-diff(lambda p:angle(q,p),p)*diff(lambda q:action(q,p),q)
close(bracket,1.)
checks.append('谐振子作用面积与角度/作用基本泊松括号')

# 13 单摆作用与周期：无端点奇异的积分和能量有限差分。
def pendperiod(E,N=2000):
    k2=E/2;return 4*simpson(lambda u:1/math.sqrt(1-k2*math.sin(u)**2),0,math.pi/2,N)
def pendaction(E,N=2000):
    k2=E/2;return 8/math.pi*k2*simpson(lambda u:math.cos(u)**2/math.sqrt(1-k2*math.sin(u)**2),0,math.pi/2,N)
pend=[]
for E in [.2,.8,1.6,1.9]:
    period=pendperiod(E);dJ=diff(pendaction,E,h=1e-5);close(dJ,period/(2*math.pi),2e-8)
    pend.append({'energy':E,'action':pendaction(E),'period':period,'dJ_dE':dJ})
close(simpson(lambda q:2*math.cos(q/2),-math.pi,math.pi)/math.pi,8/math.pi,1e-10)
assert pendperiod(1.99)>pendperiod(1.9)>pendperiod(.2)
results['pendulum']=pend
checks.append('单摆作用能量导数、准确周期及分离极限回路')

# 14 Kepler作用由偏近点角积分，不预设所得闭式作用。
m,kap,a,e=1.3,.8,2.1,.4
ell=math.sqrt(m*kap*a*(1-e*e));energy=-kap/(2*a)
Jr=math.sqrt(m*kap*a)/math.pi*simpson(lambda u:e*e*math.sin(u)**2/(1-e*math.cos(u)),0,math.pi)
close(Jr,kap*math.sqrt(m/(-2*energy))-ell,1e-10)
Jtot=Jr+ell;close(-m*kap*kap/(2*Jtot*Jtot),energy)
close(m*kap*kap/Jtot**3,math.sqrt(kap/(m*a**3)))
results['kepler']={'Jr':Jr,'Jphi':ell,'energy':energy,'frequency':m*kap*kap/Jtot**3}
checks.append('Kepler径向作用准确积分与能量/周期重构')

# 15 三类积分器的矩阵结构、修正二次型和边界Jordan行为。
h=.1;Om=omega(1)
AE=[[1,h],[-h,1]];AS=[[1-h*h,h],[-h,1]];AV=[[1-h*h/2,h],[-h*(1-h*h/4),1-h*h/2]]
for A in [AS,AV]:checkmat(mm(mm(tr(A),Om),A),Om)
GS=[[1,-h/2],[-h/2,1]];GV=[[1-h*h/4,0],[0,1]]
checkmat(mm(mm(tr(AS),GS),AS),GS);checkmat(mm(mm(tr(AV),GV),AV),GV)
checkmat(mm(mm(tr(AE),Om),AE),[[v*(1+h*h) for v in row] for row in Om])
A2=[[-3,2],[-2,1]];u=[1,1];v=[1,0]
for j in range(20):u=mv(A2,u);v=mv(A2,v)
close(max(map(abs,u)),1);assert max(map(abs,v))>20
checks.append('辛Euler/Verlet矩阵、修正二次型与h=2的特殊初值')

# 16 独立迭代算法与固定时间解析轨道比较。
def step(method,q,p,h):
    if method=='euler':return q+h*p,p-h*q
    if method=='symplectic':
        pp=p-h*q;return q+h*pp,pp
    pp=p-h*q/2;qq=q+h*pp;return qq,pp-h*qq/2
convergence=[]
for h in [.2,.1,.05,.025]:
    row={'step':h}
    for method in ['symplectic','verlet']:
        q,p=1.,0.
        for j in range(round(10/h)):q,p=step(method,q,p,h)
        row[method]=math.hypot(q-math.cos(10),p+math.sin(10))
    convergence.append(row)
ratios={method:[convergence[j][method]/convergence[j+1][method] for j in range(3)] for method in ['symplectic','verlet']}
assert all(1.7<v<2.3 for v in ratios['symplectic']),ratios
assert all(3.9<v<4.1 for v in ratios['verlet']),ratios
results['integrator_convergence']=convergence;results['convergence_ratios']=ratios
checks.append('固定时间辛Euler一阶与Verlet二阶独立迭代收敛')

# 17 非线性分裂流的逆步和面积；不将线性修正能量泛化。
def nonlinear(q,p,h):
    force=lambda q:q+q**3
    pp=p-h*force(q)/2;qq=q+h*pp;return qq,pp-h*force(qq)/2
q0,p0=.7,.2;q,p=nonlinear(q0,p0,.13);qback,pback=nonlinear(q,p,-.13)
close(qback,q0,1e-12);close(pback,p0,1e-12)
fd=1e-5
col1=[(a-b)/(2*fd) for a,b in zip(nonlinear(q0+fd,p0,.13),nonlinear(q0-fd,p0,.13))]
col2=[(a-b)/(2*fd) for a,b in zip(nonlinear(q0,p0+fd,.13),nonlinear(q0,p0-fd,.13))]
close(col1[0]*col2[1]-col2[0]*col1[1],1,1e-9)
energy=lambda q,p:.5*(q*q+p*p)+.25*q**4
assert abs(energy(q,p)-energy(q0,p0))>1e-6
checks.append('非线性Verlet逆步、局部辛面积与非精确保能')

# 18 一百周期：原能量与累计相位分开记录。
long=[];h=.1;N=round(200*math.pi/h)
for method in ['euler','symplectic','verlet']:
    q,p=1.,0.;Eerr=0;angle=0;prev=0;moderr=0
    mod=lambda q,p:.5*(q*q+p*p-h*q*p) if method=='symplectic' else .5*((1-h*h/4)*q*q+p*p)
    E0mod=mod(q,p)
    for j in range(N):
        q,p=step(method,q,p,h);Eerr=max(Eerr,abs(q*q+p*p-1))
        phase=math.atan2(-p,q);angle+=(phase-prev+math.pi)%(2*math.pi)-math.pi;prev=phase
        if method!='euler':moderr=max(moderr,abs(mod(q,p)-E0mod))
    long.append({'method':method,'steps':N,'elapsed_time':N*h,'max_relative_energy_error':Eerr,'phase_error':angle-N*h,'max_modified_energy_error':moderr if method!='euler' else None})
assert long[0]['max_relative_energy_error']>1e20
assert long[1]['max_relative_energy_error']<.06
assert long[2]['max_relative_energy_error']<.003
assert all(r['max_modified_energy_error']<1e-11 for r in long[1:])
assert .2<abs(long[2]['phase_error'])<.4
results['hundred_period_comparison']=long
checks.append('百周期能量、修正量与累计相位的分别检查')

# 数据放在书稿figures，使用确定性参数，保留可复现源。
figdir=Path(__file__).resolve().parents[1]/'figures';figdir.mkdir(exist_ok=True)
rows=['energy period']
for j in range(81):
    E=1.99*j/80;rows.append(f'{E:.12g} {pendperiod(E)/(2*math.pi):.12g}')
(figdir/'ch06_pendulum_period.dat').write_text('\n'.join(rows)+'\n')
state={method:(1.,0.) for method in ['euler','symplectic','verlet']};rows=['time euler symplectic verlet']
for j in range(601):
    if j%3==0:rows.append(f'{j*.1:.10g} '+' '.join(f'{q*q+p*p:.12g}' for q,p in state.values()))
    state={method:step(method,*s,.1) for method,s in state.items()}
(figdir/'ch06_integrator_energy.dat').write_text('\n'.join(rows)+'\n')
(figdir/'ch06_integrator_convergence.dat').write_text('step symplectic verlet\n'+'\n'.join(f"{r['step']} {r['symplectic']:.12g} {r['verlet']:.12g}" for r in convergence)+'\n')
results={'checks_passed':checks,**results}
Path(__file__).with_name('ch06_verification_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
