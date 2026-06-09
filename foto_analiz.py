"""
FalımaBak — Cihaz içi fotoğraf analizi (API yok, sadece Pillow).
El / kahve fincanı fotoğraflarını renk ve doku ile doğrular.
"""

import os
import random


def _ten_rengi(r, g, b):
    """Basit ten rengi aralığı."""
    if r < 60 or g < 40 or b < 30:
        return False
    if r > 250 and g > 240 and b > 230:
        return False
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 8:
        return False
    return (
        r > 95 and g > 60 and b > 45
        and r > g > b
        and (r - b) > 12
        and abs(r - g) < 90
    )


def _kahve_rengi(r, g, b):
    """Kahve telve / fincan tonları."""
    if r < 25 and g < 25 and b < 25:
        return True
    return (
        35 <= r <= 180
        and 20 <= g <= 130
        and 10 <= b <= 100
        and r >= g >= b
        and (r - b) > 8
    )


def _tabak_rengi(r, g, b):
    """Tabak / açık fincan izi tonları."""
    if _kahve_rengi(r, g, b):
        return True
    return (
        120 <= r <= 245
        and 100 <= g <= 230
        and 80 <= b <= 210
        and abs(r - g) < 45
    )


def _yesil_dominant(r, g, b):
    return g > r + 25 and g > b + 20 and g > 80


def _mavi_gok(r, g, b):
    return b > r + 15 and b > g + 5 and b > 100


def _analiz_et(yol, max_kenar=240):
    from PIL import Image, ImageStat

    if not yol or not os.path.isfile(yol):
        return None
    try:
        with Image.open(yol) as img:
            img = img.convert('RGB')
            img.thumbnail((max_kenar, max_kenar), Image.Resampling.LANCZOS)
            px = list(img.getdata())
            if not px:
                return None
            n = len(px)
            ten = kahve = tabak = yesil = mavi = koyu = 0
            for r, g, b in px:
                if _ten_rengi(r, g, b):
                    ten += 1
                if _kahve_rengi(r, g, b):
                    kahve += 1
                if _tabak_rengi(r, g, b):
                    tabak += 1
                if _yesil_dominant(r, g, b):
                    yesil += 1
                if _mavi_gok(r, g, b):
                    mavi += 1
                if r + g + b < 80:
                    koyu += 1
            stat = ImageStat.Stat(img)
            return {
                'ten_orani': ten / n,
                'kahve_orani': kahve / n,
                'tabak_orani': tabak / n,
                'yesil_orani': yesil / n,
                'mavi_orani': mavi / n,
                'koyu_orani': koyu / n,
                'parlaklik': sum(stat.mean) / 3.0,
                'kontrast': sum(stat.stddev) / 3.0,
                'genislik': img.width,
                'yukseklik': img.height,
            }
    except Exception as e:
        print(f'Foto analiz: {e}', flush=True)
        return None


def _el_slot_gecerli(ozellik, baslik):
    if not ozellik:
        return False, f'"{baslik}" okunamadı. Lütfen tekrar yükleyin.'
    if ozellik['mavi_orani'] > 0.38:
        return False, f'"{baslik}" gökyüzü veya manzara gibi — el fotoğrafı yükleyin.'
    if ozellik['yesil_orani'] > 0.42:
        return False, f'"{baslik}" doğa fotoğrafı gibi — avuç veya el dışı çekin.'
    if ozellik['ten_orani'] < 0.08:
        return False, (
            f'"{baslik}" el fotoğrafı gibi görünmüyor. '
            'Avuç içi veya el dışını net çekin.'
        )
    if ozellik['kontrast'] < 6 and ozellik['ten_orani'] < 0.15:
        return False, f'"{baslik}" çok bulanık veya karanlık. Daha net bir fotoğraf seçin.'
    return True, ozellik


def _kahve_slot_gecerli(ozellik, baslik):
    if not ozellik:
        return False, f'"{baslik}" okunamadı. Lütfen tekrar yükleyin.'
    if ozellik['mavi_orani'] > 0.35 and ozellik['kahve_orani'] < 0.06:
        return False, f'"{baslik}" fincan fotoğrafı gibi değil.'
    if ozellik['yesil_orani'] > 0.45 and ozellik['kahve_orani'] < 0.08:
        return False, f'"{baslik}" kahve fincanı gibi görünmüyor.'
    if 'tabak' in (baslik or '').lower():
        if ozellik['tabak_orani'] < 0.05 and ozellik['kahve_orani'] < 0.04:
            return False, f'"{baslik}" tabak/fincan izi içermiyor gibi.'
    else:
        if ozellik['kahve_orani'] < 0.05 and ozellik['koyu_orani'] < 0.12:
            return False, (
                f'"{baslik}" fincan içi telve görünmüyor. '
                'Kahve fincanının içini yakından çekin.'
            )
    return True, ozellik


def fotolar_dogrula(tip, yollar, aciklamalar=None):
    """(ok, hata_mesaji, ozellikler_listesi)"""
    aciklamalar = aciklamalar or []
    ozellikler = []
    for i, yol in enumerate(yollar or []):
        baslik = aciklamalar[i] if i < len(aciklamalar) else f'Fotoğraf {i + 1}'
        oz = _analiz_et(yol)
        if tip == 'elfali':
            ok, sonuc = _el_slot_gecerli(oz, baslik)
        elif tip == 'kahve':
            ok, sonuc = _kahve_slot_gecerli(oz, baslik)
        else:
            ok, sonuc = True, oz
        if not ok:
            return False, sonuc, []
        ozellikler.append(sonuc if isinstance(sonuc, dict) else oz)
    return True, None, ozellikler


def foto_tohum(ozellikler):
    """Aynı fotoğraflardan tutarlı rastgelelik için tohum."""
    if not ozellikler:
        return random.randint(0, 999999)
    parca = 0
    for o in ozellikler:
        if not o:
            continue
        parca += int(o.get('ten_orani', 0) * 1000)
        parca += int(o.get('kahve_orani', 0) * 1000)
        parca += int(o.get('kontrast', 0) * 10)
    return parca % 999983
