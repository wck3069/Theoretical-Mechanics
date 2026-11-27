"""Independent SR checks; use c=1, reproducible random timelike/null vectors.
Run from any directory. Checks identities, event choices, finite differences,
quadratures and on-shell final-state conservation rather than TeX strings.
"""
import math as m
import random
import json
from pathlib import Path
rng=random.Random(707)
results=[]
def near(a,b,tol=2e-9):
    assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)
def g(v): return 1/m.sqrt(1-v*v)
def dot(a,b): return a[0]*b[0]-sum(x*y for x,y in zip(a[1:],b[1:]))
def boost(a,v): return (g(v)*(a[0]-v*a[1]),g(v)*(a[1]-v*a[0]),a[2],a[3])
def p4(mass,u):
    gamma=1/m.sqrt(1-sum(x*x for x in u))
    return (mass*gamma,*(mass*gamma*x for x in u))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def simpson(f,a,b,n=4000):
    h=(b-a)/n
    return h/3*(f(a)+f(b)+4*sum(f(a+i*h) for i in range(1,n,2))+2*sum(f(a+i*h) for i in range(2,n,2)))
def check(name,fn):
    value=fn(); results.append({'name':name,'passed':True,'evidence':value})

def lorentz():
    for _ in range(200):
        v=rng.uniform(-.95,.95); a=tuple(rng.uniform(-4,4) for _ in range(4)); b=boost(a,v)
        near(dot(a,a),dot(b,b)); back=boost(b,-v)
        for x,y in zip(a,back): near(x,y)
    near(boost((5,3,0,0),.6)[0],4)
    return '200 arbitrary four-vectors; inverse and interval; worked example ctprime=4'
check('Lorentz inverse and Minkowski interval',lorentz)

def measurements():
    v=.8; L0=2.3; A=(0,0,0,0); B=(0,L0/g(v),0,0)
    apr,bpr=boost(A,v),boost(B,v)
    near(bpr[1]-apr[1],L0); near(bpr[0]-apr[0],-v*L0)
    # Same clock at x=vt; proper time in clock frame.
    dt=4.2; near(boost((dt,v*dt,0,0),v)[0],dt/g(v))
    tpass=L0/(g(v)*v); near(g(v)*tpass,L0/v)
    return {'rod_length_L0':1/g(v),'passage_time_L0_over_c':tpass/L0}
check('Clock ticks and simultaneous rod endpoint events',measurements)

def reception():
    v=.6; L=1.7; tr=L/(1+v); tl=L/(1-v)
    near(v*tr,L-tr); near(v*tl,-L+tl)
    near(boost((tr,v*tr,0,0),v)[0],tr/g(v))
    return {'right_receive_t':tr,'left_receive_t':tl,'survival':m.exp(-4/3)}
check('Reception worldline intersections and exponential lifetime',reception)

def causal():
    a=(3,5,0,0); b=(5,3,0,0)
    near(boost(a,.6)[0],0); near(boost(b,.6)[1],0)
    near(abs(boost(a,.6)[1]),4); near(boost(b,.6)[0],4)
    assert all(boost(b,v)[0]>0 for v in [-.99,-.7,0,.7,.99])
    return 'spacelike simultaneous and timelike co-located frames; future order'
check('Causal classification and special frames',causal)

def axes():
    v=.5; gamma=g(v)
    for a,expected in [((gamma,gamma*v,0,0),(1,0)),((gamma*v,gamma,0,0),(0,1))]:
        b=boost(a,v); near(b[0],expected[0]); near(b[1],expected[1])
    return 'calibrated units on both invariant hyperbolae'
check('Spacetime-axis calibration',axes)

def proper():
    T=20; v=.8
    near(T/g(v),12); near(T*(1-v*v)/2,3.6); near(T*(1+v*v)/2,16.4)
    f=lambda s:m.sqrt(1-.64*m.sin(2*m.pi*s)**2)
    a=simpson(f,0,1,2000); b=simpson(f,0,1,4000)
    near(a,b,1e-12); assert .6<b<1
    # Direct displacement integral verifies reunion.
    near(simpson(lambda s:.8*m.sin(2*m.pi*s),0,1),0)
    return {'smooth_tau_over_T':b,'quadrature_change':abs(a-b)}
check('Twin simultaneity and smooth proper-time quadrature',proper)

