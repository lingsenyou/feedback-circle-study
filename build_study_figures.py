"""Portable publication figures built only from completed scalar-study CSV outputs."""
from pathlib import Path
from xml.sax.saxutils import escape
import math
import json
import csv
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
W = 1300
SCALE = 2
NAVY = "#17354C"
TEAL = "#087F8C"
AMBER = "#AE701B"
PURPLE = "#755AA6"
GRAY = "#51616F"
LIGHT = "#D8E2E8"
PALE = "#F4F7F9"
PALE_TEAL = "#EAF5F4"
PALE_AMBER = "#FFF4DE"
PALE_PURPLE = "#F2EEF8"
WHITE = "#FFFFFF"
def find_font(bold=False):
    candidates = ["C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
                  "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                  "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, 25).path
        except OSError:
            pass
    raise RuntimeError("Install Arial, DejaVu Sans, or Liberation Sans to render figures.")

FONT = find_font(False)
BOLD = find_font(True)


class Canvas:
    def __init__(self, height, name, description):
        self.h = height
        self.name = name
        self.description = description
        self.im = Image.new("RGB", (W*SCALE, height*SCALE), WHITE)
        self.d = ImageDraw.Draw(self.im)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="6.5in" height="{height/200:.3f}in" viewBox="0 0 {W} {height}">',
                    f'<title>{escape(description)}</title>',
                    '<desc>Synthetic scalar-agent simulation; no human, clinical, or language-model data.</desc>',
                    f'<rect width="{W}" height="{height}" fill="white"/>']

    def rect(self, x, y, w, h, fill=PALE, stroke=LIGHT, radius=16, sw=2):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        self.d.rounded_rectangle([x*SCALE, y*SCALE, (x+w)*SCALE, (y+h)*SCALE], radius=radius*SCALE, fill=fill, outline=stroke, width=round(sw*SCALE))

    def circle(self, x, y, r, fill=WHITE, stroke=TEAL, sw=3):
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        self.d.ellipse([(x-r)*SCALE, (y-r)*SCALE, (x+r)*SCALE, (y+r)*SCALE], fill=fill, outline=stroke, width=round(sw*SCALE))

    def text(self, x, y, value, size=27, color=NAVY, bold=False, anchor="start", leading=None):
        """y is the top of the text, using identical baseline conventions."""
        font = ImageFont.truetype(str(BOLD if bold else FONT), size*SCALE)
        ascent, descent = font.getmetrics()
        lines = value.split("\n")
        leading = leading or size*1.22
        for i, line in enumerate(lines):
            baseline = y+i*leading+ascent/SCALE
            self.svg.append(f'<text x="{x}" y="{baseline:.2f}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{"700" if bold else "400"}" fill="{color}" text-anchor="{anchor}">{escape(line)}</text>')
            self.d.text((x*SCALE, baseline*SCALE), line, font=font, fill=color, anchor={"start":"ls", "middle":"ms", "end":"rs"}[anchor])

    def line(self, points, color=GRAY, width=3, dashed=False):
        coords = " ".join(f"{x},{y}" for x, y in points)
        dash = ' stroke-dasharray="8 7"' if dashed else ""
        self.svg.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dash}/>')
        pts = [(x*SCALE,y*SCALE) for x,y in points]
        if not dashed:
            self.d.line(pts, fill=color, width=round(width*SCALE), joint="curve")
        else:
            for (x1,y1),(x2,y2) in zip(pts,pts[1:]):
                length = math.hypot(x2-x1,y2-y1)
                if not length: continue
                for p in range(0, math.ceil(length), 15*SCALE):
                    q = min(p+8*SCALE, length)
                    self.d.line([(x1+(x2-x1)*p/length,y1+(y2-y1)*p/length),(x1+(x2-x1)*q/length,y1+(y2-y1)*q/length)], fill=color,width=round(width*SCALE))

    def arrow(self, points, color=GRAY, width=3, dashed=False, head=10):
        self.line(points,color,width,dashed)
        (x0,y0),(x,y)=points[-2:]
        angle=math.atan2(y-y0,x-x0)
        pts=[(x,y),(x-head*math.cos(angle)+head*.50*math.sin(angle),y-head*math.sin(angle)-head*.50*math.cos(angle)),(x-head*math.cos(angle)-head*.50*math.sin(angle),y-head*math.sin(angle)+head*.50*math.cos(angle))]
        self.svg.append(f'<polygon points="{" ".join(f"{a:.2f},{b:.2f}" for a,b in pts)}" fill="{color}"/>')
        self.d.polygon([(a*SCALE,b*SCALE)for a,b in pts],fill=color)

    def panel(self, letter, title, x=30, y=24):
        self.rect(x,y,39,39,fill=NAVY,stroke=NAVY,radius=9,sw=0)
        self.text(x+19.5,y+2,letter,29,WHITE,True,"middle")
        self.text(x+54,y+2,title,31,NAVY,True)

    def footer(self, label="Conceptual schematic / proposed design; no empirical data."):
        self.line([(30,self.h-56),(1270,self.h-56)],LIGHT,2)
        self.text(30,self.h-44,label,25,GRAY)

    def save(self):
        self.svg.append('</svg>')
        (OUT/(self.name+".svg")).write_text("\n".join(self.svg),encoding="utf-8")
        self.im.save(OUT/(self.name+".png"),dpi=(400,400))
        return {"name":self.name,"width_in":6.5,"height_in":self.h/200,"png_pixels":[W*SCALE,self.h*SCALE],"min_font_pt_at_6_5_in":9.0,"description":self.description}


