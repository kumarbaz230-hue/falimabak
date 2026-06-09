"""Kullanıcı ikonlarını assets/user_icons/ → menu_*.png olarak uygular."""

import os
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
SRC = os.path.join(BASE, 'user_icons')
S = 256

MAP = {
    'tarot': 'menu_tarot.png',
    'kahve': 'menu_kahve.png',
    'astroloji': 'menu_astroloji.png',
    'elfali': 'menu_elfali.png',
    'diger': 'menu_diger.png',
}


def _islem(yol):
    img = Image.open(yol).convert('RGBA')
    img = img.resize((S, S), Image.Resampling.LANCZOS)
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).ellipse([4, 4, S - 4, S - 4], fill=255)
    out = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    d = ImageDraw.Draw(out)
    d.ellipse([2, 2, S - 2, S - 2], outline=(255, 215, 0, 220), width=3)
    sh = out.filter(ImageFilter.GaussianBlur(4))
    canvas = Image.new('RGBA', (S + 10, S + 10), (0, 0, 0, 0))
    canvas.paste(sh, (5, 5), sh)
    canvas.paste(out, (0, 0), out)
    return canvas


def main():
    if not os.path.isdir(SRC):
        print('user_icons klasoru yok')
        return 1
    n = 0
    for anahtar, hedef in MAP.items():
        for ad in (f'{anahtar}.png', f'{anahtar}.jpg', f'{anahtar}.webp'):
            yol = os.path.join(SRC, ad)
            if os.path.isfile(yol):
                _islem(yol).save(os.path.join(BASE, hedef), 'PNG')
                print(f'OK {ad} -> {hedef}')
                n += 1
                break
    if not n:
        print('user_icons icinde tarot.png vb. bulunamadi')
        return 1
    print(f'{n} ikon uygulandi.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
