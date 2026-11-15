"""ShopCepte Fırsat Ekibi - Tasarımcı modülü: gönderi (1080x1350) ve hikaye (1080x1920) üretir."""
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/truetype/google-fonts/"
def F(w, s): return ImageFont.truetype(FD + f"Poppins-{w}.ttf", s)
PINK = (236, 64, 122); PINK_D = (194, 24, 91); PINK_L = (255, 228, 238)
NAVY = (30, 27, 75); GREY = (130, 130, 145); GREEN = (22, 163, 74); WHITE = (255, 255, 255); GOLD = (245, 158, 11)

def tl(v):
    s = f"{int(round(v)):,}".replace(",", ".")
    return s + " TL"

def load(p, trim=True):
    im = Image.open(os.path.join(D, "img", p)).convert("RGB")
    im = im.crop((0, 0, im.width, im.height - int(im.height * 0.02)))
    if trim:
        diff = ImageChops.difference(im, Image.new("RGB", im.size, WHITE)).convert("L").point(lambda v: 255 if v > 18 else 0)
        bb = diff.getbbox()
        if bb: im = im.crop(bb)
    return im

def fit(im, w, h):
    r = min(w / im.width, h / im.height)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def ctext(d, cx, y, s, f, fill):
    d.text((cx - d.textlength(s, font=f) / 2, y), s, font=f, fill=fill)

def strike(d, x, y, s, f, fill):
    d.text((x, y), s, font=f, fill=fill)
    w = d.textlength(s, font=f); bb = d.textbbox((x, y), s, font=f); my = (bb[1] + bb[3]) // 2
    d.line((x - 2, my, x + w + 2, my), fill=fill, width=3)

def badge(c, cx, cy, r, p, size):
    d = ImageDraw.Draw(c)
    if p.get("pct", 0) >= 5:
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=PINK, outline=WHITE, width=6)
        ctext(d, cx, cy - r * 0.78, f"%{p['pct']}", F("Bold", size), WHITE)
        ctext(d, cx, cy + r * 0.28, "İNDİRİM", F("Bold", int(size * 0.36)), WHITE)
    else:  # indirim yok ama 30 günün en düşük fiyatı
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD, outline=WHITE, width=6)
        f = F("Bold", int(size * 0.34))
        for i, t in enumerate(["30 GÜNÜN", "EN DÜŞÜK", "FİYATI"]):
            ctext(d, cx, cy - r * 0.62 + i * size * 0.4, t, f, WHITE)

def tag(d, x, y, text, fill, size=20):
    f = F("Bold", size); w = d.textlength(text, font=f)
    d.rounded_rectangle((x, y, x + w + 24, y + size + 14), 12, fill=fill)
    d.text((x + 12, y + 4), text, font=f, fill=WHITE)

def bg(W, H):
    c = Image.new("RGB", (W, H), PINK)
    return Image.composite(Image.new("RGB", (W, H), PINK_D), c, Image.linear_gradient("L").resize((W, H)))

def logo(d, x, y, s=54):
    d.text((x, y), "Shop", font=F("Bold", s), fill=WHITE)
    d.text((x + d.textlength("Shop", font=F("Bold", s)), y), "Cepte", font=F("Bold", s), fill=NAVY)

