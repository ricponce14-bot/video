"""
CONECTA 2026 – Motion Graphic Ad  (v3 – Professional)
1080×1080 · 30fps · 24s
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio, math, random

W = H = 1080
FPS = 30
DUR = 24
TOTAL = FPS * DUR
CX = CY = W // 2

# ── Palette ───────────────────────────────────────────────────────────────────
BG1   = (4,   8,  42)
BG2   = (8,  18,  68)
BLUE  = (15,  70, 210)
BLUE2 = (0,  110, 240)
CYAN  = (0,  200, 255)
WHITE = (255, 255, 255)
SILV  = (170, 200, 235)
GOLD  = (255, 192,   0)
RED   = (190,  25,  40)
NAVY  = (5,   10,  45)

# ── Math ──────────────────────────────────────────────────────────────────────
def cl(v, lo=0., hi=1.): return max(lo, min(hi, v))
def eo(t, p=3):           return 1 - (1-cl(t))**p
def eio(t):
    t=cl(t); return 4*t**3 if t<.5 else 1-(-2*t+2)**3/2
def lp(a,b,t):            return a + (b-a)*cl(t)
def rc(c,a):              return (*c[:3], int(cl(a)*255))
def ap(sec, s, d=.5):     return eo(cl((sec-s)/d))           # fade appear
def sf(sec, s, d=.5):                                         # scale+fade
    t=eo(cl((sec-s)/d)); return t, lp(.92,1.,t)

# ── Fonts ─────────────────────────────────────────────────────────────────────
F = None
def load_fonts():
    B=["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
       "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    R=["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
       "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    def g(p,s):
        for f in p:
            try: return ImageFont.truetype(f,s)
            except: pass
        return ImageFont.load_default()
    return dict(h1=g(B,114),h2=g(B,80),h3=g(B,58),
                h4=g(B,40), h5=g(B,28),reg=g(R,26),sm=g(R,21))

# ── Background assets (computed once) ─────────────────────────────────────────
GRAD = None   # numpy RGB array (H,W,3)
VIGN = None   # PIL RGBA vignette

def build_grad():
    t  = np.linspace(0,1,H).reshape(H,1,1)
    c1 = np.array(BG1,np.float32).reshape(1,1,3)
    c2 = np.array(BG2,np.float32).reshape(1,1,3)
    return np.broadcast_to(c1*(1-t)+c2*t,(H,W,3)).copy().astype(np.uint8)

def build_vignette():
    y,x = np.mgrid[-H//2:H//2, -W//2:W//2].astype(np.float32)
    d = np.sqrt(x**2+y**2)/(W*.52)
    dark = np.clip(d**2.4,0,1)*170
    v = np.zeros((H,W,4),np.uint8)
    v[:,:,3] = dark.astype(np.uint8)
    return Image.fromarray(v,'RGBA')

# Bokeh orbs — animated gaussian glows
YY,XX = np.mgrid[0:H,0:W].astype(np.float32)
ORBS = [
    (108, 108, 255, (18, 72,200), .20, .22),
    (972, 170, 205, ( 0,125,250), .15, .28),
    (165, 915, 235, (12, 52,175), .17, .18),
    (925, 945, 220, ( 0,108,215), .13, .32),
    (540, 540, 395, ( 4, 22,108), .07, .12),
    (295, 648, 180, ( 0,152,248), .12, .38),
    (798, 412, 172, (10, 78,202), .11, .42),
    (428, 318, 190, ( 0, 92,222), .11, .26),
]
def bokeh_layer(sec):
    layer = np.zeros((H,W,4),np.float32)
    for bx,by,r,col,ba,ds in ORBS:
        cx2 = bx + math.sin(sec*ds)*30
        cy2 = by + math.cos(sec*ds*.75)*22
        sig = r*.42
        m   = np.exp(-((XX-cx2)**2+(YY-cy2)**2)/(2*sig*sig))
        for ch,cv in enumerate(col): layer[:,:,ch] += m*cv*ba
        layer[:,:,3] += m*ba*255
    np.clip(layer[:,:,:3],0,255,out=layer[:,:,:3])
    np.clip(layer[:,:,3],0,255,out=layer[:,:,3])
    return Image.fromarray(layer.astype(np.uint8),'RGBA')

# Particles
random.seed(13); np.random.seed(13)
PARTS = [(random.random()*W, random.random()*H,
          random.uniform(.8,2.4), random.uniform(0,6.28),
          random.uniform(.10,.32)) for _ in range(38)]
def draw_particles(d, sec, ga=1.):
    for i,(x0,y0,spd,ang,a) in enumerate(PARTS):
        px=int((x0+math.cos(ang+sec*.05)*spd*sec*.7)%W)
        py=int((y0+math.sin(ang*.7+sec*.04)*spd*sec*.5)%H)
        fa=a*ga*(0.7+0.3*math.sin(sec*1.4+i))
        d.ellipse([(px-1,py-1),(px+1,py+1)], fill=rc(WHITE,fa))

# Light sweep — diagonal stripe every 8 s
def light_sweep(d, sec):
    t = (sec%8.)/8.
    if t>.16: return
    p   = t/.16
    sx  = int(p*(W+380))-190
    pts = [(sx-55,0),(sx+55,0),(sx+55+H//3,H),(sx-55+H//3,H)]
    d.polygon(pts, fill=rc(WHITE, math.sin(p*math.pi)*.07))

# Flash transitions
FLASHES = [5.,10.,15.,20.]
def flash_overlay(d, sec):
    for ft in FLASHES:
        dt=abs(sec-ft)
        if dt<.20:
            d.rectangle([(0,0),(W,H)], fill=rc(WHITE, eo(1-dt/.20)*.60))

# ── Text helpers ──────────────────────────────────────────────────────────────
def msz(text,font):
    tmp=Image.new('RGBA',(1,1))
    bb=ImageDraw.Draw(tmp).textbbox((0,0),text,font=font)
    return bb[2]-bb[0],bb[3]-bb[1]

def sft(img, cx, cy, text, font, color, alpha, scale=1., shad=True):
    """Scale+fade text, centered at (cx,cy), pasted on RGBA img."""
    if alpha<=0: return
    tw,th = msz(text,font)
    p=38
    tmp=Image.new('RGBA',(tw+p*2,th+p*2),(0,0,0,0))
    td=ImageDraw.Draw(tmp,'RGBA')
    if shad: td.text((p+2,p+4),text,font=font,fill=(0,0,0,int(alpha*175)))
    td.text((p,p),text,font=font,fill=(*color[:3],int(alpha*255)))
    if scale!=1.:
        sw=max(1,int(tmp.width*scale)); sh=max(1,int(tmp.height*scale))
        tmp=tmp.resize((sw,sh),Image.LANCZOS)
    img.paste(tmp,(cx-tmp.width//2, cy-tmp.height//2),tmp)

def dtxt(d, cx, cy, text, font, color, alpha, slide=0, shad=False):
    """Simple centered text via draw (fast, for small labels)."""
    tw,th=msz(text,font)
    x=cx-tw//2; y=cy-th//2+slide
    if shad: d.text((x+2,y+3),text,font=font,fill=rc((0,0,0),alpha*.5))
    d.text((x,y),text,font=font,fill=rc(color,alpha))

# ── Drawing primitives ────────────────────────────────────────────────────────
def hbar(d, cx, y, frac, col, a, h=2):
    hw=int(frac*460)
    d.rectangle([(cx-hw,y),(cx+hw,y+h)],fill=rc(col,a))

def ring(d, cx, cy, r, col, a, w=2):
    if r>1: d.ellipse([(cx-r,cy-r),(cx+r,cy+r)],outline=rc(col,a),width=w)

def glow_circ(d, cx, cy, r, col, a, layers=6):
    for i in range(layers,0,-1):
        d.ellipse([(cx-r-i*8,cy-r-i*8),(cx+r+i*8,cy+r+i*8)],
                  fill=rc(col,a*.06/i))
    d.ellipse([(cx-r,cy-r),(cx+r,cy+r)],fill=rc(col,a))

def pill(d, cx, cy, bw, bh, fc, fa, bc=None, ba=0):
    x,y=cx-bw//2,cy-bh//2
    d.rounded_rectangle([(x,y),(x+bw,y+bh)],radius=bh//2,fill=rc(fc,fa))
    if bc: d.rounded_rectangle([(x,y),(x+bw,y+bh)],radius=bh//2,
                                outline=rc(bc,ba),width=2)

def card(d, cx, cy, bw, bh, fc, fa, bc=None, ba=0, rad=20):
    x,y=cx-bw//2,cy-bh//2
    d.rounded_rectangle([(x+5,y+7),(x+bw+5,y+bh+7)],
                         radius=rad,fill=rc((0,0,0),fa*.35))
    d.rounded_rectangle([(x,y),(x+bw,y+bh)],radius=rad,fill=rc(fc,fa))
    if bc: d.rounded_rectangle([(x,y),(x+bw,y+bh)],radius=rad,
                                outline=rc(bc,ba),width=2)

def badge(d, cx, cy, text, font, tc, ta, fc, fa, bc=None, ba=0):
    tw,th=msz(text,font)
    bw=tw+60; bh=th+24
    card(d,cx,cy,bw,bh,fc,fa,bc,ba,rad=bh//2)
    dtxt(d,cx,cy,text,font,tc,ta)

# ── BG layer (used by every scene) ────────────────────────────────────────────
def draw_bg(ov, d, sec):
    bk = bokeh_layer(sec)
    ov.paste(bk,(0,0),bk)
    draw_particles(d,sec)
    light_sweep(d,sec)

# ══════════════════════════════════════════════════════════════════════════════
#  SCENE 1  ·  0–5 s  ·  Brand Opener
# ══════════════════════════════════════════════════════════════════════════════
def s1(ov,d,sec,a):
    draw_bg(ov,d,sec)
    # Center orb pulse
    orb=ap(sec,.2,.8)
    if orb>0: glow_circ(d,CX,CY,int(20*orb),CYAN,orb*.85*a,8)

    # CONECTA – scale+fade
    al,sc=sf(sec,.4,.8)
    if al>0: sft(ov,CX,470,"CONECTA",F['h1'],WHITE,al*a,sc)

    # Underline grows
    t2=ap(sec,.95,.6)
    if t2>0: hbar(d,CX,530,t2,CYAN,t2*a*.9)

    # Expo tag
    t3=ap(sec,1.15,.6)
    if t3>0: dtxt(d,CX,558,"2DA EXPO-CONFERENCIA  ·  2026",F['h5'],CYAN,t3*a)

    # City
    t4=ap(sec,1.55,.6)
    if t4>0: dtxt(d,CX,610,"Tepatitlan, Jalisco",F['reg'],SILV,t4*a*.75)

    # Subtle ring around logo area
    t5=ap(sec,.8,.8)
    if t5>0:
        for ri,ra in [(200,.15),(260,.08)]:
            ring(d,CX,CY,int(ri*t5),CYAN,t5*a*.12)

    # COONEXPO footer
    t6=ap(sec,2.0,.6)
    if t6>0: dtxt(d,CX,740,"COONEXPO",F['sm'],SILV,t6*a*.4)


# ══════════════════════════════════════════════════════════════════════════════
#  SCENE 2  ·  5–10 s  ·  Hook
# ══════════════════════════════════════════════════════════════════════════════
def s2(ov,d,sec,a):
    s=sec-5.; draw_bg(ov,d,sec)

    # eyebrow
    t0=ap(s,.0,.45)
    if t0>0:
        sl=int(lp(22,0,t0))
        dtxt(d,CX,140,"SE PARTE DE",F['h5'],CYAN,t0*a,sl)

    # Main 3-line hook
    lines=[("LA EXPO MAS",WHITE,.3),
           ("IMPORTANTE", WHITE,.65),
           ("DE LOS ALTOS",GOLD,1.0)]
    for text,col,start in lines:
        al,sc=sf(s,start,.65)
        if al>0: sft(ov,CX,248+lines.index((text,col,start))*107,
                     text,F['h2'],col,al*a,sc)

    # Divider
    t3=ap(s,1.75,.5)
    if t3>0: hbar(d,CX,548,t3,CYAN,t3*a*.55)

    # Stats trio
    stats=[("50+","Expositores"),("500+","Asistentes"),("3","Dias")]
    for i,(num,lbl) in enumerate(stats):
        ti=ap(s,2.0+i*.2,.55)
        if ti>0:
            bx=185+i*270; sl=int(lp(18,0,ti))
            dtxt(d,bx,590,num,F['h3'],CYAN,ti*a,sl)
            dtxt(d,bx,658,lbl,F['sm'],SILV,ti*a*.7,sl)

    # Date pill
    t6=ap(s,2.8,.55)
    if t6>0:
        sl=int(lp(20,0,t6))
        pill(d,CX,800-sl,490,62,BLUE,t6*a*.88,CYAN,t6*a*.6)
        dtxt(d,CX,800-sl,"ABRIL  18 · 19 · 20",F['h4'],WHITE,t6*a)


# ══════════════════════════════════════════════════════════════════════════════
#  SCENE 3  ·  10–15 s  ·  Expositor
# ══════════════════════════════════════════════════════════════════════════════
def s3(ov,d,sec,a):
    s=sec-10.; draw_bg(ov,d,sec)

    t0=ap(s,.0,.45)
    if t0>0: dtxt(d,CX,115,"UNETE COMO",F['h5'],CYAN,t0*a,int(lp(20,0,t0)))

    al,sc=sf(s,.3,.75)
    if al>0: sft(ov,CX,225,"EXPOSITOR",F['h1'],WHITE,al*a,sc)

    t2=ap(s,1.0,.5)
    if t2>0: hbar(d,CX,325,t2,CYAN,t2*a*.8)

    t3=ap(s,1.15,.55)
    if t3>0:
        dtxt(d,CX,355,"en la expo mas importante de Los Altos",
             F['reg'],SILV,t3*a*.85)

    # Benefits — centered with bullet
    bens=["Visibilidad ante cientos de empresarios",
          "Networking con lideres del sector",
          "Posiciona tu marca en Los Altos",
          "Genera clientes y alianzas de negocio"]
    for i,b in enumerate(bens):
        ti=ap(s,1.5+i*.3,.5)
        if ti>0:
            sl=int(lp(25,0,ti)); by=408+i*72
            full="·  "+b
            dtxt(d,CX,by,full,F['reg'],WHITE,ti*a,sl,shad=True)

    t7=ap(s,3.1,.55)
    if t7>0:
        pill(d,CX,790,430,56,BLUE,t7*a*.7,CYAN,t7*a*.5)
        dtxt(d,CX,790,"ABRIL 18 · 19 · 20",F['h5'],WHITE,t7*a)


# ══════════════════════════════════════════════════════════════════════════════
#  SCENE 4  ·  15–20 s  ·  Precio
# ══════════════════════════════════════════════════════════════════════════════
def s4(ov,d,sec,a):
    s=sec-15.; draw_bg(ov,d,sec)

    t0=ap(s,.0,.5)
    if t0>0: dtxt(d,CX,100,"STAND DESDE",F['h4'],WHITE,t0*a,int(lp(20,0,t0)))

    # Price card + counter
    tc=ap(s,.3,1.3)
    if tc>0:
        val=int(eo(cl((s-.3)/1.1))*5900)
        price="$"+f"{val:,}"
        # card bg
        card(d,CX,340,730,200,BLUE,tc*a*.82,CYAN,tc*a*.5,rad=22)
        # price number centered in card
        pw,ph=msz(price,F['h1'])
        # shadow
        d.text((CX-pw//2+3,253),price,font=F['h1'],fill=rc((0,0,0),tc*a*.3))
        d.text((CX-pw//2,250),price,font=F['h1'],fill=rc(GOLD,tc*a))
        d.text((CX-pw//2+pw+12,295),"pesos",font=F['reg'],fill=rc(WHITE,tc*a*.65))

    # Divider + includes
    t2=ap(s,1.5,.5)
    if t2>0:
        hbar(d,CX,452,t2,CYAN,t2*a*.6)
        dtxt(d,CX,470,"Espacio personalizado  ·  Rotulos de tu marca",
             F['reg'],SILV,t2*a*.85)

    incs=["·  Exposicion los 3 dias del evento",
          "·  Acceso a todas las conferencias"]
    for i,item in enumerate(incs):
        ti=ap(s,1.9+i*.25,.5)
        if ti>0:
            dtxt(d,CX,518+i*50,item,F['sm'],WHITE,ti*a*.9,int(lp(15,0,ti)))

    # Scarcity
    t5=ap(s,2.9,.55)
    if t5>0:
        sl=int(lp(18,0,t5))
        card(d,CX,683-sl,570,64,RED,t5*a*.9,rad=32)
        dtxt(d,CX,683-sl,"SOLO 50 STANDS DISPONIBLES",F['h5'],WHITE,t5*a)

    t6=ap(s,3.25,.5)
    if t6>0:
        dtxt(d,CX,765,"Apartalo antes de que se agote",
             F['sm'],SILV,t6*a*.65)


# ══════════════════════════════════════════════════════════════════════════════
#  SCENE 5  ·  20–24 s  ·  Pago + CTA
# ══════════════════════════════════════════════════════════════════════════════
def s5(ov,d,sec,a):
    s=sec-20.; draw_bg(ov,d,sec)

    t0=ap(s,.0,.5)
    if t0>0: dtxt(d,CX,88,"OPCIONES DE PAGO",F['h4'],WHITE,t0*a,int(lp(18,0,t0)))

    # Card 1 – reserva
    t1=ap(s,.4,.7)
    if t1>0:
        sl=int(lp(35,0,t1))
        card(d,CX,270-sl,700,185,BLUE,t1*a*.88,CYAN,t1*a*.55,rad=18)
        dtxt(d,CX,187-sl,"RESERVA TU STAND",F['h5'],CYAN,t1*a)
        dtxt(d,CX,215-sl,"con solo",F['reg'],SILV,t1*a*.7)
        # $1,000 scale+fade
        al2,sc2=sf(s,.55,.6)
        if al2>0: sft(ov,CX,305-sl,"$1,000",F['h2'],GOLD,al2*a,sc2)
        dtxt(d,CX,348-sl,"y aparta tu lugar hoy",F['sm'],SILV,t1*a*.65)

    # "o" divider
    t2=ap(s,1.15,.45)
    if t2>0:
        hw=int(t2*130)
        d.rectangle([(CX-hw-52,390),(CX-52,392)],fill=rc(SILV,t2*a*.22))
        d.rectangle([(CX+52,390),(CX+52+hw,392)],fill=rc(SILV,t2*a*.22))
        dtxt(d,CX,374,"o",F['h4'],SILV,t2*a*.38)

    # Card 2 – meses
    t3=ap(s,1.6,.7)
    if t3>0:
        sl=int(lp(35,0,t3))
        card(d,CX,575+sl,700,188,(12,30,85),t3*a*.92,SILV,t3*a*.35,rad=18)
        dtxt(d,CX,494+sl,"PAGA EL TOTAL",F['h5'],SILV,t3*a*.85)
        al3,sc3=sf(s,1.75,.6)
        if al3>0: sft(ov,CX,555+sl,"A MESES",F['h2'],WHITE,al3*a,sc3)
        dtxt(d,CX,638+sl,"SIN INTERESES",F['h3'],CYAN,t3*a)

    # CTA
    t4=ap(s,2.9,.6)
    if t4>0:
        pulse=1+.025*math.sin(sec*5)
        pill(d,CX,842,int(660*pulse),int(76*pulse),CYAN,t4*a)
        dtxt(d,CX,842,"RESERVA TU ESPACIO AHORA",F['h4'],NAVY,t4*a)

    # footer
    t5=ap(s,3.2,.5)
    if t5>0:
        dtxt(d,CX,920,"CONECTA  ·  COONEXPO  ·  2DA EXPO-CONFERENCIA 2026",
             F['sm'],SILV,t5*a*.45)


# ── Schedule ──────────────────────────────────────────────────────────────────
SCHED=[( 0.0, 5.3,s1),
       ( 4.8,10.3,s2),
       ( 9.8,15.3,s3),
       (14.8,20.3,s4),
       (19.8,24.2,s5)]
FADE=.40

def s_alpha(sec,s,e):
    if sec<s or sec>e: return 0.
    t=sec-s; dur=e-s
    if t<FADE:     return eio(t/FADE)
    if t>dur-FADE: return eio((e-sec)/FADE)
    return 1.


# ── Frame ─────────────────────────────────────────────────────────────────────
def make_frame(fn):
    sec=fn/FPS

    # Base gradient
    base=Image.fromarray(GRAD).convert('RGBA')

    # Overlay
    ov  = Image.new('RGBA',(W,H),(0,0,0,0))
    d   = ImageDraw.Draw(ov,'RGBA')

    for s_s,s_e,fn_s in SCHED:
        a=s_alpha(sec,s_s,s_e)
        if a>0: fn_s(ov,d,sec,a)

    flash_overlay(d,sec)

    # Composite: base → bokeh already embedded by scenes → vignette → final
    img=Image.alpha_composite(base,ov)
    img=Image.alpha_composite(img, VIGN)

    return np.array(img.convert('RGB'),dtype=np.uint8)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    global F,GRAD,VIGN
    print("Cargando recursos...")
    F    = load_fonts()
    GRAD = build_grad()
    VIGN = build_vignette()

    out="conecta_2026_ad.mp4"
    print(f"Generando {TOTAL} frames  ({W}x{H} · {FPS}fps · {DUR}s)...")
    w=imageio.get_writer(out,fps=FPS,codec='libx264',quality=9,
                         macro_block_size=1,
                         output_params=['-pix_fmt','yuv420p','-preset','fast'])
    for i in range(TOTAL):
        if i%(FPS*4)==0: print(f"  {i*100//TOTAL:3d}%")
        w.append_data(make_frame(i))
    w.close()
    print(f"\nListo  →  {out}")

if __name__=="__main__":
    main()
