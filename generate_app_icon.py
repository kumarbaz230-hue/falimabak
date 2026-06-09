"""FalımaBak — uygulama ikonu + açılış banner (premium)."""

import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, 'assets')
os.makedirs(ASSETS, exist_ok=True)
WIN = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')


def _font(boyut, kalin=False):
    ad = 'segoeuib.ttf' if kalin else 'segoeui.ttf'
    yol = os.path.join(WIN, ad)
    if os.path.isfile(yol):
        return ImageFont.truetype(yol, boyut)
    return ImageFont.load_default()


def _gradient_daire(draw, cx, cy, r, ic, dis):
    for i in range(r, 0, -2):
        t = i / r
        rr = int(ic[0] + (dis[0] - ic[0]) * t)
        gg = int(ic[1] + (dis[1] - ic[1]) * t)
        bb = int(ic[2] + (dis[2] - ic[2]) * t)
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(rr, gg, bb, 255))


def ikon_olustur():
    s = 512
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    _gradient_daire(draw, s // 2, s // 2, s // 2 - 8, (15, 12, 32), (45, 28, 88))
    draw.ellipse([48, 48, 464, 464], outline=(255, 215, 0, 240), width=8)
    draw.ellipse([48, 48, 464, 464], outline=(180, 140, 255, 80), width=3)
    _gradient_daire(draw, s // 2, s // 2 - 20, 120, (90, 50, 160), (160, 110, 230))
    draw.ellipse([168, 148, 268, 218], fill=(255, 255, 255, 70))
    for x, y, sz in [(92, 86, 5), (408, 102, 4), (392, 392, 5), (108, 408, 4)]:
        draw.ellipse([x, y, x + sz * 2, y + sz * 2], fill=(255, 236, 110, 240))
    f = _font(46, True)
    draw.text((s // 2, 398), 'FalımaBak', font=f, fill=(255, 215, 0, 255), anchor='mm')
    yol = os.path.join(ASSETS, 'app_icon.png')
    img.save(yol, 'PNG')
    print(f'İkon: {yol}')
    return yol


def banner_olustur():
    """Buildozer presplash + uygulama içi banner."""
    w, h = 480, 854
    img = Image.new('RGB', (w, h), (15, 12, 32))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        r = int(15 + 25 * t)
        g = int(12 + 18 * t)
        b = int(32 + 40 * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    for y in range(h // 3, h):
        t = (y - h // 3) / (h * 2 / 3)
        draw.line([(0, y), (w, y)], fill=(int(24 + 20 * t), int(18 + 12 * t), int(46 + 30 * t)))

    cx, cy = w // 2, h // 2 - 40
    _gradient_daire(draw, cx, cy, 100, (60, 35, 110), (120, 80, 200))
    draw.ellipse([cx - 102, cy - 102, cx + 102, cy + 102], outline=(255, 215, 0, 200), width=4)

    f1 = _font(42, True)
    f2 = _font(18, False)
    draw.text((w // 2, cy + 130), 'FalımaBak', font=f1, fill=(255, 215, 0), anchor='mm')
    draw.text((w // 2, cy + 168), 'Geleceğinizi Keşfedin', font=f2, fill=(214, 208, 232), anchor='mm')

    for i in range(12):
        x = 30 + (i * 37) % (w - 60)
        y = 40 + (i * 53) % (h - 120)
        draw.ellipse([x, y, x + 3, y + 3], fill=(255, 236, 110))

    yol = os.path.join(ASSETS, 'splash_banner.png')
    img.save(yol, 'PNG')
    print(f'Banner: {yol}')
    return yol


def menu_banner_olustur():
    w, h = 720, 200
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=24, fill=(26, 20, 53, 255))
    draw.rounded_rectangle([4, 4, w - 5, h - 5], radius=22, outline=(255, 215, 0, 120), width=2)
    draw.rounded_rectangle([0, 0, 6, h], radius=3, fill=(255, 215, 0, 200))
    f = _font(36, True)
    draw.text((28, 52), 'FalımaBak', font=f, fill=(255, 215, 0))
    f2 = _font(16, False)
    draw.text((28, 100), 'Premium fal deneyimi', font=f2, fill=(214, 208, 232))
    draw.text((28, 128), 'Tarot · Kahve · El · Astroloji', font=f2, fill=(155, 147, 184))
    yol = os.path.join(ASSETS, 'menu_banner.png')
    img.save(yol, 'PNG')
    print(f'Menu banner: {yol}')
    return yol


if __name__ == '__main__':
    ikon_olustur()
    banner_olustur()
    menu_banner_olustur()
