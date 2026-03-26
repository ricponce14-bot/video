"""
CONECTA 2026 – Motion Graphic Ad
Format : 1080×1080 (1:1)  |  30 fps  |  22 s
Brand  : CONECTA · COONEXPO · 2da Expo-Conferencia
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
import math

# ── Config ────────────────────────────────────────────────────────────────────
W = H = 1080
FPS = 30
DURATION = 22
TOTAL_FRAMES = FPS * DURATION

# ── Brand Palette ─────────────────────────────────────────────────────────────
NAVY      = (8,   16,  55)
NAVY_MID  = (14,  35,  90)
NAVY_LT   = (22,  60, 140)
BLUE      = (28,  95, 215)
BLUE_LT   = (65, 145, 240)
CYAN      = (0,  195, 255)
WHITE     = (255, 255, 255)
SILVER    = (190, 210, 240)
GOLD      = (255, 195,   0)
RED_WARN  = (195,  30,  45)

# ── Math utils ────────────────────────────────────────────────────────────────
def clamp(v, lo=0., hi=1.): return max(lo, min(hi, v))
def ease_out(t, p=3):       return 1-(1-clamp(t))**p
def ease_in_out(t):
    t=clamp(t); return 4*t**3 if t<.5 else 1-(-2*t+2)**3/2
def ease_expo(t):
    t=clamp(t); return 0 if t==0 else(1 if t==1 else 1-2**(-10*t))
def lerp(a,b,t): return a+(b-a)*clamp(t)
def rgba(c,a):   return (*c[:3], int(clamp(a)*255))
def appear(sec, start, dur=0.55): return ease_out(clamp((sec-start)/dur))

# ── Gradient background ───────────────────────────────────────────────────────
def gradient(c1, c2):
    t = np.linspace(0,1,H).reshape(H,1,1)
    a = np.array(c1[:3], dtype=np.float32).reshape(1,1,3)
    b = np.array(c2[:3], dtype=np.float32).reshape(1,1,3)
    arr = np.broadcast_to(a*(1-t)+b*t, (H,W,3)).copy()
    return Image.fromarray(arr.astype(np.uint8)).convert('RGBA')

# ── Font loader ───────────────────────────────────────────────────────────────
def load_fonts():
    BOLD = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    REG  = ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    def get(paths, sz):
        for p in paths:
            try: return ImageFont.truetype(p, sz)
            except: pass
        return ImageFont.load_default()
    return dict(xl=get(BOLD,118), lg=get(BOLD,82), md=get(BOLD,60),
                sm=get(BOLD,42),  xs=get(BOLD,30), reg=get(REG,26),
                tiny=get(REG,22))

# ── Draw primitives ───────────────────────────────────────────────────────────
def tsz(draw, txt, fnt):
    bb = draw.textbbox((0,0), txt, font=fnt)
    return bb[2]-bb[0], bb[3]-bb[1]

def txt_c(draw, cx, y, txt, fnt, col, a=1., shad=True):
    """Centered text with optional drop-shadow."""
    tw,th = tsz(draw, txt, fnt)
    x = cx-tw//2
    if shad: draw.text((x+2,y+3), txt, font=fnt, fill=rgba((0,0,20), a*0.45))
    draw.text((x,y), txt, font=fnt, fill=rgba(col, a))
    return tw, th

def wipe_txt(img, cx, y, txt, fnt, col, a, p):
    """Left-to-right wipe reveal of text onto img (RGBA)."""
    if p<=0 or a<=0: return
    draw_tmp = ImageDraw.Draw(img, 'RGBA')
    tw,th = tsz(draw_tmp, txt, fnt)
    x = cx-tw//2
    # Draw to temp surface
    tmp = Image.new('RGBA', (tw+6, th+6), (0,0,0,0))
    td  = ImageDraw.Draw(tmp, 'RGBA')
    td.text((2,3), txt, font=fnt, fill=rgba((0,0,20), a*0.45))
    td.text((0,0), txt, font=fnt, fill=rgba(col, a))
    clip_w = int(clamp(p)*(tw+6))
    if clip_w>0:
        img.paste(tmp.crop((0,0,clip_w,th+6)), (x,y), tmp.crop((0,0,clip_w,th+6)))

def hline(draw, cx, y, w_frac, col, a, h=3):
    hw = int(w_frac*500)
    draw.rectangle([(cx-hw,y),(cx+hw,y+h)], fill=rgba(col,a))

def ring(draw, cx, cy, r, col, a, w=2):
    if r>2: draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], outline=rgba(col,a), width=w)

def hexring(draw, cx, cy, r, off, col, a, w=1):
    pts=[(cx+math.cos(off+i*math.pi/3)*r, cy+math.sin(off+i*math.pi/3)*r) for i in range(6)]
    for i in range(6): draw.line([pts[i],pts[(i+1)%6]], fill=rgba(col,a), width=w)

def pill_box(draw, cx, cy, bw, bh, fill_c, fill_a, brd_c=None, brd_a=0., brd_w=2):
    x,y = cx-bw//2, cy-bh//2
    draw.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=bh//2,
                            fill=rgba(fill_c, fill_a))
    if brd_c:
        draw.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=bh//2,
                                outline=rgba(brd_c,brd_a), width=brd_w)

def card(draw, cx, cy, bw, bh, fill_c, fill_a, brd_c=None, brd_a=0., radius=20):
    x,y = cx-bw//2, cy-bh//2
    draw.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=radius,
                            fill=rgba(fill_c, fill_a))
    if brd_c:
        draw.rounded_rectangle([(x,y),(x+bw,y+bh)], radius=radius,
                                outline=rgba(brd_c,brd_a), width=2)

def glow(draw, cx, cy, r, col, a, layers=6):
    for i in range(layers,0,-1):
        draw.ellipse([(cx-r-i*9,cy-r-i*9),(cx+r+i*9,cy+r+i*9)],
                     fill=rgba(col, a*0.07/i))
    draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], fill=rgba(col,a))

def corner_hud(draw, a):
    cs,mg = 55,30
    for px,py,dx,dy in [(mg,mg,1,1),(W-mg,mg,-1,1),(mg,H-mg,1,-1),(W-mg,H-mg,-1,-1)]:
        draw.line([(px,py),(px+dx*cs,py)], fill=rgba(CYAN,a), width=2)
        draw.line([(px,py),(px,py+dy*cs)], fill=rgba(CYAN,a), width=2)

def bg_anim(draw, sec, a=1.):
    cx=cy=W//2
    # Slow rotating hex rings
    for i,(r,spd,c,ba) in enumerate([(490,.07,BLUE,.05),(370,-.10,BLUE_LT,.04),(255,.16,CYAN,.03)]):
        hexring(draw, cx, cy, r, sec*spd+i, c, ba*a)
        ring(draw, cx, cy, r, c, ba*a*.6)
    # Diagonal speed lines
    for i in range(6):
        x = int((i*180+sec*25)%(W+180))-90
        draw.line([(x,0),(x+160,H)], fill=rgba(BLUE_LT, .04*a), width=1)
    corner_hud(draw, .45*a)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 1  ·  0–3.5 s  ·  Intro / brand build
# ══════════════════════════════════════════════════════════════════════════════
def s1_intro(img, draw, sec, a):
    cx=cy=W//2
    bg_anim(draw, sec, a)

    # Expanding burst rings
    for i in range(5):
        rt = sec - i*.35
        if rt>0:
            r  = ease_expo(clamp(rt/2.8))*520
            ra = (1-clamp(rt/2.8))*.55*a
            ring(draw,cx,cy,int(r),[CYAN,BLUE_LT,BLUE,CYAN,BLUE_LT][i],ra,2)

    # Center orb
    glow(draw, cx, cy, int(28*ease_out(clamp(sec/1.0))), CYAN, ease_out(clamp(sec/1.0))*.9*a, 7)

    # CONECTA wordmark
    t1 = appear(sec, .5, .8)
    if t1>0: wipe_txt(img, cx, 360, "CONECTA", FONTS['xl'], WHITE, t1*a, t1)

    # Underline bar
    t2 = appear(sec, .9, .6)
    if t2>0: hline(draw, cx, 498, t2, CYAN, t2*a*.9)

    # Event tag
    t3 = appear(sec, 1.2, .6)
    if t3>0: txt_c(draw, cx, 515, "2DA EXPO-CONFERENCIA  ·  2026", FONTS['xs'], CYAN, t3*a)

    # City
    t4 = appear(sec, 1.7, .6)
    if t4>0: txt_c(draw, cx, 580, "Tepatitlán · Los Altos, Jalisco", FONTS['reg'], SILVER, t4*a*.8)

    # COONEXPO
    t5 = appear(sec, 2.1, .6)
    if t5>0: txt_c(draw, cx, 680, "COONEXPO", FONTS['reg'], SILVER, t5*a*.55)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 2  ·  3–7.5 s  ·  Hook – "La expo más importante de Los Altos"
# ══════════════════════════════════════════════════════════════════════════════
def s2_hook(img, draw, sec, a):
    s=sec-3.0; cx=W//2
    bg_anim(draw, sec, a)

    # Eyebrow
    t0=appear(s,.0,.5)
    if t0>0: txt_c(draw, cx, 115, "SE PARTE DE", FONTS['xs'], CYAN, t0*a)

    # Main headline – 3 lines, staggered wipe
    lines=[("LA EXPO MAS",WHITE),("IMPORTANTE",WHITE),("DE LOS ALTOS",GOLD)]
    for i,(line,col) in enumerate(lines):
        t=appear(s,.2+i*.45,1.0)
        if t>0: wipe_txt(img, cx, 205+i*105, line, FONTS['lg'], col, t*a, t)

    # Separator
    t3=appear(s,1.7,.6)
    if t3>0: hline(draw, cx, 530, t3, CYAN, t3*a*.8)

    # Stats bar
    for i,(num,lbl) in enumerate([("50+","Expositores"),("500+","Asistentes"),("3","Dias")]):
        ti=appear(s,2.0+i*.25,.6)
        if ti>0:
            bx=200+i*270
            glow(draw,bx,600,5,CYAN,ti*a*.8,2)
            txt_c(draw,bx,555,num,FONTS['md'],CYAN,ti*a)
            txt_c(draw,bx,625,lbl,FONTS['tiny'],SILVER,ti*a*.7)

    # Date badge
    t6=appear(s,2.8,.6)
    if t6>0:
        pill_box(draw,cx,755,500,68,BLUE,t6*a*.9,CYAN,t6*a*.7)
        txt_c(draw,cx,727,"ABRIL  18 · 19 · 20",FONTS['sm'],WHITE,t6*a)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 3  ·  7–11.5 s  ·  "Sé expositor"
# ══════════════════════════════════════════════════════════════════════════════
def s3_expositor(img, draw, sec, a):
    s=sec-7.0; cx=W//2
    bg_anim(draw, sec, a)

    t0=appear(s,.0,.6)
    if t0>0: txt_c(draw,cx,100,"ÚNETE COMO",FONTS['xs'],CYAN,t0*a)

    t1=appear(s,.3,.8)
    if t1>0:
        slide=int(lerp(55,0,t1))
        wipe_txt(img,cx,175+slide,"EXPOSITOR",FONTS['xl'],WHITE,t1*a,t1)

    t2=appear(s,1.0,.5)
    if t2>0: hline(draw,cx,310,t2,CYAN,t2*a*.8)

    benefits=[
        "· Visibilidad ante cientos de empresarios",
        "· Networking con lideres del sector",
        "· Posiciona tu marca en toda la region",
        "· Genera clientes y alianzas de negocio",
    ]
    for i,b in enumerate(benefits):
        ti=appear(s,1.3+i*.32,.55)
        if ti>0:
            slide=int(lerp(35,0,ti))
            bx=95+slide; by=350+i*77
            draw.ellipse([(bx-6,by+13),(bx+6,by+25)],fill=rgba(CYAN,ti*a*.9))
            txt_c(draw,cx+20,by,b,FONTS['xs'],WHITE,ti*a)

    t7=appear(s,2.9,.6)
    if t7>0:
        txt_c(draw,cx,720,"ABRIL 18 · 19 · 20",FONTS['sm'],CYAN,t7*a)
        txt_c(draw,cx,775,"Tepatitlan, Jalisco",FONTS['reg'],SILVER,t7*a*.7)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 4  ·  11–16.5 s  ·  Precio – $5,900
# ══════════════════════════════════════════════════════════════════════════════
def s4_precio(img, draw, sec, a):
    s=sec-11.0; cx=W//2
    bg_anim(draw, sec, a)

    t0=appear(s,.0,.6)
    if t0>0: txt_c(draw,cx,95,"STAND DESDE",FONTS['sm'],WHITE,t0*a)

    # Price card + animated counter
    t1=appear(s,.35,1.4)
    if t1>0:
        target=5900
        val=int(ease_expo(clamp((s-.35)/1.2))*target)
        price="$"+f"{val:,}"

        card(draw,cx,345,720,195,NAVY_LT,t1*a*.92,CYAN,t1*a*.8,radius=22)

        pw,ph=tsz(draw,price,FONTS['xl'])
        px=cx-pw//2
        # Gold shadow
        draw.text((px+3,193+3),price,font=FONTS['xl'],fill=rgba(GOLD,t1*a*.35))
        draw.text((px,193),price,font=FONTS['xl'],fill=rgba(GOLD,t1*a))
        draw.text((px+pw+10,230),"pesos",font=FONTS['reg'],fill=rgba(WHITE,t1*a*.7))

    # Includes
    t2=appear(s,1.4,.5)
    if t2>0: hline(draw,cx,445,t2,CYAN,t2*a*.7)

    t3=appear(s,1.6,.6)
    if t3>0: txt_c(draw,cx,460,"INCLUYE TODO",FONTS['xs'],CYAN,t3*a)

    inc=["· Espacio personalizado","· Rotulos de tu marca","· Networking VIP"]
    for i,item in enumerate(inc):
        ti=appear(s,1.9+i*.3,.55)
        if ti>0: txt_c(draw,cx,520+i*65,item,FONTS['xs'],WHITE,ti*a)

    # Scarcity badge
    t6=appear(s,3.0,.6)
    if t6>0:
        pulse=.97+.03*math.sin(sec*6)
        card(draw,cx,810,int(560*pulse),int(64*pulse),RED_WARN,t6*a*.92,radius=32)
        txt_c(draw,cx,784,"SOLO 50 STANDS DISPONIBLES",FONTS['xs'],WHITE,t6*a)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 5  ·  16–20.5 s  ·  Pago + CTA
# ══════════════════════════════════════════════════════════════════════════════
def s5_pago(img, draw, sec, a):
    s=sec-16.0; cx=W//2
    bg_anim(draw, sec, a)

    t0=appear(s,.0,.6)
    if t0>0: txt_c(draw,cx,90,"OPCIONES DE PAGO",FONTS['sm'],CYAN,t0*a)

    # Card 1 – Reserva
    t1=appear(s,.4,.75)
    if t1>0:
        slide=int(lerp(50,0,t1))
        card(draw,cx,275-slide,700,190,BLUE,t1*a*.88,CYAN,t1*a*.7)
        txt_c(draw,cx,185-slide,"RESERVA TU STAND HOY",FONTS['xs'],CYAN,t1*a)
        txt_c(draw,cx,225-slide,"con solo",FONTS['reg'],SILVER,t1*a*.7)
        txt_c(draw,cx,255-slide,"$1,000",FONTS['lg'],GOLD,t1*a)
        txt_c(draw,cx,345-slide,"y aparta tu espacio",FONTS['tiny'],SILVER,t1*a*.75)

    # Divider
    t2=appear(s,1.1,.5)
    if t2>0:
        hw=int(t2*140)
        draw.rectangle([(cx-hw-55,388),(cx-55,390)],fill=rgba(SILVER,t2*a*.3))
        draw.rectangle([(cx+55,388),(cx+55+hw,390)],fill=rgba(SILVER,t2*a*.3))
        txt_c(draw,cx,370,"o",FONTS['sm'],SILVER,t2*a*.45)

    # Card 2 – Meses sin intereses
    t3=appear(s,1.6,.75)
    if t3>0:
        slide=int(lerp(50,0,t3))
        card(draw,cx,605+slide,700,205,NAVY_LT,t3*a*.92,BLUE_LT,t3*a*.7)
        txt_c(draw,cx,510+slide,"PAGA EL TOTAL",FONTS['xs'],SILVER,t3*a)
        txt_c(draw,cx,545+slide,"A MESES",FONTS['lg'],WHITE,t3*a)
        txt_c(draw,cx,635+slide,"SIN INTERESES",FONTS['md'],CYAN,t3*a)

    # CTA button
    t4=appear(s,2.9,.6)
    if t4>0:
        pulse=1+.04*math.sin(sec*6)
        pill_box(draw,cx,835,int(660*pulse),int(80*pulse),CYAN,t4*a)
        txt_c(draw,cx,803,"RESERVA TU ESPACIO AHORA",FONTS['sm'],NAVY,t4*a,shad=False)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE 6  ·  20–22 s  ·  Outro – logos + cierre
# ══════════════════════════════════════════════════════════════════════════════
def s6_outro(img, draw, sec, a):
    s=sec-20.0; cx=cy=W//2
    bg_anim(draw, sec, a)

    # Glow center
    for i in range(8,0,-1):
        ring(draw,cx,cy,70+i*38,BLUE_LT,a*.025/i*4)
    glow(draw,cx,cy,38,CYAN,a*.85,8)

    t1=appear(s,.0,.7)
    if t1>0:
        wipe_txt(img,cx,300,"CONECTA",FONTS['xl'],WHITE,t1*a,t1)

    t2=appear(s,.4,.6)
    if t2>0: hline(draw,cx,428,t2,CYAN,t2*a)

    t3=appear(s,.6,.6)
    if t3>0: txt_c(draw,cx,448,"2DA EXPO-CONFERENCIA  ·  2026",FONTS['xs'],CYAN,t3*a)

    t4=appear(s,.9,.6)
    if t4>0:
        txt_c(draw,cx,520,"ABRIL 18 · 19 · 20",FONTS['sm'],WHITE,t4*a)
        txt_c(draw,cx,575,"Tepatitlan, Jalisco",FONTS['reg'],SILVER,t4*a*.7)

    t5=appear(s,1.2,.6)
    if t5>0:
        pulse=1+.04*math.sin(sec*5)
        pill_box(draw,cx,700,int(640*pulse),int(78*pulse),CYAN,t5*a)
        txt_c(draw,cx,668,"RESERVA TU ESPACIO",FONTS['md'],NAVY,t5*a,shad=False)

    t6=appear(s,1.6,.6)
    if t6>0:
        txt_c(draw,cx,790,"CONECTA  ·  COONEXPO",FONTS['reg'],SILVER,t6*a*.7)


# ══════════════════════════════════════════════════════════════════════════════
# SCENE SCHEDULE
# ══════════════════════════════════════════════════════════════════════════════
SCHEDULE = [
    (0.0,  3.8,  s1_intro),
    (3.2,  7.8,  s2_hook),
    (7.2, 11.8,  s3_expositor),
    (11.2,16.8,  s4_precio),
    (16.2,20.8,  s5_pago),
    (20.2,22.5,  s6_outro),
]
FADE = .55   # crossfade duration (s)

def scene_alpha(sec, s, e):
    if sec<s or sec>e: return 0.
    t=sec-s; dur=e-s
    if t<FADE:     return ease_in_out(t/FADE)
    if t>dur-FADE: return ease_in_out((e-sec)/FADE)
    return 1.


# ══════════════════════════════════════════════════════════════════════════════
# FRAME BUILDER
# ══════════════════════════════════════════════════════════════════════════════
FONTS = None   # set in main()

def create_frame(frame_num):
    sec = frame_num/FPS
    tb  = sec/DURATION

    # Animated gradient background
    c1 = (int(lerp(8,12,tb)),  int(lerp(16,28,tb)),  int(lerp(55,75,tb)))
    c2 = (int(lerp(14,20,tb)), int(lerp(35,55,tb)),  int(lerp(90,120,tb)))
    bg = gradient(c1, c2)   # RGBA, fully opaque

    # Overlay layer (transparent)
    overlay = Image.new('RGBA', (W,H), (0,0,0,0))
    draw    = ImageDraw.Draw(overlay, 'RGBA')

    # Render active scenes
    for (s_start, s_end, fn) in SCHEDULE:
        a = scene_alpha(sec, s_start, s_end)
        if a > 0:
            fn(overlay, draw, sec, a)

    # Scan line (subtle HUD feel)
    st = (sec%3.5)/3.5
    sy = int(st*H)
    draw.rectangle([(0,sy-1),(W,sy+1)], fill=rgba(CYAN, .10*math.sin(st*math.pi)))

    # Composite overlay onto background
    final = Image.alpha_composite(bg, overlay)
    return np.array(final.convert('RGB'), dtype=np.uint8)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    global FONTS
    print("Loading fonts...")
    FONTS = load_fonts()

    out = "conecta_2026_ad.mp4"
    print(f"Generating {TOTAL_FRAMES} frames  ({W}x{H} @ {FPS}fps  {DURATION}s)...")

    writer = imageio.get_writer(
        out, fps=FPS, codec='libx264', quality=9,
        macro_block_size=1,
        output_params=['-pix_fmt','yuv420p','-preset','fast']
    )
    for fn in range(TOTAL_FRAMES):
        if fn % (FPS*3) == 0:
            print(f"  {fn*100//TOTAL_FRAMES:3d}%  frame {fn}/{TOTAL_FRAMES}")
        writer.append_data(create_frame(fn))
    writer.close()
    print(f"\nListo  →  {out}")

if __name__ == "__main__":
    main()