def design():
    c = Canvas(940, "figure2_study_design", "Implemented synthetic scalar-agent experiment")
    c.panel("A", "Synthetic preferences, access, and scalar adaptation")
    cards=[(30,NAVY,PALE,"Three synthetic groups","Equal population weights: 1/3\nDistinct optima with conflict\nSynthetic participants only"),
           (460,PURPLE,PALE_PURPLE,"Feedback participation","Experience and access costs\nSelection sensitivity: 0, 1.5, 3\nThree prespecified scenarios"),
           (890,TEAL,PALE_TEAL,"Scalar model updates","Exponential moving average\nLearning rate: 0.05\n250 rounds; batch size: 96")]
    for x,col,fill,title,body in cards:
        c.rect(x,103,380,186,fill=fill,stroke=col)
        c.text(x+190,120,title,28,col,True,"middle")
        c.text(x+190,174,body,25,GRAY,False,"middle",leading=32)
    c.arrow([(421,198),(446,198)],GRAY)
    c.arrow([(851,198),(876,198)],GRAY)
    c.panel("B", "Four paired conditions in each world and seed", y=342)
    branches=[(30,NAVY,PALE,"Endogenous","Outcome-dependent\nparticipation;\nfixed batch size"),
              (350,PURPLE,PALE_PURPLE,"Static loop-off","Participation fixed\nat its initial values;\nsame update rule"),
              (670,TEAL,PALE_TEAL,"Balanced quota","Accept 32 samples\nfrom each group\nper round"),
              (990,AMBER,PALE_AMBER,"Inverse weighting","Reweight sampled\nfeedback using\nknown propensities")]
    for x,col,fill,title,body in branches:
        c.rect(x,414,280,191,fill=fill,stroke=col)
        c.text(x+140,433,title,27,col,True,"middle")
        c.text(x+140,489,body,25,GRAY,False,"middle",leading=32)
    c.panel("C", "Evaluation is independent of who supplies feedback",y=650)
    c.rect(30,717,1240,128,fill=WHITE,stroke=TEAL)
    c.text(650,735,"Fixed equal-population loss and separate losses for every group",27,TEAL,True,"middle")
    c.text(650,779,"20 independent worlds × 10 paired seeds per condition",26,NAVY,False,"middle")
    c.text(650,812,"Uncertainty is evaluated across world means, not across individual rounds",25,GRAY,False,"middle")
    c.footer("Implemented design in a synthetic scalar task; clinical and language-model claims are not tested.")
    return c.save()


