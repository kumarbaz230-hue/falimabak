[app]

# ---------------------------------------------------------------------------
# FalımaBak — Android APK (Buildozer)
# Build:  buildozer -v android debug
# Release: buildozer -v android release  (keystore gerekir)
# Not: İlk build Linux veya WSL üzerinde yapılmalıdır.
# ---------------------------------------------------------------------------

title = FalımaBak
package.name = falimabak
package.domain = org.kumar.falimabak

source.dir = .
source.main = main.py

source.include_exts = py,png,jpg,jpeg,kv,json,webp,ttf,txt
source.include_patterns = assets/*,config.ornek.json
source.exclude_dirs = tests,bin,.git,__pycache__,.buildozer,.venv,venv,env,.idea,user_photos,.github
source.exclude_patterns = license,images/*/*.jpg,*.bat,*.md,config.json,kullanici_veri.json,.env

version = 1.0.0

# opencv-python ve tkinter Android'de çalışmaz — dahil edilmedi.
# plyer: mobil kamera/galeri için (kamera.py güncellenince kullanılır).
# Gemini: urllib (stdlib). pyjnius android ile gelir — ayrı yazma.
requirements = python3,kivy,pillow,plyer,android

orientation = portrait
fullscreen = 0

# Uygulama ikonu hazır olunca satırı açın (512x512 PNG önerilir):
# icon.filename = %(source.dir)s/assets/app_icon.png

# API 30 — p4a/Gradle ile en az sorun çıkaran sürüm
android.api = 30
android.minapi = 24
android.ndk = 23b

# Android 13+ galeri için READ_MEDIA_IMAGES eklendi
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,CAMERA

# CI hızı için tek mimari; eski telefon gerekirse armeabi-v7a ekle
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.enable_androidx = True

# Koyu tema / yükleme ekranı (presplash PNG eklenirse açılır)
# presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #0F0C20

# Logcat'te hata ayıklama
# android.logcat_filters = *:S python:D

[buildozer]

log_level = 2
warn_on_root = 1

# p4a.branch = develop
