"""Menü ikonlarını Unsplash'ten indirir — menu_*.png (128→256, yuvarlak çerçeve)."""

import io
import os
import sys

import requests
from PIL import Image, ImageDraw, ImageFilter

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(BASE, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 FalimabakAssetTool/1.0'}

# Ücretsiz Unsplash — menü temalarına uygun
KAYNAKLAR = {
    'tarot': 'https://images.unsplash.com/photo-1507146426996-ef05306b995a?w=400&q=80',
    'kahve': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80',
    'astroloji': 'https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=400&q=80',
    'elfali': 'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&q=80',
    'diger': 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&q=80',
}


def _indir(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert('RGBA')


def _yuvarlak_ikon(img, boyut=256):
    img = img.resize((boyut, boyut), Image.Resampling.LANCZOS)
    # Merkez kırp (kare → daire)
    mask = Image.new('L', (boyut, boyut), 0)
    ImageDraw.Draw(mask).ellipse([4, 4, boyut - 4, boyut - 4], fill=255)
    out = Image.new('RGBA', (boyut, boyut), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)

    draw = ImageDraw.Draw(out)
    draw.ellipse([2, 2, boyut - 2, boyut - 2], outline=(255, 215, 0, 200), width=3)
    draw.ellipse([6, 6, boyut - 6, boyut - 6], outline=(255, 255, 255, 80), width=1)

    shadow = out.filter(ImageFilter.GaussianBlur(4))
    canvas = Image.new('RGBA', (boyut + 8, boyut + 8), (0, 0, 0, 0))
    canvas.paste(shadow, (4, 4), shadow)
    canvas.paste(out, (0, 0), out)
    return canvas


def main():
    for anahtar, url in KAYNAKLAR.items():
        dosya = os.path.join(BASE, f'menu_{anahtar}.png')
        try:
            img = _indir(url)
            ikon = _yuvarlak_ikon(img)
            ikon.save(dosya, 'PNG')
            print(f'OK menu_{anahtar}.png', flush=True)
        except Exception as e:
            print(f'HATA menu_{anahtar}: {e}', file=sys.stderr, flush=True)
            return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
