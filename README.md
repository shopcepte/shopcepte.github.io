# shopcepte.github.io

ShopCepte (@shopcepte) günlük fırsat paylaşımlarının yayın deposu.

- `kuyruk/<tarih-saat>/` klasörüne görseller (JPEG), `aciklama.txt` ve `paylas.json` eklenir.
- `main` dalına gelen her yeni klasörü **Instagram'a paylas** iş akışı Instagram'ın resmi API'siyle paylaşır
  ve klasöre `PAYLASILDI.json` yazar (aynı içerik ikinci kez paylaşılmaz).
- Paylaşım anahtarı yalnızca depo sırrı `IG_TOKEN` içinde durur (Settings → Secrets and variables → Actions).
  Anahtar yaklaşık 60 günde bir yenilenmelidir.
- Bağlantıyı paylaşım yapmadan denemek için: Actions → Instagram'a paylas → Run workflow (kuru = işaretli).
