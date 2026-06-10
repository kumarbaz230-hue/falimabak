"""Günlük fal limiti — burç eşleşmesi hariç, reklam ile ek hak."""

from datetime import date

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex

from gecmis import _yukle, _kaydet
from theme import RENKLER, metin_label, siyah_buton

FAL_GUNLUK_UCRETSIZ = 1  # Her fal türünde günde 1 ücretsiz (ilk fal)
REKLAM_GUNLUK_MAX = 5     # Sonrası: günde 5 ödüllü reklam (+1 fal each)
SINIRSIZ_TIPLER = frozenset({'burc_eslesme'})

TIP_ETIKET = {
    'tarot': 'Tarot',
    'kahve': 'Kahve',
    'astroloji': 'Astroloji',
    'elfali': 'El Falı',
    'diger': 'Diğer Fallar',
}


def _gunluk_veri():
    veri = _yukle()
    bugun = date.today().isoformat()
    fs = veri.get('fal_sayac') or {}
    if fs.get('tarih') != bugun:
        fs = {'tarih': bugun, 'kullanim': {}, 'bonus': {}, 'reklam_izleme': {}}
    else:
        fs.setdefault('kullanim', {})
        fs.setdefault('bonus', {})
        fs.setdefault('reklam_izleme', {})
    veri['fal_sayac'] = fs
    return veri, fs


def fal_durumu(tip):
    if tip in SINIRSIZ_TIPLER:
        return {'sinirsiz': True, 'kalan': 99, 'limit': FAL_GUNLUK_UCRETSIZ}
    _, fs = _gunluk_veri()
    kull = int(fs['kullanim'].get(tip, 0))
    bonus = int(fs['bonus'].get(tip, 0))
    hak = FAL_GUNLUK_UCRETSIZ + bonus
    return {
        'sinirsiz': False,
        'kalan': max(0, hak - kull),
        'limit': FAL_GUNLUK_UCRETSIZ,
        'kullanim': kull,
        'bonus': bonus,
    }


def fal_izinli(tip):
    d = fal_durumu(tip)
    return d.get('sinirsiz') or d['kalan'] > 0


def fal_kullanildi_kaydet(tip):
    if tip in SINIRSIZ_TIPLER:
        return
    veri, fs = _gunluk_veri()
    fs['kullanim'][tip] = int(fs['kullanim'].get(tip, 0)) + 1
    veri['fal_sayac'] = fs
    _kaydet(veri)


def reklam_kalan(tip):
    _, fs = _gunluk_veri()
    izlenen = int((fs.get('reklam_izleme') or {}).get(tip, 0))
    return max(0, REKLAM_GUNLUK_MAX - izlenen)


def reklam_hakki_var(tip):
    """Günde fal türü başına en fazla REKLAM_GUNLUK_MAX ödüllü reklam."""
    _, fs = _gunluk_veri()
    izlenen = int((fs.get('reklam_izleme') or {}).get(tip, 0))
    return izlenen < REKLAM_GUNLUK_MAX


def fal_reklam_bonus(tip):
    if not reklam_hakki_var(tip):
        return False
    veri, fs = _gunluk_veri()
    ri = fs.setdefault('reklam_izleme', {})
    ri[tip] = int(ri.get(tip, 0)) + 1
    fs['bonus'][tip] = int(fs['bonus'].get(tip, 0)) + 1
    veri['fal_sayac'] = fs
    _kaydet(veri)
    return True


def yorum_baslat(tip, devam_fn):
    """Limit uygunsa devam_fn(); değilse reklam popup."""
    if fal_izinli(tip):
        devam_fn()
        return
    if not reklam_hakki_var(tip):
        _reklam_limit_popup(tip)
        return
    _limit_popup(tip, devam_fn)


def _reklam_limit_popup(tip):
    from dil import t

    etiket = TIP_ETIKET.get(tip, tip)
    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
    icerik.add_widget(metin_label(
        t('limit_reklam_doldu', tip=etiket, reklam_max=REKLAM_GUNLUK_MAX),
        font_size='13sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(80),
    ))
    tamam = siyah_buton(t('cookie_close'), vurgu=True, font_size='14sp')
    icerik.add_widget(tamam)

    popup = Popup(
        title=t('limit_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(180),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
    )
    tamam.bind(on_press=lambda *_: popup.dismiss())
    popup.open()


def _limit_popup(tip, devam_fn):
    from dil import t

    etiket = TIP_ETIKET.get(tip, tip)
    d = fal_durumu(tip)
    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
    icerik.add_widget(metin_label(
        t('limit_msg', tip=etiket, limit=d['limit'],
          reklam_kalan=reklam_kalan(tip), reklam_max=REKLAM_GUNLUK_MAX),
        font_size='13sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(72),
    ))
    btn_satir = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
    iptal = siyah_buton(t('limit_no'), font_size='14sp')
    izle = siyah_buton(t('limit_watch_ad'), vurgu=True, font_size='14sp')
    btn_satir.add_widget(iptal)
    btn_satir.add_widget(izle)
    icerik.add_widget(btn_satir)

    popup = Popup(
        title=t('limit_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(200),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
        auto_dismiss=False,
    )

    def _kapat(*_):
        popup.dismiss()

    def _reklam(*_):
        _kapat()
        from reklam import reklam_izle

        def _sonuc(ok):
            if ok:
                fal_reklam_bonus(tip)
                Clock.schedule_once(lambda *_: devam_fn(), 0)
            else:
                _reklam_yok_popup(devam_fn, tip)

        reklam_izle(_sonuc)

    iptal.bind(on_press=_kapat)
    izle.bind(on_press=_reklam)
    popup.open()


def _reklam_yok_popup(devam_fn, tip):
    from dil import t

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(12))
    icerik.add_widget(metin_label(
        t('limit_ad_fail'),
        font_size='13sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(56),
    ))
    btn = siyah_buton(t('limit_retry'), vurgu=True, font_size='14sp')
    icerik.add_widget(btn)

    popup = Popup(
        title=t('limit_title'),
        content=icerik,
        size_hint=(0.85, None),
        height=dp(160),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
    )

    def _tekrar(*_):
        popup.dismiss()
        _limit_popup(tip, devam_fn)

    btn.bind(on_press=_tekrar)
    popup.open()
