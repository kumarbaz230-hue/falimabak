"""FalımaBak — coin ekonomisi (fal harcama, hoşgeldin bonusu, reklam ödülü)."""

from datetime import date

from gecmis import _yukle, _kaydet

HOSGELDIN_BONUS = 10
GUNLUK_GIRIS_BONUS = 3  # Her gün ilk açılışta
FAL_MALIYET = 1
REKLAM_COIN_ODUL = 3
REKLAM_GUNLUK_MAX = 5
SINIRSIZ_TIPLER = frozenset()


def _gunluk_reklam(veri=None):
    if veri is None:
        veri = _yukle()
    bugun = date.today().isoformat()
    cr = veri.get('coin_reklam') or {}
    if cr.get('tarih') != bugun:
        cr = {'tarih': bugun, 'sayac': 0}
    veri['coin_reklam'] = cr
    return veri, cr


def coin_miktar():
    return int(_yukle().get('coin', 0))


def coin_ekle(miktar):
    veri = _yukle()
    veri['coin'] = max(0, int(veri.get('coin', 0)) + int(miktar))
    _kaydet(veri)
    return veri['coin']


def coin_harca(miktar=FAL_MALIYET):
    veri = _yukle()
    mevcut = int(veri.get('coin', 0))
    if mevcut < miktar:
        return False
    veri['coin'] = mevcut - miktar
    _kaydet(veri)
    return True


def coin_iade(miktar=FAL_MALIYET):
    """Başarısız fal — harcanan coin geri ver."""
    return coin_ekle(miktar)


def hosgeldin_kontrol():
    """İlk kurulumda hoşgeldin bonusu. (yeni_verildi, miktar) döner."""
    veri = _yukle()
    if veri.get('hosgeldin_verildi'):
        return False, coin_miktar()
    veri['hosgeldin_verildi'] = True
    veri['coin'] = int(veri.get('coin', 0)) + HOSGELDIN_BONUS
    _kaydet(veri)
    return True, veri['coin']


def gunluk_giris_kontrol():
    """Her gün ilk uygulama açılışında bonus. (yeni_verildi, miktar) döner."""
    veri = _yukle()
    bugun = date.today().isoformat()
    gb = veri.get('coin_gunluk_bonus') or {}
    if gb.get('tarih') == bugun:
        return False, coin_miktar()
    veri['coin_gunluk_bonus'] = {'tarih': bugun}
    veri['coin'] = int(veri.get('coin', 0)) + GUNLUK_GIRIS_BONUS
    _kaydet(veri)
    return True, veri['coin']


def reklam_kalan():
    _, cr = _gunluk_reklam()
    return max(0, REKLAM_GUNLUK_MAX - int(cr.get('sayac', 0)))


def reklam_hakki_var():
    return reklam_kalan() > 0


def reklam_coin_kazan():
    if not reklam_hakki_var():
        return False
    veri, cr = _gunluk_reklam()
    cr['sayac'] = int(cr.get('sayac', 0)) + 1
    veri['coin_reklam'] = cr
    veri['coin'] = int(veri.get('coin', 0)) + REKLAM_COIN_ODUL
    _kaydet(veri)
    return True


def fal_ucretsiz(tip):
    return tip in SINIRSIZ_TIPLER


def fal_izinli(tip):
    if fal_ucretsiz(tip):
        return True
    return coin_miktar() >= FAL_MALIYET