def post(products, title, subtitle, date, out):
    W, H = 1080, 1350
    c = bg(W, H); d = ImageDraw.Draw(c)
    for x, y, r in [(980, 90, 160), (70, 1290, 120)]:
        d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255), width=2)
    logo(d, 60, 40)
    d.rounded_rectangle((W - 330, 52, W - 60, 112), 30, fill=WHITE); ctext(d, W - 195, 60, date, F("Bold", 32), PINK_D)
    ts = 76
    while d.textlength(title, font=F("Bold", ts)) > 960: ts -= 4
    ctext(d, W / 2, 128 + (76 - ts) / 2, title, F("Bold", ts), WHITE)
    ctext(d, W / 2, 228, subtitle, F("Medium", 32), PINK_L)
    gx, gy, gw, gh, gap = 60, 295, 465, 455, 28
    for i, p in enumerate(products):
        x = gx + (i % 2) * (gw + gap); y = gy + (i // 2) * (gh + gap)
        sh = Image.new("RGBA", (gw + 40, gh + 40), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle((20, 26, gw + 20, gh + 26), 34, fill=(90, 0, 40, 90)); sh = sh.filter(ImageFilter.GaussianBlur(12))
        c.paste(sh, (x - 20, y - 20), sh); d = ImageDraw.Draw(c)
        d.rounded_rectangle((x, y, x + gw, y + gh), 34, fill=WHITE)
        im = fit(load(p["img"], not p.get("full")), gw - 70, 250)
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), 18, fill=255)
        c.paste(im, (x + (gw - im.width) // 2, y + 22 + (250 - im.height) // 2), m)
        d = ImageDraw.Draw(c)
        badge(c, x + gw - 62, y + 62, 54, p, 40)
        d = ImageDraw.Draw(c)
        if p.get("cs"): tag(d, x + 18, y + 18, "ÇOK SATAN", NAVY, 18)
        d.multiline_text((x + 26, y + 288), p["name"], font=F("Medium", 25), fill=NAVY, spacing=2)
        if p.get("old"):
            strike(d, x + 26, y + 364, tl(p["old"]), F("Medium", 26), GREY)
        else:
            d.text((x + 26, y + 364), f"{p.get('rv', 0):,}".replace(",", ".") + " değerlendirme", font=F("Medium", 22), fill=GREY)
        d.text((x + 26, y + 390), tl(p["now"]), font=F("Bold", 44), fill=GREEN)
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((190, 1262, 890, 1322), 30, fill=NAVY)
    ctext(d, W / 2, 1270, "LİNKLER PROFİLDEKİ BAĞLANTIDA", F("Bold", 30), WHITE)
    c.save(out)

def story(p, headline, stamp, out):
    W, H = 1080, 1920
    c = bg(W, H); d = ImageDraw.Draw(c)
    hs = 56
    while d.textlength(headline, font=F("Bold", hs)) > 960: hs -= 4
    ctext(d, W / 2, 250, headline, F("Bold", hs), WHITE)
    d.rounded_rectangle((70, 360, W - 70, 1330), 48, fill=WHITE)
    im = fit(load(p["img"], not p.get("full")), 800, 560)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, *im.size), 24, fill=255)
    c.paste(im, ((W - im.width) // 2, 420 + (560 - im.height) // 2), m)
    badge(c, W - 190, 450, 120, p, 92)
    d = ImageDraw.Draw(c)
    if p.get("cs"): tag(d, 110, 400, "ÇOK SATAN", NAVY, 30)
    nm = p["name"].replace("\n", " "); ns = 46
    while d.textlength(nm, font=F("Bold", ns)) > 880: ns -= 2
    ctext(d, W / 2, 1010, nm, F("Bold", ns), NAVY)
    ctext(d, W / 2, 1072, p.get("sub", ""), F("Medium", 34), GREY)
    f_old, f_new = F("Medium", 44), F("Bold", 96)
    if p.get("old"):
        wo = d.textlength(tl(p["old"]), font=f_old); wn = d.textlength(tl(p["now"]), font=f_new)
        x0 = (W - (wo + 40 + wn)) / 2
        strike(d, x0, 1185, tl(p["old"]), f_old, GREY)
        d.text((x0 + wo + 40, 1140), tl(p["now"]), font=f_new, fill=GREEN)
        ctext(d, W / 2, 1385, f"{tl(p['old'] - p['now'])} daha ucuz!", F("Bold", 52), WHITE)
    else:
        ctext(d, W / 2, 1140, tl(p["now"]), f_new, GREEN)
        ctext(d, W / 2, 1385, "Son 30 günün en düşük fiyatı!", F("Bold", 52), WHITE)
    d.rounded_rectangle((170, 1520, W - 170, 1680), 80, fill=NAVY)
    ctext(d, W / 2, 1535, "LİNK PROFİLDE", F("Bold", 54), WHITE)
    ctext(d, W / 2, 1612, "@shopcepte  >  profildeki bağlantı", F("Medium", 30), PINK_L)
    ctext(d, W / 2, 1780, stamp, F("Regular", 28), PINK_L)
    c.save(out)
