"""
FalımaBak — Cihaz içi fotoğraf doğrulama (Pillow, API yok).
Kahve falı: fincan (her renk) + telve görülmeden yorum yapılmaz.
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
    """Kahve telvesi — koyu kahverengi / siyahımsı (ışık farkına dayanıklı)."""
    if r < 28 and g < 28 and b < 28:
        return True
    toplam = r + g + b
    if toplam < 95 and r >= g >= b:
        return True
    return (
        25 <= r <= 190
        and 15 <= g <= 140
        and 8 <= b <= 110
        and r >= g >= b
        and (r - b) > 8
        and toplam < 320
    )


def _fincan_seramik(r, g, b):
    """Beyaz / krem fincan (renk şartı değil, ek sinyal)."""
    if _kahve_telve(r, g, b):
        return False
    return (
        135 <= r <= 252
        and 120 <= g <= 245
        and 95 <= b <= 235
        and abs(r - g) < 50
        and abs(g - b) < 55
    )


def _fincan_kap(r, g, b):
    """Fincan/tabağın gövdesi — mavi, kırmızı, yeşil, beyaz, her renk."""
    if _ten_rengi(r, g, b) or _kahve_telve(r, g, b):
        return False
    toplam = r + g + b
    if toplam < 55 or toplam > 740:
        return False
    mx, mn = max(r, g, b), min(r, g, b)
    doygunluk = mx - mn
    # Renkli seramik (mavi fincan vb.) veya açık nötr yüzey
    if doygunluk >= 12:
        return True
    if doygunluk >= 6 and 80 <= toplam / 3 <= 240:
        return True
    return _fincan_seramik(r, g, b)


def _analiz_et(yol, max_kenar=320):
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
            ten = kahve = seramik = kap = koyu = 0
            for r, g, b in px:
                if _ten_rengi(r, g, b):
                    ten += 1
                if _kahve_telve(r, g, b):
                    kahve += 1
                if _fincan_seramik(r, g, b):
                    seramik += 1
                if _fincan_kap(r, g, b):
                    kap += 1
                if r + g + b < 80:
                    koyu += 1

            ten_b, kahve_b, seramik_b, kap_b = _bolge_say(pixels=px, w=w, h=h)

            stat = ImageStat.Stat(img)
            return {
                'ten_orani': ten / n,
                'kahve_orani': kahve / n,
                'seramik_orani': seramik / n,
                'kap_orani': kap / n,
                'koyu_orani': koyu / n,
                'ten_bolge': ten_b,
                'kahve_bolge': kahve_b,
                'seramik_bolge': seramik_b,
                'kap_bolge': kap_b,
                'kontrast': sum(stat.stddev) / 3.0,
                'parlaklik': sum(stat.mean) / 3.0,
                'genislik': w,
                'yukseklik': h,
            }
    except Exception as e:
        print(f'Foto analiz: {e}', flush=True)
        return None


def _bolge_say(pixels, w, h, esik=0.08):
    """3x3 ızgarada ten / kahve / seramik / kap bölge sayısı."""
    cols, rows = 3, 3
    cw = max(w // cols, 1)
    rh = max(h // rows, 1)
    ten_b = kahve_b = seramik_b = kap_b = 0

    for row in range(rows):
        for col in range(cols):
            x0, y0 = col * cw, row * rh
            x1 = min(x0 + cw, w)
            y1 = min(y0 + rh, h)
            toplam = ten = kahve = seramik = kap = 0
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
                    if _fincan_kap(r, g, b):
                        kap += 1
            if not toplam:
                continue
            if ten / toplam >= esik:
                ten_b += 1
            if kahve / toplam >= esik:
                kahve_b += 1
            if seramik / toplam >= esik:
                seramik_b += 1
            if kap / toplam >= esik:
                kap_b += 1

    return ten_b, kahve_b, seramik_b, kap_b


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


def _telve_var_mi(oz):
    """Fotoğrafta kahve telvesi / koyu telve lekeleri var mı?"""
    kahve = oz.get('kahve_orani', 0)
    koyu = oz.get('koyu_orani', 0)
    kahve_b = oz.get('kahve_bolge', 0)
    kontrast = oz.get('kontrast', 0)
    return (
        kahve >= 0.035
        or kahve_b >= 1
        or (koyu >= 0.09 and kontrast >= 4)
        or (koyu >= 0.14)
    )


def _kap_var_mi(oz):
    """Fincan veya tabak gövdesi — renk fark etmez."""
    kap = oz.get('kap_orani', 0)
    kap_b = oz.get('kap_bolge', 0)
    seramik = oz.get('seramik_orani', 0)
    seramik_b = oz.get('seramik_bolge', 0)
    return (
        kap >= 0.04
        or kap_b >= 1
        or seramik >= 0.04
        or seramik_b >= 1
    )


def _fincan_gorunuyor_mu(oz, tabak_mi=False):
    """
    Kahve falı fotoğrafı geçerli mi?
    Şart: telve + (fincan/tabağın herhangi bir rengi) birlikte görünsün.
    """
    if not _telve_var_mi(oz):
        return False

    if tabak_mi:
        return _kap_var_mi(oz) or oz.get('kahve_bolge', 0) >= 2

    # Fincan içi: telveyi net gör + fincan duvarı/kenarı (mavi, beyaz, her renk)
    if _kap_var_mi(oz):
        return True
    # Sadece iç çekim — telvenin yoğun ve dağınık olması fincan içi imzası
    if oz.get('kahve_orani', 0) >= 0.06 and oz.get('kahve_bolge', 0) >= 2:
        return True
    if oz.get('koyu_orani', 0) >= 0.12 and oz.get('kontrast', 0) >= 7:
        return True
    return False


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
        parca += int(o.get('kap_orani', 0) * 1000)
        parca += int(o.get('kontrast', 0) * 10)
    return parca % 999983