COLORS={"endogenous":NAVY,"static":PURPLE,"quota":TEAL,"ipw":AMBER}
LABELS={"endogenous":"Endogenous","static":"Static loop-off","quota":"Balanced quota","ipw":"Known-propensity IPW"}
PLOT_VALUES=[]


def csv_rows(name):
    with (ROOT/"results"/name).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def lighten(color, amount=.86):
    rgb=[int(color[i:i+2],16) for i in (1,3,5)]
    return "#"+"".join(f"{round(v+(255-v)*amount):02x}" for v in rgb)


def polygon(c, points, fill):
    c.svg.append(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in points)}" fill="{fill}"/>')
    c.d.polygon([(x*SCALE,y*SCALE) for x,y in points],fill=fill)


def axes(c,x,y,w,h,xlim,ylim,xticks,yticks,yformat=None):
    fx=lambda value:x+(value-xlim[0])/(xlim[1]-xlim[0])*w
    fy=lambda value:y+h-(value-ylim[0])/(ylim[1]-ylim[0])*h
    for value in yticks:
        yy=fy(value)
        c.line([(x,yy),(x+w,yy)],LIGHT,1.5)
        c.text(x-14,yy-15,yformat(value) if yformat else f"{value:g}",25,GRAY,False,"end")
    c.line([(x,y),(x,y+h),(x+w,y+h)],GRAY,2)
    for value in xticks:
        xx=fx(value)
        c.line([(xx,y+h),(xx,y+h+8)],GRAY,2)
        c.text(xx,y+h+16,f"{value:g}",25,GRAY,False,"middle")
    return fx,fy


def trajectory_data(rows,metric,condition,indices):
    selected=[r for r in rows if r["scenario"]=="main" and float(r["beta"])==3.0 and r["condition"]==condition]
    times=sorted({int(r["completed_updates"]) for r in selected})
    lookup={(int(r["world"]),int(r["completed_updates"])):float(r[metric]) for r in selected}
    arr=np.array([[lookup[(world,t)] for t in times] for world in range(20)])
    if not np.isfinite(arr).all(): raise ValueError(f"Non-finite plotted value for {metric}, {condition}")
    replicates=arr[indices].mean(axis=1)
    lo,hi=np.quantile(replicates,[.025,.975],axis=0)
    mean=arr.mean(axis=0)
    for t,m,l,u in zip(times,mean,lo,hi):
        PLOT_VALUES.append({"figure":3,"panel_metric":metric,"scenario":"main","beta":3,"condition_or_contrast":condition,"completed_updates":t,"mean":m,"ci95_low":l,"ci95_high":u})
    return np.array(times),mean,lo,hi


