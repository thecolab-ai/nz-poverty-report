#!/usr/bin/env python3
"""Render the ultra-deep NZ poverty report (poverty.json + poverty_baseline.json)
to a branded PDF. uv run --with weasyprint --with matplotlib python render_poverty.py
"""
from __future__ import annotations
import base64, datetime, html, json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__)); FONTS = os.path.join(HERE, "fonts")
OUT = os.path.join(HERE, "out"); CH = os.path.join(HERE, "charts")
os.makedirs(OUT, exist_ok=True); os.makedirs(CH, exist_ok=True)
NAVY="#1C1917"; INDIGO="#2E4057"; CYAN="#0EA5E9"; CYAN_DK="#0284C7"; ORANGE="#C2410C"
CREAM="#FBF9F6"; STONE="#44403C"; MUTED="#78716C"; BORDER="#E7E2DA"
TODAY = datetime.date(2026, 5, 31).strftime("%-d %B 2026"); ACC=[INDIGO,CYAN_DK,ORANGE]
for f in ["Inter-Regular.ttf","Inter-Medium.ttf","Inter-Bold.ttf"]:
    p=os.path.join(FONTS,f)
    if os.path.exists(p): font_manager.fontManager.addfont(p)
plt.rcParams.update({"font.family":["Inter","DejaVu Sans"],"font.size":11,"text.color":STONE,"axes.edgecolor":BORDER,
    "axes.labelcolor":STONE,"xtick.color":MUTED,"ytick.color":MUTED,"figure.facecolor":"white","axes.facecolor":"white"})

DATA = json.load(open(os.path.join(HERE,"poverty.json")))
SYN=DATA["synthesis"]; DRIVERS=DATA["drivers"]; SOLUTIONS=DATA["solutions"]
BASE = json.load(open(os.path.join(HERE,"poverty_baseline.json")))

def esc(s): return html.escape(str(s or ""))
def paras(t): return "".join(f"<p>{esc(p.strip())}</p>" for p in str(t or "").split("\n") if p.strip())
def b64(p):
    with open(p,"rb") as fh: return "data:image/png;base64,"+base64.b64encode(fh.read()).decode()
def img(p,style=""): return f'<img style="{style}" src="{b64(p)}"/>' if p else ""
def axes(ax):
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.yaxis.grid(True,color=BORDER,linewidth=0.8); ax.set_axisbelow(True)
def save(fig,n):
    p=os.path.join(CH,n); fig.savefig(p,dpi=150,bbox_inches="tight",facecolor="white"); plt.close(fig); return p

def chart_baseline():
    m=BASE["measures"]
    order=[("MEASA","BHC<50%\n(primary)"),("MEASB","AHC<50%\n(anchored)"),("MEASF","AHC<60%"),
           ("MEASC","Material\nhardship"),("MEASI","Severe\nhardship")]
    labels=[l for _,l in order]; vals=[m[c]["pct"] for c,_ in order]
    cols=[INDIGO,INDIGO,INDIGO,ORANGE,ORANGE]
    fig,ax=plt.subplots(figsize=(6.6,3.1)); bars=ax.bar(labels,vals,color=cols,width=0.6)
    for b,v,c in zip(bars,vals,[c for c,_ in order]):
        ax.text(b.get_x()+b.get_width()/2,v+0.3,f"{v}%\n{m[c]['n']:.0f}k",ha="center",fontsize=8.5,color=NAVY,fontweight="bold")
    ax.set_ylim(0,max(vals)+5); axes(ax); ax.set_ylabel("% of children"); ax.tick_params(axis="x",labelsize=8.5)
    return save(fig,"pov_baseline.png")

