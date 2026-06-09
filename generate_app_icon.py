"""FalımaBak — premium görsel üretici (ikon, splash, menü banner)."""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(BASE, exist_ok=True)
WIN = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')

random.seed(42)


def _font(boyut, kalin=False):
    for ad in ('segoeuib.ttf', 'segoeui.ttf') if kalin else ('segoeui.ttf',):
        yol = os.path.join(WIN, ad)
        if os.path.isfile(yol):
            return ImageFont.truetype(yol, boyut)
    return ImageFont.load_default()


def _dikey_gradient(w, h, ust, alt):
    img = Image.new('RGB', (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(ust[0] + (alt[0] - ust[0]) * t)
        g = int(ust[1] + (alt[1] - ust[1]) * t)
        b = int(ust[2] + (alt[2] - ust[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


def _yildizlar(draw, w, h, adet=80, parlak=True):
    for _ in range(adet):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        sz = random.choice([1, 1, 2, 2, 3])
        alpha = random.randint(140, 255) if parlak else random.randint(60, 160)
        renk = (255, 236, 170, alpha) if random.random() > 0.3 else (200, 180, 255, alpha)
        draw.ellipse([x, y, x + sz, y + sz], fill=renk)


def _isik_halkasi(img, cx, cy, r, renk=(255, 215, 0), opak=90):
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(r, 0, -3):
        t = i / r
        a = int(opak * (1 - t) * 0.35)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], outline=(*renk, a), width=2)
    return Image.alpha_composite(img.convert('RGBA'), layer)


def _metin_golge(draw, xy, text, font, fill, golge=(0, 0, 0, 160), offset=2):
    x, y = xy
    draw.text((x + offset, y + offset), text, font=font, fill=golge)
    draw.text((x, y), text, font=font, fill=fill)


def ikon_olustur():
    s = 512
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for i in range(s // 2, 0, -2):
        t = i / (s // 2)
        c = (
            int(12 + 30 * t),
            int(8 + 18 * t),
            int(28 + 55 * t),
            255,
        )
        draw.ellipse([s // 2 - i, s // 2 - i, s // 2 + i, s // 2 + i], fill=c)

    draw.ellipse([36, 36, 476, 476], outline=(255, 215, 0, 230), width=10)
    draw.ellipse([44, 44, 468, 468], outline=(180, 130, 255, 100), width=4)
    draw.ellipse([52, 52, 460, 460], outline=(255, 236, 120, 60), width=2)

    cx, cy = s // 2, s // 2 - 24
    for i in range(118, 0, -2):
        t = i / 118
        draw.ellipse(
            [cx - i, cy - i, cx + i, cy + i],
            fill=(int(70 + 50 * t), int(35 + 40 * t), int(130 + 60 * t), 255),
        )
    draw.ellipse([cx - 118, cy - 118, cx + 118, cy + 118], outline=(255, 215, 0, 200), width=3)
    draw.ellipse([cx - 42, cy - 58, cx + 18, cy + 8], fill=(255, 255, 255, 85))

    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1 = cx + int(math.cos(rad) * 95)
        y1 = cy + int(math.sin(rad) * 95)
        x2 = cx + int(math.cos(rad) * 115)
        y2 = cy + int(math.sin(rad) * 115)
        draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0, 120), width=2)

    _yildizlar(draw, s, s, adet=28)
    f = _font(44, True)
    txt = 'FalımaBak'
    bb = draw.textbbox((0, 0), txt, font=f)
    tx = (s - bb[2] + bb[0]) // 2 - bb[0]
    ty = 378
    _metin_golge(draw, (tx, ty), txt, f, (255, 215, 0, 255), offset=3)
    draw.text((tx, ty), txt, font=f, fill=(255, 215, 0, 255))

    img = _isik_halkasi(img, s // 2, cy, 130)
    yol = os.path.join(BASE, 'app_icon.png')
    img.save(yol, 'PNG')
    print(f'İkon: {yol}')
    return yol


def menu_banner_olustur():
    """Ana menü üst banner — mobil genişliğe uygun oran."""
    w, h = 1080, 220
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for y in range(h):
        t = y / max(h - 1, 1)
        renk = (int(16 + 10 * t), int(12 + 8 * t), int(36 + 14 * t), 255)
        draw.line([(0, y), (w, y)], fill=renk)

    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=28, outline=(255, 215, 0, 200), width=3)
    draw.rounded_rectangle([5, 5, w - 6, h - 6], radius=24, outline=(150, 110, 230, 80), width=2)
    draw.rounded_rectangle([0, 0, 8, h], radius=4, fill=(255, 215, 0, 235))

    f = _font(52, True)
    f2 = _font(24, False)
    f3 = _font(20, False)
    _metin_golge(draw, (36, 42), 'FalımaBak', f, (255, 215, 0, 255), offset=2)
    draw.text((36, 42), 'FalımaBak', font=f, fill=(255, 215, 0, 255))
    draw.text((36, 108), 'Premium fal deneyimi', font=f2, fill=(225, 218, 245, 255))
    draw.text((36, 148), 'Tarot · Kahve · El · Astroloji', font=f3, fill=(155, 147, 184, 255))

    badge_w, badge_h = 168, 44
    bx, by = w - badge_w - 28, 28
    draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=22, fill=(255, 215, 0, 40))
    draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=22, outline=(255, 215, 0, 210), width=2)
    draw.text((bx + badge_w // 2, by + badge_h // 2), 'PREMIUM', font=_font(18, True), fill=(255, 215, 0), anchor='mm')

    yol = os.path.join(BASE, 'menu_banner.png')
    img.save(yol, 'PNG')
    print(f'Menu banner: {yol}')
    return yol


def banner_olustur():
    """Splash — 720x1280 optimize (APK boyutu)."""
    w, h = 720, 1280
    img = _dikey_gradient(w, h, (8, 6, 18), (22, 14, 48)).convert('RGBA')
    draw = ImageDraw.Draw(img)
    _yildizlar(draw, w, h, adet=120)

    for i in range(6):
        cx = random.randint(w // 4, 3 * w // 4)
        cy = random.randint(h // 5, h // 2)
        for r in range(180, 0, -4):
            t = r / 180
            draw.ellipse(
                [cx - r, cy - r, cx + r, cy + r],
                fill=(int(40 * t), int(25 * t), int(80 * t), int(18 * t)),
            )

    cx, cy = w // 2, h // 2 - 80
    for i in range(200, 0, -3):
        t = i / 200
        draw.ellipse(
            [cx - i, cy - i, cx + i, cy + i],
            fill=(int(55 + 60 * t), int(30 + 35 * t), int(110 + 70 * t), 255),
        )
    draw.ellipse([cx - 205, cy - 205, cx + 205, cy + 205], outline=(255, 215, 0, 220), width=6)
    draw.ellipse([cx - 195, cy - 195, cx + 195, cy + 195], outline=(200, 160, 255, 80), width=3)

    draw.line([(cx - 120, cy), (cx + 120, cy)], fill=(255, 215, 0, 60), width=1)
    draw.line([(cx, cy - 120), (cx, cy + 120)], fill=(255, 215, 0, 60), width=1)

    f1 = _font(58, True)
    f2 = _font(24, False)
    f3 = _font(18, False)
    _metin_golge(draw, (cx, cy + 180), 'FalımaBak', f1, (255, 215, 0, 255), offset=3)
    draw.text((cx, cy + 180), 'FalımaBak', font=f1, fill=(255, 215, 0), anchor='mm')
    draw.text((cx, cy + 240), 'Geleceğinizi Keşfedin', font=f2, fill=(230, 222, 248), anchor='mm')
    draw.text((cx, cy + 278), '✦  Premium Fal Deneyimi  ✦', font=f3, fill=(200, 175, 255), anchor='mm')

    img = _isik_halkasi(img, cx, cy, 160, opak=110)
    yol = os.path.join(BASE, 'splash_banner.png')
    img.convert('RGB').save(yol, 'PNG', optimize=True)
    print(f'Splash: {yol}')
    return yol


if __name__ == '__main__':
    banner_olustur()
    menu_banner_olustur()
