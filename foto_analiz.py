"""
FalımaBak — Cihaz içi fotoğraf doğrulama (Pillow, API yok).
El falında el/ten görünmeden, kahve falında fincan/telve görünmeden yorum yapılmaz.
"""

import os
import random


def _ten_rengi(r, g, b):
    if r < 70 or g < 45 or b < 35:
        return False
    if r > 248 and g > 238 and b > 228:
        return False
    mx, mn = max(r, g, b), min(r, g, b)
    if mx - mn < 10:
        return False
    return (
        r > 100 and g > 65 and b > 50
        and r > g > b
        and (r - b) > 15
        and abs(r - g) < 85
    )


def _kahve_telve(r, g, b):
    if r < 22 and g < 22 and b < 22:
        return True
    return (
        30 <= r <= 175
        and 18 <= g <= 125
        and 8 <= b <= 95
        and r >= g >= b
        and (r - b) > 10
    )


def _fincan_seramik(r, g, b):
    """Beyaz / krem fincan kenarı ve tabak."""
    if _kahve_telve(r, g, b):
        return False
    return (
        135 <= r <= 252
        and 120 <= g <= 245
        and 95 <= b <= 235
        and abs(r - g) < 50
        and abs(g - b) < 55
    )


def _analiz_et(yol, max_kenar=280):
    from PIL import Image, ImageStat

    if not yol or not os.path.isfile(yol):
        return None
    try:
        with Image.open(yol) as img:
            img = img.convert('RGB')
            img.thumbnail((max_kenar, max_kenar), Image.Resampling.LANCZOS)
            w, h = img.size
            px = list(img.getdata())
            if not px or w < 8 or h < 8:
                return None

            n = len(px)
            ten = kahve = seramik = koyu = 0
            for r, g, b in px:
                if _ten_rengi(r, g, b):
                    ten += 1
                if _kahve_telve(r, g, b):
                    kahve += 1
                if _fincan_seramik(r, g, b):
                    seramik += 1
                if r + g + b < 75:
                    koyu += 1

            ten_bolge, kahve_bolge, seramik_bolge = _bolge_say(pixels=px, w=w, h=h)

            stat = ImageStat.Stat(img)
            return {
                'ten_orani': ten / n,
                'kahve_orani': kahve / n,
                'seramik_orani': seramik / n,
                'koyu_orani': koyu / n,
                'ten_bolge': ten_bolge,
                'kahve_bolge': kahve_bolge,
                'seramik_bolge': seramik_bolge,
                'kontrast': sum(stat.stddev) / 3.0,
                'parlaklik': sum(stat.mean) / 3.0,
                'genislik': w,
                'yukseklik': h,
            }
    except Exception as e:
        print(f'Foto analiz: {e}', flush=True)
        return None


def _bolge_say(pixels, w, h, esik=0.10):
    """3x3 ızgarada ten / kahve / seramik görünen bölge sayısı."""
    cols, rows = 3, 3
    cw = max(w // cols, 1)
    rh = max(h // rows, 1)
    ten_b = kahve_b = seramik_b = 0

    for row in range(rows):
        for col in range(cols):
            x0, y0 = col * cw, row * rh
            x1 = min(x0 + cw, w)
            y1 = min(y0 + rh, h)
            toplam = ten = kahve = seramik = 0
            for y in range(y0, y1):
                satir = y * w
                for x in range(x0, x1):
                    r, g, b = pixels[satir + x]
                    toplam += 1
                    if _ten_rengi(r, g, b):
                        ten += 1
                    if _kahve_telve(r, g, b):
                        kahve += 1
                    if _fincan_seramik(r, g, b):
                        seramik += 1
            if not toplam:
                continue
            oran_t = ten / toplam
            oran_k = kahve / toplam
            oran_s = seramik / toplam
            if oran_t >= esik:
                ten_b += 1
            if oran_k >= esik:
                kahve_b += 1
            if oran_s >= esik:
                seramik_b += 1

    return ten_b, kahve_b, seramik_b


def _el_gorunuyor_mu(oz):
    """Fotoğrafta anlamlı el/ten alanı var mı?"""
    ten = oz.get('ten_orani', 0)
    bolge = oz.get('ten_bolge', 0)
    kontrast = oz.get('kontrast', 0)

    if ten < 0.20:
        return False
    if bolge < 2:
        return False
    if kontrast < 7 and ten < 0.28:
        return False
    return True


def _fincan_gorunuyor_mu(oz, tabak_mi=False):
    """Fotoğrafta kahve fincanı / telve / tabak var mı?"""
    kahve = oz.get('kahve_orani', 0)
    seramik = oz.get('seramik_orani', 0)
    koyu = oz.get('koyu_orani', 0)
    kontrast = oz.get('kontrast', 0)
    kahve_b = oz.get('kahve_bolge', 0)
    seramik_b = oz.get('seramik_bolge', 0)

    if tabak_mi:
        tabak_var = (kahve >= 0.06 and seramik >= 0.10) or (kahve >= 0.08 and koyu >= 0.12)
        return tabak_var and (kahve_b >= 1 or seramik_b >= 1)

    telve_var = kahve >= 0.09 or (koyu >= 0.22 and kontrast >= 8)
    fincan_var = seramik >= 0.08 or seramik_b >= 1
    bolgesel = kahve_b >= 1 or (telve_var and koyu >= 0.18)

    if not telve_var:
        return False
    if not bolgesel:
        return False
    if not fincan_var and kahve < 0.14 and koyu < 0.28:
        return False
    if kontrast < 6 and kahve < 0.12:
        return False
    return True


def _el_slot_gecerli(ozellik, baslik):
    if not ozellik:
        return False, f'"{baslik}" okunamadı. Lütfen tekrar yükleyin.'

    if not _el_gorunuyor_mu(ozellik):
        from dil import t
        return False, t('foto_el_yok', baslik=baslik)
    return True, dict(ozellik, _baslik=baslik)


def _kahve_slot_gecerli(ozellik, baslik):
    if not ozellik:
        return False, f'"{baslik}" okunamadı. Lütfen tekrar yükleyin.'

    tabak_mi = 'tabak' in (baslik or '').lower()
    if not _fincan_gorunuyor_mu(ozellik, tabak_mi=tabak_mi):
        from dil import t
        return False, t('foto_kahve_yok', baslik=baslik)
    return True, dict(ozellik, _baslik=baslik)


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