def chart_ethnicity():
    d=BASE["hardship_by_ethnicity"]
    keys=["European","Asian","All ethnicities","Māori","Other ethnicity","Pacific peoples"]
    keys=[k for k in keys if k in d]; vals=[d[k] for k in keys]
    short={"All ethnicities":"All children","Pacific peoples":"Pacific","Other ethnicity":"Other","Middle Eastern/Latin American/African":"MELAA"}
    labels=[short.get(k,k) for k in keys]
    cols=[ORANGE if "Pacific" in k or k=="Māori" else (NAVY if k=="All ethnicities" else INDIGO) for k in keys]
    fig,ax=plt.subplots(figsize=(6.6,3.0)); bars=ax.bar(labels,vals,color=cols,width=0.62)
    for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+0.4,f"{v}%",ha="center",fontsize=9,color=NAVY,fontweight="bold")
    ax.set_ylim(0,max(vals)+5); axes(ax); ax.set_ylabel("Children in material hardship (%)")
    return save(fig,"pov_ethnicity.png")

import re as _re
def short_lever(t):
    s=_re.split(r"\s*[—:(]\s*", str(t), 1)[0].strip()
    return (s[:34]+"…") if len(s)>35 else s

def chart_leverage():
    items=sorted([(short_lever(s.get("lever","?")), s.get("leverage")) for s in SOLUTIONS if s.get("leverage") is not None], key=lambda x:x[1])
    if not items: return None
    labels=[l for l,_ in items]; vals=[v for _,v in items]
    cols=["#16A34A" if v>=8 else "#CA8A04" if v>=6 else MUTED for v in vals]
    fig,ax=plt.subplots(figsize=(7.0,3.4)); ax.barh(labels,vals,color=cols,height=0.6)
    for i,v in enumerate(vals): ax.text(v+0.1,i,f"{v:g}/10",va="center",fontsize=8.5,color=NAVY)
    ax.set_xlim(0,10.5); ax.set_xlabel("Leverage — impact per effort on the poverty baseline (0–10)")
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.xaxis.grid(True,color=BORDER,linewidth=0.8); ax.set_axisbelow(True)
    return save(fig,"pov_leverage.png")

def chart_confidence():
    items=[(c["title"],(c.get("verdict") or {}).get("confidence"),(c.get("verdict") or {}).get("logic_ok")) for c in DRIVERS]
    items=[(t,c,lo) for t,c,lo in items if c is not None]; items.sort(key=lambda x:x[1])
    labels=[t for t,_,_ in items]; vals=[c for _,c,_ in items]
    cols=["#16A34A" if v>=8 else "#CA8A04" if v>=6 else ORANGE for v in vals]
    fig,ax=plt.subplots(figsize=(7.0,3.0)); ax.barh(labels,vals,color=cols,height=0.6)
    for i,(v,lo) in enumerate(zip(vals,[x[2] for x in items])):
        ax.text(v+0.1,i,f"{v}/10"+("" if lo else "  ⚠ logic"),va="center",fontsize=8.5,color=NAVY)
    ax.set_xlim(0,11); ax.set_xlabel("Fact + logic-check confidence (0–10)")
    for s in ("top","right"): ax.spines[s].set_visible(False)
    ax.xaxis.grid(True,color=BORDER,linewidth=0.8); ax.set_axisbelow(True)
    return save(fig,"pov_conf.png")

CHARTS={"baseline":chart_baseline(),"ethnicity":chart_ethnicity(),"leverage":chart_leverage(),"conf":chart_confidence()}

