#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1080, 1920
OUT = "ov"
os.makedirs(OUT, exist_ok=True)

SERIF = "/System/Library/Fonts/Supplemental/Didot.ttc"
FUT   = "/System/Library/Fonts/Supplemental/Futura.ttc"
AVE   = "/System/Library/Fonts/Avenir Next.ttc"
CJK   = "/System/Library/Fonts/STHeiti Medium.ttc"

CREAM = (245, 239, 230, 255)
WHITE = (255, 255, 255, 255)
AMBER = (232, 162, 61, 255)
DARK  = (26, 20, 16, 255)

def font(path, size, idx=0):
    return ImageFont.truetype(path, size, index=idx)

def measure(draw, text, fnt, track=0):
    if track == 0:
        b = draw.textbbox((0, 0), text, font=fnt)
        return b[2] - b[0]
    w = 0
    for ch in text:
        b = draw.textbbox((0, 0), ch, font=fnt)
        w += (b[2] - b[0]) + track
    return w - track if text else 0

def draw_text(img, cx, cy, text, fnt, fill, track=0, anchor_center=True, lx=None):
    """Draw text with a soft shadow. Centered at (cx,cy) unless lx given (left x)."""
    # shadow layer
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    tw = measure(sd, text, fnt, track)
    x0 = (lx if lx is not None else cx - tw / 2)
    asc, desc = fnt.getmetrics()
    th = asc + desc
    y0 = cy - th / 2
    # draw shadow text (offset)
    def render(d, ox, oy, col):
        x = x0
        if track == 0:
            d.text((x + ox, y0 + oy), text, font=fnt, fill=col)
        else:
            for ch in text:
                d.text((x + ox, y0 + oy), ch, font=fnt, fill=col)
                b = d.textbbox((0, 0), ch, font=fnt)
                x += (b[2] - b[0]) + track
    render(sd, 0, 4, (0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    img.alpha_composite(sh)
    dd = ImageDraw.Draw(img)
    render(dd, 0, 0, fill)

def canvas():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def save(img, name):
    img.save(os.path.join(OUT, name))
    print("saved", name)

# ---- fonts (indices verified by trial; fall back to 0) ----
def safe(path, size, idx):
    try:
        return font(path, size, idx)
    except Exception:
        return font(path, size, 0)

f_brand   = safe(SERIF, 188, 1)   # Didot bold-ish
f_hook    = safe(FUT, 80, 3)      # Futura bold
f_kick    = safe(FUT, 30, 0)
f_line    = safe(SERIF, 70, 0)
f_sub     = safe(AVE, 38, 0)
f_corner  = safe(SERIF, 44, 0)
f_spec    = safe(FUT, 40, 0)
f_specbig = safe(FUT, 48, 3)
f_cta     = safe(FUT, 42, 3)
f_url     = safe(AVE, 40, 0)
f_cjk     = font(CJK, 48, 0)
f_brandsm = safe(SERIF, 64, 1)

CREAM85 = (245, 239, 230, 220)

# ===== Scene 1 =====
img = canvas()
draw_text(img, W/2, H*0.40, "WAKE UP TO THIS", f_hook, WHITE, track=6)
save(img, "s1_hook.png")

img = canvas()
draw_text(img, W/2, H*0.355, "AURÉA", f_brand, CREAM)
d = ImageDraw.Draw(img)
d.rectangle([W/2-130, H*0.355+120, W/2+130, H*0.355+123], fill=AMBER)
draw_text(img, W/2, H*0.355+165, "R H O D E S   W A T E R F R O N T", f_kick, AMBER, track=2)
save(img, "s1_brand.png")

# corner wordmark helper
def add_corner(img):
    draw_text(img, None, H-95, "AURÉA", f_corner, CREAM85, lx=70)

# ===== Scene 2 =====
img = canvas()
draw_text(img, W/2, H*0.70, "Light that follows the day", f_line, CREAM)
draw_text(img, W/2, H*0.70+78, "Floor to ceiling glass, water to sky", f_sub, WHITE)
add_corner(img)
save(img, "s2.png")

# ===== Scene 3 =====
img = canvas()
draw_text(img, W/2, H*0.70, "Crafted for the way you live", f_line, CREAM)
draw_text(img, W/2, H*0.70+78, "Stone, timber and warmth", f_sub, WHITE)
add_corner(img)
save(img, "s3.png")

# ===== Scene 4 =====
img = canvas()
draw_text(img, W/2, H*0.71, "Wake to the harbour", f_line, CREAM)
add_corner(img)
save(img, "s4.png")

# ===== Scene 5 =====
img = canvas()
draw_text(img, W/2, H*0.70, "Rooftop infinity pool", f_line, CREAM)
draw_text(img, W/2, H*0.70+78, "A sky lounge for residents", f_sub, AMBER)
add_corner(img)
save(img, "s5.png")

# ===== Scene 6 =====
img = canvas()  # persistent top brand
draw_text(img, W/2, 150, "AURÉA", f_brandsm, CREAM)
save(img, "s6_brand.png")

img = canvas()  # specs
draw_text(img, W/2, H*0.30, "TWO & THREE BEDROOM RESIDENCES", f_spec, CREAM, track=2)
draw_text(img, W/2, H*0.30+78, "PRICED FROM $1.2M", f_specbig, AMBER, track=2)
draw_text(img, W/2, H*0.30+156, "LAUNCHING SPRING 2026", f_spec, CREAM, track=2)
save(img, "s6_specs.png")

img = canvas()  # CTA
d = ImageDraw.Draw(img)
bx0, by0, bx1, by1 = W/2-310, H*0.60, W/2+310, H*0.60+112
# soft shadow for button
sh = canvas(); sd = ImageDraw.Draw(sh)
sd.rounded_rectangle([bx0, by0+6, bx1, by1+6], radius=8, fill=(0,0,0,150))
sh = sh.filter(ImageFilter.GaussianBlur(9)); img.alpha_composite(sh)
d.rounded_rectangle([bx0, by0, bx1, by1], radius=8, fill=AMBER)
draw_text(img, W/2, (by0+by1)/2, "REGISTER YOUR INTEREST", f_cta, DARK, track=3)
draw_text(img, W/2, H*0.60+158, "AUREARhodes.com.au", f_url, CREAM)
draw_text(img, W/2, H*0.74, "臨水尊邸 · 誠邀預約", f_cjk, AMBER, track=4)
save(img, "s6_cta.png")

print("ALL OVERLAYS GENERATED")
