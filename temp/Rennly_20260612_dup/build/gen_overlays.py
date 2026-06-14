#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1080, 1920
OUT = "ov2"
os.makedirs(OUT, exist_ok=True)

SERIF = "/System/Library/Fonts/Supplemental/Didot.ttc"
FUT   = "/System/Library/Fonts/Supplemental/Futura.ttc"
AVE   = "/System/Library/Fonts/Avenir Next.ttc"
CJK   = "/System/Library/Fonts/STHeiti Medium.ttc"

CREAM = (245, 239, 230, 255)
WHITE = (255, 255, 255, 255)
AMBER = (232, 162, 61, 255)
DARK  = (40, 26, 12, 255)
CREAM85 = (245, 239, 230, 220)

def font(path, size, idx=0):
    return ImageFont.truetype(path, size, index=idx)
def safe(path, size, idx):
    try: return font(path, size, idx)
    except Exception: return font(path, size, 0)

def measure(draw, text, fnt, track=0):
    if track == 0:
        b = draw.textbbox((0, 0), text, font=fnt); return b[2]-b[0]
    w = 0
    for ch in text:
        b = draw.textbbox((0, 0), ch, font=fnt); w += (b[2]-b[0]) + track
    return w - track if text else 0

def draw_text(img, cx, cy, text, fnt, fill, track=0, lx=None):
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    tw = measure(sd, text, fnt, track)
    x0 = (lx if lx is not None else cx - tw/2)
    asc, desc = fnt.getmetrics(); th = asc + desc; y0 = cy - th/2
    def render(d, ox, oy, col):
        x = x0
        if track == 0:
            d.text((x+ox, y0+oy), text, font=fnt, fill=col)
        else:
            for ch in text:
                d.text((x+ox, y0+oy), ch, font=fnt, fill=col)
                b = d.textbbox((0,0), ch, font=fnt); x += (b[2]-b[0]) + track
    render(sd, 0, 4, (0,0,0,150)); sh = sh.filter(ImageFilter.GaussianBlur(7))
    img.alpha_composite(sh); render(ImageDraw.Draw(img), 0, 0, fill)

def canvas(): return Image.new("RGBA", (W, H), (0,0,0,0))
def save(img, name): img.save(os.path.join(OUT, name)); print("saved", name)

def gradient_button(img, box, radius=10):
    """Premium golden gradient rounded-rectangle button with a soft sheen."""
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1-x0, y1-y0
    top = (247, 210, 130); mid = (232, 162, 61); bot = (176, 116, 30)
    grad = Image.new("RGBA", (w, h))
    px = grad.load()
    for yy in range(h):
        t = yy/(h-1)
        if t < 0.5:
            tt = t/0.5; r = int(top[0]+(mid[0]-top[0])*tt); g = int(top[1]+(mid[1]-top[1])*tt); b = int(top[2]+(mid[2]-top[2])*tt)
        else:
            tt = (t-0.5)/0.5; r = int(mid[0]+(bot[0]-mid[0])*tt); g = int(mid[1]+(bot[1]-mid[1])*tt); b = int(mid[2]+(bot[2]-mid[2])*tt)
        # subtle top sheen
        sheen = int(38*(1-t)) if t < 0.35 else 0
        for xx in range(w):
            px[xx, yy] = (min(r+sheen,255), min(g+sheen,255), min(b+sheen,255), 255)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,w-1,h-1], radius=radius, fill=255)
    # soft drop shadow
    sh = canvas(); ImageDraw.Draw(sh).rounded_rectangle([x0, y0+7, x1, y1+7], radius=radius, fill=(0,0,0,150))
    sh = sh.filter(ImageFilter.GaussianBlur(10)); img.alpha_composite(sh)
    img.paste(grad, (x0, y0), mask)
    # thin top highlight line
    hl = canvas(); ImageDraw.Draw(hl).line([x0+18, y0+3, x1-18, y0+3], fill=(255,240,210,120), width=2)
    img.alpha_composite(hl)

f_brand   = safe(SERIF, 188, 1)
f_hook    = safe(FUT, 80, 3)
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

# ===== Scene 1 =====
img = canvas(); draw_text(img, W/2, H*0.40, "WAKE UP TO THIS", f_hook, WHITE, track=6); save(img, "s1_hook.png")

img = canvas()
draw_text(img, W/2, H*0.355, "AURÉA", f_brand, CREAM)
ImageDraw.Draw(img).rectangle([W/2-130, H*0.355+120, W/2+130, H*0.355+123], fill=CREAM)  # white accent line
draw_text(img, W/2, H*0.355+165, "R H O D E S   W A T E R F R O N T", f_kick, CREAM, track=2)  # white kicker
save(img, "s1_brand.png")

def add_corner(img): draw_text(img, None, H-95, "AURÉA", f_corner, CREAM85, lx=70)

# ===== Scenes 2-5 =====
img = canvas(); draw_text(img, W/2, H*0.70, "Light that follows the day", f_line, CREAM); draw_text(img, W/2, H*0.70+78, "Floor to ceiling glass, water to sky", f_sub, WHITE); add_corner(img); save(img, "s2.png")
img = canvas(); draw_text(img, W/2, H*0.70, "Crafted for the way you live", f_line, CREAM); draw_text(img, W/2, H*0.70+78, "Stone, timber and warmth", f_sub, WHITE); add_corner(img); save(img, "s3.png")
img = canvas(); draw_text(img, W/2, H*0.71, "Wake to the harbour", f_line, CREAM); add_corner(img); save(img, "s4.png")
img = canvas(); draw_text(img, W/2, H*0.70, "Rooftop infinity pool", f_line, CREAM); draw_text(img, W/2, H*0.70+78, "A sky lounge for residents", f_sub, AMBER); add_corner(img); save(img, "s5.png")

# ===== Scene 6 =====
img = canvas(); draw_text(img, W/2, 150, "AURÉA", f_brandsm, CREAM); save(img, "s6_brand.png")

img = canvas()
draw_text(img, W/2, H*0.30, "TWO & THREE BEDROOM RESIDENCES", f_spec, CREAM, track=2)
draw_text(img, W/2, H*0.30+78, "PRICED FROM $1.2M", f_specbig, AMBER, track=2)
draw_text(img, W/2, H*0.30+156, "LAUNCHING SPRING 2026", f_spec, CREAM, track=2)
save(img, "s6_specs.png")

img = canvas()
gradient_button(img, [W/2-310, H*0.60, W/2+310, H*0.60+112], radius=10)
draw_text(img, W/2, H*0.60+56, "REGISTER YOUR INTEREST", f_cta, DARK, track=3)
draw_text(img, W/2, H*0.60+158, "AUREA-Rhodes.com.au", f_url, CREAM)
draw_text(img, W/2, H*0.74, "臨水尊邸 | 誠邀預約", f_cjk, AMBER, track=3)
save(img, "s6_cta.png")
print("V2 OVERLAYS DONE")
