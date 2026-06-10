"""Altın coin ikonu — assets/icon_coin.png"""
import os
import math

from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
S = 128


def main():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    r = 52

    # Dış gölge
    for i in range(8, 0, -1):
        d.ellipse(
            [cx - r - i, cy - r - i + 2, cx + r + i, cy + r + i + 2],
            fill=(0, 0, 0, 18 * i),
        )

    # Altın gradient (halka halka)
    for i in range(r, 0, -1):
        t = i / r
        rr = int(180 + 75 * t)
        gg = int(130 + 90 * t)
        bb = int(20 + 30 * t)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(rr, gg, bb, 255))

    # İç parlaklık
    d.ellipse([cx - r + 8, cy - r + 6, cx + r - 18, cy + r - 18], fill=(255, 236, 120, 90))

    # Kenar çizgisi
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 215, 0, 255), width=4)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], outline=(255, 248, 200, 120), width=2)

    # Yıldız / fal sembolü
    points = []
    for k in range(10):
        ang = math.pi / 2 + k * math.pi / 5
        rad = 22 if k % 2 == 0 else 10
        points.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(points, fill=(120, 80, 10, 255), outline=(255, 230, 140, 220))

    out = img.filter(ImageFilter.SHARPEN)
    yol = os.path.join(BASE, 'icon_coin.png')
    out.save(yol, 'PNG')
    print(f'OK {yol}', flush=True)


if __name__ == '__main__':
    main()
