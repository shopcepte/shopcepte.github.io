# ShopCepte Fırsat Ekibi — günlük çalışma talimatı

Hesap: @shopcepte (Instagram). Kullanıcı tam otomatik paylaşımı onayladı: onay sorma, işi bitir, sonunda kısa Türkçe özet yaz.
Bu görev günde 3 kez tetiklenir (öğle, akşamüstü, akşam). **Günün içeriğini ilk başarılı çalışma hazırlar; sonrakiler hiçbir şey yapmadan biter.** Kullanımı (token) düşük tut: gereksiz ekran görüntüsü, tekrar okuma ve uzun açıklama yapma.

## 0. Hızlı çıkış
Depoyu klonla (`git clone --depth 1`). Bugünün tarihiyle (İstanbul) başlayan `kuyruk/YYYY-AA-GG-*` klasörü varsa: "Bugünün içeriği hazır" de ve bitir.
Tarayıcıya (kullanıcının Chrome'u / yerleşik tarayıcı) ulaşılamıyorsa: hiçbir şey yapma, "bilgisayar ya da Chrome kapalıydı, bu tur atlandı" de ve bitir. Bildirim gerekmez.

## 1. Zaman pencereleri (İstanbul saati)
A 12:00–13:00 · B 17:30–19:00 · C 20:30–22:00.
Şu andan sonra bitecek her pencere için 1 "paket" hazırla (en fazla 3). Her paketin paylaşım zamanı o pencerenin içinde **rastgele bir dakika** olsun (pencere başlamışsa: şimdi + rastgele 6–25 dk). Yuvarlak dakikalardan (:00, :15, :30, :45) kaçın; her gün farklı olsun (`random` kullan).
Saat 21:40'tan sonraysa bugün için paket hazırlama; bitir.

## 2. Ürün bulma (yalnızca kullanıcının tarayıcısından; çalışma ortamından hepsiburada.com engelli)
- Kaynaklar: https://www.hepsiburada.com/gunun-firsati-teklifi ve gerekirse https://www.hepsiburada.com/kampanyalar ile kategori sayfaları. Sayfayı sona kadar kaydır.
- JS ile kartları çıkar: her `a[href*="-p-"]` için, içinde tek ürün kimliği (`-p-<ID>`) kalan en büyük üst eleman karttır. Fiyatlar `/[\d.]+(,\d+)? TL/g` (ilk = eski, son = yeni). Değerlendirme sayısı parantez içindeki sayı, puan, "En çok satan" rozeti, "30 günün en düşük fiyatı" etiketi, ürün yolu (`a.pathname`, sorgu dizesi olmadan).
- JS çıktısında çerez/sorgu dizesi döndürme (engellenir); kısa metin döndür.
- Puan: indirim%×1.2 + log10(1+yorum)×12 + çok satan 15 + 30 günün en düşüğü 10 + puan≥4.3 ise 6 + fiyat<3000 ise 8, <10000 ise 3, değilse −6.
- Uygunluk: eski fiyat görünür ve indirim ≥ %5 (ya da 30 günün en düşüğü). Fiyatı asla tahmin etme.
- Her paket = **farklı bir kategori/tema**, 4 ürün (ör. mutfak, teknoloji, ev/kış, kişisel bakım, çok satanlar, süpermarket). Son 7 günün `aciklama.txt` dosyalarındaki ürünleri tekrar etme. Gerçek kişi/ünlü yüzü içeren ürün fotoğrafı kullanma.
- Bir tema için 4 uygun ürün çıkmazsa o paketi atla; hiç paket çıkmazsa bildir ve bitir.

## 3. Fotoğraflar
CORS yüzünden indirilemez. Sayfaya tam ekran beyaz bir `div` ekle, görseli `/s/<n>/1000-1000/` adresiyle 560×560 `object-fit:contain` göster, tarayıcının `zoom` ekran görüntüsünü diske kaydet (ölçek ~0.6), tüm ürünler bitince div'i kaldır. PNG'leri `tasarim/img/` altına kopyala (**bu klasörü commit etme**).

## 4. Tasarım (`tasarim/ekip.py`, Python + Pillow, Poppins fontu)
- `post(products, title, subtitle, date, out)` → 1080×1350 gönderi (4 ürün). `story(p, headline, stamp, out)` → 1080×1920 hikaye (tek ürün; altında "LİNK PROFİLDE" yazar).
- Ürün sözlüğü: `img`, `name` (2 satır, `\n`), `old`, `now`, `pct`, `cs` (çok satan), `full` (fotoğraf arka planı beyaz değilse 1), `sub` (hikaye alt satırı).
- Poppins `/usr/share/fonts/truetype/google-fonts/` altında yoksa Google Fonts'tan Bold/Medium/Regular indirip `FD` yolunu uyarlayarak çalıştır (depodaki dosyayı değiştirme).
- Her paket: 1 gönderi + **3 hikaye** (paketin en iyi 3 ürünü). Tarih rozeti "GG AY" (Türkçe, büyük harf). Hikaye damgası: "Fiyatlar GG Ay SS:DD itibarıyladır".
- JPEG kalite 90. Her paketten yalnızca gönderi görselini bir kez açıp kontrol et (taşan yazı, yanlış fiyat).

## 5. Kuyruğa yaz
`kuyruk/YYYY-AA-GG-a/` (b, c) içine: `gonderi.jpg`, `hikaye_1.jpg`…`hikaye_3.jpg`, `aciklama.txt`, `paylas.json`:
`{"zaman": "YYYY-AA-GGTSS:DD:00Z", "gonderi": ["gonderi.jpg"], "hikayeler": ["hikaye_1.jpg","hikaye_2.jpg","hikaye_3.jpg"]}` — `zaman` **UTC** (İstanbul − 3 saat).
Açıklama: `🔥 <BAŞLIK> | GG Ay`, boş satır, ürün başına bir satır (emoji + kısa ad → eski TL yerine yeni TL), boş satır, `👆 Linkler profildeki bağlantıda`, `Fiyatlar GG Ay SS:DD itibarıyladır; sepette geçerlidir, stok ve süreyle sınırlıdır. #işbirliği`, boş satır, 6–8 hedefli hashtag (#hepsiburada #indirim #gününfırsatı #fırsat #shopcepte + temaya özel; #takipet gibi genel etiket yok).

## 6. Link sayfası
Depo kökündeki `linkler.json` dosyasını bugünün tüm paketleriyle yeniden yaz:
`{"guncelleme": "GG Ay SS:DD", "gruplar": [{"baslik": "...", "urunler": [{"ad","eski","yeni","url"}]}]}`; `url` = `https://www.hepsiburada.com` + ürün yolu. (Sayfa: https://shopcepte.github.io/)

## 7. Gönder
Tek commit, `git -c push.negotiate=true push origin main`. Paylaşımı depo yapar (GitHub Actions 15 dakikada bir zamanı gelen paketi paylaşır, `PAYLASILDI.json` yazar). Bekleme, kontrol etme.
Varsa önceki günlerin `PAYLASILDI.json` dosyalarında `hatalar` dolu olan son kaydı özette bildir; token hatasıysa (OAuth / expired / 190): "Meta panosunda yeni token oluşturup GitHub'da IG_TOKEN sırrını güncelle".

## Kurallar
- Token, şifre, doğrulama kodu isteme, arama, girme. Paylaşım anahtarı yalnızca GitHub sırrındadır.
- Bir site "bekle" ya da hata verirse zorlama; dur ve bildir.
- Günde en fazla 3 gönderi + 9 hikaye.