def velocities():
    for _ in range(200):
        u=[rng.uniform(-.45,.45) for _ in range(3)]; v=rng.uniform(-.9,.9)
        dt=g(v)*(1-v*u[0]); up=((u[0]-v)*g(v)/dt,u[1]/dt,u[2]/dt)
        near(1-sum(x*x for x in up),(1-sum(x*x for x in u))/dt**2)
        assert sum(x*x for x in up)<1
    near((.6+.6)/(1+.36),15/17)
    near(m.tanh(2*m.atanh(.6)),15/17)
    return '200 three-dimensional velocities; rapidity; no superluminal result'
check('Velocity transformation and rapidity composition',velocities)

def light():
    for _ in range(200):
        theta=rng.uniform(0,2*m.pi); v=rng.uniform(-.9,.9)
        K=(1,m.cos(theta),m.sin(theta),0); Kp=boost(K,v)
        near(dot(Kp,Kp),0); near(Kp[0],g(v)*(1-v*m.cos(theta)))
        near((Kp[1]/Kp[0])**2+(Kp[2]/Kp[0])**2,1)
        near(Kp[1]/Kp[0],(m.cos(theta)-v)/(1-v*m.cos(theta)))
    Kp=boost((1,.5,m.sqrt(3)/2,0),.6)
    near(Kp[0],7/8); near(Kp[1]/Kp[0],-1/7)
    return 'null wave vectors, Doppler and aberration; exercise ratio 7/8'
check('Light speed, wave phase and Doppler angles',light)

def energy():
    for _ in range(150):
        mass=rng.uniform(.4,2); u=[rng.uniform(-.45,.45) for _ in range(3)]
        p=p4(mass,u); pp=boost(p,.7)
        near(dot(p,p),mass*mass); near(dot(pp,pp),mass*mass)
        for i in range(3): near(p[i+1]/p[0],u[i])
        W=p4(1,[.3,0,0]); near(dot(p,W),dot(pp,boost(W,.7)))
    return '150 mass shells; velocity inversion; observer-energy invariance'
check('Four-momentum mass shell and observer energy',energy)

def photon_system():
    e1,e2,theta=1.7,.9,1.2
    p=add((e1,e1,0,0),(e2,e2*m.cos(theta),e2*m.sin(theta),0))
    near(dot(p,p),2*e1*e2*(1-m.cos(theta)))
    # Equal opposite photons possess a rest frame, equal parallel do not.
    near(dot((2,0,0,0),(2,0,0,0)),4)
    near(dot((2,2,0,0),(2,2,0,0)),0)
    return {'invariant_mass':m.sqrt(dot(p,p))}
check('Composite mass of photons',photon_system)

def force():
    mass=1.4; u=[.3,.4,.1]; acc=[.13,-.08,.11]; gamma=1/m.sqrt(1-sum(x*x for x in u))
    udota=sum(x*y for x,y in zip(u,acc)); F=[mass*gamma*a+mass*gamma**3*udota*x for a,x in zip(acc,u)]
    eps=1e-6; pm=p4(mass,[x-eps*a for x,a in zip(u,acc)]); pp=p4(mass,[x+eps*a for x,a in zip(u,acc)])
    for i in range(3): near((pp[i+1]-pm[i+1])/(2*eps),F[i],2e-8)
    power=sum(x*y for x,y in zip(F,u)); near((pp[0]-pm[0])/(2*eps),power,2e-8)
    f=(gamma*power,*(gamma*x for x in F)); U=p4(1,u); near(dot(f,U),0)
    return 'finite-difference dp/dt and dE/dt, four-force orthogonality'
check('Three-force, power and four-force',force)

def constant_force():
    for z in [.001,.1,.75,1,10]:
        gamma=m.sqrt(1+z*z); x=gamma-1; u=z/gamma; tau=m.asinh(z)
        near(m.sinh(tau),z); near(m.cosh(tau)-1,x); near(u,m.tanh(tau)); near(gamma-1,x)
        near((x+1)**2-z*z,1)
    return {'z_0.75_tau':m.asinh(.75),'ln2':m.log(2),'z_1_acceleration':2**(-1.5)}
check('Constant force, work and proper acceleration',constant_force)

def lagrange():
    mass=1.3; u=[.25,-.33,.12]; gamma=1/m.sqrt(1-sum(x*x for x in u)); eps=1e-5
    def L(a): return -mass*m.sqrt(1-sum(x*x for x in a))
    p=[]
    for i in range(3):
        a=u.copy(); b=u.copy(); a[i]+=eps; b[i]-=eps
        val=(L(a)-L(b))/(2*eps); near(val,mass*gamma*u[i],2e-8); p.append(val)
    H=sum(a*b for a,b in zip(p,u))-L(u); near(H,m.sqrt(mass*mass+sum(x*x for x in p)),2e-8)
    for i in range(3):
        for j in range(3):
            a=u.copy(); b=u.copy(); a[j]+=eps; b[j]-=eps
            pi=lambda w:mass*w[i]/m.sqrt(1-sum(x*x for x in w))
            num=(pi(a)-pi(b))/(2*eps)
            near(num,mass*gamma*(i==j)+mass*gamma**3*u[i]*u[j],2e-8)
    return 'independent L and momentum derivatives, Hessian and Legendre energy'
