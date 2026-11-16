"""Paket üretici: python tasarim/uret.py paket.json  (paket.json: out, baslik, alt, hikaye_baslik, tarih, damga, kategori, urunler[id,name,sub,old,now,rt,rev,low,full,post]).
Görseller tasarim/img/<id>.png. İlk 4 ürün (post=0 olmayan) gönderiye, tüm ürünler hikayeye girer. İndirimsiz ve 30-gün etiketsiz üründe rozet = puan."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekip
from ekip import *
from PIL import ImageDraw

_badge = ekip.badge
def badge(c, cx, cy, r, p, size):
    if p.get("pct", 0) >= 5 or p.get("low"):
        return _badge(c, cx, cy, r, p, size)
    d = ImageDraw.Draw(c)  # indirim yok: puan rozeti
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=NAVY, outline=WHITE, width=6)
    ctext(d, cx, cy - r * 0.72, f"{p['rt']:.1f}".replace(".", ","), F("Bold", int(size * 0.95)), WHITE)
    ctext(d, cx, cy + r * 0.28, "PUAN", F("Bold", int(size * 0.36)), WHITE)
ekip.badge = badge
_src = open(ekip.__file__, encoding="utf-8").read()
_old = 'f"{p.get(\'rv\', 0):,}".replace(",", ".") + " değerlendirme"' 
assert _old in _src
_src = _src.replace(_old, """("30 günün en düşük fiyatı" if p.get("low") else f"{p.get('rv', 0):,}".replace(",", ".") + " değerlendirme")""")
exec(compile(_src, ekip.__file__, "exec"), ekip.__dict__)
ekip.badge = badge

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
        msg = "Son 30 günün en düşük fiyatı!" if p.get("low") else (f"{p['rv']:,}".replace(",", ".") + " değerlendirme, " + f"{p['rt']:.1f}".replace(".", ",") + " puan")
        ctext(d, W / 2, 1385, msg, F("Bold", 52 if p.get("low") else 46), WHITE)
    d.rounded_rectangle((170, 1520, W - 170, 1680), 80, fill=NAVY)
    ctext(d, W / 2, 1535, "LİNK PROFİLDE", F("Bold", 54), WHITE)
    ctext(d, W / 2, 1612, "@shopcepte  >  profildeki bağlantı", F("Medium", 30), PINK_L)
    ctext(d, W / 2, 1780, stamp, F("Regular", 28), PINK_L)
    c.save(out, quality=90)

cfg = json.load(open(sys.argv[1]))
os.makedirs(cfg["out"], exist_ok=True)
ps = cfg["urunler"]
for p in ps:
    p["img"] = p["id"] + ".png"; p["pct"] = round((p["old"] - p["now"]) / p["old"] * 100) if p.get("old") else 0
    p.setdefault("rv", p.get("rev", 0))
post_ps = [p for p in ps if p.get("post", 1)][:4]
ekip.post(post_ps, cfg["baslik"], cfg["alt"], cfg["tarih"], cfg["out"] + "/gonderi.png")
Image.open(cfg["out"] + "/gonderi.png").convert("RGB").save(cfg["out"] + "/gonderi.jpg", quality=90); os.remove(cfg["out"] + "/gonderi.png")
for i, p in enumerate(ps, 1):
    story(p, cfg["hikaye_baslik"], cfg["damga"], cfg["out"] + f"/hikaye_{i}.jpg")
print("ok", cfg["out"])
