"""ShopCepte paylaşımcı: kuyruk/ altındaki paylaşılmamış klasörleri Instagram'a gönderir.

Her klasör:
  kuyruk/<ad>/paylas.json   {"zaman": "2026-11-15T09:23:00Z", "gonderi": ["gonderi.jpg", ...], "hikayeler": ["hikaye_1.jpg", ...]}
                            zaman (UTC, isteğe bağlı): bu andan önce paylaşılmaz; 6 saatten fazla gecikmişse hiç paylaşılmaz.
  kuyruk/<ad>/aciklama.txt  gönderi açıklaması
  kuyruk/<ad>/*.jpg         görseller (JPEG)
Paylaşılan klasöre PAYLASILDI.json yazılır; o dosya varsa klasör atlanır.
Token yalnızca IG_TOKEN ortam değişkeninden okunur, hiçbir yere yazılmaz.
"""
import calendar, json, os, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

API = "https://graph.instagram.com"
TOKEN = os.environ.get("IG_TOKEN", "").strip()
REPO = os.environ["GITHUB_REPOSITORY"]
SHA = os.environ["GITHUB_SHA"]
KURU = os.environ.get("KURU_CALISMA") == "1"  # 1 ise paylaşmaz, sadece kontrol eder


def call(method, path, **params):
    params["access_token"] = TOKEN
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        url, data = url + "?" + data.decode(), None
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace").replace(TOKEN, "***")
        raise RuntimeError(f"Instagram hatası {e.code}: {body}") from None


def raw_url(p: Path):
    return f"https://raw.githubusercontent.com/{REPO}/{SHA}/{urllib.parse.quote(p.as_posix())}"


def wait_ready(cid):
    for _ in range(30):
        st = call("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st == "ERROR":
            raise RuntimeError(f"Görsel işlenemedi: {cid}")
        time.sleep(4)
    raise RuntimeError(f"Görsel zamanında hazır olmadı: {cid}")


def container(**params):
    cid = call("POST", "me/media", **params)["id"]
    wait_ready(cid)
    return cid


def publish(cid):
    return call("POST", "me/media_publish", creation_id=cid)["id"]


def post(folder: Path, files, caption):
    if len(files) == 1:
        cid = container(image_url=raw_url(folder / files[0]), caption=caption)
    else:
        kids = [container(image_url=raw_url(folder / f), is_carousel_item="true") for f in files]
        cid = container(media_type="CAROUSEL", children=",".join(kids), caption=caption)
    return publish(cid)


def story(folder: Path, f):
    return publish(container(image_url=raw_url(folder / f), media_type="STORIES"))


BEKLE = os.environ.get("BEKLE") == "1"


def kaydet(folder):
    """Bekleme modunda her paketin sonucunu hemen depoya yazar (tekrar paylaşımı önler)."""
    if not BEKLE:
        return
    import subprocess
    for c in (["git", "add", "-A", str(folder)], ["git", "commit", "-qm", f"Paylasim sonucu {folder.name} [skip ci]"],
              ["git", "pull", "-q", "--rebase", "origin", "main"], ["git", "push", "-q", "origin", "HEAD:main"]):
        subprocess.run(c, check=False)


def main():
    if not TOKEN:
        sys.exit("IG_TOKEN tanımlı değil (Settings > Secrets and variables > Actions).")
    me = call("GET", "me", fields="username,account_type")
    print("Hesap:", me.get("username"), me.get("account_type"))
    hata = False
    bitis = time.time() + 5.5 * 3600  # GitHub iş sınırı 6 saat
    while True:
      sonraki = None
      for folder in sorted(Path("kuyruk").glob("*/")):
          plan, done = folder / "paylas.json", folder / "PAYLASILDI.json"
          if not plan.exists() or done.exists():
              continue
          cfg = json.loads(plan.read_text(encoding="utf-8"))
          if cfg.get("zaman"):
              bekle = calendar.timegm(time.strptime(cfg["zaman"], "%Y-%m-%dT%H:%M:%SZ")) - time.time()
              if bekle > 0:
                  print(f"{folder}: zamanı gelmedi ({int(bekle // 60)} dk)")
                  hedef = time.time() + bekle
                  if sonraki is None or hedef < sonraki: sonraki = hedef
                  continue
              if bekle < -6 * 3600:
                  print(f"{folder}: 6 saatten fazla gecikmiş, fiyatlar eskimiş olabilir; paylaşılmadı")
                  if not KURU:
                      done.write_text(json.dumps({"atlandi": "gecikme"}), encoding="utf-8")
                  continue
          cap_file = folder / "aciklama.txt"
          caption = cap_file.read_text(encoding="utf-8").strip() if cap_file.exists() else ""
          eksik = [f for f in cfg.get("gonderi", []) + cfg.get("hikayeler", []) if not (folder / f).exists()]
          if eksik:
              print(f"{folder}: eksik dosya {eksik}, atlandı"); hata = True; continue
          print(f"{folder}: {len(cfg.get('gonderi', []))} gönderi görseli, {len(cfg.get('hikayeler', []))} hikaye")
          if KURU:
              continue
          sonuc = {"zaman": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "gonderi": None, "hikayeler": [], "hatalar": []}
          try:
              if cfg.get("gonderi"):
                  sonuc["gonderi"] = post(folder, cfg["gonderi"], caption)
                  print("  gönderi paylaşıldı:", sonuc["gonderi"])
          except Exception as e:
              sonuc["hatalar"].append(f"gonderi: {e}"); print("  HATA", e); hata = True
          for f in cfg.get("hikayeler", []):
              try:
                  sonuc["hikayeler"].append(story(folder, f)); print("  hikaye paylaşıldı:", f)
              except Exception as e:
                  sonuc["hatalar"].append(f"{f}: {e}"); print("  HATA", e); hata = True
          # Tekrar paylaşımı önlemek için sonuç her durumda yazılır.
          done.write_text(json.dumps(sonuc, ensure_ascii=False, indent=2), encoding="utf-8")
          kaydet(folder)
      if KURU or not BEKLE or sonraki is None or sonraki > bitis:
          break
      uyku = max(5, sonraki - time.time() + 5)
      print(f"Sıradaki paket için {int(uyku // 60)} dk bekleniyor"); sys.stdout.flush()
      time.sleep(uyku)
    if hata:
        sys.exit(1)


if __name__ == "__main__":
    main()
