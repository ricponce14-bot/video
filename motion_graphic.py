"""
Motion Graphic Video Generator
Generates a 15-second motion graphic style video using PIL + imageio
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
import math

# ── Video Settings ────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 30
DURATION = 15          # seconds
TOTAL_FRAMES = FPS * DURATION

# ── Color Palette ─────────────────────────────────────────────────────────────
BG       = (8,  12,  24)
CYAN     = (0,  220, 255)
PURPLE   = (160, 90, 255)
ORANGE   = (255, 120,  40)
GREEN    = (40,  230, 140)
WHITE    = (240, 245, 255)
PINK     = (255,  80, 160)

PALETTE  = [CYAN, PURPLE, ORANGE, GREEN, PINK]

# ── Easing Functions ──────────────────────────────────────────────────────────
def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3

def ease_in_out(t):
    t = clamp(t)
    return 4 * t**3 if t < 0.5 else 1 - (-2*t + 2)**3 / 2

def ease_out_expo(t):
    t = clamp(t)
    return 0 if t == 0 else (1 if t == 1 else 1 - 2**(-10 * t))

def ease_in_back(t):
    t = clamp(t)
    c1 = 1.70158
    return (c1 + 1) * t**3 - c1 * t**2

def lerp(a, b, t):
    return a + (b - a) * clamp(t)

def lerp_color(c1, c2, t):
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

# ── Drawing Helpers ───────────────────────────────────────────────────────────
def rgba(color, alpha):
    """Return RGBA tuple from RGB + float alpha 0-1."""
    return (*color, int(clamp(alpha) * 255))

def draw_ring(draw, cx, cy, r, color, alpha, width=2):
    a = int(clamp(alpha) * 255)
    if r > 1:
        draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)],
                     outline=(*color, a), width=width)

def draw_glow_circle(draw, cx, cy, r, color, alpha, layers=6):
    for i in range(layers, 0, -1):
        gr = r + i * 10
        ga = alpha * 0.12 / i
        draw.ellipse([(cx-gr, cy-gr), (cx+gr, cy+gr)],
                     fill=rgba(color, ga))
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)],
                 fill=rgba(color, alpha))

def draw_line_a(draw, p1, p2, color, alpha, width=1):
    draw.line([p1, p2], fill=rgba(color, alpha), width=width)

def polygon_points(cx, cy, n, r, angle_offset=0):
    pts = []
    for i in range(n):
        a = angle_offset + i * 2 * math.pi / n
        pts.append((cx + math.cos(a)*r, cy + math.sin(a)*r))
    return pts


# ── Text Helpers ──────────────────────────────────────────────────────────────
def load_fonts():
    paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    paths_reg = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    font_l = None
    for p in paths:
        try:
            font_l = ImageFont.truetype(p, 78)
            break
        except:
            pass
    font_m = None
    for p in paths:
        try:
            font_m = ImageFont.truetype(p, 36)
            break
        except:
            pass
    font_s = None
    for p in paths_reg:
        try:
            font_s = ImageFont.truetype(p, 24)
            break
        except:
            pass
    font_l = font_l or ImageFont.load_default()
    font_m = font_m or ImageFont.load_default()
    font_s = font_s or ImageFont.load_default()
    return font_l, font_m, font_s

def text_size(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[2] - bb[0], bb[3] - bb[1]

def draw_text_centered(draw, cx, cy, text, font, color, alpha, scale_y=0):
    """Draw centered text; scale_y offsets vertically."""
    w, h = text_size(draw, text, font)
    x = cx - w // 2
    y = cy - h // 2 + scale_y
    # Subtle glow
    for ox, oy in [(-2,0),(2,0),(0,-2),(0,2)]:
        draw.text((x+ox, y+oy), text, font=font, fill=rgba(color, alpha*0.3))
    draw.text((x, y), text, font=font, fill=rgba(WHITE, alpha))


# ── Frame Generator ───────────────────────────────────────────────────────────
def create_frame(frame_num, fonts):
    font_l, font_m, font_s = fonts
    t   = frame_num / TOTAL_FRAMES   # 0 → 1 over entire video
    sec = frame_num / FPS            # seconds elapsed

    img  = Image.new('RGBA', (WIDTH, HEIGHT), (*BG, 255))
    draw = ImageDraw.Draw(img, 'RGBA')

    cx, cy = WIDTH // 2, HEIGHT // 2

    # ── 1. Animated background grid ──────────────────────────────────────────
    grid_alpha = 0.06 + 0.03 * math.sin(sec * 0.4)
    grid_size  = 60
    for xi in range(0, WIDTH + grid_size, grid_size):
        draw_line_a(draw, (xi, 0), (xi, HEIGHT), CYAN, grid_alpha)
    for yi in range(0, HEIGHT + grid_size, grid_size):
        draw_line_a(draw, (0, yi), (WIDTH, yi), CYAN, grid_alpha)

    # ── 2. Expanding rings (0–6 s) ────────────────────────────────────────────
    ring_window = 6.0
    if sec < ring_window + 2:
        for i in range(6):
            rt = sec - i * 0.5
            if rt > 0:
                ring_t = rt / 4.5
                r       = ease_out_expo(ring_t) * 460
                alpha   = (1 - clamp(ring_t)) * 0.7
                color   = PALETTE[i % len(PALETTE)]
                draw_ring(draw, cx, cy, int(r), color, alpha, width=2)

    # ── 3. Background accent – large slow ring ────────────────────────────────
    slow_r = 320 + 20 * math.sin(sec * 0.6)
    draw_ring(draw, cx, cy, int(slow_r), PURPLE,
              0.12 + 0.06 * math.sin(sec * 0.8), width=40)

    # ── 4. Rotating outer square ──────────────────────────────────────────────
    sq_appear = ease_out(clamp((sec - 1.0) / 1.5))
    if sq_appear > 0:
        rot   = -sec * 0.25
        sq_r  = 260
        verts = polygon_points(cx, cy, 4, sq_r * math.sqrt(2), rot + math.pi/4)
        for i in range(4):
            draw_line_a(draw, verts[i], verts[(i+1)%4],
                        PURPLE, sq_appear * 0.7, width=2)

    # ── 5. Rotating triangle ──────────────────────────────────────────────────
    tri_appear = ease_out(clamp((sec - 1.5) / 1.5))
    if tri_appear > 0:
        rot   = sec * 0.4
        verts = polygon_points(cx, cy, 3, 200, rot)
        for i in range(3):
            draw_line_a(draw, verts[i], verts[(i+1)%3],
                        CYAN, tri_appear * 0.6, width=2)

    # ── 6. Rotating hexagon ───────────────────────────────────────────────────
    hex_appear = ease_out(clamp((sec - 2.0) / 1.5))
    if hex_appear > 0:
        rot   = -sec * 0.15
        verts = polygon_points(cx, cy, 6, 310, rot)
        for i in range(6):
            draw_line_a(draw, verts[i], verts[(i+1)%6],
                        ORANGE, hex_appear * 0.45, width=1)

    # ── 7. Orbiting dots ──────────────────────────────────────────────────────
    dots_appear = ease_out(clamp((sec - 2.5) / 1.2))
    num_dots = 10
    for i in range(num_dots):
        angle = (i / num_dots) * 2 * math.pi + sec * 0.5
        dist  = 300 + 18 * math.sin(sec * 1.8 + i * 1.1)
        dx    = cx + math.cos(angle) * dist
        dy    = cy + math.sin(angle) * dist
        dot_r = 4 + 2 * math.sin(sec * 2 + i)
        color = PALETTE[i % len(PALETTE)]
        draw_glow_circle(draw, dx, dy, int(dot_r), color,
                         dots_appear * 0.85, layers=4)
        # spoke
        if dots_appear > 0.4:
            draw_line_a(draw, (cx, cy), (dx, dy), color,
                        (dots_appear - 0.4) / 0.6 * 0.18)

    # ── 8. Inner cross lines ──────────────────────────────────────────────────
    cross_appear = ease_out(clamp((sec - 3.0) / 1.2))
    if cross_appear > 0:
        cross_len = 90
        for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
            px = cx + math.cos(angle) * cross_len
            py = cy + math.sin(angle) * cross_len
            draw_line_a(draw, (cx, cy), (px, py), WHITE, cross_appear * 0.5, width=2)

    # ── 9. Center glowing orb ────────────────────────────────────────────────
    orb_appear = ease_out(clamp(sec / 1.0))
    orb_pulse  = 1.0 + 0.15 * math.sin(sec * 4)
    orb_r      = int(22 * orb_pulse)
    draw_glow_circle(draw, cx, cy, orb_r, CYAN, orb_appear * 0.95, layers=7)

    # ── 10. Corner HUD brackets ───────────────────────────────────────────────
    hud_appear = ease_out(clamp((sec - 1.0) / 1.5))
    cs = 35   # corner size
    mg = 22   # margin
    corners_info = [
        (mg,       mg,        1,  1),
        (WIDTH-mg, mg,       -1,  1),
        (mg,       HEIGHT-mg, 1, -1),
        (WIDTH-mg, HEIGHT-mg,-1, -1),
    ]
    for px, py, dx, dy in corners_info:
        draw_line_a(draw, (px, py), (px + dx*cs, py), CYAN, hud_appear * 0.9, width=2)
        draw_line_a(draw, (px, py), (px, py + dy*cs), CYAN, hud_appear * 0.9, width=2)

    # ── 11. Scan line (top to bottom, loops every 4 s) ────────────────────────
    scan_t  = (sec % 4.0) / 4.0
    scan_y  = int(scan_t * HEIGHT)
    scan_a  = 0.25 * math.sin(scan_t * math.pi)
    draw.rectangle([(0, scan_y - 1), (WIDTH, scan_y + 1)],
                   fill=rgba(CYAN, scan_a))

    # ── 12. Main title text (appears at 3.5 s) ────────────────────────────────
    title_start = 3.5
    if sec > title_start:
        tt     = ease_out(clamp((sec - title_start) / 1.2))
        slide  = int(lerp(80, 0, tt))
        title  = "MOTION GRAPHICS"
        tw, th = text_size(draw, title, font_l)
        ty     = cy - 70 + slide
        draw_text_centered(draw, cx, ty + th//2, title, font_l, CYAN, tt)

        # Underline bar that grows
        bar_t   = ease_out(clamp((sec - title_start - 0.3) / 0.8))
        bar_w   = int(bar_t * (tw + 60))
        bar_x   = cx - bar_w // 2
        bar_y   = ty + th + 10
        if bar_w > 0:
            draw.rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 3)],
                           fill=rgba(CYAN, bar_t * 0.9))

        # Subtitle (appears 0.8 s after title)
        sub_start = title_start + 0.8
        if sec > sub_start:
            st  = ease_out(clamp((sec - sub_start) / 1.0))
            sub = "Geometric  ·  Kinetic  ·  Dynamic"
            sw, sh = text_size(draw, sub, font_s)
            draw.text((cx - sw//2, bar_y + 20), sub,
                      font=font_s, fill=rgba(GREEN, st * 0.85))

        # Decorative horizontal lines flanking title
        flank_start = title_start + 0.5
        if sec > flank_start:
            ft       = ease_out(clamp((sec - flank_start) / 0.9))
            gap      = 24
            line_len = int(ft * 170)
            lx_left  = cx - tw // 2 - gap
            lx_right = cx + tw // 2 + gap
            mid_y    = ty + th // 2
            draw_line_a(draw, (lx_left, mid_y), (lx_left - line_len, mid_y),
                        PURPLE, ft * 0.8, width=2)
            draw_line_a(draw, (lx_right, mid_y), (lx_right + line_len, mid_y),
                        PURPLE, ft * 0.8, width=2)
            # diamonds at ends
            for ox in [lx_left - line_len, lx_right + line_len]:
                d = 5
                draw.polygon([(ox, mid_y-d), (ox+d, mid_y),
                               (ox, mid_y+d), (ox-d, mid_y)],
                             fill=rgba(PURPLE, ft * 0.8))

    # ── 13. Bottom status bar (appears at 5 s) ────────────────────────────────
    bar_start = 5.0
    if sec > bar_start:
        bt   = ease_out(clamp((sec - bar_start) / 1.0))
        bar_h = HEIGHT - 48
        label = f"FRAME {frame_num:05d}  ·  {sec:05.2f}s  ·  {FPS} FPS"
        lw, lh = text_size(draw, label, font_s)
        draw.text((cx - lw//2, bar_h),
                  label, font=font_s, fill=rgba(CYAN, bt * 0.5))
        # Left and right decorative ticks
        tick_len = int(bt * 120)
        draw_line_a(draw, (20, bar_h + lh//2),
                    (20 + tick_len, bar_h + lh//2), CYAN, bt * 0.4, width=1)
        draw_line_a(draw, (WIDTH-20, bar_h + lh//2),
                    (WIDTH-20 - tick_len, bar_h + lh//2), CYAN, bt * 0.4, width=1)

    # ── 14. Outro pulse (last 2 s) ────────────────────────────────────────────
    outro_start = DURATION - 2.0
    if sec > outro_start:
        ot = clamp((sec - outro_start) / 2.0)
        # Fade to white flash then dark
        flash = math.sin(ot * math.pi) * 0.25
        overlay = Image.new('RGBA', (WIDTH, HEIGHT), (255, 255, 255, int(flash * 255)))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img, 'RGBA')

    # ── Convert RGBA → RGB ───────────────────────────────────────────────────
    bg_img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    bg_img.paste(img.convert('RGB'), mask=img.split()[3])
    return np.array(bg_img, dtype=np.uint8)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Loading fonts...")
    fonts = load_fonts()

    output = "motion_graphic.mp4"
    print(f"Generating {TOTAL_FRAMES} frames at {WIDTH}x{HEIGHT} @ {FPS} fps...")

    writer = imageio.get_writer(
        output, fps=FPS,
        codec='libx264',
        quality=8,
        output_params=['-pix_fmt', 'yuv420p', '-preset', 'fast']
    )

    for fn in range(TOTAL_FRAMES):
        if fn % (FPS * 2) == 0:
            pct = fn * 100 // TOTAL_FRAMES
            print(f"  {pct:3d}%  frame {fn}/{TOTAL_FRAMES}")
        frame = create_frame(fn, fonts)
        writer.append_data(frame)

    writer.close()
    print(f"\nDone!  Saved → {output}")


if __name__ == "__main__":
    main()