def trajectories(cfg):
    rows=csv_rows("trajectories_world.csv")
    rng=np.random.default_rng(cfg["bootstrap_seed"])
    indices=rng.integers(0,cfg["worlds"],size=(cfg["bootstrap_resamples"],cfg["worlds"]))
    c=Canvas(880,"figure3_trajectories","Measured simulation trajectories with world-bootstrap uncertainty")
    c.text(30,24,"Outcome-dependent participation changes the path of adaptation",31,NAVY,True)
    c.text(30,77,"Conflict + access friction; selection sensitivity beta = 3",27,GRAY)
    settings=[("A","Group 0 loss","Squared-loss units","g0_risk",(0,2.5),[0,.5,1,1.5,2,2.5],lambda v:f"{v:.1f}"),
              ("B","Population regret","Excess above oracle","population_regret",(0,.3),[0,.1,.2,.3],lambda v:f"{v:.1f}"),
              ("C","Group 0 feedback","Expected sample share","g0_expected_feedback_share",(0,.4),[0,.1,.2,.3,.4],lambda v:f"{v:.1f}")]
    for k,(letter,title,sub,metric,ylim,yticks,yfmt) in enumerate(settings):
        left=30+k*433
        c.panel(letter,title,x=left,y=144)
        c.text(left+54,195,sub,25,GRAY)
        fx,fy=axes(c,left+65,260,310,337,(0,250),ylim,[0,125,250],yticks,yfmt)
        data={cond:trajectory_data(rows,metric,cond,indices) for cond in COLORS}
        for cond in ["quota","ipw","static","endogenous"]:
            time,mean,lo,hi=data[cond]
            if np.min(lo)<ylim[0]-1e-10 or np.max(hi)>ylim[1]+1e-10:
                raise ValueError(f"Interval exceeds plotted axis: {metric} {cond}")
            pts=[(fx(t),fy(v)) for t,v in zip(time,lo)]+[(fx(t),fy(v)) for t,v in zip(time[::-1],hi[::-1])]
            polygon(c,pts,lighten(COLORS[cond]))
        for cond in ["quota","ipw","static","endogenous"]:
            time,mean,lo,hi=data[cond]
            c.line([(fx(t),fy(v)) for t,v in zip(time,mean)],COLORS[cond],4)
            for t,v in zip(time[::5],mean[::5]):c.circle(fx(t),fy(v),3,COLORS[cond],COLORS[cond],0)
        c.text(left+220,656,"Completed updates",25,NAVY,False,"middle")
    for x,cond in [(40,"endogenous"),(350,"static"),(685,"quota"),(987,"ipw")]:
        c.line([(x,734),(x+36,734)],COLORS[cond],5)
        label="IPW (known prop.)" if cond=="ipw" else LABELS[cond]
        c.text(x+48,716,label,25,COLORS[cond],True)
    c.text(30,771,"Means across 20 worlds (10 seeds each); bands are pointwise 95% bootstrap intervals.",25,GRAY)
    c.footer("Actual saved values every 10 updates are joined by straight segments; no curve smoothing.")
    return c.save()


def contrast_record(rows,scenario,beta,other):
    # Published contrasts use IPW minus endogenous. Reverse its sign and limits
    # when the figure consistently displays endogenous minus each comparator.
    label="ipw minus endogenous" if other=="ipw" else "endogenous minus "+other
    found=[r for r in rows if r["scenario"]==scenario and float(r["beta"])==beta and r["contrast"]==label and r["metric"]=="g0_risk"]
    if len(found)!=1: raise ValueError((scenario,beta,label,len(found)))
    r=found[0]
    mean,lo,hi=map(float,[r["mean"],r["ci95_low"],r["ci95_high"]])
    if other=="ipw":mean,lo,hi=-mean,-hi,-lo
    PLOT_VALUES.append({"figure":4,"panel_metric":"g0_risk","scenario":scenario,"beta":beta,"condition_or_contrast":"endogenous minus "+other,"completed_updates":"mean last 50 rounds","mean":mean,"ci95_low":lo,"ci95_high":hi})
    return mean,lo,hi


