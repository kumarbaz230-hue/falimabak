"""
FalımaBak — Cihaz içi premium fal yorumu (API / internet gerekmez).
Fotoğraf analizi + zengin Türkçe şablonlar ile derin yorumlar üretir.
"""

import random
import textwrap

from fal_cesit import (
    rng_olustur,
    paragraf_sec,
    premium_uzun_mu,
    ASK_UZUN,
    KARIYER_UZUN,
    SAGLIK_UZUN,
    GENEL_UZUN,
    KAPANIS_CUMLE,
    ISKAMBIL_BAGLANTI,
    ISKAMBIL_TAVSIYE,
    CICEK_BUKET,
    CICEK_OZEL,
    NAZAR_DURUM,
    NAZAR_UZUN,
    NAZAR_KORUNMA,
    TAROT_GIRIS,
    TAROT_KART_EK,
    ELEMENT_YORUM,
)


def _temiz(metin):
    try:
        from theme import emoji_temizle
        return emoji_temizle(metin or '')
    except Exception:
        return metin or ''


def _hitap():
    try:
        from gecmis import kullanici_ismi
        isim = (kullanici_ismi() or '').strip()
        if isim:
            return f'{isim}, '
    except Exception:
        pass
    return ''


def _paragraf(metin, genislik=72):
    return textwrap.fill(metin, width=genislik)


def _el_veri():
    import elfali
    return elfali.EL_CIZGILERI, elfali.EL_TIPLERI


def _kahve_veri():
    import kahve
    return kahve.KAHVE_SEKILLERI, kahve.GENEL_YORUMLAR


def _foto_gozlem_elfali(ozellikler, aciklamalar):
    if not ozellikler:
        return ''
    satirlar = []
    for i, oz in enumerate(ozellikler):
        if not oz:
            continue
        baslik = aciklamalar[i] if aciklamalar and i < len(aciklamalar) else f'Fotoğraf {i + 1}'
        ten = oz.get('ten_orani', 0)
        kontrast = oz.get('kontrast', 0)
        if 'avuç' in baslik.lower() or 'içi' in baslik.lower():
            if ten > 0.35 and kontrast > 18:
                satirlar.append(
                    f'{baslik}: Çizgiler belirgin ve avuç yapısı net okunuyor; '
                    'karakter ve kader hattı güçlü bir enerji taşıyor.'
                )
            elif ten > 0.2:
                satirlar.append(
                    f'{baslik}: Avuç içi yumuşak ve dengeli; duygusal derinlik '
                    'ile pratik zekâ bir arada.'
                )
            else:
                satirlar.append(
                    f'{baslik}: Avuç hatları incelikli; sezgi ve içgörü ön planda.'
                )
        else:
            if kontrast > 15:
                satirlar.append(
                    f'{baslik}: El formu güçlü; dış görünüş cesaret ve '
                    'kararlılıkla uyumlu.'
                )
            else:
                satirlar.append(
                    f'{baslik}: El dışı yapısı zarif; sanatsal ve sosyal '
                    'yeteneklere işaret ediyor.'
                )
    return '\n'.join(satirlar)


def _foto_gozlem_kahve(ozellikler, aciklamalar):
    if not ozellikler:
        return ''
    satirlar = []
    for i, oz in enumerate(ozellikler):
        if not oz:
            continue
        baslik = aciklamalar[i] if aciklamalar and i < len(aciklamalar) else f'Fotoğraf {i + 1}'
        kahve = oz.get('kahve_orani', 0)
        koyu = oz.get('koyu_orani', 0)
        if 'tabak' in baslik.lower():
            satirlar.append(
                f'{baslik}: Tabaktaki izler yolculuk ve haber enerjisi taşıyor; '
                'yakın çevreden güzel gelişmeler müjdeleniyor.'
            )
        elif kahve > 0.15 or koyu > 0.25:
            satirlar.append(
                f'{baslik}: Telve desenleri yoğun; fincan güçlü semboller barındırıyor '
                've dönüşüm dönemi işaret ediyor.'
            )
        else:
            satirlar.append(
                f'{baslik}: Telveler ince ama anlamlı; sabır ve doğru zamanlama '
                'mesajı öne çıkıyor.'
            )
    return '\n'.join(satirlar)


