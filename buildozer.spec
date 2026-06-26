[app]

title = FalımaBak
package.name = falimabak
package.domain = org.kumar.falimabak

source.dir = .
source.main = main.py

source.include_exts = py,png,jpg,jpeg,kv,json,webp,ttf,txt,html,wav,ogg,mp3
source.include_patterns = assets/*,assets/muzik/*,config.ornek.json,store/*
source.exclude_dirs = tests,bin,.git,__pycache__,.buildozer,.venv,venv,env,.idea,user_photos,.github,recipes,tools,images,keystore
source.exclude_patterns = license,images/*/*.jpg,*.bat,config.json,kullanici_veri.json,.env,secrets.json,secrets.ornek.json,assets/muzik/ambiyans.wav

version = 1.8.0

icon.filename = %(source.dir)s/assets/app_icon.png
presplash.filename = %(source.dir)s/assets/splash_banner.png

requirements = python3,kivy==2.3.1,pillow,android,certifi

orientation = portrait
fullscreen = 0
android.window_softinput_mode = adjustResize

android.api = 35
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24

android.permissions = INTERNET,ACCESS_NETWORK_STATE,AD_ID,CAMERA,POST_NOTIFICATIONS,SCHEDULE_EXACT_ALARM,RECEIVE_BOOT_COMPLETED,WAKE_LOCK

# Android: sadece kamera. Medya izinleri yalnizca p4a hook ile kaldirilir (extra_manifest yok).
p4a.hook = %(source.dir)s/hooks/p4a_manifest.py

android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True
android.enable_androidx = True

android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1,androidx.activity:activity:1.8.2,androidx.core:core:1.12.0,com.google.android.gms:play-services-ads:22.6.0

# Bildirim receiver Java siniflari (FalimabakAlarmReceiver / BootReceiver)
android.add_src = java

# Gradle bellek (CI packageDebug OOM önleme)
android.gradle_arguments = -Dorg.gradle.jvmargs=-Xmx2560m,-Dorg.gradle.daemon=false,-Dorg.gradle.parallel=false,-Dorg.gradle.workers.max=1

# AdMob (onaylı hesap — canlı birimler)
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-9430596197237392~1799758284

android.add_resources = android_res/res
android.add_application_xml = %(source.dir)s/android_res/application.xml

android.presplash_color = #0F0C20

# Release AAB: GitHub Actions "Build Release AAB" veya buildozer.spec push
# İmzalama: keystore/PLAY_IMZA.md dosyasına bak

[buildozer]

log_level = 2
warn_on_root = 1
p4a.branch = develop
p4a.local_recipes = recipes
