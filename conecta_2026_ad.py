"""
CONECTA 2026 – Motion Graphic Ad  (v2 – Clean & Modern)
Format : 1080x1080 (1:1)  |  30 fps  |  24 s
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio, math

# ── Config ────────────────────────────────────────────────────────────────────
W = H = 1080
FPS   = 30
DUR   = 24
TOTAL = FPS * DUR

# ── Palette ───────────────────────────────────────────────────────────────────
BG1   = (6,  12, 48)      # top
BG2   = (10, 22, 75)      # bottom
BLUE  = (20, 80, 200)
CYAN  = (0,  200, 255)
WHITE = (255, 255, 255)
SILVER= (180, 205, 235)
GOLD  = (255, 195,  0)
RED   = (185,  28,  42)
NAVY  = (8,   16,  52)

# ── Utils ─────────────────────────────────────────────────────────────────────
def cl(v, lo=0., hi=1.): return max(lo, min(hi, v))
def eo(t, p=3): return 1-(1-cl(t))**p          # ease-out
def eio(t):                                      # ease-in-out
    t=cl(t); return 4*t**3 if t<.5 else 1-(-2*t+2)**3/2
def lp(a,b,t): return a+(b-a)*cl(t)
def ap(sec,s,d=.55): return eo(cl((sec-s)/d))   # appear(sec, start, dur)
def rc(c,a): return (*c[:3], int(cl(a)*255))     # rgba

# ── Gradient ──────────────────────────────────────────────────────────────────
def make_bg():
    t  = np.linspace(0,1,H).reshape(H,1,1)
    c1 = np.array(BG1,np.float32).reshape(1,1,3)
    c2 = np.array(BG2,np.float32).reshape(1,1,3)
    return Image.fromarray(
        np.broadcast_to(c1*(1-t)+c2*t,(H,W,3)).copy().astype(np.uint8)
    ).convert('RGBA')

BG_IMG = None   # cached, built once

# ── Fonts ─────────────────────────────────────────────────────────────────────
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
    return dict(h1=g(B,108),h2=g(B,80),h3=g(B,58),
                h4=g(B,40), h5=g(B,30),reg=g(R,26),sm=g(R,22))
F=None

# ── Text ──────────────────────────────────────────────────────────────────────
def tw(d,t,f):
    b=d.textbbox((0,0),t,font=f); return b[2]-b[0],b[3]-b[1]

def txt(d, cx, y, text, font, color, alpha, slide=0, shadow=True):
    """Draw centered text.  slide: vertical offset (positive = lower)."""
    w,h = tw(d, text, font)
    x   = cx - w//2
    yy  = y + int(slide)
    if shadow:
        d.text((x+2, yy+3), text, font=font, fill=rc((0,0,0), alpha*0.5))
    d.text((x, yy), text, font=font, fill=rc(color, alpha))
    return w, h

def fade_in(sec, start, dur=0.55, slide_px=28):
    """Returns (alpha, slide) for a clean fade+rise animation."""
    t = ap(sec, start, dur)
    return t, int(lp(slide_px, 0, t))

# ── Primitives ────────────────────────────────────────────────────────────────
def hbar(d, cx, y, frac, col, a, h=2):
    hw=int(frac*480)
    d.rectangle([(cx-hw,y),(cx+hw,y+h)], fill=rc(col,a))

def ring(d, cx, cy, r, col, a, w=1):
    if r>1: d.ellipse([(cx-r,cy-r),(cx+r,cy+r)], outline=rc(col,a), width=w)

def pill(d, cx, cy, bw, bh, fc, fa, bc=None, ba=0):
    x,y=cx-bw//2,cy-bh//2
    d.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=bh//2, fill=rc(fc,fa))
    if bc: d.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=bh//2,
                                outline=rc(bc,ba), width=2)

def card(d, cx, cy, bw, bh, fc, fa, bc=None, ba=0, r=18):
    x,y=cx-bw//2,cy-bh//2
    d.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=r, fill=rc(fc,fa))
    if bc: d.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=r,
                                outline=rc(bc,ba), width=2)

def subtle_ring(d, sec):
    """Single slow-rotating faint accent ring — barely visible."""
    cx=cy=W//2
    for i,r in enumerate([420,340]):
        ring(d,cx,cy,r,CYAN, 0.04+0.01*math.sin(sec*0.3+i), w=1)

# ══════════════════════════════════════════════════════════════════════════════
#  SCENES
# ══════════════════════════════════════════════════════════════════════════════

# ── Scene 1  (0–4 s)  Brand opener ───────────────────────────────────────────
def scene1(d, sec, a):
    cx=W//2; subtle_ring(d,sec)

    # CONECTA
    t1,s1 = fade_in(sec, .4, .8)
    if t1>0: txt(d,cx,360,"CONECTA",F['h1'],WHITE,t1*a,s1)

    # Underline
    t2 = ap(sec,.9,.6)
    if t2>0: hbar(d,cx,495,t2,CYAN,t2*a)

    # Expo tag
    t3,s3 = fade_in(sec,1.1,.6)
    if t3>0: txt(d,cx,515,"2DA EXPO-CONFERENCIA  2026",F['h5'],CYAN,t3*a,s3,shadow=False)

    # City
    t4,s4 = fade_in(sec,1.5,.6)
    if t4>0: txt(d,cx,572,"Tepatitlan, Jalisco",F['reg'],SILVER,t4*a*.7,s4,shadow=False)

    # COONEXPO
    t5,s5 = fade_in(sec,2.0,.6)
    if t5>0: txt(d,cx,700,"COONEXPO",F['sm'],SILVER,t5*a*.45,s5,shadow=False)


# ── Scene 2  (4–9 s)  Hook ───────────────────────────────────────────────────
def scene2(d, sec, a):
    cx=W//2; s=sec-4.0; subtle_ring(d,sec)

    t0,s0 = fade_in(s,.0,.5,20)
    if t0>0: txt(d,cx,130,"SE PARTE DE",F['h5'],CYAN,t0*a,s0,shadow=False)

    t1,sl1 = fade_in(s,.3,.7)
    if t1>0: txt(d,cx,220,"NO LE DEJES",F['h2'],WHITE,t1*a,sl1)

    t2,sl2 = fade_in(s,.65,.7)
    if t2>0: txt(d,cx,320,"EL MERCADO",F['h2'],WHITE,t2*a,sl2)

    t3,sl3 = fade_in(s,1.0,.7)
    if t3>0: txt(d,cx,420,"A LA COMPETENCIA",F['h2'],GOLD,t3*a,sl3)

    # Divider
    t4 = ap(s,1.6,.5)
    if t4>0: hbar(d,cx,530,t4,CYAN,t4*a*.6)

    # Stats
    stats=[("50+","Expositores"),("500+","Asistentes"),("3","Dias")]
    for i,(num,lbl) in enumerate(stats):
        ti,si = fade_in(s,1.9+i*.2,.6)
        if ti>0:
            bx=190+i*270
            txt(d,bx,575,num,F['h3'],CYAN,ti*a,si)
            txt(d,bx,648,lbl,F['sm'],SILVER,ti*a*.7,si,shadow=False)

    # Date
    t6,s6 = fade_in(s,2.7,.6)
    if t6>0:
        pill(d,cx,790,480,62,BLUE,t6*a*.85,CYAN,t6*a*.6)
        txt(d,cx,766,"ABRIL  18 · 19 · 20",F['h4'],WHITE,t6*a,0,shadow=False)


# ── Scene 3  (9–14 s)  Expositor ─────────────────────────────────────────────
def scene3(d, sec, a):
    cx=W//2; s=sec-9.0; subtle_ring(d,sec)

    t0,s0 = fade_in(s,.0,.5,20)
    if t0>0: txt(d,cx,110,"UNETE COMO",F['h5'],CYAN,t0*a,s0,shadow=False)

    t1,sl1 = fade_in(s,.3,.8)
    if t1>0: txt(d,cx,195,"EXPOSITOR",F['h1'],WHITE,t1*a,sl1)

    t2 = ap(s,.9,.5)
    if t2>0: hbar(d,cx,325,t2,CYAN,t2*a*.8)

    t3,s3 = fade_in(s,1.1,.6)
    if t3>0: txt(d,cx,350,"en la expo mas importante de Los Altos",F['h5'],SILVER,t3*a*.85,s3,shadow=False)

    bens=["Visibilidad ante empresarios de la region",
          "Networking con lideres del sector",
          "Posiciona tu marca en Los Altos",
          "Genera clientes y alianzas estrategicas"]
    for i,b in enumerate(bens):
        ti,si = fade_in(s,1.5+i*.3,.55)
        if ti>0:
            by=415+i*72
            # dot
            d.ellipse([(cx-380,by+8),(cx-366,by+22)], fill=rc(CYAN,ti*a*.9))
            # text (left-aligned from cx-360)
            bw,bh=tw(d,b,F['reg'])
            d.text((cx-356,by), b, font=F['reg'], fill=rc(WHITE,ti*a))

    t7,s7 = fade_in(s,3.0,.6)
    if t7>0:
        txt(d,cx,730,"ABRIL 18 · 19 · 20  —  Tepatitlan",F['h5'],CYAN,t7*a*.8,s7,shadow=False)


# ── Scene 4  (14–19 s)  Precio ───────────────────────────────────────────────
def scene4(d, sec, a):
    cx=W//2; s=sec-14.0; subtle_ring(d,sec)

    t0,s0 = fade_in(s,.0,.6,20)
    if t0>0: txt(d,cx,110,"STAND DESDE",F['h4'],WHITE,t0*a,s0)

    # Price card
    t1 = ap(s,.3,1.4)
    if t1>0:
        val = int((1-(1-cl((s-.3)/1.1))**3)*5900)
        price = "$"+f"{val:,}"
        card(d,cx,330,740,195,BLUE,t1*a*.8,CYAN,t1*a*.5,r=20)
        pw,_ = tw(d,price,F['h1'])
        d.text((cx-pw//2+2,243), price, font=F['h1'], fill=rc((0,0,0),t1*a*.3))
        d.text((cx-pw//2,240),   price, font=F['h1'], fill=rc(GOLD,t1*a))
        d.text((cx-pw//2+pw+12,288), "pesos", font=F['reg'], fill=rc(WHITE,t1*a*.6))

    t2 = ap(s,1.4,.5)
    if t2>0: hbar(d,cx,440,t2,CYAN,t2*a*.6)

    t3,s3 = fade_in(s,1.6,.6)
    if t3>0: txt(d,cx,458,"Espacio personalizado  ·  Rotulos incluidos",F['reg'],SILVER,t3*a*.8,s3,shadow=False)

    includes=["Exposicion de tu marca los 3 dias","Acceso a conferencias y networking"]
    for i,item in enumerate(includes):
        ti,si = fade_in(s,1.9+i*.25,.55)
        if ti>0:
            by=510+i*46
            d.ellipse([(cx-320,by+7),(cx-308,by+19)], fill=rc(CYAN,ti*a*.8))
            bw,_=tw(d,item,F['sm'])
            d.text((cx-300,by), item, font=F['sm'], fill=rc(WHITE,ti*a*.85))

    # Scarcity
    t6,s6 = fade_in(s,2.8,.6)
    if t6>0:
        card(d,cx,680,560,62,RED,t6*a*.9,r=31)
        txt(d,cx,656,"SOLO 50 STANDS DISPONIBLES",F['h5'],WHITE,t6*a,0,shadow=False)

    t7,s7 = fade_in(s,3.2,.6)
    if t7>0: txt(d,cx,770,"Apartalo antes de que se agote",F['sm'],SILVER,t7*a*.7,s7,shadow=False)


# ── Scene 5  (19–24 s)  Pago + CTA ──────────────────────────────────────────
def scene5(d, sec, a):
    cx=W//2; s=sec-19.0; subtle_ring(d,sec)

    t0,s0 = fade_in(s,.0,.6,20)
    if t0>0: txt(d,cx,90,"OPCIONES DE PAGO",F['h4'],WHITE,t0*a,s0)

    # Card 1 — Reserva
    t1 = ap(s,.4,.7)
    if t1>0:
        sl=int(lp(40,0,t1))
        card(d,cx,265-sl,700,178,BLUE,t1*a*.88,CYAN,t1*a*.55,r=16)
        txt(d,cx,188-sl,"RESERVA TU STAND",F['h5'],CYAN,t1*a,.0,shadow=False)
        txt(d,cx,218-sl,"con solo  $1,000",F['h2'],GOLD,t1*a)
        txt(d,cx,318-sl,"y aparta tu lugar hoy",F['sm'],SILVER,t1*a*.7,.0,shadow=False)

    # Divider
    t2 = ap(s,1.1,.5)
    if t2>0:
        hbar(d,cx,383,t2*.4,SILVER,t2*a*.25)
        txt(d,cx,366,"o",F['h4'],SILVER,t2*a*.35,.0,shadow=False)

    # Card 2 — Meses sin intereses
    t3 = ap(s,1.5,.7)
    if t3>0:
        sl=int(lp(40,0,t3))
        card(d,cx,565+sl,700,180,(14,35,90),t3*a*.92,SILVER,t3*a*.4,r=16)
        txt(d,cx,488+sl,"PAGA EL TOTAL",F['h5'],SILVER,t3*a,.0,shadow=False)
        txt(d,cx,520+sl,"A MESES",F['h2'],WHITE,t3*a)
        txt(d,cx,610+sl,"SIN INTERESES",F['h3'],CYAN,t3*a)

    # CTA
    t4 = ap(s,2.8,.6)
    if t4>0:
        pulse = 1+.025*math.sin(sec*5)
        pill(d,cx,830,int(650*pulse),int(74*pulse),CYAN,t4*a)
        txt(d,cx,800,"RESERVA TU ESPACIO AHORA",F['h4'],NAVY,t4*a,.0,shadow=False)


# ── Scene 6  (not needed — extended scene 5 outro already covers it)

# ══════════════════════════════════════════════════════════════════════════════
#  SCHEDULE
# ══════════════════════════════════════════════════════════════════════════════
SCHED = [
    ( 0.0,  4.5, scene1),
    ( 4.0,  9.5, scene2),
    ( 9.0, 14.5, scene3),
    (14.0, 19.5, scene4),
    (19.0, 24.2, scene5),
]
FADE = .45

def s_alpha(sec, s, e):
    if sec<s or sec>e: return 0.
    t=sec-s; dur=e-s
    if t<FADE:     return eio(t/FADE)
    if t>dur-FADE: return eio((e-sec)/FADE)
    return 1.


# ══════════════════════════════════════════════════════════════════════════════
#  FRAME
# ══════════════════════════════════════════════════════════════════════════════
def make_frame(fn):
    sec = fn/FPS
    bg  = BG_IMG.copy()
    ov  = Image.new('RGBA',(W,H),(0,0,0,0))
    d   = ImageDraw.Draw(ov,'RGBA')
    for (s,e,fn_s) in SCHED:
        a = s_alpha(sec,s,e)
        if a>0: fn_s(d,sec,a)
    return np.array(Image.alpha_composite(bg,ov).convert('RGB'),dtype=np.uint8)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    global F, BG_IMG
    print("Cargando fuentes...")
    F      = load_fonts()
    BG_IMG = make_bg()

    out = "conecta_2026_ad.mp4"
    print(f"Generando {TOTAL} frames  ({W}x{H} · {FPS}fps · {DUR}s)...")
    w = imageio.get_writer(out, fps=FPS, codec='libx264', quality=9,
                           macro_block_size=1,
                           output_params=['-pix_fmt','yuv420p','-preset','fast'])
    for i in range(TOTAL):
        if i%(FPS*4)==0: print(f"  {i*100//TOTAL:3d}%")
        w.append_data(make_frame(i))
    w.close()
    print(f"\nListo  →  {out}")

if __name__=="__main__":
    main()