def ff(n,f,w): return f"@font-face{{font-family:'{n}';src:url('file://{FONTS}/{f}') format('truetype');font-weight:{w};font-style:normal;}}"
CSS=("".join([ff("Inter","Inter-Regular.ttf",400),ff("Inter","Inter-Medium.ttf",500),ff("Inter","Inter-Bold.ttf",700),ff("Playfair Display","PlayfairDisplay-Bold.ttf",700)])+"""
@page { size:A4; margin:16mm 15mm 18mm 15mm;
  @bottom-center{content:"thecolab.ai  ·  The Baseline Challenge  ·  Poverty in Aotearoa"; font-family:'Inter'; font-size:7.5pt; color:#a8a29e;}
  @bottom-right{content:counter(page); font-family:'Inter'; font-size:8pt; color:#a8a29e;} }
@page cover { margin:0; @bottom-center{content:none} @bottom-right{content:none} }
*{box-sizing:border-box;} body{font-family:'Inter','Helvetica Neue',Arial,sans-serif;color:%STONE%;font-size:10.2pt;line-height:1.5;margin:0;}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;color:%NAVY%;letter-spacing:-0.01em;margin:0 0 6px;}
h2{font-size:18pt;margin-top:6px;} h3{font-size:12.5pt;}
p{margin:0 0 8px;} .muted{color:%MUTED%;font-size:9.5pt;}
.accent-bar{height:4px;width:64px;border-radius:2px;background:linear-gradient(90deg,%INDIGO%,%CYAN%);margin:2px 0 12px;}
.cover{page:cover;height:297mm;background:%NAVY%;color:#FBF9F6;position:relative;overflow:hidden;padding:34mm 22mm;}
.cover .blob{position:absolute;border-radius:50%;opacity:0.2;} .wm{font-family:'Playfair Display';font-size:22pt;} .wm .ai{color:%CYAN%;}
.kicker{margin-top:30mm;font-size:10pt;letter-spacing:0.14em;text-transform:uppercase;color:%CYAN%;}
.cover h1{color:#FBF9F6;font-size:40pt;line-height:1.05;margin-top:6px;} .cover .grad{color:%CYAN%;}
.cover .sub{font-size:13pt;color:#d6d3cf;margin-top:14px;max-width:140mm;}
.cover .meta{position:absolute;bottom:26mm;left:22mm;right:22mm;font-size:10pt;color:#a8a29e;border-top:1px solid #44403c;padding-top:10px;display:flex;justify-content:space-between;}
.section{padding:6px 0 4px;} .break{break-before:page;}
.exec{background:linear-gradient(160deg,rgba(46,64,87,0.05),rgba(14,165,233,0.05));border:1px solid %BORDER%;border-radius:12px;padding:14px 18px;}
.exec ul{margin:6px 0 0;padding-left:18px;} .exec li{margin:5px 0;}
.tiles{display:flex;flex-wrap:wrap;gap:7px;margin:8px 0;} .tile{flex:1 1 30%;border:1px solid %BORDER%;border-radius:9px;padding:8px 10px;background:white;}
.tile-val{font-size:15pt;font-weight:700;} .tile-lbl{font-size:7.8pt;color:%MUTED%;text-transform:uppercase;letter-spacing:0.03em;margin-top:1px;} .tile-src{font-size:7pt;color:#a8a29e;margin-top:2px;}
.chapter{page-break-inside:avoid;margin-bottom:6px;} .chap-head{display:flex;justify-content:space-between;align-items:baseline;}
.badge{display:inline-block;font-size:7.6pt;font-weight:600;color:white;border-radius:999px;padding:1px 8px;}
.headline{font-size:11.5pt;color:%NAVY%;font-weight:600;margin:2px 0 6px;}
.callout{background:%CREAM%;border-left:3px solid %ORANGE%;padding:7px 12px;border-radius:6px;margin:6px 0;font-size:9.6pt;}
.callout b{color:%ORANGE%;}
.rank{border-left:3px solid %CYAN%;padding:4px 12px;margin:7px 0;} .rank b{color:%NAVY%;}
.lev{border:1px solid %BORDER%;border-radius:11px;background:white;padding:11px 14px;margin:8px 0;page-break-inside:avoid;}
.lev .h{display:flex;justify-content:space-between;align-items:baseline;} .lev h3{margin:0;}
.lev .score{font-size:9pt;color:white;background:%INDIGO%;border-radius:999px;padding:1px 9px;font-weight:600;}
.lev .row{font-size:9.4pt;margin:3px 0;} .lev .row b{color:%NAVY%;}
.toc{border-left:3px solid %INDIGO%;background:linear-gradient(90deg,rgba(46,64,87,0.06),rgba(14,165,233,0.04));padding:9px 14px;border-radius:8px;margin:8px 0;}
.toc .m{font-family:'Playfair Display';color:%NAVY%;font-size:12pt;}
.src{font-size:7.6pt;color:%MUTED%;margin-top:4px;}
""")
for k,v in {"%NAVY%":NAVY,"%INDIGO%":INDIGO,"%CYAN%":CYAN,"%STONE%":STONE,"%MUTED%":MUTED,"%BORDER%":BORDER,"%CREAM%":CREAM,"%ORANGE%":ORANGE}.items():
    CSS=CSS.replace(k,v)

