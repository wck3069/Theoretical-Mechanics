"""第2章模型复核。运行：python3 review/verify_ch02.py；仅依赖标准库。"""
import math,json
from pathlib import Path
checks=[]
def close(a,b,tol=1e-9):
 assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)
def simpson(f,a,b,n=4000):
 h=(b-a)/n
 return h/3*(f(a)+f(b)+sum((4 if k%2 else 2)*f(a+k*h) for k in range(1,n)))
def root(f,a,b):
 fa=f(a); assert fa*f(b)<=0
 for _ in range(90):
  c=(a+b)/2
  if fa*f(c)<=0:b=c
  else:a=c;fa=f(a)
 return (a+b)/2
# 一阶与二阶变分，有限差精确公式
for eps in [.1,-.2,.35]:
 val=simpson(lambda x:(1+eps*(1-2*x))**2,0,1)
 close(val-1,eps*eps/3)
checks.append('有限差与一、二阶变分的精确关系')
# 折射图数值与斯涅尔关系
close(1*.6,(3/math.sqrt(5))*(1/math.sqrt(5)))
checks.append('折射图的斜率、折射率与斯涅尔关系')
# 多项式极小解与泛函值
y=lambda x:x**3/6+5*x/6
yp=lambda x:x*x/2+5/6
close(simpson(lambda x:yp(x)**2+2*x*y(x),0,1),74/45)
checks.append('多项式驻值路径及最小值74/45')
# 正定三对角矩阵求解

def tridiagonal(diag,rhs):
 n=len(diag);b=diag[:];d=rhs[:]
 for k in range(1,n):
  factor=-1/b[k-1];b[k]-=factor*(-1);d[k]-=factor*d[k-1]
 x=[0.]*n;x[-1]=d[-1]/b[-1]
 for k in range(n-2,-1,-1):x[k]=(d[k]+x[k+1])/b[k]
 return x
for N in [20,40,80]:
 h=1/N;rhs=[-h*h*(k*h) for k in range(1,N)];rhs[-1]+=1
 nodes=tridiagonal([2.]*(N-1),rhs)
 assert max(abs(val-y(k*h)) for k,val in enumerate(nodes,1))<1e-12
errors=[]
for N in [20,40,80]:
 h=1/N;rhs=[0.]*(N-1);rhs[-1]=1
 nodes=tridiagonal([2+h*h]*(N-1),rhs)
 err=max(abs(val-math.sinh(k*h)/math.sinh(1)) for k,val in enumerate(nodes,1))
 errors.append({'N':N,'max_node_error':err})
ratios=[errors[k]['max_node_error']/errors[k+1]['max_node_error'] for k in range(2)]
assert all(3.9<r<4.1 for r in ratios)
checks.append('三次解节点精确性与双曲正弦模型的二阶收敛')
# 自由端与Robin端点，唯一极小来自正二次型
free=lambda x:math.cosh(1-x)/math.cosh(1)
close(free(0),1);close(-math.sinh(0)/math.cosh(1),0)
for kappa in [0,.5,2]:
 B=-(math.sinh(1)+kappa*math.cosh(1))/(math.cosh(1)+kappa*math.sinh(1))
 close(math.sinh(1)+B*math.cosh(1)+kappa*(math.cosh(1)+B*math.sinh(1)),0)
checks.append('自然边界与含端点代价的Robin边界')
# 悬链线长度与内部欧拉残差
D=1.;length=3.;z=root(lambda z:math.sinh(z)/z-length/(2*D),1e-5,5)
a=D/z
close(2*a*math.sinh(D/a),length)
for x in [-.8,0,.7]:
 yy=a*math.cosh(x/a);ypc=math.sinh(x/a);ypp=math.cosh(x/a)/a
 close(1+ypc*ypc-yy*ypp,0)
checks.append('悬链线长度方程及变分、受力结果一致性')
# 圆弧积分面积与长度
d=1.;alpha=.9;R=d/(2*math.sin(alpha));L=2*R*alpha
curve=lambda x:math.sqrt(R*R-(x-d/2)**2)-R*math.cos(alpha)
close(simpson(curve,0,d),R*R*(alpha-math.sin(alpha)*math.cos(alpha)),1e-8)
assert d<L<math.pi*d/2
checks.append('图形圆弧约束及面积公式')
# 最速降线：求解端点，并检查两分支与时间
X=Y=1.;g=9.8
ratio=lambda th:(th-math.sin(th))/(1-math.cos(th))
th=root(lambda t:ratio(t)-X/Y,1e-5,2*math.pi-1e-5)
ab=Y/(1-math.cos(th));T=th*math.sqrt(ab/g);Tline=math.sqrt(2*(X*X+Y*Y)/(g*Y))
close(ab*(th-math.sin(th)),X);close(ab*(1-math.cos(th)),Y);assert T<Tline
for t in [.3,1,2.4,3.5,5.]:
 yy=ab*(1-math.cos(t));slope=math.sin(t)/(1-math.cos(t))
 close(slope*slope,(2*ab-yy)/yy)
 close(2*ab*math.sin(t/2)/math.sqrt(2*g*yy),math.sqrt(ab/g))
checks.append('摆线两分支、端点求解、时间可积性与直线比较')
# 归一化m=omega=A=1的二阶变分符号
modes={}
for mult in [.5,1,1.5]:
 Tspan=mult*math.pi
 vals=[Tspan/2*((n*math.pi/Tspan)**2-1) for n in [1,2]]
 modes[str(mult)]=vals
assert modes['0.5'][0]>0 and abs(modes['1'][0])<1e-12
assert modes['1.5'][0]<0<modes['1.5'][1]
checks.append('谐振子极小、零模、鞍点与共轭时刻')
# 积分约束抛物线与控制全局下界
A=.3
close(simpson(lambda x:6*A*x*(1-x),0,1),A)
close(simpson(lambda x:.5*(6*A*(1-2*x))**2,0,1),6*A*A)
checks.append('积分约束乘子及极小泛函值')
report={'checks_passed':checks,'finite_difference_errors':errors,'error_ratios':ratios,
 'catenary':{'a':a,'d':D,'length':length},
 'brachistochrone':{'X':X,'Y':Y,'g':g,'theta_B':th,'a':ab,'time_s':T,'line_time_s':Tline},'oscillator_mode_values':modes}
Path(__file__).with_name('ch02_verification_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
