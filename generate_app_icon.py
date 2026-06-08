"""FalımaBak uygulama ikonu oluşturur (512x512 PNG)."""

import os
from PIL import Image, ImageDraw, ImageFont

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(ASSETS, exist_ok=True)

WIN = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts')


def _font(boyut, kalin=False):
    ad = 'segoeuib.ttf' if kalin else 'segoeui.ttf'
    yol = os.path.join(WIN, ad)
    if os.path.isfile(yol):
        return ImageFont.truetype(yol, boyut)
    return ImageFont.load_default()


def olustur():
    s = 512
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Koyu mor gradient daire
    for i in range(s // 2, 0, -2):
        t = i / (s // 2)
        r = int(15 + 30 * t)
        g = int(12 + 20 * t)
        b = int(32 + 50 * t)
        draw.ellipse([s // 2 - i, s // 2 - i, s // 2 + i, s // 2 + i], fill=(r, g, b, 255))

    # Altın halka
    draw.ellipse([56, 56, 456, 456], outline=(255, 215, 0, 220), width=6)

    # Kristal küre (basit)
    draw.ellipse([140, 120, 372, 340], fill=(120, 80, 200, 200), outline=(200, 170, 255, 180), width=3)
    draw.ellipse([180, 150, 280, 220], fill=(255, 255, 255, 60))

    # Yıldızlar
    for x, y, sz in [(100, 90, 4), (400, 110, 3), (380, 380, 4), (120, 400, 3)]:
        draw.ellipse([x, y, x + sz * 2, y + sz * 2], fill=(255, 236, 110, 230))

    # Yazı
    f = _font(52, True)
    draw.text((s // 2, 400), 'FalımaBak', font=f, fill=(255, 215, 0, 255), anchor='mm')

    yol = os.path.join(ASSETS, 'app_icon.png')
    img.save(yol, 'PNG')
    print(f'İkon oluşturuldu: {yol}')
    return yol


if __name__ == '__main__':
    olustur()