def _elfali_yorum(veri, ozellikler=None):
    cizgiler_db, tipler = _el_veri()
    hitap = _hitap()
    foto_t = 0
    if ozellikler:
        from foto_analiz import foto_tohum
        foto_t = foto_tohum(ozellikler)
    rng = rng_olustur(veri, foto_t)
    uzun = premium_uzun_mu(rng)

    el_tipi = rng.choice(tipler)
    secilen = rng.sample(cizgiler_db, min(rng.randint(5, 8), len(cizgiler_db)))
    aciklamalar = veri.get('foto_aciklamalari') or []

    bolum = []
    bolum.append('EL FALI YORUMUNUZ')
    bolum.append('')
    bolum.append(f'El tipiniz: {_temiz(el_tipi["tip"])}')
    bolum.append(el_tipi['ozellik'])
    bolum.append(
        f'Karakter: {el_tipi["karakter"]}. Bu tip genelde {el_tipi["meslek"]} '
        'alanlarında parlar.'
    )
    bolum.append('')

    gozlem = _foto_gozlem_elfali(ozellikler, aciklamalar)
    if gozlem:
        bolum.append('Fotoğraf gözlemleri:')
        bolum.append(gozlem)
        bolum.append('')

    bolum.append('Çizgi analizi:')
    for c in secilen:
        durum = rng.choice(['Pozitif', 'Güçlü', 'Belirgin', 'Net'])
        yorum = c['pozitif'] if durum != 'Negatif' else c.get('negatif', c['pozitif'])
        bolum.append(f'• {_temiz(c["isim"])} ({durum}): {_temiz(yorum)}')
        if uzun and rng.random() < 0.4:
            bolum.append(f'  {_temiz(c.get("ipucu", ""))}')

    bolum.append('')
    bolum.append('Aşk ve ilişkiler:')
    for p in paragraf_sec(rng, ASK_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Kariyer ve para:')
    for p in paragraf_sec(rng, KARIYER_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Sağlık ve enerji:')
    for p in paragraf_sec(rng, SAGLIK_UZUN, 1 if not uzun else 2):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Genel mesaj:')
    for p in paragraf_sec(rng, GENEL_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    bolum.append(f'Şanslı renginiz: {rng.choice(["altın", "mor", "mavi", "pembe", "yeşil", "bordo"])}')
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def _kahve_yorum(veri, ozellikler=None):
    sekiller_db, genel_db = _kahve_veri()
    hitap = _hitap()
    foto_t = 0
    if ozellikler:
        from foto_analiz import foto_tohum
        foto_t = foto_tohum(ozellikler)
    rng = rng_olustur(veri, foto_t + 17)
    uzun = premium_uzun_mu(rng)

    adet = rng.randint(4, 7)
    secilen = rng.sample(sekiller_db, min(adet, len(sekiller_db)))
    aciklamalar = veri.get('foto_aciklamalari') or []

    kategoriler = {}
    for s in secilen:
        kategoriler.setdefault(s['kategori'], []).append(s)

    bolum = []
    bolum.append('KAHVE FALI YORUMUNUZ')
    bolum.append('')

    gozlem = _foto_gozlem_kahve(ozellikler, aciklamalar)
    if gozlem:
        bolum.append('Fincan gözlemleri:')
        bolum.append(gozlem)
        bolum.append('')

    bolum.append('Fincanda öne çıkan semboller:')
    for kat, liste in kategoriler.items():
        bolum.append(f'\n{kat}:')
        for s in liste:
            durum = rng.choice(['Pozitif', 'Güçlü', 'Belirgin'])
            y = s['pozitif'] if durum != 'Negatif' else s.get('negatif', s['pozitif'])
            bolum.append(f'  • {_temiz(s["isim"])}: {_temiz(y)}')

    bolum.append('')
    bolum.append('Aşk:')
    for p in paragraf_sec(rng, ASK_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Para ve iş:')
    for p in paragraf_sec(rng, KARIYER_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Sağlık:')
    for p in paragraf_sec(rng, SAGLIK_UZUN, 1 if not uzun else 2):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Genel yorum:')
    bolum.append(_paragraf(_temiz(rng.choice(genel_db))))
    if uzun:
        for p in paragraf_sec(rng, GENEL_UZUN, 1):
            bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    bolum.append(f'Şanslı renginiz: {rng.choice(["kahve", "altın", "krem", "yeşil", "bordo"])}')
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def _tarot_yorum(veri):
    hitap = _hitap()
    kartlar = veri.get('kartlar') or []
    rng = rng_olustur(veri, len(kartlar) * 131)
    uzun = premium_uzun_mu(rng)

    bolum = ['TAROT YORUMUNUZ', '']
    bolum.append(_paragraf(rng.choice(TAROT_GIRIS)))
    bolum.append('')

    if kartlar:
        bolum.append('Çekilen kartlar:')
        for k in kartlar:
            satir = (
                f'• {k.get("pozisyon", "")}: {k.get("isim", "")} '
                f'({k.get("durum", "")}) — {k.get("anlam", "")}'
            )
            bolum.append(_temiz(satir))
            if uzun or rng.random() < 0.5:
                ek = rng.choice(TAROT_KART_EK)
                if k.get('durum') == 'Ters':
                    ek = 'Ters konum: içsel direnç veya gecikme olabilir; sabırla ilerleyin.'
                bolum.append(f'  {_temiz(ek)}')
        bolum.append('')

    bolum.append('Genel enerji:')
    for p in paragraf_sec(rng, GENEL_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Aşk:')
    for p in paragraf_sec(rng, ASK_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Kariyer:')
    for p in paragraf_sec(rng, KARIYER_UZUN, 1 if not uzun else 2):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def _astroloji_yorum(veri):
    hitap = _hitap()
    burc = veri.get('burc', 'yıldızlar')
    dogum = veri.get('dogum', '')
    rng = rng_olustur(veri, hash(burc) % 99999)
    uzun = premium_uzun_mu(rng)

    try:
        import astroloji
        burc_yorumlari = astroloji.BURC_YORUMLARI.get(burc, [])
        burc_bilgi = astroloji.BURCLAR.get(burc, {})
        element = burc_bilgi.get('element', '')
        gezegen = burc_bilgi.get('gezegen', '')
    except Exception:
        burc_yorumlari = []
        element = ''
        gezegen = ''

    bolum = ['ASTROLOJİ YORUMUNUZ', '']
    if dogum:
        bolum.append(f'Doğum tarihiniz: {dogum}')
    if gezegen:
        bolum.append(f'Yönetici gezegen: {gezegen}')
    bolum.append('')

    if burc_yorumlari:
        for y in paragraf_sec(rng, burc_yorumlari, 2 if uzun else 1):
            bolum.append(_paragraf(hitap + y))
            bolum.append('')

    if element and element in ELEMENT_YORUM:
        bolum.append('Element etkisi:')
        bolum.append(_paragraf(ELEMENT_YORUM[element]))
        bolum.append('')

    bolum.append('Aşk:')
    for p in paragraf_sec(rng, ASK_UZUN, 1 if not uzun else 2):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Kariyer ve para:')
    for p in paragraf_sec(rng, KARIYER_UZUN, 1 if not uzun else 2):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Sağlık:')
    bolum.append(_paragraf(hitap + rng.choice(SAGLIK_UZUN)))

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def _iskambil_yorum(veri, rng, hitap, uzun):
    kartlar = veri.get('kartlar') or []
    bolum = ['İSKAMBİL FALI YORUMUNUZ', '']
    bolum.append(_paragraf(rng.choice(ISKAMBIL_BAGLANTI)))
    bolum.append('')

    for k in kartlar:
        poz = k.get('pozisyon', '')
        isim = _temiz(k.get('isim', ''))
        anlam = _temiz(k.get('anlam', ''))
        bolum.append(f'{poz}: {isim}')
        bolum.append(_paragraf(anlam))
        if rng.random() < 0.55:
            bolum.append(_paragraf(rng.choice(TAROT_KART_EK)))
        bolum.append('')

    bolum.append('Aşk:')
    for p in paragraf_sec(rng, ASK_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Kariyer:')
    for p in paragraf_sec(rng, KARIYER_UZUN, 1 if not uzun else 2):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Tavsiyeler:')
    for t in paragraf_sec(rng, ISKAMBIL_TAVSIYE, 2 if uzun else 1):
        bolum.append(f'• {t}')

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def _cicek_yorum(veri, rng, hitap, uzun):
    cicekler = veri.get('cicekler') or []
    bolum = ['ÇİÇEK FALI YORUMUNUZ', '']
    bolum.append(_paragraf(rng.choice(CICEK_BUKET)))
    bolum.append('')

    for c in cicekler:
        bolum.append(_temiz(c.get('isim', 'Çiçek')))
        bolum.append(_paragraf(_temiz(c.get('anlam', ''))))
        bolum.append('')

    bolum.append('Aşk ve duygular:')
    for p in paragraf_sec(rng, ASK_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Genel mesaj:')
    for p in paragraf_sec(rng, GENEL_UZUN, 1 if not uzun else 2):
        bolum.append(_paragraf(hitap + p))

    bolum.append('')
    bolum.append('Çiçek tavsiyesi:')
    for t in paragraf_sec(rng, CICEK_OZEL, 2 if uzun else 1):
        bolum.append(f'• {t}')

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def _nazar_yorum(veri, rng, hitap, uzun):
    bolum = ['NAZAR FALI YORUMUNUZ', '']
    bolum.append('Nazar boncuğu durumu:')
    bolum.append(_paragraf(rng.choice(NAZAR_DURUM)))
    bolum.append('')

    for p in paragraf_sec(rng, NAZAR_UZUN, 2 if uzun else 1):
        bolum.append(_paragraf(hitap + p))
        bolum.append('')

    bolum.append('Korunma önerileri:')
    for k in paragraf_sec(rng, NAZAR_KORUNMA, 3 if uzun else 2):
        bolum.append(f'• {k}')

    bolum.append('')
    bolum.append('Genel enerji:')
    bolum.append(_paragraf(hitap + rng.choice(GENEL_UZUN)))

    bolum.append('')
    bolum.append(f'Şanslı sayınız: {rng.randint(1, 99)}')
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def _diger_yorum(veri):
    hitap = _hitap()
    rng = rng_olustur(veri, hash(veri.get('alt_tip', '')) % 99999)
    uzun = premium_uzun_mu(rng)
    alt = (veri.get('alt_tip') or veri.get('tur') or '').lower()

    if 'iskambil' in alt:
        return _iskambil_yorum(veri, rng, hitap, uzun)
    if 'cicek' in alt or 'çiçek' in alt:
        return _cicek_yorum(veri, rng, hitap, uzun)
    if 'nazar' in alt:
        return _nazar_yorum(veri, rng, hitap, uzun)

    tur = veri.get('tur', 'Fal')
    sonuc = veri.get('sonuc', '')
    bolum = [
        f'{_temiz(tur).upper()} YORUMUNUZ',
        '',
        _paragraf(hitap + sonuc),
        '',
    ]
    for p in paragraf_sec(rng, GENEL_UZUN, 2):
        bolum.append(_paragraf(hitap + p))
    bolum.append(rng.choice(KAPANIS_CUMLE))
    return '\n'.join(bolum)


def offline_yorum_uret(tip, veri, foto_ozellikleri=None):
    """API'siz premium fal metni — her çağrıda farklı."""
    veri = dict(veri or {})
    return _uret_ic(tip, veri, foto_ozellikleri)


def _uret_ic(tip, veri, foto_ozellikleri=None):
    if tip == 'elfali':
        return _elfali_yorum(veri, foto_ozellikleri)
    if tip == 'kahve':
        return _kahve_yorum(veri, foto_ozellikleri)
    if tip == 'tarot':
        return _tarot_yorum(veri)
    if tip == 'astroloji':
        return _astroloji_yorum(veri)
    if tip == 'diger':
        return _diger_yorum(veri)
    return _diger_yorum({'tur': tip, 'sonuc': '', 'alt_tip': tip})
