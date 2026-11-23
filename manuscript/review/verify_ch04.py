"""第4章独立模型核验；标准库。运行 python3 review/verify_ch04.py。"""
import cmath
import json
import math
from pathlib import Path

checks = []
results = {}
def close(a, b, tol=1e-9):
    assert abs(a-b) <= tol*max(1,abs(a),abs(b)), (a,b)
def mv(A,v): return [sum(x*y for x,y in zip(row,v)) for row in A]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def quadratic(A,v): return dot(v,mv(A,v))
def modes(M,K,cols,lams):
    for i,a in enumerate(cols):
        for x,y in zip(mv(K,a),mv(M,a)): close(x,lams[i]*y)
        for j,b in enumerate(cols): close(dot(a,mv(M,b)),float(i==j))
def rk4(rhs,t,s,h):
    k1=rhs(t,s);k2=rhs(t+h/2,[x+h*y/2 for x,y in zip(s,k1)])
    k3=rhs(t+h/2,[x+h*y/2 for x,y in zip(s,k2)])
    k4=rhs(t+h,[x+h*y for x,y in zip(s,k3)])
    return [x+h*(a+2*b+2*c+d)/6 for x,a,b,c,d in zip(s,k1,k2,k3,k4)]

# 一、用有限差分EL验证位置相关惯性的精确惯性项。
m,k,l=1.4,2.1,1.3
q,v,acc=.2,-.3,.4
momentum=lambda q,v:m*(1+q*q/l**2)*v
L=lambda q,v:.5*m*(1+q*q/l**2)*v*v-.5*k*q*q
h=1e-5
EL=(momentum(q+h*v,v+h*acc)-momentum(q-h*v,v-h*acc))/(2*h)-(L(q+h,v)-L(q-h,v))/(2*h)
close(EL,m*(1+q*q/l**2)*acc+m*q*v*v/l**2+k*q,1e-8)
checks.append('位形相关惯性精确方程的EL有限差分')

# 二、阻尼共振：独立时间平均输入与耗散，并检验功率带宽。
m,w0,gamma,F=1.3,1.7,.12,.6
P=lambda w:gamma*F*F*w*w/m/((w0*w0-w*w)**2+4*gamma*gamma*w*w)
wminus=math.sqrt(w0*w0+gamma*gamma)-gamma
wplus=math.sqrt(w0*w0+gamma*gamma)+gamma
close(wplus-wminus,2*gamma);close(P(wminus),P(w0)/2);close(P(wplus),P(w0)/2)
w=1.4;X=(F/m)/complex(w0*w0-w*w,2*gamma*w)
N=2000;pin=pout=0
for j in range(N):
    phase=2*math.pi*(j+.5)/N
    vel=(1j*w*X*cmath.exp(1j*phase)).real
    pin+=F*math.cos(phase)*vel/N;pout+=2*m*gamma*vel*vel/N
close(pin,pout);close(pin,P(w))
checks.append('阻尼响应相位、周期功率与精确半功率带宽')

# 三、符号纠正后的交叉项，两模分别代回原矩阵。
m=2.;w0=1.6;kap=.3
M=[[m,0],[0,m]];K=[[m*w0*w0,-m*kap],[-m*kap,m*w0*w0]]
cols=[[1/math.sqrt(2*m),1/math.sqrt(2*m)],[1/math.sqrt(2*m),-1/math.sqrt(2*m)]]
modes(M,K,cols,[w0*w0-kap,w0*w0+kap])
checks.append('交叉项频率与同相/反相振型配对')

# 四、不等质量：初值、能量、非欧氏正交与坐标缩放。
m,k,a=1.7,2.2,.3
M=[[m,0],[0,2*m]];K=[[3*k,-2*k],[-2*k,4*k]]
cols=[[1/math.sqrt(3*m),1/math.sqrt(3*m)],[2/math.sqrt(6*m),-1/math.sqrt(6*m)]]
lams=[k/m,4*k/m];modes(M,K,cols,lams)
assert abs(dot(cols[0],cols[1]))>.01
x0=[a,0];xi=[dot(g,mv(M,x0)) for g in cols]
reconstructed=[sum(cols[r][j]*xi[r] for r in range(2)) for j in range(2)]
for x,y in zip(reconstructed,x0):close(x,y)
close(.5*quadratic(K,x0),sum(.5*lam*z*z for lam,z in zip(lams,xi)))
Mz=[[m,0],[0,.5*m]];Kz=[[3*k,-k],[-k,k]]
modes(Mz,Kz,[[g[0],2*g[1]] for g in cols],lams)
checks.append('不等质量的正交、初值能量分解与坐标标度不变性')

