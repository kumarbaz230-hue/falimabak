"""Menü ikonları — kare siyah/beyaz arka planı kaldır (dairesel alpha). Nav ikonları yenile."""

import math
import os

from PIL import Image, ImageDraw

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')


def _dairesel_alpha(img, yaricap_oran=0.96, yumusak=5):
    img = img.convert('RGBA')
    w, h = img.size
    cx, cy = w / 2, h / 2
    r = min(w, h) / 2 * yaricap_oran
    px = img.load()
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            r0, g0, b0, a0 = px[x, y]
            if d > r:
                px[x, y] = (0, 0, 0, 0)
            elif d > r - yumusak:
                t = (r - d) / max(yumusak, 1)
                px[x, y] = (r0, g0, b0, int(a0 * t))
            elif a0 > 0 and (r0 < 18 and g0 < 18 and b0 < 18) and d > r * 0.82:
                # Daire içinde kalan saf siyah halka
                px[x, y] = (0, 0, 0, 0)
            elif a0 > 0 and (r0 > 235 and g0 > 235 and b0 > 235) and d > r * 0.82:
                # Daire içinde kalan saf beyaz halka
                px[x, y] = (0, 0, 0, 0)
    return img


def _menu_ikonlari():
    for ad in os.listdir(BASE):
        if ad.startswith('menu_') and ad.endswith('.png') and 'banner' not in ad and 'kart' not in ad:
            yol = os.path.join(BASE, ad)
            _dairesel_alpha(Image.open(yol)).save(yol, 'PNG')
            print(f'OK {ad}', flush=True)


def _nav_ikonlari():
    s = 128
    gold = (255, 215, 0, 255)
    dark = (18, 12, 32, 255)

    # Ana sayfa
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(64, 22), (104, 48), (104, 98), (24, 98), (24, 48)], fill=gold)
    d.rectangle([52, 58, 76, 98], fill=dark)
    img.save(os.path.join(BASE, 'nav_anasayfa.png'), 'PNG')

    # Geçmiş — parşömen
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([28, 24, 100, 104], radius=10, outline=gold, width=5)
    d.line([(40, 44), (88, 44)], fill=gold, width=3)
    d.line([(40, 58), (88, 58)], fill=gold, width=3)
    d.line([(40, 72), (72, 72)], fill=gold, width=3)
    img.save(os.path.join(BASE, 'nav_gecmis.png'), 'PNG')

    # Ayarlar — dişli
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy, ir, or_ = 64, 64, 22, 44
    for i in range(8):
        a = math.radians(i * 45)
        x1 = cx + ir * math.cos(a)
        y1 = cy + ir * math.sin(a)
        x2 = cx + or_ * math.cos(a)
        y2 = cy + or_ * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=gold, width=8)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=gold, width=4)
    img.save(os.path.join(BASE, 'nav_ayarlar.png'), 'PNG')
    print('OK nav_*.png', flush=True)


def main():
    _menu_ikonlari()
    _nav_ikonlari()
    print('Ikon duzeltme tamam.', flush=True)


if __name__ == '__main__':
    main()