def effects_controls():
    rows=csv_rows("contrasts.csv")
    c=Canvas(900,"figure4_effects_controls","Paired intervention contrasts and mechanism controls from the simulation")
    c.panel("A","Main correction effects",x=30,y=26)
    c.panel("B","Mechanism controls",x=705,y=26)
    c.text(30,88,"Conflict + friction; beta = 3",25,GRAY)
    c.text(705,88,"Endogenous minus static loop-off",25,GRAY)
    c.text(30,127,"Group 0 loss: endogenous minus comparator",25,NAVY)
    c.text(705,127,"Group 0 loss across selection sensitivities",25,NAVY)
    x,y,w,h=270,218,335,360
    fx=lambda v:x+v/1.4*w
    for v in [0,.4,.8,1.2]:
        c.line([(fx(v),y),(fx(v),y+h)],LIGHT,1.5)
        c.text(fx(v),y+h+16,f"{v:.1f}",25,GRAY,False,"middle")
    c.line([(x,y),(x,y+h),(x+w,y+h)],GRAY,2)
    for yy,cond in [(267,"static"),(387,"quota"),(507,"ipw")]:
        mean,lo,hi=contrast_record(rows,"main",3.0,cond)
        c.text(245,yy-15,LABELS[cond].replace("Known-propensity IPW","IPW"),25,COLORS[cond],True,"end")
        c.line([(fx(lo),yy),(fx(hi),yy)],COLORS[cond],4)
        for v in [lo,hi]:c.line([(fx(v),yy-10),(fx(v),yy+10)],COLORS[cond],3)
        c.circle(fx(mean),yy,7,COLORS[cond],COLORS[cond],0)
        c.text(fx(mean),yy+22,f"{mean:.2f}",25,COLORS[cond],True,"middle")
    c.text(435,651,"Loss difference",26,NAVY,False,"middle")
    c.text(30,702,"Positive values: higher loss under endogenous feedback",25,GRAY)
    fx,fy=axes(c,788,218,445,360,(0,3),(-.2,1.0),[0,1.5,3],[-.2,0,.2,.4,.6,.8,1],lambda v:f"{v:.1f}")
    c.line([(fx(0),fy(0)),(fx(3),fy(0))],GRAY,2,dashed=True)
    controls=[("main",NAVY),("symmetric",PURPLE),("no_conflict",TEAL)]
    for scenario,col in controls:
        points=[]
        for beta in [0,1.5,3]:
            mean,lo,hi=contrast_record(rows,scenario,float(beta),"static")
            xx=fx(beta)
            c.line([(xx,fy(lo)),(xx,fy(hi))],col,3)
            c.line([(xx-8,fy(lo)),(xx+8,fy(lo))],col,3)
            c.line([(xx-8,fy(hi)),(xx+8,fy(hi))],col,3)
            points.append((xx,fy(mean)))
        c.line(points,col,3)
        for xx,yy in points:c.circle(xx,yy,6,col,col,0)
    c.text(1010,651,"Selection sensitivity beta",26,NAVY,False,"middle")
    for yy,label,col in [(709,"Conflict + friction",NAVY),(751,"Conflict + equal access",PURPLE),(793,"No conflict + friction",TEAL)]:
        c.line([(740,yy),(778,yy)],col,4)
        c.text(793,yy-18,label,25,col,True)
    c.text(30,757,"Endpoints: mean of final 50 rounds",25,GRAY)
    c.text(30,795,"All differences are paired within worlds",25,GRAY)
    c.footer("95% bootstrap intervals across 20 world means (10 seeds each); secondary intervals are descriptive.")
    return c.save()


if __name__ == "__main__":
    cfg=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
    summary=json.loads((ROOT/"results"/"summary.json").read_text(encoding="utf-8"))
    assert summary["actual_runs"]==7200 and summary["checks"]["status"]=="passed"
    records=[design(),trajectories(cfg),effects_controls()]
    fields=["figure","panel_metric","scenario","beta","condition_or_contrast","completed_updates","mean","ci95_low","ci95_high"]
    with (OUT/"plotted_values.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(PLOT_VALUES)
    manifest={"source":"Completed synthetic scalar simulation; no human or LLM data", "figures":records,
              "bootstrap_resamples":cfg["bootstrap_resamples"],"bootstrap_seed":cfg["bootstrap_seed"],
              "uncertainty_unit":"20 independent world means; each averages 10 paired seeds",
              "trajectory_intervals":"pointwise percentile intervals, not simultaneous bands",
              "trajectory_connections":"Straight line segments between recorded time points; no smoothing",
              "effect_direction":"endogenous minus comparator; IPW source contrast sign reversed consistently",
              "source_sha256":{name:hashlib.sha256((ROOT/"results"/name).read_bytes()).hexdigest() for name in ["trajectories_world.csv","contrasts.csv","summary.json"]}}
    (OUT/"figure_manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    print(json.dumps(manifest,indent=2))