# 五、从准确弹簧几何独立提取二次势能，并验证拍初值。
d,l,kap=3.,2.,.4
angle1,angle2=.7,-.3
errors=[]
for eps in [.02,.01]:
    t1,t2=eps*angle1,eps*angle2
    length=math.hypot(d+l*math.sin(t2)-l*math.sin(t1),l*math.cos(t1)-l*math.cos(t2))
    exact=.5*kap*(length-d)**2
    leading=.5*kap*l*l*(t2-t1)**2
    errors.append(abs(exact-leading))
assert errors[0]/errors[1]>12
wp,wm=1.,math.sqrt(1.2);beat_t=math.pi/(wm-wp)
close(math.cos((wm-wp)*beat_t/2),0)
close(.5*(1+1),1);close(.5*(1-1),0)
results['beat_first_transfer_dimensionless_time']=beat_t
checks.append('耦合摆弹簧几何二次项与拍包络')

# 六、双摆：独立质量对角化与精确非线性运动/线性解比较。
M=[[2.,1.],[1.,1.]];K=[[2.,0.],[0.,1.]]
sq=math.sqrt(2);lams=[2-sq,2+sq]
cols=[[1/math.sqrt(4+2*sq),sq/math.sqrt(4+2*sq)],[1/math.sqrt(4-2*sq),-sq/math.sqrt(4-2*sq)]]
modes(M,K,cols,lams)
close(quadratic(K,[1,1])/quadratic(M,[1,1]),.6)
def pend_rhs(t,s):
    a,b,u,v=s;c=math.cos(a-b);sn=math.sin(a-b)
    r1=-sn*v*v-2*math.sin(a);r2=sn*u*u-math.sin(b);det=2-c*c
    return [u,v,(r1-c*r2)/det,(2*r2-c*r1)/det]
def pend_energy(s):
    a,b,u,v=s;return u*u+.5*v*v+math.cos(a-b)*u*v+2*(1-math.cos(a))+1-math.cos(b)
def linear_angles(eps,t):
    lo,hi=math.sqrt(2-sq),math.sqrt(2+sq)
    return [.5*eps*(math.cos(lo*t)+math.cos(hi*t)),eps/sq*(math.cos(lo*t)-math.cos(hi*t))]
def pend_run(eps,h):
    s=[eps,0.,0.,0.];maxerr=max_energy=0;E0=pend_energy(s)
    for j in range(round(10/h)):
        s=rk4(pend_rhs,j*h,s,h);t=(j+1)*h
        lin=linear_angles(eps,t)
        maxerr=max(maxerr,max(abs(s[i]-lin[i]) for i in range(2)))
        max_energy=max(max_energy,abs(pend_energy(s)-E0)/E0)
    return s,maxerr,max_energy
amp=[]
for eps in [.08,.04,.02]:
    _,err,de=pend_run(eps,.005);amp.append({'angle':eps,'max_angle_error':err,'relative_energy_error':de})
ratios=[amp[j]['max_angle_error']/amp[j+1]['max_angle_error'] for j in range(2)]
assert all(7.5<r<8.5 for r in ratios),ratios
coarse=pend_run(.08,.02)[0];fine=pend_run(.08,.01)[0];finer=pend_run(.08,.005)[0]
step_ratio=max(abs(x-y) for x,y in zip(coarse,fine))/max(abs(x-y) for x,y in zip(fine,finer))
assert 13<step_ratio<19,step_ratio
results['double_pendulum']={'amplitudes':amp,'amplitude_error_ratios':ratios,'RK4_step_error_ratio':step_ratio}
checks.append('双摆模态、Rayleigh界、振幅误差与积分步长分离')

# 七、三质点：三模矩阵残差和质量正交、质心动量。
m,mu,k=1.3,2.1,.8
M=[[m,0,0],[0,mu,0],[0,0,m]];K=[[k,-k,0],[-k,2*k,-k],[0,-k,k]]
raw=[[1,1,1],[1,0,-1],[1,-2*m/mu,1]]
cols=[[x/math.sqrt(quadratic(M,g)) for x in g] for g in raw]
modes(M,K,cols,[0,k/m,k*(1/m+2/mu)])
for g in raw[1:]:close(dot([m,mu,m],g),0)
checks.append('三质点平移零模、两伸缩模及质心约束')

# 八、阻尼投影和外力功率，不把局部阻尼误写成模态独立。
m=1.7;c=.4
cols=[[1/math.sqrt(3*m),1/math.sqrt(3*m)],[2/math.sqrt(6*m),-1/math.sqrt(6*m)]]
M=[[m,0],[0,2*m]];K=[[3.,-2.],[-2.,4.]];C=[[c,0],[0,0]]
expected=[[c/(3*m),c*math.sqrt(2)/(3*m)],[c*math.sqrt(2)/(3*m),2*c/(3*m)]]
for i,g in enumerate(cols):
    for j,h in enumerate(cols):close(dot(g,mv(C,h)),expected[i][j])
