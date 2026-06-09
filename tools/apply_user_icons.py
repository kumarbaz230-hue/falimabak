"""Kullanıcı ikonlarını menu_*.png olarak işler (kahve+tarot birleşik görseli ayırır)."""

import os
from PIL import Image

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets')
USER = os.path.join(BASE, 'user_icons')
S = 256

# Cursor workspace'teki kaynak görseller (bir kez kopyalandı)
SRC = {
    'kahve_tarot': os.path.join(
        USER,
        '_src_kahve_tarot.png',
    ),
    'astroloji': os.path.join(USER, '_src_astroloji.png'),
    'elfali': os.path.join(USER, '_src_elfali.png'),
    'diger': os.path.join(USER, '_src_diger.png'),
}


def _kare_kirp(img):
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))


def _kaydet(img, hedef):
    img = _kare_kirp(img.convert('RGBA'))
    img = img.resize((S, S), Image.Resampling.LANCZOS)
    img.save(os.path.join(BASE, hedef), 'PNG')
    print(f'OK -> {hedef} ({S}x{S})', flush=True)


def _kahve_tarot_ayir(yol):
    img = Image.open(yol).convert('RGBA')
    w, h = img.size
    yarim = w // 2
    side = min(yarim, h)
    top = (h - side) // 2
    kahve = img.crop((0, top, yarim, top + side))
    # Sağ yarım — tarot (ortalanmış kare)
    left = yarim + (yarim - side) // 2
    tarot = img.crop((left, top, left + side, top + side))
    _kaydet(kahve, 'menu_kahve.png')
    _kaydet(tarot, 'menu_tarot.png')


def main():
    os.makedirs(USER, exist_ok=True)
    kt = SRC['kahve_tarot']
    if not os.path.isfile(kt):
        print(f'Eksik: {kt}')
        return 1
    _kahve_tarot_ayir(kt)
    _kaydet(Image.open(SRC['astroloji']), 'menu_astroloji.png')
    _kaydet(Image.open(SRC['elfali']), 'menu_elfali.png')
    _kaydet(Image.open(SRC['diger']), 'menu_diger.png')
    print('Tum menu ikonlari hazir.', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