check('Free action, regular Hessian and Legendre transform',lagrange)

def minimal():
    mass,e=1.2,-.7; A=[.3,-.2,.1]; u=[.4,.1,-.2]; phi=.6
    pi=p4(mass,u); pcan=[pi[i+1]+e*A[i] for i in range(3)]
    H=m.sqrt(mass*mass+sum((p-e*a)**2 for p,a in zip(pcan,A)))+e*phi
    near(H,pi[0]+e*phi)
    # Spatial gauge gradient changes canonical p with e*A, leaves kinetic p.
    grad=[.2,.5,-.1]
    for p,a,d,k in zip(pcan,A,grad,pi[1:]): near(p+e*d-e*(a+d),k)
    return 'canonical versus mechanical momentum; gauge-invariant kinetic energy'
check('Electromagnetic Hamiltonian minimal coupling',minimal)

def sticky():
    for E in [1,5/3,3,7]:
        p=m.sqrt(E*E-1); total=(E+1,p,0,0); mass=m.sqrt(2+2*E); v=p/(E+1)
        rest=boost(total,v); near(rest[0],mass); near(rest[1],0)
    near(m.sqrt(2+2*5/3),4/m.sqrt(3))
    return 'fixed-target sticky collisions checked in both frames'
check('Inelastic collision and system mass',sticky)

def decay():
    M,m1,m2=5,1,2; E1=(M*M+m1*m1-m2*m2)/(2*M); E2=M-E1
    p=m.sqrt(E1*E1-m1*m1); near(p,4*m.sqrt(6)/5)
    P1=(E1,p,0,0); P2=(E2,-p,0,0)
    near(dot(P2,P2),m2*m2)
    for v in [-.8,0,.6]:
        a,b=boost(P1,-v),boost(P2,-v); total=add(a,b)
        expect=boost((M,0,0,0),-v)
        for x,y in zip(total,expect): near(x,y)
    # 2 photons, theta*=0, beta=.6
    near(boost((.5,.5,0,0),-.6)[0],1)
    near(boost((.5,-.5,0,0),-.6)[0],.25)
    return {'daughter_E': [E1,E2],'daughter_p':p}
check('Massive two-body decay and photon decay boosts',decay)

def compton():
    for energy in [.001,.5,1,3]:
        for theta in [0,.3,m.pi/2,m.pi]:
            out=energy/(1+energy*(1-m.cos(theta)))
            recoil=(1+energy-out,energy-out*m.cos(theta),-out*m.sin(theta),0)
            near(dot(recoil,recoil),1)
    out=.5/1.5; near(out,1/3); p2=.5**2+out**2; near(p2,13/36)
    return '16 scattering kinematics; on-shell recoil; quantum relation kept separate'
check('Compton scattering conservation',compton)

def thresholds():
    for Mf,expected in [(3,3.5),(4,7)]:
        E=(Mf*Mf-2)/2; near(E,expected)
        p=m.sqrt(E*E-1); total=(E+1,p,0,0)
        near(dot(total,total),Mf*Mf)
        rest=boost(total,p/(E+1)); near(rest[0],Mf)
    MT=10; eps=2*(1+1/MT)
    near(MT*MT+2*MT*eps,(MT+2)**2)
    return {'fixed_target_K_Mf4':6,'collider_total_K_Mf4':2,'photon_target_threshold':eps}
check('Massive-channel thresholds and photon recoil threshold',thresholds)

def magnet():
    mass,e,B,rho=1.4,-.7,2.3,1.8
    p=abs(e)*B*rho; E=m.sqrt(mass*mass+p*p); u=p/E; omega=abs(e)*B/E
    near(u/rho,omega); near(E*E-p*p,mass*mass)
    return 'p=|e|Brho and omega=u/rho=|e|B/(gamma*m)'
check('Magnetic rigidity and cyclotron frequency',magnet)