def tiles(stats,accent):
    return "<div class='tiles'>"+"".join(f"<div class='tile'><div class='tile-val' style='color:{accent}'>{esc(s['value'])}</div><div class='tile-lbl'>{esc(s['label'])}</div><div class='tile-src'>{esc(s.get('source',''))}</div></div>" for s in stats[:9])+"</div>"

def chapter(c,i):
    f=c["findings"]; accent=ACC[i%len(ACC)]; v=c.get("verdict") or {}
    conf=v.get("confidence"); logic=v.get("logic_ok")
    badges=f"<span class='badge' style='background:{accent}'>{esc(c['title'])}</span>"
    meta=[]
    if conf is not None: meta.append(f"confidence {conf}/10")
    if logic is False: meta.append("⚠ logic flag")
    return f"""<section class="section chapter"><div class="chap-head"><h2>{esc(c['title'])}</h2><span class="muted">{' · '.join(meta)}</span></div>
      <div class="accent-bar" style="background:linear-gradient(90deg,{accent},{CYAN})"></div>
      <div class="headline">{esc(f['headline'])}</div>{tiles(f['key_stats'],accent)}
      <div class="callout"><b>Who bears it.</b> {esc(f['incidence'])}</div>
      {paras(f['narrative'])}<p class="muted"><b>Why it drives poverty:</b> {esc(f['contribution'])}</p>
      <div class="src"><b>Sources:</b> {esc('; '.join(f.get('sources',[])))}</div></section>"""

def lever(s):
    sc=s.get("leverage")
    return f"""<div class="lev"><div class="h"><h3>{esc(short_lever(s['lever']))}</h3>{f'<span class="score">leverage {sc}/10</span>' if sc is not None else ''}</div>
      <div class="row"><b>How it works:</b> {esc(s['mechanism'])}</div>
      <div class="row"><b>Evidence:</b> {esc(s['evidence'])}</div>
      <div class="row"><b>Estimated impact:</b> {esc(s['est_impact'])}</div>
      {f'<div class="row"><b>Cost:</b> {esc(s.get("cost"))}</div>' if s.get('cost') else ''}
      <div class="row"><b>Trade-offs:</b> {esc(s['tradeoffs'])}</div>
      {f'<div class="row"><b>Who benefits:</b> {esc(s.get("who_benefits"))}</div>' if s.get('who_benefits') else ''}</div>"""

def cover_title():
    t=SYN.get("title","The Baseline Challenge")
    for sep in ("—"," - ",": "):
        if sep in t:
            a,b=t.split(sep,1); return f"{esc(a.strip())}<br><span class='grad'>{esc(b.strip())}</span>"
    return esc(t)

