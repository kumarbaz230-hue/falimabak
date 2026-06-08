# FalımaBak - Google Colab APK Build
# colab.research.google.com ac -> Yeni notebook -> hucreleri sirayla calistir

# === HUCRE 1 ===
# !sudo apt-get update -qq
# !sudo apt-get install -y -qq git zip unzip openjdk-17-jdk autoconf libtool pkg-config \
#   zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
#   libgl1-mesa-dev libgles2-mesa-dev libegl1-mesa-dev \
#   libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
#   libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libavutil-dev
# !pip install -q "cython==0.29.34" "buildozer==1.5.0"

# === HUCRE 2 - GitHub'dan cek ===
# !git clone https://github.com/kumarbaz230-hue/falimabak.git
# %cd falimabak

# === HUCRE 3 - Build (20-40 dk) ===
# !cp config.ornek.json config.json
# !yes | buildozer -v android debug

# === HUCRE 4 - APK indir ===
# from google.colab import files
# import glob
# apk = glob.glob("bin/*.apk")[0]
# print("APK:", apk)
# files.download(apk)
