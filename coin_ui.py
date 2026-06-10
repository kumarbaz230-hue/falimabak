"""Coin göstergesi (sağ üst) ve reklam popup."""

from kivy.clock import Clock
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex

from coin import (
    FAL_MALIYET, HOSGELDIN_BONUS, REKLAM_COIN_ODUL, REKLAM_GUNLUK_MAX,
    coin_miktar, hosgeldin_kontrol, reklam_hakki_var, reklam_kalan, reklam_coin_kazan,
)
from theme import RENKLER, metin_label, siyah_buton

_CHIPLER = []


def coin_ui_yenile():
    for chip in list(_CHIPLER):
        try:
            chip.guncelle()
        except Exception:
            pass


class CoinChip(ButtonBehavior, BoxLayout):
    """Sağ üst coin butonu."""

    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.size_hint = (None, None)
        self.size = (dp(72), dp(34))
        self.padding = [dp(8), dp(4), dp(10), dp(4)]
        self.spacing = dp(4)
        gold = get_color_from_hex(RENKLER['altin'])
        with self.canvas.before:
            Color(0.12, 0.08, 0.22, 0.92)
            self._bg = RoundedRectangle(radius=[dp(16)])
            Color(gold[0], gold[1], gold[2], 0.55)
            self._kenar = Line(width=dp(1.2), rounded_rectangle=(0, 0, 0, 0, dp(16)))
        self.bind(pos=self._ciz, size=self._ciz)
        self._ikon = metin_label(
            '🪙', font_size='15sp', size_hint_x=None, width=dp(20),
        )
        self._sayi = metin_label(
            '0', font_size='14sp', bold=True, color=RENKLER['altin_parlak'],
            halign='left', size_hint_x=1,
        )
        self.add_widget(self._ikon)
        self.add_widget(self._sayi)
        _CHIPLER.append(self)
        Clock.schedule_once(lambda *_: self.guncelle(), 0)

    def _ciz(self, *_):
        x, y = self.pos
        w, h = self.size
        if w < 1 or h < 1:
            return
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._kenar.rounded_rectangle = (x, y, w, h, dp(16))

    def guncelle(self):
        self._sayi.text = str(coin_miktar())

    def on_release(self):
        coin_popup_goster()

    def __del__(self):
        try:
            _CHIPLER.remove(self)
        except ValueError:
            pass


def coin_satir_ekle(ust_layout):
    """Sağ üste hizalı coin satırı (BoxLayout/vertical içine)."""
    from kivy.uix.anchorlayout import AnchorLayout

    satir = BoxLayout(size_hint_y=None, height=dp(38))
    satir.add_widget(BoxLayout(size_hint_x=1))
    anchor = AnchorLayout(size_hint_x=None, width=dp(80), anchor_x='right', anchor_y='center')
    chip = CoinChip()
    anchor.add_widget(chip)
    satir.add_widget(anchor)
    ust_layout.add_widget(satir)
    return chip


def coin_popup_goster():
    from dil import t
    from reklam import reklam_onyukle, reklam_izle

    reklam_onyukle()
    kalan = reklam_kalan()
    bakiye = coin_miktar()

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
    icerik.add_widget(metin_label(
        t('coin_balance', coin=bakiye),
        font_size='16sp', bold=True, color=RENKLER['altin'],
        halign='center', size_hint_y=None, height=dp(28),
    ))
    icerik.add_widget(metin_label(
        t('coin_fal_cost', cost=FAL_MALIYET),
        font_size='12sp', color=RENKLER['gri_acik'],
        halign='center', size_hint_y=None, height=dp(40),
    ))
    icerik.add_widget(metin_label(
        t('coin_ad_info', odul=REKLAM_COIN_ODUL, kalan=kalan, max=REKLAM_GUNLUK_MAX),
        font_size='12sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(52),
    ))
    btn_satir = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(10))
    kapat = siyah_buton(t('coin_close'), font_size='14sp')
    btn_satir.add_widget(kapat)
    izle = siyah_buton(t('coin_watch_ad', odul=REKLAM_COIN_ODUL), vurgu=True, font_size='14sp')
    if not reklam_hakki_var():
        izle.disabled = True
        izle.opacity = 0.45
    btn_satir.add_widget(izle)
    icerik.add_widget(btn_satir)

    popup = Popup(
        title=t('coin_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(240),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
        auto_dismiss=False,
    )

    def _kapat(*_):
        popup.dismiss()

    def _reklam(*_):
        def _sonuc(ok):
            if ok and reklam_coin_kazan():
                coin_ui_yenile()
                _kapat()
                Clock.schedule_once(lambda *_: coin_popup_goster(), 0.15)
            elif not ok:
                _reklam_hata_popup()

        reklam_izle(_sonuc)

    kapat.bind(on_press=_kapat)
    izle.bind(on_press=_reklam)
    popup.open()


def _reklam_hata_popup():
    from dil import t

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
    icerik.add_widget(metin_label(
        t('limit_ad_fail'),
        font_size='12sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(56),
    ))
    tamam = siyah_buton(t('coin_close'), vurgu=True, font_size='14sp')
    icerik.add_widget(tamam)
    popup = Popup(
        title=t('coin_title'),
        content=icerik,
        size_hint=(0.85, None),
        height=dp(160),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
    )
    tamam.bind(on_press=lambda *_: popup.dismiss())
    popup.open()


def hosgeldin_popup_goster():
    from dil import t

    icerik = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(10))
    icerik.add_widget(metin_label(
        t('coin_welcome', bonus=HOSGELDIN_BONUS),
        font_size='14sp', color=RENKLER['beyaz'],
        halign='center', size_hint_y=None, height=dp(72),
    ))
    tamam = siyah_buton(t('coin_welcome_ok'), vurgu=True, font_size='14sp')
    icerik.add_widget(tamam)
    popup = Popup(
        title=t('coin_welcome_title'),
        content=icerik,
        size_hint=(0.88, None),
        height=dp(200),
        separator_color=get_color_from_hex(RENKLER['altin']),
        title_color=get_color_from_hex(RENKLER['altin']),
    )
    tamam.bind(on_press=lambda *_: popup.dismiss())
    popup.open()
    coin_ui_yenile()


def coin_baslangic_kontrol():
    """Uygulama açılışında hoşgeldin bonusu popup."""
    yeni, _ = hosgeldin_kontrol()
    if yeni:
        Clock.schedule_once(lambda *_: hosgeldin_popup_goster(), 0.6)
    else:
        coin_ui_yenile()
