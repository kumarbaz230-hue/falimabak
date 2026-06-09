"""Menü ve nav ikonlarını assets/ klasörüne üretir."""
import math
import os

from PIL import Image, ImageDraw

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(BASE, exist_ok=True)


def circle_icon(name, bg, fg, draw_fn):
    s = 128
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([8, 8, s - 8, s - 8], fill=bg)
    draw_fn(d, s, fg)
    img.save(os.path.join(BASE, name))


circle_icon('menu_tarot.png', (26, 20, 53, 255), (255, 215, 0, 255), lambda d, s, c: (
    d.ellipse([36, 40, 92, 96], fill=(124, 77, 255, 255)),
    d.ellipse([48, 52, 62, 66], fill=(200, 200, 220, 180)),
    d.polygon([(64, 28), (68, 36), (60, 36)], fill=c),
))

circle_icon('menu_kahve.png', (42, 24, 16, 255), (255, 145, 0, 255), lambda d, s, c: (
    d.rectangle([44, 50, 84, 90], fill=(109, 76, 65, 255)),
    d.ellipse([40, 44, 88, 58], fill=(161, 136, 127, 255)),
    d.arc([88, 58, 108, 82], 270, 90, fill=c, width=4),
))

circle_icon('menu_astroloji.png', (16, 30, 53, 255), (64, 196, 255, 255), lambda d, s, c: (
    d.polygon([
        (64, 30), (70, 54), (96, 54), (74, 68), (82, 94),
        (64, 78), (46, 94), (54, 68), (32, 54), (58, 54),
    ], fill=c),
))

circle_icon('menu_elfali.png', (34, 21, 53, 255), (224, 64, 251, 255), lambda d, s, c: (
    d.ellipse([46, 38, 82, 100], fill=(255, 204, 188, 255)),
    d.line([(64, 50), (64, 88)], fill=(180, 80, 120, 255), width=3),
    d.line([(52, 62), (76, 62)], fill=(180, 80, 120, 200), width=2),
))

circle_icon('menu_diger.png', (18, 40, 32, 255), (0, 230, 118, 255), lambda d, s, c: (
    d.line([(64, 32), (64, 96)], fill=c, width=3),
    d.line([(32, 64), (96, 64)], fill=c, width=3),
    d.line([(40, 40), (88, 88)], fill=c, width=2),
    d.line([(88, 40), (40, 88)], fill=c, width=2),
))

for name, col, sym in [
    ('nav_anasayfa.png', (255, 215, 0, 255), 'home'),
    ('nav_gecmis.png', (255, 215, 0, 255), 'hist'),
    ('nav_ayarlar.png', (255, 215, 0, 255), 'gear'),
]:
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if sym == 'home':
        d.polygon([(32, 14), (54, 30), (54, 52), (10, 52), (10, 30)], fill=col)
        d.rectangle([26, 36, 38, 52], fill=(15, 12, 32, 255))
    elif sym == 'hist':
        d.rectangle([14, 16, 50, 48], outline=col, width=3)
        d.line([(20, 26), (44, 26), (44, 38), (20, 38)], fill=col, width=2)
    else:
        d.ellipse([20, 20, 44, 44], outline=col, width=3)
        for i in range(8):
            a = math.pi * 2 * i / 8
            d.line([(32, 32), (32 + 18 * math.cos(a), 32 + 18 * math.sin(a))], fill=col, width=2)
    img.save(os.path.join(BASE, name))

print('menu icons ok')
