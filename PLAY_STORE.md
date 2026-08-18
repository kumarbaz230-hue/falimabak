# FalımaBak — Play Store Yayın Rehberi

## 1. AdMob hesabı (reklamlar)

1. [AdMob](https://admob.google.com/) → Uygulama ekle → **Android**
2. Paket adı: `org.kumar.falimabak.falimabak`
3. Oluştur:
   - **Banner** reklam birimi
   - **Interstitial** (geçiş) reklam birimi — fal sonrası ara sıra
   - **Rewarded** (ödüllü) reklam birimi — fal limiti dolunca +1 hak
4. `secrets.json` dosyana yaz (repo'ya **ekleme**):

```json
{
  "gemini_api_key": "AIza...",
  "admob_test_mod": false,
  "admob_app_id": "ca-app-pub-XXXX~YYYY",
  "admob_banner_id": "ca-app-pub-XXXX/ZZZZ",
  "admob_interstitial_id": "ca-app-pub-XXXX/WWWW",
  "admob_rewarded_id": "ca-app-pub-XXXX/RRRR"
}
```

5. `buildozer.spec` içinde `android.meta_data` satırını gerçek **App ID** ile güncelle.

Test için `admob_test_mod: true` bırak — Google test reklamları gösterilir. `admob_rewarded_id` boş bırakılırsa Google test ödüllü birimi kullanılır.

**Önemli:** APK içine `secrets.json` girmez. Gerçek AdMob birim ID'lerini `config.ornek.json` dosyasına yaz (reklam birim ID'leri gizli değildir). Ödüllü birim ID'sini AdMob → Reklam birimleri → **Ödüllü** oluşturduktan sonra ekle.

---

## 2. Gizlilik politikası URL

Play Console **Gizlilik politikası URL** alanına:

```
https://kumarbaz230-hue.github.io/falimabak/gizlilik.html
```

GitHub Pages etkinleştir:
- Repo → Settings → Pages → Source: **GitHub Actions**
- Push sonrası otomatik deploy olur

**Gizlilik:** `https://kumarbaz230-hue.github.io/falimabak/gizlilik.html`

**app-ads.txt (AdMob):** `https://kumarbaz230-hue.github.io/falimabak/app-ads.txt`

---

## 2b. app-ads.txt (AdMob doğrulama)

Dosya repoda hazır: `store/app-ads.txt`

Play Console'da uygulama yayınlanırken **Geliştirici web sitesi** alanına şunu yaz:
```
https://kumarbaz230-hue.github.io/falimabak
```

AdMob dosyayı şu adresten arar (7 güne kadar sürebilir):
```
https://kumarbaz230-hue.github.io/falimabak/app-ads.txt
```

AdMob → Uygulamalar → app-ads.txt sekmesinde **"app-ads.txt dosyasını ayarlama"** → talimatları takip et.

Uygulama henüz Play'de yoksa "henüz istek yok" uyarısı normaldir; mağazaya yükledikten sonra düzelir.

---

## 3. İmzalama anahtarı (keystore)

PowerShell (bir kez):

```powershell
keytool -genkey -v -keystore falimabak-release.keystore -alias falimabak -keyalg RSA -keysize 2048 -validity 10000
```

- Keystore dosyasını **asla** Git'e ekleme
- Şifreleri güvenli yerde sakla

Release build (lokal):

```powershell
$env:P4A_RELEASE_KEYSTORE = "C:\yol\falimabak-release.keystore"
$env:P4A_RELEASE_KEYSTORE_PASSWD = "sifren"
$env:P4A_RELEASE_KEYALIAS = "falimabak"
$env:P4A_RELEASE_KEYALIAS_PASSWD = "sifren"
buildozer android release
```

Çıktı: `bin/falimabak-1.9.1-arm64-v8a_armeabi-v7a-release.aab`

---

## 4. GitHub Actions release

`.github/workflows/android-release.yml` — manuel çalıştır.

GitHub repo Secrets ekle:
| Secret | Açıklama |
|--------|----------|
| `KEYSTORE_BASE64` | keystore dosyasının base64 hali |
| `KEYSTORE_PASSWORD` | keystore şifresi |
| `KEY_ALIAS` | falimabak |
| `KEY_PASSWORD` | alias şifresi |

---

## 5. Play Console listesi

| Alan | Öneri |
|------|--------|
| **Uygulama adı** | FalımaBak — Tarot & Kahve Falı |
| **Kısa açıklama** | Tarot, kahve, el ve astroloji falı. Fotoğraf çek, anında yorum al. |
| **Uzun açıklama** | `store/listing_tr.txt` |
| **Kategori** | Yaşam Tarzı |
| **İçerik derecelendirmesi** | Anket doldur (şiddet yok, simüle edilmiş fal) |
| **Hedef kitle** | 13+ |

### Data safety (Veri güvenliği)

- Konum: **Hayır**
- Kişisel bilgi: **İsteğe bağlı isim** (cihazda)
- Fotoğraflar: **Evet** — fal yorumu için
- Reklam kimliği: **Evet** — AdMob
- Veri şifreleme: transit (HTTPS)
- Silme: kullanıcı geçmişi temizleyebilir

---

## 6. Store görselleri

Gerekli:
- **512×512** ikon (zaten `assets/app_icon.png`)
- **1024×500** feature graphic
- **En az 2** telefon ekran görüntüsü (1080×1920 veya 9:16)

Mevcut uygulama ekranından screenshot al veya `tools/generate_store_assets.py` çalıştır.

---

## 7. Sürüm kontrol listesi

- [ ] `secrets.json` gerçek AdMob + Gemini key
- [ ] `buildozer.spec` meta_data gerçek App ID
- [ ] Gizlilik URL canlı
- [ ] Release AAB imzalı
- [ ] Internal testing → kapalı test → production

---

## 8. Reklam gelmiyorsa teşhis

AdMob panelindeki **"Hazır"** durumu tek başına cihazın reklam isteği gönderdiğini göstermez. Önce yeni oluşturulan AAB/APK'yı gerçekten telefona kurup test edin; Play Store'daki eski sürümdeki kod değişiklikleri otomatik olarak çalışmaz.

1. Geçici bir test build'inde `config.ornek.json` içindeki `admob_test_mod` değerini `true` yapın. Google'ın test banner'ı bile görünmüyorsa sorun canlı reklam doluluğu değil, manifest/SDK/Android bridge tarafındadır. Test reklamlarına tıklamayın.
2. Telefonda logcat'te şu mesajları arayın:
   - `AdMob SDK başlatıldı`
   - `Banner reklam isteği gönderildi`
   - `Banner reklam yüklendi`
   - veya `Banner reklam yüklenemedi: kod / alan / mesaj`
3. `3` genellikle **no fill**, `2` ağ, `1` geçersiz istek, `0` dahili hata anlamına gelir. No fill durumunda interneti, ülkeyi, reklam biriminin etkinliğini ve AdMob Policy Center'daki reklam sunma kısıtlarını kontrol edin.
4. AdMob → **Raporlar** bölümünde önce **Ad requests** değerine bakın. İstek sayısı sıfırsa kod/manifest/uygulama sürümü; istek var ama gösterim sıfırsa birim, no-fill veya politika sorunudur.
5. `app-ads.txt` adresi tarayıcıda doğrudan yalnızca tek satır düz metin döndürmeli ve Play Console'daki geliştirici web sitesi alanı bu alan adıyla aynı olmalıdır. AdMob doğrulaması birkaç gün sürebilir.

Log almak için USB hata ayıklama açık cihazda:

```bash
adb logcat -c
adb logcat -v time | grep -iE "AdMob|Ads|Banner reklam|Interstitial|Ödüllü"
```

---

## Paket bilgisi

- **Application ID:** `org.kumar.falimabak.falimabak`
- **Sürüm:** 1.9.1
- **Min SDK:** 24 (Android 7.0)
- **Target SDK:** 36
