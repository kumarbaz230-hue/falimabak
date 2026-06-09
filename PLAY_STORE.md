# FalımaBak — Play Store Yayın Rehberi

## 1. AdMob hesabı (reklamlar)

1. [AdMob](https://admob.google.com/) → Uygulama ekle → **Android**
2. Paket adı: `org.kumar.falimabak.falimabak`
3. Oluştur:
   - **Banner** reklam birimi
   - **Interstitial** (geçiş) reklam birimi
4. `secrets.json` dosyana yaz (repo'ya **ekleme**):

```json
{
  "gemini_api_key": "AIza...",
  "admob_test_mod": false,
  "admob_app_id": "ca-app-pub-XXXX~YYYY",
  "admob_banner_id": "ca-app-pub-XXXX/ZZZZ",
  "admob_interstitial_id": "ca-app-pub-XXXX/WWWW"
}
```

5. `buildozer.spec` içinde `android.meta_data` satırını gerçek **App ID** ile güncelle.

Test için `admob_test_mod: true` bırak — Google test reklamları gösterilir.

---

## 2. Gizlilik politikası URL

Play Console **Gizlilik politikası URL** alanına:

```
https://kumarbaz230-hue.github.io/falimabak/gizlilik.html
```

GitHub Pages etkinleştir:
- Repo → Settings → Pages → Source: **main** → Folder: `/store` veya `docs`
- `store/gizlilik.html` dosyasını root'a kopyala veya Pages klasörünü ayarla

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

Çıktı: `bin/falimabak-1.1.0-arm64-v8a_armeabi-v7a-release.aab`

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

## Paket bilgisi

- **Application ID:** `org.kumar.falimabak.falimabak`
- **Sürüm:** 1.1.0
- **Min SDK:** 24 (Android 7.0)
- **Target SDK:** 34