def limits():
    errors=[]
    for u in [.12,.06,.03]:
        kinetic=g(u)-1
        series=u*u/2+3*u**4/8
        errors.append(abs(kinetic-series))
        momentum=g(u)*u
        near(m.sqrt(1+momentum*momentum)-1,kinetic)
    assert 63<errors[0]/errors[1]<66
    assert 63<errors[1]/errors[2]<66
    # Distinct p-series and u-series describe the same energy only after inversion.
    p=.01
    near(m.sqrt(1+p*p),1+p*p/2-p**4/8,1e-12)
    return {'velocity_series_remainder_ratios':[errors[i]/errors[i+1] for i in range(2)]}
check('Low-speed and low-momentum expansions',limits)

def two_to_two():
    # Build final states in the CM frame, then check four-vector conservation
    # and invariants after boosting back to the fixed-target laboratory.
    scenarios = [(0, 1, 0, 1, 1/3), (1, 1, 1, 1, 2),
                 (1, 1.01, 1, 1.01, 1.6), (1, 1, .8, 1.1, 2.5)]
    for m1, m2, m3, m4, E1 in scenarios:
        p1 = m.sqrt(E1**2-m1**2)
        initial1 = (E1, p1, 0, 0)
        initial2 = (m2, 0, 0, 0)
        total = add(initial1, initial2)
        s = m1**2+m2**2+2*m2*E1
        W = m.sqrt(s)
        beta = p1/(E1+m2)
        near(g(beta), (E1+m2)/W)
        near(dot(total, total), s)
        rest = boost(total, beta)
        near(rest[0], W)
        near(rest[1], 0)
        E3 = (s+m3**2-m4**2)/(2*W)
        E4 = W-E3
        pstar = m.sqrt((s-(m3+m4)**2)*(s-(m3-m4)**2))/(2*W)
        near(pstar**2, E3**2-m3**2)
        for mu in [-1, -.5, 0, .5, 1]:
            y = pstar*m.sqrt(1-mu**2)
            f3 = boost((E3, pstar*mu, y, 0), -beta)
            f4 = boost((E4, -pstar*mu, -y, 0), -beta)
            for actual, expected in zip(add(f3, f4), total):
                near(actual, expected)
            near(dot(f3, f3), m3**2)
            near(dot(f4, f4), m4**2)
            diff3 = tuple(a-b for a, b in zip(initial1, f3))
            diff4 = tuple(a-b for a, b in zip(initial1, f4))
            t, u = dot(diff3, diff3), dot(diff4, diff4)
            near(s+t+u, m1**2+m2**2+m3**2+m4**2)
            if (m1, m2) == (m3, m4):
                near(t, -2*pstar**2*(1-mu))
            if m1 == 0:
                cos_lab = f3[1]/f3[0]
                near(cos_lab, (mu+beta)/(1+beta*mu))
                near(f3[0], E1/(1+E1/m2*(1-cos_lab)))
                near(-t, 2*m2*(f4[0]-m2))
            if m1 == m2 == m3 == m4 == 1:
                K = E1-m1
                near(f3[0]-m3, K*(1+mu)/2)
                near(f4[0]-m4, K*(1-mu)/2)
                if abs(mu) < 1:
                    near(y/f3[1], m.sqrt((1-mu)/(1+mu))/g(beta))
                    near(y/f4[1], m.sqrt((1+mu)/(1-mu))/g(beta))
                    assert m.atan2(y, f3[1])+m.atan2(y, f4[1]) < m.pi/2
                else:
                    near(min(f3[0], f4[0]), 1)
    # Independent substitutions for the examples and exercises.
    photon = boost((1/m.sqrt(15), 2/(7*m.sqrt(15)), 3*m.sqrt(5)/(7*m.sqrt(15)), 0), -.25)
    near(photon[0], 2/7)
    near(photon[1]/photon[0], .5)
    exercise_photon = boost((1/(2*m.sqrt(2)), 0, 1/(2*m.sqrt(2)), 0), -1/3)
    near(exercise_photon[0], 3/8)
    near(exercise_photon[1]/exercise_photon[0], 1/3)
    nn = boost((m.sqrt(2), .5, m.sqrt(3)/2, 0), -1/m.sqrt(2))
    near(nn[0]-1, 1.5)
    near(nn[2]/nn[1], 1/m.sqrt(6))
    return {'events_checked': len(scenarios)*5,
            'photon_example_out_energy': photon[0],
            'equal_mass_example_lab_opening_deg': m.degrees(2*m.atan(m.sqrt(2/3)))}
check('Photon-nucleon and nucleon-nucleon two-to-two kinematics',two_to_two)

out=Path(__file__).with_name('ch07_verification_results.json')
out.write_text(json.dumps({'units':'c=1','checks':results,'passed':len(results)},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(results),'smooth_proper_time':results[5]['evidence']},ensure_ascii=False,indent=2))
