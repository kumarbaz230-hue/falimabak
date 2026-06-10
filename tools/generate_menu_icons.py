"""
FalımaBak — menü ikonları (256px, fal temalı vektör çizim).
Unsplash yerine her fal türüne özel çizim — yanlış fotoğraf riski yok.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(BASE, exist_ok=True)
S = 256


def _zemin(ust, alt):
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for y in range(S):
        t = y / max(S - 1, 1)
        r = int(ust[0] + (alt[0] - ust[0]) * t)
        g = int(ust[1] + (alt[1] - ust[1]) * t)
        b = int(ust[2] + (alt[2] - ust[2]) * t)
        d.line([(0, y), (S, y)], fill=(r, g, b, 255))
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).ellipse([6, 6, S - 6, S - 6], fill=255)
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


def _cerceve(img):
    d = ImageDraw.Draw(img)
    d.ellipse([3, 3, S - 3, S - 3], outline=(255, 215, 0, 220), width=4)
    d.ellipse([10, 10, S - 10, S - 10], outline=(255, 255, 255, 70), width=2)
    return img


def _golge(img):
    sh = img.filter(ImageFilter.GaussianBlur(5))
    canvas = Image.new('RGBA', (S + 12, S + 12), (0, 0, 0, 0))
    canvas.paste(sh, (6, 6), sh)
    canvas.paste(img, (0, 0), img)
    return canvas


def _kaydet(ad, img):
    yol = os.path.join(BASE, ad)
    _golge(_cerceve(img)).save(yol, 'PNG')
    print(f'OK {ad}', flush=True)


def ikon_tarot():
    """Kristal küre + tarot kartı."""
    img = _zemin((18, 12, 42), (40, 22, 72))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2 - 8
    # Küre
    for i in range(72, 0, -2):
        t = i / 72
        d.ellipse([cx - i, cy - i, cx + i, cy + i],
                  fill=(int(90 * t), int(50 * t), int(180 * t), 200))
    d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], outline=(180, 140, 255, 200), width=2)
    d.ellipse([cx - 22, cy - 30, cx - 6, cy - 14], fill=(255, 255, 255, 120))
    # Altın kaide
    d.polygon([(cx - 28, cy + 52), (cx + 28, cy + 52), (cx + 18, cy + 72), (cx - 18, cy + 72)],
              fill=(255, 200, 60, 255))
    # Mini tarot kartı
    d.rounded_rectangle([cx + 38, cy - 48, cx + 78, cy + 8], radius=6,
                        fill=(124, 77, 255, 230), outline=(255, 215, 0, 180), width=2)
    d.polygon([(cx + 58, cy - 38), (cx + 64, cy - 22), (cx + 52, cy - 22)], fill=(255, 215, 0, 255))
    # Yıldızlar
    for sx, sy in [(48, 52), (200, 60), (62, 200), (196, 188)]:
        d.ellipse([sx, sy, sx + 4, sy + 4], fill=(255, 236, 170, 200))
    _kaydet('menu_tarot.png', img)


def ikon_kahve():
    """Türk kahvesi fincanı — üstten telve deseni."""
    img = _zemin((36, 18, 10), (58, 32, 18))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    # Fincan dış
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=(120, 78, 52, 255), outline=(255, 180, 80, 200), width=3)
    # Kahve yüzeyi
    d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=(62, 38, 22, 255))
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=(82, 48, 28, 255))
    # Telve desenleri
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = cx + int(38 * math.cos(rad))
        y1 = cy + int(38 * math.sin(rad))
        x2 = cx + int(18 * math.cos(rad + 0.4))
        y2 = cy + int(18 * math.sin(rad + 0.4))
        d.line([(x1, y1), (x2, y2)], fill=(45, 25, 12, 220), width=3)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=(100, 60, 35, 180))
    # Kulplu fincan silüeti
    d.arc([cx + 48, cy - 20, cx + 98, cy + 30], 270, 90, fill=(255, 180, 80, 220), width=5)
    _kaydet('menu_kahve.png', img)


def ikon_astroloji():
    """Burç yıldızı + takım yıldızı noktaları."""
    img = _zemin((8, 16, 42), (14, 32, 68))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    # Büyük 5 köşeli yıldız
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        r = 62 if i % 2 == 0 else 28
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=(255, 215, 0, 255), outline=(255, 236, 120, 200))
    # Takım yıldızı çizgileri
    nokta = [(52, 78), (88, 52), (128, 68), (168, 48), (204, 82), (190, 128), (148, 148)]
    for x, y in nokta:
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(100, 200, 255, 255))
    d.line([(52, 78), (88, 52), (128, 68), (168, 48)], fill=(100, 200, 255, 120), width=2)
    d.line([(128, 68), (204, 82), (190, 128), (148, 148)], fill=(100, 200, 255, 120), width=2)
    _kaydet('menu_astroloji.png', img)


def ikon_elfali():
    """Avuç içi — fal çizgileri."""
    img = _zemin((28, 14, 40), (48, 24, 62))
    d = ImageDraw.Draw(img)
    cx = S // 2
    # Avuç şekli
    d.polygon([
        (cx, 48), (cx - 58, 100), (cx - 52, 178), (cx - 18, 210),
        (cx + 18, 210), (cx + 52, 178), (cx + 58, 100),
    ], fill=(255, 210, 190, 255), outline=(220, 160, 140, 200), width=2)
    # Parmak boşlukları (üst)
    for dx in (-38, -12, 12, 38):
        d.ellipse([cx + dx - 10, 42, cx + dx + 10, 72], fill=(240, 185, 165, 255))
    # Fal çizgileri
    d.arc([cx - 42, 88, cx + 42, 168], 200, 340, fill=(180, 70, 100, 255), width=3)
    d.arc([cx - 32, 108, cx + 32, 188], 200, 340, fill=(160, 60, 90, 220), width=2)
    d.line([(cx, 72), (cx, 188)], fill=(170, 65, 95, 240), width=3)
    d.line([(cx - 28, 130), (cx + 30, 118)], fill=(150, 55, 85, 200), width=2)
    _kaydet('menu_elfali.png', img)


def ikon_diger():
    """İskambil + nazar + çiçek — diğer fallar."""
    img = _zemin((12, 28, 22), (20, 48, 36))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    # İskambil kart (sol) — kupa sembolü
    d.rounded_rectangle([cx - 78, cy - 52, cx - 22, cy + 38], radius=8,
                        fill=(240, 240, 250, 255), outline=(255, 215, 0, 180), width=2)
    d.polygon([(cx - 50, cy + 18), (cx - 50, cy - 2), (cx - 38, cy - 14), (cx - 62, cy - 14)],
              fill=(220, 40, 40, 255))
    d.ellipse([cx - 56, cy + 2, cx - 44, cy + 14], fill=(220, 40, 40, 255))
    # Nazar boncuğu (sağ)
    d.ellipse([cx + 18, cy - 48, cx + 78, cy + 12], fill=(30, 80, 200, 255), outline=(255, 255, 255, 200), width=2)
    d.ellipse([cx + 34, cy - 32, cx + 62, cy - 4], fill=(255, 255, 255, 255))
    d.ellipse([cx + 42, cy - 24, cx + 54, cy - 12], fill=(20, 20, 30, 255))
    # Çiçek (alt)
    for a in range(0, 360, 72):
        rad = math.radians(a)
        px = cx + int(36 * math.cos(rad))
        py = cy + 52 + int(18 * math.sin(rad))
        d.ellipse([px - 12, py - 12, px + 12, py + 12], fill=(255, 120, 180, 230))
    d.ellipse([cx - 10, cy + 42, cx + 10, cy + 62], fill=(255, 215, 0, 255))
    # Parıltı
    d.line([(cx - 8, cy - 68), (cx + 8, cy - 52)], fill=(0, 230, 118, 220), width=3)
    d.line([(cx, cy - 72), (cx, cy - 48)], fill=(0, 230, 118, 220), width=3)
    _kaydet('menu_diger.png', img)


def ikon_ruya():
    """Hilal ay + bulut + yıldız — rüya tabiri."""
    img = _zemin((14, 10, 38), (30, 16, 58))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2 - 18
    bg = (24, 18, 50)
    # Hilal ay
    d.ellipse([cx - 54, cy - 54, cx + 54, cy + 54], fill=(255, 236, 160, 255))
    d.ellipse([cx - 30, cy - 58, cx + 68, cy + 46], fill=(*bg, 255))
    d.ellipse([cx - 54, cy - 54, cx + 54, cy + 54], outline=(255, 215, 100, 180), width=2)
    # Bulutlar
    for bx, by, bw in [(-62, 38, 48), (-28, 28, 56), (18, 34, 52)]:
        d.ellipse([cx + bx, cy + by, cx + bx + bw, cy + by + 36], fill=(190, 178, 230, 215))
        d.ellipse([cx + bx + 12, cy + by - 10, cx + bx + bw - 8, cy + by + 28], fill=(210, 198, 245, 230))
    # Yıldızlar
    for sx, sy, r in [(52, 62, 4), (198, 48, 3), (186, 178, 3), (64, 188, 2)]:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 255, 210, 255))
    # Rüya baloncukları
    for bx, by in [(58, -68), (72, -58), (86, -48)]:
        d.ellipse([cx + bx, cy + by, cx + bx + 10, cy + by + 10], fill=(180, 160, 255, 200))
    _kaydet('menu_ruya.png', img)


def main():
    import sys
    if '--hepsi' in sys.argv:
        ikon_tarot()
        ikon_kahve()
        ikon_astroloji()
        ikon_elfali()
        ikon_diger()
    ikon_ruya()
    print('Menu ikonlari hazir.', flush=True)


if __name__ == '__main__':
    main()