F=[.7,-.2];xi=[.2,-.1];vel=[sum(cols[r][j]*xi[r] for r in range(2)) for j in range(2)]
close(dot(vel,F),dot(xi,[dot(g,F) for g in cols]))
close(quadratic(C,vel),sum(xi[i]*expected[i][j]*xi[j] for i in range(2) for j in range(2)))
checks.append('非比例阻尼矩阵、模态力与功率不变性')

# 九、吸振器：直接代入两条Newton方程核验反共振。
m,mu,k,kap,F=1.2,.4,2.3,.6,.8
w2=kap/mu;X1=0;X2=-F/kap
close((k+kap-m*w2)*X1-kap*X2,F);close(-kap*X1+(kap-mu*w2)*X2,0)
for z in [(3-math.sqrt(5))/2,(3+math.sqrt(5))/2]:close((2-z)*(1-z)-1,0)
checks.append('吸振器反共振零点与两质量本征极点')

# 十、有限链边界与长波误差，用差分矩阵直接作用本征矢量。
N=8
for j in range(N):
    p=2*math.pi*j/N;lam=4*math.sin(p/2)**2
    vec=[cmath.exp(1j*p*n) for n in range(N)]
    for n in range(N):close(2*vec[n]-vec[(n+1)%N]-vec[(n-1)%N],lam*vec[n])
N=3
for j in range(1,N+1):
    p=math.pi*j/(N+1);v=[0]+[math.sin(p*n) for n in range(1,N+1)]+[0]
    for n in range(1,N+1):close(2*v[n]-v[n+1]-v[n-1],4*math.sin(p/2)**2*v[n])
longerr=[1-2*math.sin(x/2)/x for x in [.2,.1,.05]]
assert all(3.99<longerr[j]/longerr[j+1]<4.01 for j in range(2))
results['long_wave_relative_errors']=longerr
checks.append('周期/固定端链本征残差、模数与长波二阶误差')

# 十一、Duffing：准确能量积分的无奇点周期，与首阶频移比较。
# q=A sin(theta)后端点平方根奇异性被消去，Simpson积分。
def duffing_frequency(A,beta,N=4000):
    f=lambda t:1/math.sqrt(1+beta*A*A*(1+math.sin(t)**2)/2)
    h=math.pi/(2*N);integ=h/3*(f(0)+f(math.pi/2)+sum((4 if j%2 else 2)*f(j*h) for j in range(1,N)))
    return 2*math.pi/(4*integ)
beta=.2;freq=[]
for A in [.4,.2,.1]:
    exact=duffing_frequency(A,beta);approx=1+3*beta*A*A/8
    freq.append({'A':A,'energy_integral_frequency':exact,'first_order_frequency':approx,'error':abs(exact-approx)})
assert all(15<freq[j]['error']/freq[j+1]['error']<17 for j in range(2))
results['duffing']=freq
checks.append('四次势能准确周期积分与首阶幅频移动')

# 十二、Floquet：两个基解推进一周期，与慢振幅近似独立比较。
def floquet(eps,Omega,gamma=0,N=2000):
    period=2*math.pi/Omega;h=period/N
    def rhs(t,s):
        stiffness=1+eps*math.cos(Omega*t)
        return [s[1],-stiffness*s[0]-2*gamma*s[1],s[3],-stiffness*s[2]-2*gamma*s[3]]
    s=[1.,0.,0.,1.]
    for j in range(N):s=rk4(rhs,j*h,s,h)
    a,c,b,d=s;trace=a+d;det=a*d-b*c
    disc=cmath.sqrt(trace*trace-4*det);eig=[(trace+disc)/2,(trace-disc)/2]
    close(det,math.exp(-2*gamma*period),1e-10)
    rate=math.log(max(abs(x) for x in eig))/period
    return {'max_multiplier_modulus':max(abs(x) for x in eig),'growth_rate':rate,'determinant':det}
inside=floquet(.1,2);outside=floquet(.1,2.1);damped=floquet(.1,2,.03)
assert abs(inside['growth_rate']-.025)<1e-4
assert abs(outside['growth_rate'])<1e-10
assert damped['growth_rate']<0
coarse=floquet(.1,2,N=1000)
assert abs(coarse['growth_rate']-inside['growth_rate'])<1e-10
results['floquet']={'inside':inside,'outside':outside,'damped':damped,'step_refinement_growth_difference':abs(coarse['growth_rate']-inside['growth_rate'])}
checks.append('单周期Floquet乘子、行列式、阻尼阈值与步长核查')

results={'checks_passed':checks,**results}
Path(__file__).with_name('ch04_verification_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
