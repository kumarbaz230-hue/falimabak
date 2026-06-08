"""
FalımaBak - Google Colab ile APK build (GitHub Actions yedek yolu)

Colab'da yeni notebook ac, bu dosyadaki hucreleri sirayla calistir.
Veya: GitHub'dan zip indir -> Colab'a yukle -> buildozer calistir.
"""

# %% Hucre 1 - Bagimliliklar
# !sudo apt-get update
# !sudo apt-get install -y git zip unzip openjdk-17-jdk autoconf libtool pkg-config \
#   zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
#   libgl1-mesa-dev libgles2-mesa-dev libegl1-mesa-dev \
#   libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
#   libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev libavutil-dev
# !pip install "cython==0.29.34" "buildozer==1.5.0"

# %% Hucre 2 - Projeyi al
# Secenek A: GitHub'dan klonla (private ise token gerekir)
# !git clone https://github.com/kumarbaz230-hue/falimabak.git
# %cd falimabak

# Secenek B: Bilgisayardan ZIP yukle (Colab sol menuden Files -> Upload)
# %cd /content/falimabak

# %% Hucre 3 - Build
# !cp config.ornek.json config.json
# !yes | buildozer -v android debug

# %% Hucre 4 - APK indir
# from google.colab import files
# import glob
# apk = glob.glob("bin/*.apk")[0]
# files.download(apk)
# print("APK indirildi:", apk)