def build():
    cover=f"""<section class="cover"><div class="blob" style="width:340px;height:340px;background:{INDIGO};top:-60px;left:-40px;"></div>
      <div class="blob" style="width:300px;height:300px;background:{CYAN};bottom:40px;right:-30px;"></div>
      <div class="wm">thecolab<span class="ai">.ai</span></div><div class="kicker">An ultra-deep data report</div>
      <h1>{cover_title()}</h1><div class="sub">{esc(SYN.get('subtitle',''))}</div>
      <div class="meta"><span>Poverty as the baseline challenge · {TODAY}</span><span>AI expertise, built together</span></div></section>"""
    summ="<section class='section'><h2>Executive summary</h2><div class='accent-bar'></div><div class='exec'><ul>"+ \
        "".join(f"<li>{esc(b)}</li>" for b in SYN.get("executive_summary",[]))+"</ul></div>"+paras(SYN.get("verdict",""))+"</section>"
    baseline=("<section class='section break'><h2>The baseline: poverty in Aotearoa today</h2><div class='accent-bar'></div>"
        +paras(SYN.get("baseline",""))
        +f"<h3>The official measures</h3>{img(CHARTS['baseline'],'width:100%;max-width:165mm')}"
        +"<p class='muted'>The Child Poverty Reduction Act measures for the year ended June 2025 (Stats NZ). Material hardship counts children going without 6+ of 17 essentials; severe hardship 9+.</p>"
        +f"<h3 style='margin-top:8px'>Hardship is not shared evenly</h3>{img(CHARTS['ethnicity'],'width:100%;max-width:165mm')}"
        +"<p class='muted'>Children in material hardship by ethnicity (Stats NZ). Pacific and Māori children are two to three times more likely to be in hardship than the national average.</p></section>")
    ranked="<section class='section'><h2>The drivers, ranked</h2><div class='accent-bar'></div>"+ \
        "".join(f"<div class='rank'><b>{i+1}. {esc(r['driver'])}.</b> {esc(r['why'])}</div>" for i,r in enumerate(SYN.get("ranked_drivers",[])))+"</section>"
    chapters="<section class='section break'><h2>The drivers in depth</h2><div class='accent-bar'></div></section>"+ \
        "".join(chapter(c,i) for i,c in enumerate(DRIVERS))
    levchart=f"<section class='section break'><h2>What works — ranked by leverage</h2><div class='accent-bar'></div>{img(CHARTS['leverage'],'width:100%;max-width:170mm') if CHARTS['leverage'] else ''}<p class='muted'>Each lever rated for impact per effort on the poverty baseline — the evidence-led case for where to act first.</p>"
    levers="".join(lever(s) for s in sorted(SOLUTIONS,key=lambda s:-(s.get("leverage") or 0)))+"</section>"
    toc_moves="<section class='section break'><h2>The path: a theory of change</h2><div class='accent-bar'></div>"+ \
        "".join(f"<div class='toc'><div class='m'>{i+1}. {esc(t['move'])}</div><p style='margin:4px 0 2px'>{esc(t['rationale'])}</p><p class='muted'><b>Expected impact:</b> {esc(t['impact'])}</p></div>" for i,t in enumerate(SYN.get("theory_of_change",[])))
    if SYN.get("targets_note"): toc_moves+=f"<div class='callout'><b>Against the targets.</b> {esc(SYN['targets_note'])}</div>"
    if SYN.get("tensions"): toc_moves+="<h3>Tensions &amp; trade-offs</h3><ul>"+"".join(f"<li>{esc(x)}</li>" for x in SYN['tensions'])+"</ul>"
    toc_moves+="</section>"
    conf=(f"<section class='section break'><h2>How confident are these figures?</h2><div class='accent-bar'></div>"
        "<p>Each driver chapter was independently fact-checked AND run through internal-consistency logic checks "
        "(a subset can't exceed its total; after-housing-cost poverty can't fall below before-housing-cost). Lower bars "
        "or a logic flag mark where the data is thinner or needed care.</p>"
        f"{img(CHARTS['conf'],'width:100%;max-width:170mm')}</section>")
    method=("<div class='src' style='border-top:1px solid "+BORDER+";margin-top:12px;padding-top:8px'><b>Method.</b> Built by a "
        "multi-agent research process drawing live data from New Zealand public sources — the Stats NZ Child Poverty "
        "Reduction Act measures, household material hardship, the NZ Index of Deprivation, MSD benefit statistics, HUD "
        "public-housing data, and the Reserve Bank and Treasury — enriched with public web research and the published "
        "evidence base, with every chapter independently fact- and logic-checked. Point-in-time as at "+TODAY+"; "
        "indicative analysis, not advice. Built by thecolab.ai.</div>")
    return ("<!DOCTYPE html><html><head><meta charset='utf-8'><style>"+CSS+"</style></head><body>"+cover+
        "<div style='padding:0 2mm'>"+summ+baseline+ranked+chapters+levchart+levers+toc_moves+conf+method+"</div></body></html>")

if __name__=="__main__":
    from weasyprint import HTML
    out=os.path.join(OUT,"thecolab-poverty-baseline-challenge-nz.pdf")
    HTML(string=build()).write_pdf(out); print("wrote",out)
