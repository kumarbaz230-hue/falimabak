"""FalımaBak — premium PNG üretici (banner, menü kartları, splash). İkon: ikon_olustur()."""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(BASE, exist_ok=True)
WIN = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')

random.seed(42)

KARTLAR = {
    'tarot': {'c1': (22, 16, 48), 'c2': (38, 24, 78), 'accent': (124, 77, 255)},
    'kahve': {'c1': (36, 20, 14), 'c2': (62, 34, 22), 'accent': (255, 145, 0)},
    'astroloji': {'c1': (12, 22, 48), 'c2': (18, 38, 72), 'accent': (64, 196, 255)},
    'elfali': {'c1': (28, 18, 44), 'c2': (48, 28, 68), 'accent': (224, 64, 251)},
    'diger': {'c1': (14, 32, 26), 'c2': (22, 52, 40), 'accent': (0, 230, 118)},
}


def _font(boyut, kalin=False):
    for ad in ('segoeuib.ttf', 'segoeui.ttf') if kalin else ('segoeui.ttf',):
        yol = os.path.join(WIN, ad)
        if os.path.isfile(yol):
            return ImageFont.truetype(yol, boyut)
    return ImageFont.load_default()


def _gradient(w, h, ust, alt):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = int(ust[0] + (alt[0] - ust[0]) * t)
        g = int(ust[1] + (alt[1] - ust[1]) * t)
        b = int(ust[2] + (alt[2] - ust[2]) * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
    return img


def _yildiz_serpiştir(draw, w, h, adet=18):
    for _ in range(adet):
        x, y = random.randint(8, w - 8), random.randint(8, h - 8)
        s = random.choice([1, 2])
        draw.ellipse([x, y, x + s, y + s], fill=(255, 236, 170, random.randint(60, 180)))


def _yuvarlak_kart(zemin, r=24):
    mask = Image.new('L', zemin.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, zemin.width - 1, zemin.height - 1], radius=r, fill=255)
    out = Image.new('RGBA', zemin.size, (0, 0, 0, 0))
    out.paste(zemin, (0, 0), mask)
    return out


def menu_banner_olustur():
    w, h = 1080, 200
    zemin = _gradient(w, h, (14, 10, 32), (28, 18, 58))
    draw = ImageDraw.Draw(zemin)

    _yildiz_serpiştir(draw, w, h, 22)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=26, outline=(255, 215, 0, 190), width=3)
    draw.rounded_rectangle([6, 6, w - 7, h - 7], radius=22, outline=(140, 100, 220, 70), width=1)
    draw.rounded_rectangle([0, 0, 7, h], radius=3, fill=(255, 215, 0, 220))

    # Sağ dekor — mistik halka (yazı yok)
    cx, cy = w - 110, h // 2
    for i in range(58, 0, -3):
        t = i / 58
        draw.ellipse(
            [cx - i, cy - i, cx + i, cy + i],
            outline=(int(180 * t), int(140 * t), int(255 * t), int(90 * t)),
            width=2,
        )
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(255, 215, 0, 200))

    f1 = _font(50, True)
    f2 = _font(22, False)
    draw.text((34, 48), 'FalımaBak', font=f1, fill=(255, 215, 0, 255))
    draw.text((34, 118), 'Geleceğinizi Keşfedin', font=f2, fill=(220, 212, 240, 255))
    draw.text((34, 152), 'Tarot  ·  Kahve  ·  El  ·  Astroloji', font=_font(18), fill=(150, 142, 180, 255))

    yol = os.path.join(BASE, 'menu_banner.png')
    _yuvarlak_kart(zemin, 26).save(yol, 'PNG')
    print(f'Menu banner: {yol}')


def menu_kart_olustur(anahtar, cfg):
    w, h = 1080, 192
    zemin = _gradient(w, h, cfg['c1'], cfg['c2'])
    draw = ImageDraw.Draw(zemin)
    _yildiz_serpiştir(draw, w, h, 10)

    acc = cfg['accent']
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=22, outline=(255, 215, 0, 120), width=2)
    draw.rounded_rectangle([0, 10, 8, h - 10], radius=4, fill=(*acc, 230))
    draw.rounded_rectangle([0, 0, 5, h], radius=2, fill=(255, 215, 0, 180))

    # Sol ikon alanı — daire zemin
    ix, iy, ir = 96, h // 2, 56
    for i in range(ir, 0, -2):
        t = i / ir
        draw.ellipse(
            [ix - i, iy - i, ix + i, iy + i],
            fill=(int(acc[0] * t * 0.35), int(acc[1] * t * 0.35), int(acc[2] * t * 0.35), 180),
        )
    draw.ellipse([ix - ir, iy - ir, ix + ir, iy + ir], outline=(255, 215, 0, 140), width=2)

    ikon_yol = os.path.join(BASE, f'menu_{anahtar}.png')
    if os.path.isfile(ikon_yol):
        ikon = Image.open(ikon_yol).convert('RGBA')
        ikon = ikon.resize((88, 88), Image.Resampling.LANCZOS)
        zemin.paste(ikon, (ix - 44, iy - 44), ikon)

    # Sağ ok işareti
    ox = w - 52
    draw.polygon([(ox, iy - 14), (ox + 18, iy), (ox, iy + 14)], fill=(255, 215, 0, 200))

    yol = os.path.join(BASE, f'menu_kart_{anahtar}.png')
    _yuvarlak_kart(zemin, 22).save(yol, 'PNG')
    print(f'Menu kart: {yol}')


def menu_kartlari_olustur():
    tools = os.path.join(os.path.dirname(__file__), 'tools', 'generate_assets.py')
    if os.path.isfile(tools):
        import importlib.util
        spec = importlib.util.spec_from_file_location('gen_assets', tools)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f'İkon üretimi atlandı: {e}', flush=True)
    for key, cfg in KARTLAR.items():
        menu_kart_olustur(key, cfg)


def banner_olustur():
    w, h = 720, 1280
    zemin = _gradient(w, h, (8, 6, 18), (22, 14, 48))
    draw = ImageDraw.Draw(zemin)
    _yildiz_serpiştir(draw, w, h, 80)

    cx, cy = w // 2, h // 2 - 60
    for i in range(150, 0, -3):
        t = i / 150
        draw.ellipse(
            [cx - i, cy - i, cx + i, cy + i],
            fill=(int(55 + 60 * t), int(30 + 35 * t), int(110 + 70 * t), 255),
        )
    draw.ellipse([cx - 152, cy - 152, cx + 152, cy + 152], outline=(255, 215, 0, 220), width=5)

    draw.text((cx, cy + 170), 'FalımaBak', font=_font(54, True), fill=(255, 215, 0), anchor='mm')
    draw.text((cx, cy + 228), 'Geleceğinizi Keşfedin', font=_font(22), fill=(230, 222, 248), anchor='mm')

    yol = os.path.join(BASE, 'splash_banner.png')
    zemin.convert('RGB').save(yol, 'PNG', optimize=True)
    print(f'Splash: {yol}')


def ikon_olustur():
    """Mevcut ikon — dokunma."""
    pass


if __name__ == '__main__':
    menu_banner_olustur()
    banner_olustur()
    # Menü ikonları: tools/generate_assets.py
    import importlib.util
    tools = os.path.join(os.path.dirname(__file__), 'tools', 'generate_assets.py')
    if os.path.isfile(tools):
        spec = importlib.util.spec_from_file_location('gen_assets', tools)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f'İkon: {e}', flush=True)
