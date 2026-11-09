import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT="latex-report/figures"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({
    "font.family":"Noto Sans CJK SC",
    "font.size":9,
    "axes.titlesize":12,
    "axes.labelsize":9,
    "axes.edgecolor":"#B9C5CF",
    "axes.linewidth":0.7,
    "xtick.color":"#526273",
    "ytick.color":"#526273",
    "text.color":"#172B4D",
    "axes.labelcolor":"#526273",
    "figure.facecolor":"white",
    "axes.facecolor":"white",
    "savefig.facecolor":"white",
})
NAVY="#173B57"; BLUE="#477A9E"; TEAL="#2D8580"; RED="#B35A58"; GOLD="#B38A45"; GRID="#E5EBF0"
def finish(name):
    plt.grid(axis="y",color=GRID,linewidth=.7)
    plt.tight_layout()
    plt.savefig(f"{OUT}/{name}.png",dpi=240,bbox_inches="tight")
    plt.close()

q=["Q1","Q2","Q3","Q4"]
fig,ax=plt.subplots(figsize=(8.2,3.7))
occ=[90.59,92.24,88.83,89.54]; rent=[35.04,34.15,34.42,33.07]
ax.plot(q,occ,marker="o",lw=2.4,color=BLUE,label="期末出租率（%）")
ax.set_ylim(85,95); ax.set_ylabel("出租率（%）")
ax2=ax.twinx(); ax2.plot(q,rent,marker="s",lw=2.4,color=RED,label="期末租金（元/㎡/月）")
ax2.set_ylim(30,37); ax2.set_ylabel("租金（元/㎡/月）")
ax.set_title("普洛斯 REIT：出租率回升与租金下行并存",loc="left",fontweight="bold",color=NAVY,pad=12)
lines=ax.get_lines()+ax2.get_lines(); ax.legend(lines,[x.get_label() for x in lines],loc="lower left",frameon=False,ncol=2)
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
finish("glp_ops")

fig,ax=plt.subplots(figsize=(8.2,3.8))
names=["北京空港","增城","淀山湖","顺德","苏州望亭"]
occ=[96.05,100,73.15,97.29,100]; rent=[66.02,40.50,24.96,36.88,36.30]
x=np.arange(len(names)); w=.36
ax.bar(x-w/2,occ,w,color=BLUE,label="出租率（%）")
ax.set_ylim(0,115); ax.set_ylabel("出租率（%）")
ax2=ax.twinx(); ax2.bar(x+w/2,rent,w,color=GOLD,label="租金（元/㎡/月）"); ax2.set_ylim(0,80); ax2.set_ylabel("租金（元/㎡/月）")
ax.set_xticks(x,names); ax.set_title("项目层运营分化",loc="left",fontweight="bold",color=NAVY,pad=12)
lines=ax.containers+ax2.containers
ax.legend([lines[0],lines[1]],["出租率（%）","租金（元/㎡/月）"],frameon=False,ncol=2,loc="upper right")
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
finish("glp_projects")

fig,ax=plt.subplots(figsize=(8.2,3.6))
rev=np.array([108.70,107.56,102.41,105.02]); dist=np.array([82.83,83.96,84.04,86.65])
x=np.arange(4); w=.35
ax.bar(x-w/2,rev,w,color=BLUE,label="营业收入")
ax.bar(x+w/2,dist,w,color=TEAL,label="可供分配金额")
ax.set_xticks(x,q); ax.set_ylabel("百万元"); ax.set_title("普洛斯 REIT：单季收入与可供分配",loc="left",fontweight="bold",color=NAVY,pad=12)
ax.legend(frameon=False,ncol=2)
finish("glp_cash")

fig,ax=plt.subplots(figsize=(8.2,3.7))
occ=[92.07,92.94,81.26,89.35]; rent=[31.52,32.13,29.05,27.92]
ax.plot(q,occ,marker="o",lw=2.5,color=BLUE,label="期末出租率（%）")
ax.set_ylim(75,98); ax.set_ylabel("出租率（%）")
ax2=ax.twinx(); ax2.plot(q,rent,marker="s",lw=2.5,color=RED,label="期末有效租金（元/㎡/月）"); ax2.set_ylim(24,35); ax2.set_ylabel("租金（元/㎡/月）")
ax.set_title("华夏深国际：出租率修复未扭转租金下行",loc="left",fontweight="bold",color=NAVY,pad=12)
lines=ax.get_lines()+ax2.get_lines(); ax.legend(lines,[x.get_label() for x in lines],frameon=False,ncol=2,loc="lower left")
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
finish("huaxia_ops")

fig,ax=plt.subplots(figsize=(7.8,3.4))
ax.bar(["第一大租户","前五大租户","其他租户"],[25.12,71.32,28.68],color=[RED,BLUE,TEAL],width=.55)
ax.set_ylim(0,85); ax.set_ylabel("租金收入占比（%）"); ax.set_title("华夏深国际：租金收入集中度",loc="left",fontweight="bold",color=NAVY,pad=12)
for i,v in enumerate([25.12,71.32,28.68]): ax.text(i,v+1,f"{v:.2f}%",ha="center",fontweight="bold")
finish("huaxia_tenants")

fig,ax=plt.subplots(figsize=(7.8,3.4))
sc=["基准","租金-5%","租金-10%","重复2025跌幅"]
vals=[4.98,4.61,4.23,3.66]
ax.bar(sc,vals,color=[BLUE,TEAL,GOLD,RED],width=.58)
ax.set_ylim(0,6); ax.set_ylabel("分派率（%）"); ax.set_title("租金压力情景下的分派率变化",loc="left",fontweight="bold",color=NAVY,pad=12)
for i,v in enumerate(vals): ax.text(i,v+.12,f"{v:.2f}%",ha="center",fontweight="bold")
finish("huaxia_sensitivity")

fig,ax=plt.subplots(figsize=(7.8,3.4))
sc=["悲观","中性","乐观","评估假设"]
vals=[-2.68,.55,2.10,2.67]
ax.bar(sc,vals,color=[RED,BLUE,TEAL,GOLD],width=.58)
ax.axhline(0,color="#596579",lw=.8)
ax.set_ylabel("持有到期 IRR（%）"); ax.set_title("首农 REIT：有限土地期限下的持有到期回报",loc="left",fontweight="bold",color=NAVY,pad=12)
for i,v in enumerate(vals): ax.text(i,v+(0.15 if v>=0 else -0.35),f"{v:.2f}%",ha="center",fontweight="bold")
finish("sino_irr")

fig,ax=plt.subplots(figsize=(7.8,3.4))
sc=["悲观","中性","乐观"]; renew=[55,85,95]; rent=[-15,-8,-3]
x=np.arange(3); w=.36
ax.bar(x-w/2,renew,w,color=BLUE,label="续租率（%）")
ax2=ax.twinx(); ax2.bar(x+w/2,[-v for v in rent],w,color=GOLD,label="租金降幅绝对值（%）")
ax.set_xticks(x,sc); ax.set_ylim(0,110); ax.set_ylabel("续租率（%）"); ax2.set_ylim(0,20); ax2.set_ylabel("续租租金降幅绝对值（%）")
ax.set_title("2028 年到期组重定价情景",loc="left",fontweight="bold",color=NAVY,pad=12)
lines=ax.containers+ax2.containers; ax.legend([lines[0],lines[1]],["续租率（%）","租金降幅绝对值（%）"],frameon=False,ncol=2)
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
finish("sino_scenarios")
