"""Publication-sized conceptual figures. No empirical values are plotted.

Outputs are 6.5-inch SVG masters and 400-dpi PNGs, using Arial.
Only this script and figures_en/ are written by the figure-design task.
"""
from pathlib import Path
from xml.sax.saxutils import escape
import math
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "concept_figures"
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
FONT = next((p for p in [Path("C:/Windows/Fonts/arial.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf")] if p.exists()), None)
BOLD = next((p for p in [Path("C:/Windows/Fonts/arialbd.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"), Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf")] if p.exists()), None)
if FONT is None or BOLD is None:
    raise RuntimeError("Install Arial, DejaVu Sans, or Liberation Sans to regenerate figures.")


class Canvas:
    def __init__(self, height, name, description):
        self.h = height
        self.name = name
        self.description = description
        self.im = Image.new("RGB", (W*SCALE, height*SCALE), WHITE)
        self.d = ImageDraw.Draw(self.im)
        self.svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="6.5in" height="{height/200:.3f}in" viewBox="0 0 {W} {height}">',
                    f'<title>{escape(description)}</title>',
                    '<desc>Conceptual schematic / proposed design; no empirical data.</desc>',
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


def figure1():
    c=Canvas(910,"figure1_feedback_selection","Feedback selection and a proposed iterative loop")
    c.panel("A","Feedback passes through several selection steps")
    stages=[("Affected people","Users and nonusers",NAVY,PALE),
            ("People reached","Access and exposure",TEAL,PALE_TEAL),
            ("Feedback offered","Time, language, cost",PURPLE,PALE_PURPLE),
            ("Feedback admitted","Filters and weights",AMBER,PALE_AMBER)]
    for i,(title,sub,col,fill) in enumerate(stages):
        x=30+i*320
        c.rect(x,107,280,159,fill=fill,stroke=col)
        c.circle(x+140,137,6,fill=col,stroke=col,sw=0)
        c.text(x+140,161,title,27,col,True,"middle")
        c.text(x+140,205,sub,25,GRAY,False,"middle")
        if i<3:c.arrow([(x+290,186),(x+310,186)],GRAY,3,head=9)
    c.text(650,291,"Define membership before observing outcomes;",27,NAVY,False,"middle")
    c.text(650,326,"estimate the influence of admitted feedback separately.",27,NAVY,False,"middle")
    c.panel("B","Participation and exit can change the next feedback pool",y=396)
    c.rect(55,480,290,134,fill=PALE_AMBER,stroke=AMBER)
    c.text(200,516,"Admitted feedback",28,AMBER,True,"middle")
    c.text(200,559,"At iteration t",25,GRAY,False,"middle")
    c.rect(483,462,334,169,fill=PALE_TEAL,stroke=TEAL)
    c.text(650,480,"System changes",29,TEAL,True,"middle")
    c.text(650,522,"Parameters",25,GRAY,False,"middle")
    c.text(650,552,"Context / memory",25,GRAY,False,"middle")
    c.text(650,582,"Deployment selection",25,GRAY,False,"middle")
    c.rect(955,480,290,134,fill=PALE,stroke=NAVY)
    c.text(1100,514,"Actions + outcomes",27,NAVY,True,"middle")
    c.text(1100,559,"Who remains engaged?",25,GRAY,False,"middle")
    c.arrow([(356,546),(468,546)],TEAL)
    c.arrow([(831,546),(941,546)],TEAL)
    c.arrow([(1100,627),(1100,685),(200,685),(200,626)],AMBER,dashed=True)
    c.text(650,695,"Changes in exposure, participation, and exit",25,AMBER,False,"middle")
    c.rect(55,760,1190,77,fill=WHITE,stroke=TEAL)
    c.text(650,781,"Independent assessment: fixed cohort, nonusers, and people who exit",26,TEAL,True,"middle")
    c.footer()
    return c.save()


def figure2():
    c=Canvas(940,"figure2_diagnostic_dissociation","Separate knowledge and preference tests from action responsiveness")
    c.panel("A","Three endpoints tested on matched unseen situations")
    items=[(30,TEAL,PALE_TEAL,"Knowledge","Describe relevant constraints"),
           (460,PURPLE,PALE_PURPLE,"Preference prediction","Predict stated preferences"),
           (890,NAVY,PALE,"Action responsiveness","Use constraints in decisions")]
    for x,col,fill,title,sub in items:
        c.rect(x,95,380,111,fill=fill,stroke=col)
        c.text(x+190,111,title,28,col,True,"middle")
        c.text(x+190,159,sub,25,GRAY,False,"middle")
    c.panel("B","Interpretation requires separate retention and loss criteria",y=251)
    c.text(478,320,"Knowledge / preference tests",25,GRAY,False,"middle")
    c.text(478,354,"Decline",29,NAVY,True,"middle")
    c.text(1005,320,"Knowledge / preference tests",25,GRAY,False,"middle")
    c.text(1005,354,"Preserved",29,TEAL,True,"middle")
    c.text(35,449,"Actions",27,NAVY,True)
    c.text(35,485,"Decline",27,GRAY)
    c.text(35,640,"Actions",27,NAVY,True)
    c.text(35,676,"Preserved",27,GRAY)
    cells=[(220,410,516,164,PALE,NAVY,"Information or memory loss","First examine forgetting, retrieval,\nand missing task information."),
           (754,410,516,164,PALE_AMBER,AMBER,"Candidate dissociation","Preserved tests; worse decisions.\nA mechanism is not yet established."),
           (220,592,516,164,PALE_PURPLE,PURPLE,"Shortcut or measurement mismatch","Check whether tests measure what\nthe decision task actually requires."),
           (754,592,516,164,PALE_TEAL,TEAL,"No observed responsiveness loss","The proposed action loss is absent\nin this experimental setting.")]
    for x,y,w,h,fill,col,title,sub in cells:
        c.rect(x,y,w,h,fill=fill,stroke=col)
        c.text(x+22,y+24,title,27,col,True)
        c.text(x+22,y+76,sub,25,GRAY,leading=34)
    c.text(650,789,"Retention requires equivalence tests; loss requires a prespecified meaningful margin.",25,NAVY,False,"middle")
    c.text(650,827,"Control retrieval and task ability; test whether matched feedback restores actions.",25,NAVY,False,"middle")
    c.footer("Conceptual schematic; no empirical data. Test performance is not subjective understanding.")
    return c.save()


def figure3():
    c=Canvas(960,"figure3_proposed_experiment","Four proposed experimental conditions and mechanism controls")
    c.panel("A","Four conditions with separately matched update budgets")
    c.rect(30,94,1240,88,fill=PALE,stroke=LIGHT)
    c.text(650,110,"Same initial model, environments, and paired random seeds",27,NAVY,True,"middle")
    c.text(650,142,"Match knowledge supervision and action updates separately",25,GRAY,False,"middle")
    c.text(47,199,"CONDITION",25,GRAY,True)
    c.text(350,199,"FEEDBACK RULE",25,GRAY,True)
    c.text(950,199,"MECHANISM TARGET",25,GRAY,True)
    rows=[("Balanced feedback","Equal accepted feedback from\neach prespecified group","Cross-group\nreference",TEAL,PALE_TEAL),
          ("Endogenous\nselection","Participation varies with\ncost and past experience","Selection\nand exit",NAVY,PALE),
          ("Knowledge replay","Replace matched fact and\npreference examples","Information\nrescue",PURPLE,PALE_PURPLE),
          ("Cross-group quotas","Replace matched action feedback\nfrom low-feedback groups","Feedback-source\nrescue",AMBER,PALE_AMBER)]
    for i,(title,rule,target,col,fill) in enumerate(rows):
        y=240+i*100
        c.rect(30,y,1240,88,fill=fill,stroke=LIGHT,radius=10)
        c.rect(30,y,8,88,fill=col,stroke=col,radius=3,sw=0)
        c.text(51,y+(12 if "\n" in title else 25),title,27,col,True,leading=31)
        c.text(350,y+12,rule,26,NAVY,leading=31)
        c.text(950,y+12,target,26,col,leading=31)
    c.panel("B","Controls distinguish competing explanations",y=671)
    controls=[(30,"Same data, different order","Test migration-path effects"),
              (460,"Matched sample replacement","Match task difficulty and type"),
              (890,"Fixed group sampling","Vary aggregation alone")]
    for x,title,sub in controls:
        c.rect(x,738,380,101,fill=WHITE,stroke=LIGHT)
        c.text(x+190,755,title,25,NAVY,True,"middle")
        c.text(x+190,797,sub,25,GRAY,False,"middle")
    c.text(650,860,"Independent unit: a training run. Fix target groups and service objectives in advance.",25,NAVY,False,"middle")
    c.footer()
    return c.save()


def figure4():
    c=Canvas(900,"figure4_agent_correction_channels","Agent diversity versus independent stakeholder correction channels")
    c.panel("A","Shared sources can limit diversity",x=30)
    c.panel("B","Independent correction channels",x=680)
    c.line([(650,88),(650,735)],LIGHT,2)
    c.rect(61,108,550,80,fill=PALE,stroke=NAVY)
    c.text(336,122,"Shared model and evaluation rules",27,NAVY,True,"middle")
    c.text(336,155,"Different roles, potentially shared blind spots",25,GRAY,False,"middle")
    for x in [145,336,527]:
        c.arrow([(x,202),(x,272)],NAVY)
    for i,x in enumerate([145,336,527]):
        c.circle(x,333,62,PALE_TEAL,TEAL)
        c.text(x,305,"Agent",27,TEAL,True,"middle")
        c.text(x,342,str(i+1),27,TEAL,True,"middle")
    c.arrow([(214,333),(266,333)],TEAL)
    c.arrow([(405,333),(458,333)],TEAL)
    c.line([(145,404),(145,443),(527,443),(527,404)],TEAL)
    c.arrow([(336,404),(336,492)],TEAL)
    c.rect(108,506,456,94,fill=PALE_TEAL,stroke=TEAL)
    c.text(336,524,"Shared decision",29,TEAL,True,"middle")
    c.text(336,565,"Agreement can conceal common gaps",25,GRAY,False,"middle")
    c.arrow([(108,553),(47,553),(47,221),(95,221),(95,201)],AMBER,dashed=True)
    c.rect(77,639,519,98,fill=PALE_AMBER,stroke=AMBER)
    c.text(337,654,"More agents do not establish",27,AMBER,True,"middle")
    c.text(337,695,"more independent sources of correction.",25,GRAY,False,"middle")

    sources=[(700,TEAL,PALE_TEAL,"Users"),(898,PURPLE,PALE_PURPLE,"Nonusers"),(1096,AMBER,PALE_AMBER,"People\nwho exit")]
    for x,col,fill,label in sources:
        c.rect(x,108,174,99,fill=fill,stroke=col)
        c.text(x+87,124 if "\n" in label else 142,label,27,col,True,"middle",leading=32)
        c.arrow([(x+87,219),(x+87,270)],col)
    c.rect(701,284,568,111,fill=WHITE,stroke=NAVY)
    c.text(985,301,"Consented, auditable evidence",28,NAVY,True,"middle")
    c.text(985,346,"Keep source provenance and uncertainty",25,GRAY,False,"middle")
    c.arrow([(985,409),(985,458)],TEAL)
    c.rect(743,472,484,87,fill=PALE_TEAL,stroke=TEAL)
    c.text(985,486,"Agents organise evidence",28,TEAL,True,"middle")
    c.text(985,521,"Preserve disagreement",25,GRAY,False,"middle")
    c.arrow([(985,573),(985,624)],TEAL)
    c.rect(701,638,568,99,fill=PALE_PURPLE,stroke=PURPLE)
    c.text(985,654,"Participant validation and correction",27,PURPLE,True,"middle")
    c.text(985,695,"Document how feedback changes decisions",25,GRAY,False,"middle")
    c.arrow([(1269,687),(1284,687),(1284,244),(1200,244),(1200,272)],PURPLE,dashed=True)
    c.text(650,782,"Role-play is not stakeholder representation; access to correction must be demonstrated.",25,NAVY,False,"middle")
    c.footer()
    return c.save()


if __name__ == "__main__":
    records=[figure1(),figure2(),figure3(),figure4()]
    (OUT/"figure_manifest.json").write_text(json.dumps({"type":"Conceptual figures; no empirical data", "figures":records},indent=2),encoding="utf-8")
    print(json.dumps(records,indent=2))
