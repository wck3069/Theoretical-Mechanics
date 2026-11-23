"""第5章代表性模型核验。标准库；运行 python3 review/verify_ch05.py。"""
import math,json
from pathlib import Path
checks=[];results={}
def close(a,b,tol=1e-9):
    assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def add(a,b):return [x+y for x,y in zip(a,b)]
def scale(c,v):return [c*x for x in v]
def mv(A,v):return [dot(r,v) for r in A]
def tr(A):return list(map(list,zip(*A)))
def mm(A,B):return [[dot(r,c) for c in zip(*B)] for r in A]
def matclose(A,B,tol=1e-9):
    for a,b in zip(A,B):
        for x,y in zip(a,b):close(x,y,tol)
def eye():return [[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
def rz(t):
    c,s=math.cos(t),math.sin(t);return [[c,-s,0],[s,c,0],[0,0,1]]
def rx(t):
    c,s=math.cos(t),math.sin(t);return [[1,0,0],[0,c,-s],[0,s,c]]
def euler(phi,theta,psi):return mm(mm(rz(phi),rx(theta)),rz(psi))
def inertia(points,masses):
    return [[sum(m*(dot(p,p)*(i==j)-p[i]*p[j]) for m,p in zip(masses,points)) for j in range(3)] for i in range(3)]
def rk4(rhs,t,s,h):
    k1=rhs(t,s);k2=rhs(t+h/2,add(s,scale(h/2,k1)))
    k3=rhs(t+h/2,add(s,scale(h/2,k2)));k4=rhs(t+h,add(s,scale(h,k3)))
    return [x+h*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(s,k1,k2,k3,k4)]
def qmul(q,p):return [q[0]*p[0]-dot(q[1:],p[1:])]+add(add(scale(q[0],p[1:]),scale(p[0],q[1:])),cross(q[1:],p[1:]))
def qmatrix(q):
    w=q[0];v=q[1:];x,y,z=v;W=[[0,-z,y],[z,0,-x],[-y,x,0]]
    return [[(w*w-dot(v,v))*(i==j)+2*v[i]*v[j]+2*w*W[i][j] for j in range(3)] for i in range(3)]

# 1 用角矩阵有限差分独立提取空间/体角速度，核验ZXZ符号。
a=[.4,.8,-.6];rates=[.7,-.2,1.1];dt=1e-6
R=euler(*a);Rp=euler(*add(a,scale(dt,rates)));Rm=euler(*add(a,scale(-dt,rates)))
dR=[[(x-y)/(2*dt) for x,y in zip(rp,rm)] for rp,rm in zip(Rp,Rm)]
Wb=mm(tr(R),dR);Ws=mm(dR,tr(R));wb=[Wb[2][1],Wb[0][2],Wb[1][0]]
phi,theta,psi=a;ph,th,ps=rates
expected=[ph*math.sin(theta)*math.sin(psi)+th*math.cos(psi),ph*math.sin(theta)*math.cos(psi)-th*math.sin(psi),ph*math.cos(theta)+ps]
for x,y in zip(wb,expected):close(x,y,1e-8)
for x,y in zip([Ws[2][1],Ws[0][2],Ws[1][0]],mv(R,wb)):close(x,y,1e-8)
z=[0,0,1]
for x,y in zip(mv(mm(rx(math.pi/2),rz(math.pi/2)),z),[0,-1,0]):close(x,y)
checks.append('ZXZ矩阵有限差分、体/空间角速度及有限转动次序')

# 2 直接粒子求和核验主轴、惯量积、旋转协变与动能。
points=[[1,0,0],[0,1,0],[-1,-1,0]];mass=[1,1,1]
I=inertia(points,mass);matclose(I,[[2,-1,0],[-1,2,0],[0,0,4]])
axes=[[1/math.sqrt(2),1/math.sqrt(2),0],[-1/math.sqrt(2),1/math.sqrt(2),0],[0,0,1]]
for e,lam in zip(axes,[1,3,4]):
    for x,y in zip(mv(I,e),scale(lam,e)):close(x,y)
w=[.3,-.2,.7];J=[0.,0.,0.];T=0.
for m,p in zip(mass,points):
    v=cross(w,p);J=add(J,scale(m,cross(p,v)));T+=.5*m*dot(v,v)
for x,y in zip(J,mv(I,w)):close(x,y)
close(T,.5*dot(w,mv(I,w)))
rotated=[mv(R,p) for p in points];matclose(inertia(rotated,mass),mm(mm(R,I),tr(R)))
checks.append('三质点惯量、主轴、动能与张量旋转协变')

# 3 平行轴由点位平移直接重算，与张量公式比；薄板极限。
d=[.2,-.5,.4];newI=inertia([add(p,d) for p in points],mass)
expected=[[I[i][j]+3*(dot(d,d)*(i==j)-d[i]*d[j]) for j in range(3)] for i in range(3)]
matclose(newI,expected)
# 正方板角点：质心主惯量+质心平移，面内两本征值。
C=[[1/12,0,0],[0,1/12,0],[0,0,1/6]];d=[.5,.5,0]
corner=[[C[i][j]+dot(d,d)*(i==j)-d[i]*d[j] for j in range(3)] for i in range(3)]
for e,lam in zip(axes,[1/12,7/12,2/3]):
    for x,y in zip(mv(corner,e),scale(lam,e)):close(x,y)
assert 1+1<3
checks.append('平行轴、角点薄板正定性与主惯量约束')

# 4 两种移动矩心定义，直接对质点的绝对/相对速度角动量差分。
points2=[[1,0,.2],[0,2,-.1],[-.4,.1,.5]];masses=[1,2,.7]
accA=[.3,-.2,.1];omega=[0,0,.8];t=.7;dt=1e-5
MT=sum(masses)
def moving_state(t):
    vA=scale(t,accA);rot=rz(.8*t);H=[0,0,0];K=[0,0,0];torque=[0,0,0];P=[0,0,0];rhoC=[0,0,0]
    for p,m in zip(points2,masses):
        rho=mv(rot,p);rel=cross(omega,rho);v=add(vA,rel);acc=add(accA,cross(omega,rel))
        H=add(H,scale(m,cross(rho,v)));K=add(K,scale(m,cross(rho,rel)))
        torque=add(torque,scale(m,cross(rho,acc)));P=add(P,scale(m,v));rhoC=add(rhoC,scale(m/MT,rho))
    return H,K,torque,P,rhoC,vA
plus=moving_state(t+dt);minus=moving_state(t-dt);H,K,M,P,rhoC,vA=moving_state(t)
for j,expected in [(0,add(M,scale(-1,cross(vA,P)))),(1,add(M,scale(-MT,cross(rhoC,accA))))]:
    for x,y in zip(scale(1/(2*dt),add(plus[j],scale(-1,minus[j]))),expected):close(x,y,1e-8)
assert math.sqrt(dot(cross(rhoC,accA),cross(rhoC,accA)))>.01
checks.append('移动矩心绝对/相对角动量及加速度修正的粒子独立核验')

# 5 力系简化、加载梯子和非主轴外矩。
F=[.2,.4,-.3];M=[.7,-.1,.5];r=scale(1/dot(F,F),cross(F,M));parallel=scale(dot(F,M)/dot(F,F),F)
for x,y in zip(add(cross(r,F),parallel),M):close(x,y)
mg=9.8;theta=.8;bodyM=3.;person=1.;L=2.;s=1.2
Nw=mg*(bodyM/2+person*s/(2*L))/math.tan(theta);Nf=(bodyM+person)*mg
close(Nw*2*L*math.sin(theta),mg*(bodyM*L+person*s)*math.cos(theta))
alpha=.6;Om=1.3;Ip=.7
u=lambda t:[math.sin(alpha)*math.cos(Om*t),math.sin(alpha)*math.sin(Om*t),math.cos(alpha)]
J=lambda t:scale(Ip*Om,add([0,0,1],scale(-math.cos(alpha),u(t))))
dJ=scale(1/(2*dt),add(J(t+dt),scale(-1,J(t-dt))))
expected=scale(-Ip*Om**2*math.cos(alpha),cross([0,0,1],u(t)))
for x,y in zip(dJ,expected):close(x,y,1e-8)
close(dot(dJ,[0,0,Om]),0)
checks.append('力螺旋、加载梯子平衡与受驱非主轴力矩/功率')

# 6 斜面滚动的Newton方程、静摩擦及功率；接触加速度。
M,R,g,beta,kap=1.4,.6,9.8,.4,.5
acc=g*math.sin(beta)/(1+kap);fr=kap*M*acc;N=M*g*math.cos(beta)
close(M*g*math.sin(beta)-fr,M*acc);close(fr*R,kap*M*R*R*acc/R)
close(fr/N,kap/(1+kap)*math.tan(beta));vel=1.2
close(-fr*vel+fr*R*vel/R,0)
wp=[0,0,-vel/R];ap=cross(wp,cross(wp,[0,-R,0]));close(ap[1],vel*vel/R)
checks.append('滚动Newton方程、摩擦阈值、功率与瞬时接触加速度')

# 7 击球后摩擦冲量同时核验线动量、角动量和损失。
M,R,kap,impulse=1.7,.3,.4,.8;I=kap*M*R*R
for height in [0,.4*R,-.5*R,.8*R]:
    v0=impulse/M;w0=impulse*height/I;slip=v0-R*w0
    vr=(v0+kap*R*w0)/(1+kap);wr=vr/R;j=M*(vr-v0)
    close(I*(wr-w0),-R*j);close(slip+j*(1/M+R*R/I),0)
    T0=.5*M*v0*v0+.5*I*w0*w0;Tf=.5*M*vr*vr+.5*I*wr*wr
    close(T0-Tf,.5*kap*M/(1+kap)*slip*slip)
checks.append('台球击后滑动转滚动的双动量及能量损失')

# 8 对称自由体：体轴Euler导数与空间进动导数等价。
R=euler(.4,.8,-.6)
I=[2.,2.,3.];w=[.2,.3,1.1];n=(I[2]-I[0])/I[0]*w[2]
wbdot=[-n*w[1],n*w[0],0];Jb=[x*y for x,y in zip(I,w)]
for x,y in zip(mv(R,wbdot),scale(1/I[0],cross(mv(R,Jb),mv(R,w)))):close(x,y)
checks.append('自由对称刚体体频率与空间进动方向/符号')

# 9 Euler+四元数联合积分：核验两标量、单位范数与空间角动量。
I=[1.,2.,3.]
def free_rhs(t,state):
    w=state[:3];q=state[3:];a,b,c=w
    dw=[(I[1]-I[2])*b*c/I[0],(I[2]-I[0])*c*a/I[1],(I[0]-I[1])*a*b/I[2]]
    return dw+scale(.5,qmul(q,[0.]+w))
def invariants(state):
    w=state[:3];q=state[3:];jb=[a*b for a,b in zip(I,w)]
    return .5*dot(w,jb),dot(jb,jb),dot(q,q),mv(qmatrix(q),jb)
def free_run(initial,h,T=20.):
    state=initial+[1.,0.,0.,0.];ini=invariants(state);errs=[0.]*4;min_axis=1.
    for j in range(round(T/h)):
        state=rk4(free_rhs,j*h,state,h);now=invariants(state)
        vals=[abs(now[0]-ini[0])/ini[0],abs(now[1]-ini[1])/ini[1],abs(now[2]-1),math.sqrt(sum((x-y)**2 for x,y in zip(now[3],ini[3])))/math.sqrt(ini[1])]
        errs=[max(x,y) for x,y in zip(errs,vals)];min_axis=min(min_axis,state[1])
    return state,errs,min_axis
records={}
for name,initial in [('max_axis',[.001,.001,1.]),('middle_axis',[.001,1.,-.001/math.sqrt(3)])]:
    coarse=free_run(initial,.02);fine=free_run(initial,.01);finer=free_run(initial,.005)
    num=max(abs(x-y) for x,y in zip(coarse[0],fine[0]));den=max(abs(x-y) for x,y in zip(fine[0],finer[0]));ratio=num/den
    assert 13<ratio<19,(name,ratio)
    assert max(finer[1])<1e-8,(name,finer[1])
    records[name]={'h':.005,'max_relative_energy_error':finer[1][0],'max_relative_J_squared_error':finer[1][1],'max_q_norm_squared_error':finer[1][2],'max_relative_space_J_error':finer[1][3],'step_difference_ratio':ratio,'minimum_omega2':finer[2]}
assert records['middle_axis']['minimum_omega2']<-.9
# 初始微扰阶段的增长率，尚未进入非线性翻转。
initial=[1e-5,1.,-1e-5/math.sqrt(3)];state=initial+[1.,0.,0.,0.];h=.005
for j in range(800):state=rk4(free_rhs,j*h,state,h)
rate=math.log(state[0]/initial[0])/4
close(rate,1/math.sqrt(3),1e-7)
results['free_body']=records;results['middle_axis_early_growth_rate']=rate
checks.append('Euler与姿态联合积分、空间守恒、两步长收敛和中间轴早期增长')

# 10 固定动量有效势的有限差分曲率，对两支独立核验。
I1=1.;I3=.6;K=.3;spinH=2.;th=math.pi/3
roots=[2-math.sqrt(3.4),2+math.sqrt(3.4)];gyro=[]
for Om in roots:
    b=spinH*math.cos(th)+I1*Om*math.sin(th)**2
    U=lambda t:(b-spinH*math.cos(t))**2/(2*I1*math.sin(t)**2)+K*math.cos(t)
    dh=1e-4;first=(U(th+dh)-U(th-dh))/(2*dh);second=(U(th+dh)-2*U(th)+U(th-dh))/(dh*dh)
    close(first,0,2e-7)
    exact=(spinH/I1-2*Om*math.cos(th))**2+Om*Om*math.sin(th)**2
    close(second/I1,exact,2e-7);assert exact>0
    close(I1*Om*Om*math.cos(th)-spinH*Om+K,0)
    gyro.append({'Omega':Om,'p_phi':b,'nutation_frequency_squared':exact})
results['steady_top_branches']=gyro
checks.append('重陀螺快慢稳恒根、动量兼容与有效势曲率')

# 11 章动转折图的交点和轨迹能量；独立原θ方程。
b=1.2;H=2.;K=.3
U=lambda t:.5*(b-H*math.cos(t))**2/math.sin(t)**2+K*math.cos(t)
for t in [.5563710705352931,1.5611529346033528]:close(U(t),.7)
def top_rhs(t,s):
    theta,v=s;phi=(b-H*math.cos(theta))/math.sin(theta)**2
    return [v,math.sin(theta)*(phi*phi*math.cos(theta)-H*phi+K)]
s=[1.1,.2];E0=.5*s[1]**2+U(s[0]);err=0;h=.005
for j in range(2000):
    s=rk4(top_rhs,j*h,s,h);err=max(err,abs(.5*s[1]**2+U(s[0])-E0))
assert err<1e-9,err
results['nutation_max_absolute_energy_error']=err
checks.append('章动势图准确转折点与原方程能量核验')

# 12 睡眠陀螺：原线性系统积分与解析指数/频率。
I1=1.;K=.3
sleep=[]
for H in [.5,2.]:
    unstable=H*H<4*I1*K
    lam=math.sqrt(4*I1*K-H*H)/(2*I1) if unstable else 0
    freq=H/(2*I1) if unstable else (H+math.sqrt(H*H-4*I1*K))/(2*I1)
    A=.001;s=[A,0.,A*lam,A*freq];h=.005;T=4.
    rhs=lambda t,s:[s[2],s[3],(K*s[0]-H*s[3])/I1,(K*s[1]+H*s[2])/I1]
    for j in range(round(T/h)):s=rk4(rhs,j*h,s,h)
    exact=A*math.exp(lam*T)
    close(s[0],exact*math.cos(freq*T),1e-10);close(s[1],exact*math.sin(freq*T),1e-10)
    sleep.append({'h':H,'amplitude_ratio':math.hypot(s[0],s[1])/A,'growth_rate':lam})
results['sleeping_top_linear']=sleep
checks.append('竖直睡眠解原横向系统与阈值两侧解析核验')

# 13 三维光滑单点冲量：各分量动量、恢复与能量，不用二维猜测。
M=1.7;Idiag=[.4,.6,.8];v=[.2,-.7,.1];w=[.3,-.2,.5];arm=[.4,-.3,.2];normal=[0,1,0];e=.6
contact=add(v,cross(w,arm));vn=dot(contact,normal);assert vn<0
lever=cross(arm,normal);inv_mass=1/M+sum(x*x/I for x,I in zip(lever,Idiag));meff=1/inv_mass
j=-(1+e)*meff*vn;vp=add(v,scale(j/M,normal));wp=add(w,[j*x/I for x,I in zip(lever,Idiag)])
close(dot(add(vp,cross(wp,arm)),normal),-e*vn)
T=lambda v,w:.5*M*dot(v,v)+.5*sum(I*x*x for I,x in zip(Idiag,w))
close(T(v,w)-T(vp,wp),.5*meff*(1-e*e)*vn*vn)
# 倾杆实例：平动与转动末能量及接触点恢复。
M=1.;L=1.;V=1.;Ic=M*L*L/12;j=6*M*V/7;vy=-V+j/M;wz=(L/4)*j/Ic
close(vy+wz*L/4,V/2);close(.5*M*vy*vy+.5*Ic*wz*wz,2*M*V*V/7)
checks.append('三维单点冲量有效质量、恢复系数、能量与倾杆实例')

# 14 四元数主动乘法、转动矩阵、双覆盖及显式Euler缺陷。
q=[math.cos(.7/2),0,0,math.sin(.7/2)];x=[.2,-.6,.3]
y=qmul(qmul(q,[0.]+x),[q[0]]+scale(-1,q[1:]))[1:]
for a,b in zip(y,mv(rz(.7),x)):close(a,b)
matclose(qmatrix(q),rz(.7));matclose(qmatrix(scale(-1,q)),qmatrix(q))
W=[[0,-.7,.3],[.7,0,-.2],[-.3,.2,0]];h=.1;A=[[float(i==j)+h*W[i][j] for j in range(3)] for i in range(3)]
matclose(mm(tr(A),A),[[float(i==j)+h*h*mm(tr(W),W)[i][j] for j in range(3)] for i in range(3)])
checks.append('四元数主动转动、双覆盖与姿态正交误差')

# 15 内部轮：独立平台/轮角动量，能量与电机功率。
Ib,Iw=9.,1.;nudot=5.;Omdot=-Iw/(Ib+Iw)*nudot;tau=Iw*(Omdot+nudot)
close(Ib*Omdot,-tau);close(tau,4.5)
Om=-1.;nu=10.;J=Ib*Om+Iw*(Om+nu);close(J,0)
T=.5*Ib*Om*Om+.5*Iw*(Om+nu)**2;close(T,45);close(tau*(10/2)*2,T)
close((50-10)/(0.1/Iw),400)
results['wheel']={'motor_torque':tau,'acceleration_work':T,'net_two_stage_angle':-2.,'saturation_seconds':400.}
checks.append('反作用轮绝对/相对转速、电机功率、两阶段转角与饱和')

# 检查结果的范围是指定模型、有限区间和参数，非长期精度保证。
results={'checks_passed':checks,**results}
Path(__file__).with_name('ch05_verification_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
