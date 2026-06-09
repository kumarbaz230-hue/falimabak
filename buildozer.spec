[app]

title = FalımaBak
package.name = falimabak
package.domain = org.kumar.falimabak

source.dir = .
source.main = main.py

source.include_exts = py,png,jpg,jpeg,kv,json,webp,ttf,txt
source.include_patterns = assets/*,config.ornek.json,recipes/*
source.exclude_dirs = tests,bin,.git,__pycache__,.buildozer,.venv,venv,env,.idea,user_photos,.github
source.exclude_patterns = license,images/*/*.jpg,*.bat,*.md,config.json,kullanici_veri.json,.env

version = 1.0.0

requirements = python3,kivy==2.3.0,pillow,android,pyjnius==1.5.0

orientation = portrait
fullscreen = 0

android.api = 31
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA

android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True
android.enable_androidx = True

android.presplash_color = #0F0C20

[buildozer]

log_level = 2
warn_on_root = 1
p4a.branch = v2024.01.21
p4a.local_recipes = ./recipes
