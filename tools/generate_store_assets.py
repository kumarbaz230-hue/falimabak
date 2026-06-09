"""Play Store feature graphic (1024x500) — app_icon + banner stili."""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
OUT = os.path.join(os.path.dirname(__file__), '..', 'store', 'feature_graphic.png')

W, H = 1024, 500


def main():
    img = Image.new('RGB', (W, H), (15, 12, 32))
    d = ImageDraw.Draw(img)

    for i in range(80):
        x = (i * 137) % W
        y = (i * 89) % H
        d.ellipse([x, y, x + 2, y + 2], fill=(255, 215, 0, 40))

    d.rounded_rectangle([40, 40, W - 40, H - 40], radius=24, outline=(255, 215, 0), width=3)

    icon_path = os.path.join(BASE, 'app_icon.png')
    if os.path.isfile(icon_path):
        icon = Image.open(icon_path).convert('RGBA')
        icon = icon.resize((180, 180), Image.LANCZOS)
        img.paste(icon, (80, (H - 180) // 2), icon)

    try:
        font_l = ImageFont.truetype('arial.ttf', 72)
        font_s = ImageFont.truetype('arial.ttf', 32)
    except OSError:
        font_l = ImageFont.load_default()
        font_s = ImageFont.load_default()

    d.text((300, 160), 'FalımaBak', fill=(255, 215, 0), font=font_l)
    d.text((300, 260), 'Tarot · Kahve · El · Astroloji', fill=(214, 208, 232), font=font_s)
    d.text((300, 320), 'Geleceğinizi keşfedin', fill=(155, 147, 184), font=font_s)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print(f'Feature graphic: {OUT}')


if __name__ == '__main__':
    main()
